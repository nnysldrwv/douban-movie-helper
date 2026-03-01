# 🎬 豆瓣电影/读书助手

> 在豆瓣电影详情页直接查看 IMDb / 烂番茄评分，在各种列表页一眼识别自己「看过」「想看」的条目。

[![Greasy Fork](https://img.shields.io/greasyfork/v/567725?label=Greasy%20Fork)](https://greasyfork.org/en/scripts/567725)
[![License](https://img.shields.io/badge/license-MIT-green)](https://opensource.org/licenses/MIT)

## ✨ 功能一览

### 🌟 IMDb & 烂番茄评分（电影详情页）

在豆瓣电影详情页的评分区域下方，自动展示 **IMDb 评分**（/10）和 **烂番茄 Tomatometer**（%），并提供直达链接。

- 优先通过 OMDb API 获取，失败时自动回退抓取 IMDb / RT 原始页面
- 烂番茄采用「搜索 → 详情页」两步法，覆盖率高
- 评分数据多种提取策略逐级降级，确保稳定性

### ✅ 已看 / 已读 · 想看 / 想读 标记（列表页）

浏览 Top 250、排行榜、豆列等页面时，自动检测每部电影/每本书的个人状态，并在标题旁显示醒目标签：

| 标签 | 含义 |
|------|------|
| ✅ 已看 ★★★★☆ | 你看过，并打了 4 星 |
| ✅ 已读 ★★★★★ | 你读过，并打了 5 星 |
| 🎬 想看 | 你标记了想看 |
| 📖 想读 | 你标记了想读 |

- 已看/已读显示为**绿色**标签，附带你的星级评分
- 想看/想读显示为**粉色**标签
- 支持瀑布流/动态加载页面，新内容自动标记

### 🛡️ 防风控 & 智能缓存

- **请求队列**：逐条顺序请求，间隔 800ms，避免触发豆瓣风控
- **本地缓存**：所有状态缓存 3 天，减少重复请求
- **进度提示**：右下角浮动状态栏，实时显示同步队列进度

## 📦 安装

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展（Chrome / Edge / Firefox 均可）
2. 前往 **[Greasy Fork 安装页](https://greasyfork.org/en/scripts/567725)** 点击安装
3. 首次使用时，Tampermonkey 会弹窗请求跨域权限，请点击 **「总是允许」**

## 🌐 支持页面

| 页面 | URL | 功能 |
|------|-----|------|
| 电影详情页 | `movie.douban.com/subject/*` | IMDb / 烂番茄评分 |
| 读书详情页 | `book.douban.com/subject/*` | — |
| 电影 Top 250 | `movie.douban.com/top250` | 已看 / 想看标记 |
| 读书 Top 250 | `book.douban.com/top250` | 已读 / 想读标记 |
| 分类排行榜 | `movie.douban.com/typerank` | 已看 / 想看标记 |
| 选电影 | `movie.douban.com/explore` | 已看 / 想看标记（瀑布流） |
| 读书标签 | `book.douban.com/tag/*` | 已读 / 想读标记 |
| 图书排行榜 | `book.douban.com/chart` | 已读 / 想读标记 |
| 豆列 | `www.douban.com/doulist/*` | 电影 + 书籍混合标记 |

## ⚠️ 注意事项

- 脚本使用公共 OMDb API Key，如遇评分加载失败可申请自己的 [OMDb API Key](https://www.omdbapi.com/apikey.aspx)
- 豆瓣前端更新可能影响部分页面的标签渲染，欢迎 [提 Issue](https://github.com/nnysldrwv/douban-movie-helper/issues) 反馈

## 📄 许可证

[MIT](https://opensource.org/licenses/MIT)
