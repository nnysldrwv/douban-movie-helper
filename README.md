# 豆瓣电影/读书附加功能 Tampermonkey 脚本

这是一个为豆瓣电影和豆瓣读书量身定制的 Tampermonkey (油猴) 脚本，旨在提升你在浏览豆瓣时的体验。

## 主要功能

1. **显示外部权威评分**
   - 在豆瓣电影的详情页中，不仅展示豆瓣评分，还会自动获取并展示 **IMDb 评分** 和 **烂番茄 (Rotten Tomatoes) 评分**。
   - 提供一键直达 IMDb 和烂番茄对应电影页面的快捷链接。

2. **全局智能标记“已看/已读”与星级打分**
   - 在豆瓣的各大列表页面（如 Top250、分类排行榜、选电影/Explore 瀑布流、用户自建的豆列等），自动扫描并标记你已经看过/读过的条目。
   - 显著地以绿色标签（如 `✅ 已看 ★★★★☆` 或 `✅ 已读 ★★★★★`）展示你的标记状态和具体打分。
   - 支持动态加载页面（比如向下滑动不断加载新电影的瀑布流页面），脚本会智能雷达轮询，新出现的条目也会立刻被标记。

3. **安全防风控与本地缓存**
   - 脚本内置了强大的本地缓存机制（看过的缓存 30 天，没看过的缓存 3 天）。
   - 只有未缓存的条目才会向豆瓣服务器发起请求，并采用延迟队列（Queue）顺序请求，避免瞬间高并发请求导致豆瓣账号被封禁（防风控）。

## 安装说明

由于脚本涉及跨域请求（例如访问 OMDb 获取外站评分，以及在当前列表页请求其他详情页判断状态），需要赋予脚本一定的运行权限。

1. **安装 Tampermonkey 插件**：在你的浏览器（Chrome、Edge 等）扩展商店中搜索并安装 Tampermonkey。
2. **新建脚本**：在 Tampermonkey 管理面板中点击“添加新脚本”。
3. **复制代码**：将 `douban_movie_helper.user.js` 中的全部代码复制并粘贴到新建的脚本编辑器中。
4. **保存**：按下 `Ctrl + S` 保存脚本。

*(可选：本地文件同步开发模式)*
如果你想直接加载本地的脚本文件以方便开发和实时更新：
- 在浏览器的扩展管理页面，找到 Tampermonkey 的“详细信息”，开启 **“允许访问文件网址”**。
- 在油猴中新建脚本，输入以下包含 `@require` 和对应 `@grant`、`@connect` 权限的壳子代码（注意修改为你的实际本地路径）：

```javascript
// ==UserScript==
// @name         豆瓣电影/读书附加功能 (本地同步版)
// @namespace    http://tampermonkey.net/
// @version      4.0
// @match        *://movie.douban.com/subject/*
// @match        *://movie.douban.com/top250*
// @match        *://movie.douban.com/typerank*
// @match        *://movie.douban.com/explore*
// @match        *://book.douban.com/subject/*
// @match        *://book.douban.com/top250*
// @match        *://book.douban.com/tag/*
// @match        *://book.douban.com/chart*
// @match        *://www.douban.com/doulist/*
// @grant        GM_xmlhttpRequest
// @grant        GM_setValue
// @grant        GM_getValue
// @connect      imdb.com
// @connect      movie.douban.com
// @connect      book.douban.com
// @connect      omdbapi.com
// @require      file:///d:/AIWorkspace/doubanscript/douban_movie_helper.user.js
// ==/UserScript==
```

## 支持的页面范围

* 豆瓣电影 / 豆瓣读书 详情页
* 豆瓣电影 / 豆瓣读书 Top250
* 豆瓣电影 分类排行榜 (`typerank`)
* 豆瓣电影 选电影 (`explore`)
* 豆瓣读书 标签分类页 (`tag`)
* 豆瓣读书 图书排行榜 (`chart`)
* 用户自建的综合豆列 (`doulist`)

## 注意事项

* 初次在电影页获取 IMDb / 烂番茄评分时，Tampermonkey 可能会弹窗提示是否允许跨域访问 `omdbapi.com`，请点击 **“总是允许” (Always allow)**。
* 因为网页结构的差异和豆瓣前端的偶尔更新，少数特殊结构的豆列或特殊条目可能无法精确渲染标签。

## 许可证

MIT License
