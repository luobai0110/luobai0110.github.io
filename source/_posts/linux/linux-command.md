---
title: linux命令杂记
date: 2024-12-22 15:47:20
category:
  - linux
tag:
  - 炸鸡
  - linux
---

## 添加用户到组

```bash
sudo usermod -aG <groupname> <username>
```

- **a**: 表示追加, 不会覆盖用户原有的组
- **G**: 指定组名

示例

```bash
sudo usermod -aG docker doomer
```

配置使用`newgrp`命令可以不重新登录

```bash
sudo newgrp docker
```

可以使用`groups <username>`或者`id <username>` 验证是否加入成功

```BASH
groups doomer
```

输出

```bash
doomer : doomer cdrom floppy audio dip video plugdev users netdev docker
```
