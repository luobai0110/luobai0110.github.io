---
title: "MyBatis 动态 SQL 中固定过滤条件的注意事项"
date: 2026-10-10
categories: ["后端开发"]
tags: ["MyBatis", "SQL", "动态SQL", "Java"]
description: "MyBatis 的 trim 标签在动态条件全部未命中时，紧跟其后的固定过滤条件会被拼进 JOIN 的 ON 子句，导致软删除数据被查出。记录成因与三种正确写法。"
ShowToc: true
---

用 MyBatis 动态标签拼 SQL 时，如果过滤条件里混着「固定条件」（比如软删除标记 `is_deleted = 0`），它出现的位置就很关键。当 `<trim>` 里的动态条件一个都没命中时，紧跟在 `<trim>` 后面的固定条件不会变成 `WHERE` 条件，而是被 SQL 解析器当成前面 `JOIN ... ON` 的一部分 —— 查询语义就此改变，软删除的数据会被照常查出来。

下面还原这个坑：怎么触发、为什么会这样、以及三种正确写法。

## 问题复现

### 有问题的写法

```xml
<select id="adminPageOrder" resultType="cn.yyt.shop.pay.general.model.dto.OrderPageResultDTO">
    SELECT
        *
    FROM order_item oi
    LEFT JOIN order_pay_sec ops
        ON oi.order_item_code = ops.order_item_code
        AND ops.is_valid = 1
    LEFT JOIN order_pay op
        ON ops.order_pay_code = op.order_pay_code
        AND op.pay_status = 2
    <trim prefix="WHERE" prefixOverrides="AND |OR">
        <if test="orderItemCode != null and orderItemCode != ''">
            AND oi.order_item_code = #{orderItemCode}
        </if>
        <if test="startTime != null">
            AND oi.create_time >= #{startTime}
        </if>
    </trim>
    AND oi.is_deleted = 0
    ORDER BY oi.create_time DESC, oi.id
</select>
```

（`<if>` 只是示意，重点在于：这两个动态条件有可能同时不成立。）

### 动态条件全部未命中时生成的 SQL

`<trim>` 内没有任何内容时，它既不会输出 `WHERE`，也不会输出任何条件，于是变成这样：

```sql
SELECT
    *
FROM order_item oi
LEFT JOIN order_pay_sec ops
    ON oi.order_item_code = ops.order_item_code
    AND ops.is_valid = 1
LEFT JOIN order_pay op
    ON ops.order_pay_code = op.order_pay_code
    AND op.pay_status = 2
AND oi.is_deleted = 0
ORDER BY oi.create_time DESC, oi.id
```

注意 `AND oi.is_deleted = 0` 前面已经没有任何 `WHERE` 了。它悬空在 `LEFT JOIN order_pay op` 的 `ON` 后面，于是被解析成这个 `ON` 条件的一部分，等价于：

```sql
LEFT JOIN order_pay op
    ON ops.order_pay_code = op.order_pay_code
    AND op.pay_status = 2
    AND oi.is_deleted = 0
```

### 后果

`oi.is_deleted = 0` 从「`order_item` 要满足什么条件」变成了「`order_pay` 这张表怎么关联」。因为是 `LEFT JOIN`，左表 `order_item` 的行无论如何都会保留：被软删除的订单项依然出现在结果里，只是关联出来的 `order_pay` 字段变成 `NULL`。

这比直接报错更难发现 —— SQL 能跑通，结果也「看起来正常」，只有拿数据核对时才会发现多了一批本该过滤掉的记录。

## 为什么会拼到 ON 里

根因在 SQL 语法本身：`ON` 后面接的是一个布尔表达式，而 `AND` 是表达式运算符，所以 `ON a = b AND c = d` 里的 `AND c = d` 天然属于这个 `ON`。SQL 并没有「`AND` 必须归属于最近的 `WHERE`」这种规则。

由此可以提炼出一条判据：

> 以 `AND` / `OR` 开头的条件，前面必须已经存在 `WHERE`；否则它会被粘到最近的 `ON` 上。如果整条语句里连 `JOIN` 都没有，那就是直接的语法错误（`SELECT * FROM t AND x = 1` 根本跑不起来）。

所以这类问题的表现分两种：没有 JOIN 时立刻报错，属于好事，能马上发现；有 JOIN 时则静默改变语义，属于坏事，容易漏到线上。

## 正确写法

### 方式一：把固定条件放进 `<trim>` 内部（推荐）

让固定条件和动态条件待在同一个容器里。`<trim>` 只要有任何内容，就会补上 `WHERE`，并把开头的 `AND` 去掉：

```xml
<select id="adminPageOrder" resultType="cn.yyt.shop.pay.general.model.dto.OrderPageResultDTO">
    SELECT
        *
    FROM order_item oi
    LEFT JOIN order_pay_sec ops
        ON oi.order_item_code = ops.order_item_code
        AND ops.is_valid = 1
    LEFT JOIN order_pay op
        ON ops.order_pay_code = op.order_pay_code
        AND op.pay_status = 2
    <trim prefix="WHERE" prefixOverrides="AND |OR">
        AND oi.is_deleted = 0
        <if test="orderItemCode != null and orderItemCode != ''">
            AND oi.order_item_code = #{orderItemCode}
        </if>
        <if test="startTime != null">
            AND oi.create_time >= #{startTime}
        </if>
    </trim>
    ORDER BY oi.create_time DESC, oi.id
</select>
```

无论动态条件是否命中，生成的 SQL 都成立：

```sql
-- 动态条件全部未命中
WHERE oi.is_deleted = 0

-- 动态条件命中时（开头的 AND 已被 prefixOverrides 去掉，WHERE 由 prefix 补上）
WHERE oi.is_deleted = 0 AND oi.order_item_code = ? AND oi.create_time >= ?
```

### 方式二：改用 `<where>` 标签

`<where>` 就是 `<trim prefix="WHERE" prefixOverrides="AND |OR">` 的语法糖，语义完全一致，写起来更短：

```xml
    <where>
        AND oi.is_deleted = 0
        <if test="orderItemCode != null and orderItemCode != ''">
            AND oi.order_item_code = #{orderItemCode}
        </if>
    </where>
```

### 方式三：用 `WHERE 1 = 1` 占位

老项目里常见：用一个恒真条件把 `WHERE` 钉死，后面的 `AND` 就都有着落了。

```xml
    WHERE 1 = 1
    AND oi.is_deleted = 0
    <if test="orderItemCode != null and orderItemCode != ''">
        AND oi.order_item_code = #{orderItemCode}
    </if>
```

代价是每个条件都得自己带 `AND`，而且 `1 = 1` 会一直留在最终 SQL 里。能用方式一就不必用它。

## 小结

- 固定过滤条件不要留在可能为空的 `<trim>` 外面，尤其不要紧跟在 `</trim>` 后面。
- 记住判据：以 `AND` / `OR` 开头的条件，前面必须已有 `WHERE`，否则会被吸进最近的 `ON`。
- 首选把固定条件写进 `<trim>` / `<where>` 内部；维护老代码时再用 `WHERE 1 = 1`。
- 自查很快：在 mapper 里搜 `</trim>` 或 `</where>` 紧跟 `AND` / `OR` 的位置，正则 `</(trim|where)>\s*(AND|OR)\b` 命中的都值得看一眼。
