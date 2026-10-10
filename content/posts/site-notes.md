---
title: "本站说明：结构、写作与部署"
date: 2026-10-10
categories: ["站点说明"]
tags: ["Hugo", "PaperMod", "建站", "GitHub Pages"]
description: "这个站点是怎么搭起来的、文章怎么写、分类和标签怎么用、怎么发布上线。"
ShowToc: true
TocOpen: true
---

这篇把站点的构成和使用方式写清楚，以后忘了可以直接回来查。

## 技术栈

| 部分 | 用的是什么 |
| --- | --- |
| 静态站点生成器 | [Hugo](https://gohugo.io/) 0.167.0（extended） |
| 主题 | [PaperMod](https://github.com/adityatelange/hugo-PaperMod) |
| 源码仓库 | [luobai0110/luobai0110.github.io](https://github.com/luobai0110/luobai0110.github.io) |
| 构建与部署 | GitHub Actions 构建 → GitHub Pages 发布 |
| 访问域名 | `https://doomer.dpdns.org/` |

源码留在 `main` 分支，`public/` 不进仓库 —— 每次 `git push` 后由 Actions 现场用 Hugo 构建再发布。所以**不要手动提交 `public/`**，它已经在 `.gitignore` 里了。

## 目录结构

```
.
├── .github/workflows/hugo.yaml   # 自动构建 + 部署流水线
├── archetypes/default.md         # hugo new 生成新文章时的模板
├── assets/                       # 需要 Hugo 处理的资源（可选）
├── content/                      # 所有内容都在这
│   ├── archives.md               # 归档页（layout: archives）
│   ├── search.md                 # 搜索页（layout: search）
│   └── posts/                    # 文章目录，首页列表就取这里
├── data/  i18n/  layouts/        # 目前为空，需要时再放东西
├── static/                       # 原样拷贝到站点根目录的文件
│   ├── CNAME                     # 自定义域名，删了域名就失效
│   └── favicon*                  # 网站图标
├── themes/PaperMod/              # 主题（git submodule）
└── hugo.yaml                     # 站点配置
```

## 写一篇新文章

```bash
hugo new content posts/我的新文章.md
```

也可以直接在 `content/posts/` 下建 `.md` 文件。front matter 常用字段：

```yaml
---
title: "文章标题"
date: 2026-10-10                 # 必填。归档页按这个日期分年月
categories: ["随笔"]             # 分类，建议少而稳定
tags: ["Hugo", "建站"]           # 标签，可以多而具体
description: "一句话摘要"         # 用于 SEO 和社交分享卡片
ShowToc: true                    # 是否显示目录
draft: true                      # 草稿：本地可见，构建时不发布
---
```

写完记得把 `draft` 去掉或改成 `false`，否则线上看不到。

## 分类与标签

配置在 `hugo.yaml` 的 `taxonomies` 里，用的是 Hugo 默认的 `categories` 和 `tags`。只要在 front matter 里写了，Hugo 就会自动生成这些页面，不需要任何模板：

- `/categories/`、`/tags/` —— 所有分类／标签的汇总，带文章数
- `/categories/随笔/`、`/tags/Hugo/` —— 某个分类／标签下的文章列表

区别在于：**分类**适合表达「这属于哪一类」，数量少、相对固定；**标签**适合表达「涉及哪些点」，可以有很多。导航栏已经放好了「分类」「标签」两个入口。

## 归档与搜索

**归档页**（`/archives/`）由 `content/archives.md` 指定 `layout: archives` 启用，按年份和月份分组列出文章。它只列 `hugo.yaml` 里 `mainSections` 指定的 section（目前是 `posts`），并且依赖文章的 `date` 字段来分组。

**搜索页**（`/search/`）由 `content/search.md` 指定 `layout: search` 启用，纯前端模糊搜索，数据来自 `/index.json` —— 这就是 `hugo.yaml` 里 `outputs.home` 必须包含 `JSON` 的原因。搜索的匹配参数在 `params.fuseOpts` 里调。

## 本地预览与发布

```bash
hugo server -D          # 本地预览，含草稿；改文件会热重载
hugo server             # 本地预览，不含草稿
hugo --gc --minify      # 手动构建到 public/（CI 用的就是这条）
```

发布就是提交推送：

```bash
git add -A
git commit -m "post: 新文章"
git push
```

推上去之后 Actions 会自动跑构建和部署，去仓库的 Actions 页面能看到进度。

## 几个踩过的坑

- **`baseURL` 结尾必须有斜杠**：`https://doomer.dpdns.org/`。少了斜杠线上 CSS/JS 会全部 404。
- **`mainSections` 决定首页和归档显示什么**：PaperMod 直接读这个值，不配置的话首页会是空的。文章要放在 `content/posts/` 下。
- **Hugo 0.158 起 `languageCode` 已废弃**，改用 `locale`。
- **代码高亮要 `noClasses: false`**：Hugo 默认是 `true`，而 PaperMod 的高亮样式依赖 CSS class。
- **归档只认 `date`**：没有日期的文章不会出现在归档里。
- **改了 `hugo.yaml` 要重新 push** 才会生效，线上不认识本地文件。
