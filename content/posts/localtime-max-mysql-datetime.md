---
title: 'LocalTime.MAX 遇上 MySQL 时间精度：按天查询多查了第二天'
date: '2026-11-26T14:40:00+08:00'
categories: ['数据库']
tags: ['MySQL', 'Java', '时间处理', 'MyBatis']
description: '按天查询用 date.atTime(LocalTime.MAX) 当右边界，Java 给出 23:59:59.999999999，而 MySQL 的时间类型最多到微秒：多出来的位数被四舍五入，右边界进位成次日 00:00:00，闭区间 BETWEEN 于是把第二天的临界数据也查了出来。'
ShowToc: true
---

按天统计时，右边界习惯写成 `date.atTime(LocalTime.MAX)`。这在 Java 里是 `2026-11-22T23:59:59.999999999` —— 纳秒精度；而 MySQL 的 `DATETIME` / `TIMESTAMP` 最多只到微秒（6 位）。超出的位数不会被丢掉，而是被**四舍五入**：`.999999999` 逐位进位到整秒，右边界实际变成了 `2026-11-23 00:00:00`。

于是 `BETWEEN '2026-11-22 00:00:00' AND '2026-11-22 23:59:59.999999999'` 等价于 `BETWEEN '2026-11-22 00:00:00' AND '2026-11-23 00:00:00'`，第二天零点整的那批数据就被算进了前一天。

## 问题

### 现象

一条按天统计退款明细的 SQL：

```mysql
SELECT * FROM `order_refund_detail`
WHERE create_time BETWEEN '2026-11-22 00:00:00' AND '2026-11-22 23:59:59.999999999';
```

结果里出现了 `create_time = '2026-11-23 00:00:00'` 的记录。

### 右边界是怎么来的

区间由这段代码生成：

```java
public static DateRangeDTO dateRange(LocalDate date) {
    return new DateRangeDTO(date.atStartOfDay(), date.atTime(LocalTime.MAX));
}
```

`LocalTime.MAX` 就是 `23:59:59.999999999`，所以 `endTime` 的时间部分精确到了纳秒。

### 真正执行的 SQL

业务侧用 MyBatis-Plus 拼条件：

```java
List<OrderRefundDetailPO> orderRefundDetailList = orderRefundDetailMapper.selectList(new LambdaQueryWrapper<OrderRefundDetailPO>()
        .in(OrderRefundDetailPO::getRefundWay, List.of(2, 3))
        .ne(OrderRefundDetailPO::getIsValid, 2)
        .between(BaseEntity::getCreateTime, dateRangeDTO.getStartTime(), dateRangeDTO.getEndTime())
);
```

`between` 会把首尾两个时间作为参数绑进去，生成的 SQL 形如：

```mysql
SELECT * FROM order_refund_detail
WHERE refund_way IN (2, 3)
  AND is_valid <> 2
  AND create_time BETWEEN ? AND ?
-- ? = 2026-11-22 00:00:00
-- ? = 2026-11-22 23:59:59.999999999
```

问题在第二个参数上。

## 原因

### 精度对不上：9 位 vs 6 位

Java 的 `LocalDateTime` 是纳秒精度，秒的小数部分取值 `0 ~ 999999999`，也就是 9 位。MySQL 的时间类型最高只有微秒精度，`fsp` 只允许 0 到 6：

```sql
CREATE TABLE t1 (t TIME(3), dt DATETIME(6));
```

`fsp`（fractional seconds precision）不写就是 0，连秒以下都不要。`.999999999` 的最后三位在 MySQL 里无处安放。

### 多出来的位是舍入，不是截断

这是整件事的关键。官方手册「时间值中的小数秒」一节写得很明确：把带小数秒的值放进同类型但小数位数更少的列，会发生**舍入（rounding）**，并且**不产生任何警告或错误**；想改成截断，得显式打开 `TIME_TRUNCATE_FRACTIONAL` SQL 模式。

所以 `.999999999` 不是被砍成 `.999999`，而是：

```
2026-11-22 23:59:59.999999999
  ↓ 舍入到 6 位（小数第 7 位是 9，进一位）
2026-11-22 23:59:59.999999 + 0.000001
  ↓ 秒的小数部分满 1，向秒进位
2026-11-23 00:00:00.000000
```

秒进到 60，再进到分、时、日 —— 右边界整整跳到了第二天零点。

注意舍入的目标精度取决于**参与比较的那个类型**，不一定都是 6 位：

- 字面量与 `DATETIME(6)` 列比较 → 舍到 6 位，`.999999999` 进位到次日 `00:00:00`；
- 字面量与 `DATETIME(0)`（也就是建表只写 `datetime` 的常见情况）比较 → 舍到秒，`.999999` 同样进位到次日 `00:00:00`。

两种列精度下，只要右边界是「当天 23:59:59 加上一长串 9」，就都会踩到。

## 复现

在 MySQL 8.0.36 上按顺序执行

```mysql
-- 以该SQL举例, 临界的SQL为
SELECT create_time FROM `order_refund_detail`
WHERE create_time BETWEEN '2026-11-22 00:00:00' and '2026-11-22T23:59:59.9999995'
ORDER BY create_time DESC
LIMIT 1;
-- 结果: 2026-11-23 00:00:00
SELECT create_time FROM `order_refund_detail`
WHERE create_time BETWEEN '2026-11-22 00:00:00' and '2026-11-22T23:59:59.9999994'
ORDER BY create_time DESC
LIMIT 1
-- 结果: 2026-11-22 23:54:04
-- 
```
## 解决方案

### 方案一：改用半开区间 `[当天 00:00:00, 次日 00:00:00)`


```java
public static DateRangeDTO dateRange(LocalDate date) {
    return new DateRangeDTO(date.atStartOfDay(), date.plusDays(1).atStartOfDay());
}
```

```java
List<OrderRefundDetailPO> orderRefundDetailList = orderRefundDetailMapper.selectList(new LambdaQueryWrapper<OrderRefundDetailPO>()
        .in(OrderRefundDetailPO::getRefundWay, List.of(2, 3))
        .ne(OrderRefundDetailPO::getIsValid, 2)
        .ge(BaseEntity::getCreateTime, dateRangeDTO.getStartTime())
        .lt(BaseEntity::getCreateTime, dateRangeDTO.getEndTime())
);
```

生成的 SQL：

```mysql
create_time >= '2026-11-22 00:00:00' AND create_time < '2026-11-23 00:00:00'
```

代价是语义改了：`DateRangeDTO.endTime` 从「闭区间终点」变成「开区间终点」。同一个 DTO 若在别处按闭区间使用，要一起改，并在字段注释里写清是否包含。

### 方案二：手动设置尾部的时间精度

由于本次`BUG`的截止条件是工具类引入的, 且未涉及到核心的业务, 所以更改工具类的时间是代码改动量最小的改动

```java
    public static DateRangeDTO dateRange(LocalDate date) {
   return new DateRangeDTO(date.atStartOfDay(), date.atTime(23, 59, 59, 999_000_000));
}
```

右边界变成 `2026-11-22 23:59:59.999`，不会再进位。

## 小结

- `LocalTime.MAX` 是 `23:59:59.999999999`，纳秒精度；MySQL 的时间类型最多到微秒，`fsp` 取值 0 ~ 6。
- 超出精度的位数 MySQL 按**四舍五入**处理，且不告警：`.999999999` 一路进位到 `次日 00:00:00`，闭区间 `BETWEEN` 就把第二天零点整的数据框了进来。
- 舍入的目标精度跟着参与比较的类型走，列是 `DATETIME(0)` 时连 `.999999` 都会进位，所以这不是「9 位小数」独有的问题。
- 顶层修法是半开区间 `>= 当天 00:00:00 AND < 次日 00:00:00`，对列精度和值精度都不敏感。
- 这类问题的共同特征是「不报错、不告警、只在跨天边界多几条」，靠日常抽查发现不了，只能靠边界数据的固定用例兜住。
