---
title: 'SQL优化杂记'
date: '2026-10-13T10:02:42+08:00'
draft: true
tags: ['SQL优化']
categories: ['数据库']
description: '关联字段类型不一致会导致索引失效：一条 3 分 15 秒的 SQL，只在 join 条件上做一次显式类型转换，就降到 1 秒以内。'
ShowToc: true
---

关联条件两边的字段类型不一致时，数据库无法直接用索引定位，只能退化成全表扫描。这次的 SQL 从 **3 分 15 秒** 降到 **874 毫秒**，改动只有一处：把 join 条件里的字段类型显式转换一下。

## 问题

### 表结构

```mysql
create table pay_order
(
    id               bigint                                not null comment '统计编号'
        primary key,
    nonce_str        varchar(64)                           not null comment '随机串',
    status           int                                   not null comment '订单状态，0-发起，1-支付中（预提交），2-成功， 3-失败',
    -- others
)
    charset = utf8mb4;
create index IDX_sc_order_pay_way_pay_no
    on sc_order_pay_way (pay_no);

create index idx_orderid_biztype_CREATEDBY_officeid_paytype
    on sc_order_pay_way (order_id, biz_type, CREATED_BY, office_id, pay_type);

create index idx_pay_way_id
    on sc_order_pay_way (order_id);

create index ix_pay_way_payno
    on sc_order_pay_way (pay_type, pay_no, CREATED_DATE, tenant_id);

create index order_pay_way_idx
    on sc_order_pay_way (pay_type, office_id, CREATED_DATE);

```

注意 `id` 是 `bigint`，而 `nonce_str` 是 `varchar(64)`，两者类型并不一致 —— 这就是后面的根因。

### 慢查询

```mysql
SELECT *
FROM sc_pos_order spo
         LEFT JOIN sc_order_pay_way sopw on sopw.order_id = spo.id and sopw.pay_type = xxx
         LEFT JOIN pay_order po on sopw.pay_no = po.nonce_str
         LEFT JOIN pay_order poo on poo.prepay_id = po.id AND poo.status = x
         JOIN sys_common_human sch ON spo.human_id = sch.human_id
WHERE spo.seller_id = xxx
ORDER BY barcode;
```

执行耗时：

```
[2026-10-13 10:13:34] 在 3 m 16 s 38 ms (execution: 3 m 15 s 476 ms, fetching: 562 ms) 内检索到从 1 开始的 103 行
```

执行计划：

```
SELECT (select)
NESTED_LOOPS (nested loops)      1259390   Using where; Using temporary; Using filesort
SORT (Using filesort)            1259390   Using where; Using temporary; Using filesort
TEMPORARY (Using temporary)      1259390   Using where; Using temporary; Using filesort
SEQ_SCAN (ALL)   table: spo;     1259390   Using where; Using temporary; Using filesort
UNIQUE_INDEX_SCAN (eq_ref)   table: sch;  index: PRIMARY;   1
UNIQUE_INDEX_SCAN (ref)      table: sopw; index: idx_orderid_biztype_CREATEDBY_officeid_paytype;  1   Using where
UNIQUE_INDEX_SCAN (ref)      table: po;   index: idx_nonce_str;   1   Using where
SEQ_SCAN (ALL)   table: poo;     1664776   Using where; Using join buffer (Block Nested Loop)
```

问题出在 `poo` 这一行：`table: poo` 走的是 `SEQ_SCAN (ALL)`，扫描了 166 万行，还退化成 `Block Nested Loop`。它本该用索引定位。

## 原因

关联条件是 `poo.prepay_id = po.id`。`po.id` 是 `bigint`，当 `poo.prepay_id` 的字段类型与它不一致时，数据库需要在关联时对两边做隐式类型转换；一旦字段被函数或转换包住，`prepay_id` 上的索引就无法用于定位，优化器只能放弃索引、改成全表扫描 + join buffer。

## 优化

在关联时先把 `po.id` 显式转换成与关联字段一致的类型：

```mysql
...
LEFT JOIN pay_order poo on poo.prepay_id = cast(po.id as char) AND poo.status = x
...
```

执行耗时：

```
[2026-10-13 10:15:39] 在 1 s 487 ms (execution: 874 ms, fetching: 613 ms) 内检索到从 1 开始的 103 行
```

执行计划：

```
SELECT (select)
NESTED_LOOPS (nested loops)      1259391   Using where; Using filesort
SORT (Using filesort)            1259391   Using where; Using filesort
SEQ_SCAN (ALL)   table: spo;     1259391   Using where; Using filesort
UNIQUE_INDEX_SCAN (eq_ref)   table: sch;  index: PRIMARY;   1
UNIQUE_INDEX_SCAN (ref)      table: sopw; index: idx_orderid_biztype_CREATEDBY_officeid_paytype;  1   Using where
UNIQUE_INDEX_SCAN (ref)      table: po;   index: idx_nonce_str;   1   Using where
UNIQUE_INDEX_SCAN (ref)      table: poo;  index: tmp_idx_prepay;   3   Using where
```

对比可以看到三处变化：

- `poo` 从 `SEQ_SCAN (ALL)` 变成 `UNIQUE_INDEX_SCAN (ref)`，扫描行数从 166 万降到 3 行，`Block Nested Loop` 也消失了；
- 执行计划里不再有 `TEMPORARY`，临时表开销省掉了；
- 总耗时从 3 分 15 秒降到 874 毫秒。

## 小结

- 关联字段两边类型不一致会触发隐式类型转换，使被转换字段上的索引失效，优化器只能走全表扫描。
- 在关联条件中显式转换类型（本例 `cast(po.id as char)`），比让数据库隐式转换更容易命中索引。
- 治本的做法是建表时就统一关联字段的类型；已经上线的表，则在 SQL 层显式转换。
- 定位手段很直接：看执行计划里是否出现 `SEQ_SCAN (ALL)` / `Using join buffer`，出现就说明该表的索引没被用上。
