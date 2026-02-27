# 🎬 豆瓣电影/读书附加功能

> 一个为豆瓣电影和豆瓣读书量身定制的 Tampermonkey 油猴脚本，让你的豆瓣浏览体验更上一层楼。

![Version](https://img.shields.io/badge/version-4.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tampermonkey](https://img.shields.io/badge/Tampermonkey-compatible-brightgreen)

## ✨ 功能特性

### 🌟 IMDb & 烂番茄评分展示

在豆瓣电影详情页中，自动获取并展示 **IMDb 评分** 和 **烂番茄 (Rotten Tomatoes) 评分**，无需跳转即可对比多平台评分。同时提供一键直达 IMDb / 烂番茄对应页面的快捷链接。

### ✅ 智能标记「已看 / 已读」与星级打分

在豆瓣各大列表页面自动扫描，用醒目的绿色标签标记你看过/读过的条目及打分：

```
✅ 已看 ★★★★☆
✅ 已读 ★★★★★
```

支持动态加载的瀑布流页面 —— 新加载的条目也会自动被标记。

### 🛡️ 安全防风控 & 本地缓存

- **差异化缓存策略**：已看/已读条目缓存 30 天，未看条目缓存 3 天
- **延迟请求队列**：逐条顺序请求，间隔 800ms，避免高并发触发豆瓣风控
- **实时进度提示**：右下角浮动状态栏显示同步队列进度

## 📦 安装

### 前置条件

- 现代浏览器（Chrome / Edge / Firefox 等）
- [Tampermonkey](https://www.tampermonkey.net/) 浏览器扩展

1. 安装 [Tampermonkey](https://www.tampermonkey.net/) 扩展
2. 打开 Tampermonkey 管理面板 → 点击 **「添加新脚本」**
3. 将 [`douban_movie_helper.user.js`](./douban_movie_helper.user.js) 的全部代码复制粘贴到编辑器中
4. `Ctrl + S` 保存即可

## 🌐 支持的页面

| 页面类型 | URL 模式 | 说明 |
|---------|---------|------|
| 电影详情页 | `movie.douban.com/subject/*` | IMDb/烂番茄评分 + 已看标记 |
| 读书详情页 | `book.douban.com/subject/*` | 已读标记 |
| 电影 Top 250 | `movie.douban.com/top250` | 已看标记 |
| 读书 Top 250 | `book.douban.com/top250` | 已读标记 |
| 分类排行榜 | `movie.douban.com/typerank` | 已看标记 |
| 选电影 | `movie.douban.com/explore` | 已看标记（瀑布流） |
| 读书标签页 | `book.douban.com/tag/*` | 已读标记 |
| 图书排行榜 | `book.douban.com/chart` | 已读标记 |
| 豆列 | `www.douban.com/doulist/*` | 电影/书籍混合标记 |

## ⚠️ 注意事项

- 首次使用时，Tampermonkey 可能弹窗请求跨域访问 `omdbapi.com` 的权限，请点击 **「总是允许」**
- 豆瓣前端偶尔更新可能影响少数特殊页面的标签渲染
- 脚本使用公共 OMDb API Key，如遇评分加载失败可尝试申请自己的 [OMDb API Key](https://www.omdbapi.com/apikey.aspx)

## 🔧 技术实现

- **评分获取**：通过 [OMDb API](https://www.omdbapi.com/) 根据 IMDb ID 获取评分数据
- **状态检测**：解析豆瓣详情页 HTML，匹配多种 DOM 结构识别用户的「看过/读过」状态及星级
- **缓存层**：基于 Tampermonkey 的 `GM_setValue` / `GM_getValue` 实现持久化本地缓存
- **请求调度**：自建 FIFO 队列 + 800ms 间隔，兼顾效率与安全

## 📄 许可证

[MIT License](https://opensource.org/licenses/MIT) — 随意使用、修改和分发。
