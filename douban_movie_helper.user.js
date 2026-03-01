// ==UserScript==
// @name         豆瓣电影/读书附加功能 (IMDb评分 + 标记看过/已读及评分)
// @name:en      Douban Movie & Book Helper (IMDb/RT Ratings + Watched/Read Marker)
// @namespace    https://github.com/nnysldrwv/douban-movie-helper
// @version      4.9
// @description  在豆瓣电影详情页显示IMDb/烂番茄评分，列表页自动标记已看/已读状态及星级打分。智能缓存+请求队列防风控。
// @description:en  Show IMDb & Rotten Tomatoes ratings on Douban movie pages. Auto-mark watched/read items with star ratings in list views. Smart caching & request queue to avoid rate limiting.
// @author       nnysldrwv
// @license      MIT
// @homepageURL  https://github.com/nnysldrwv/douban-movie-helper
// @supportURL   https://github.com/nnysldrwv/douban-movie-helper/issues
// @compatible   chrome
// @compatible   firefox
// @compatible   edge
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
// @connect      www.omdbapi.com
// @connect      www.imdb.com
// @connect      rottentomatoes.com
// @connect      www.rottentomatoes.com
// @icon         https://img3.doubanio.com/favicon.ico
// ==/UserScript==

(function() {
    'use strict';

    const isSubjectPage = window.location.href.includes('/subject/');
    const isDoulistPage = window.location.href.includes('/doulist/');
    const isMovieListPage = window.location.href.includes('movie.douban.com') && !isSubjectPage;
    const isBookListPage = window.location.href.includes('book.douban.com') && !isSubjectPage;

    // 仅在电影详情页获取 IMDb 评分
    if (isSubjectPage && window.location.href.includes('movie.douban.com')) {
        handleSubjectPage();
    }

    // 列表页和豆列页执行“已看/已读”扫描
    if (isMovieListPage || isBookListPage || isDoulistPage) {
        handleListPages();
    }

    // ==========================================
    // 功能 1：在详情页获取并展示 IMDb 评分与烂番茄评分
    // ==========================================
    function handleSubjectPage() {
        const infoDiv = document.getElementById('info');
        if (!infoDiv) return;

        // 正则提取 IMDb 编号
        const match = infoDiv.innerText.match(/IMDb:\s*(tt\d+)/);
        if (match && match[1]) {
            const imdbId = match[1];
            fetchMovieRatings(imdbId);
        }
    }

    function fetchMovieRatings(imdbId) {
        // 先尝试 OMDb API，失败后回退到直接抓取 IMDb 页面
        console.log('[DBHelper] Fetching OMDb for', imdbId);
        GM_xmlhttpRequest({
            method: "GET",
            url: `https://www.omdbapi.com/?i=${imdbId}&apikey=thewdb`,
            timeout: 8000,
            onload: function(response) {
                if (response.status === 200) {
                    try {
                        const data = JSON.parse(response.responseText);
                        console.log('[DBHelper] OMDb response:', data.Response, 'Ratings:', data.Ratings);
                        if (data.Response === "True") {
                            let imdbRating = data.imdbRating && data.imdbRating !== 'N/A' ? data.imdbRating : '暂无';
                            let rtRating = '暂无';
                            if (data.Ratings && data.Ratings.length > 0) {
                                const rt = data.Ratings.find(r => r.Source === 'Rotten Tomatoes');
                                if (rt) rtRating = rt.Value;
                            }
                            // 如果 OMDb 拿到了 IMDb 评分但没有 RT，单独补抓 RT
                            if (rtRating === '暂无') {
                                console.log('[DBHelper] OMDb missing RT, fetching from RT directly');
                                fetchRTScore(imdbId, imdbRating);
                            } else {
                                displayRatings(imdbRating, rtRating, imdbId);
                            }
                            return;
                        }
                    } catch (e) {
                        console.warn('[DBHelper] OMDb parse error:', e);
                    }
                }
                // OMDb 完全失败，回退到直接抓取 IMDb + RT
                console.log('[DBHelper] OMDb failed, falling back to IMDb direct');
                fetchIMDbDirect(imdbId);
            },
            onerror: function() {
                console.warn('[DBHelper] OMDb network error');
                fetchIMDbDirect(imdbId);
            },
            ontimeout: function() {
                console.warn('[DBHelper] OMDb timeout');
                fetchIMDbDirect(imdbId);
            }
        });
    }

    // 备用方案：直接从 IMDb 页面抓取评分（精确解析 JSON-LD aggregateRating）
    function fetchIMDbDirect(imdbId) {
        console.log('[DBHelper] Fetching IMDb direct for', imdbId);
        GM_xmlhttpRequest({
            method: "GET",
            url: `https://www.imdb.com/title/${imdbId}/`,
            headers: { "Accept-Language": "en-US,en;q=0.9" },
            timeout: 10000,
            onload: function(response) {
                if (response.status === 200) {
                    const html = response.responseText;
                    let imdbRating = '暂无';
                    // 精确提取 JSON-LD 中 aggregateRating 块的 ratingValue
                    const ldBlocks = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi);
                    if (ldBlocks) {
                        for (const block of ldBlocks) {
                            try {
                                const jsonStr = block.replace(/<script[^>]*>/, '').replace(/<\/script>/i, '');
                                const ld = JSON.parse(jsonStr);
                                if (ld.aggregateRating && ld.aggregateRating.ratingValue) {
                                    imdbRating = String(ld.aggregateRating.ratingValue);
                                    break;
                                }
                            } catch (e) { /* try next block */ }
                        }
                    }
                    // 如果 JSON-LD 解析失败，使用备用正则（限定 aggregateRating 上下文）
                    if (imdbRating === '暂无') {
                        const aggMatch = html.match(/"aggregateRating"\s*:\s*\{[^}]*"ratingValue"\s*:\s*"?([\d.]+)"?/);
                        if (aggMatch) imdbRating = aggMatch[1];
                    }
                    console.log('[DBHelper] IMDb direct rating:', imdbRating);
                    // IMDb 拿到后，抓 RT 评分
                    fetchRTScore(imdbId, imdbRating);
                } else {
                    displayRatings('暂无', '暂无', imdbId);
                }
            },
            onerror: function() {
                displayRatings('暂无', '暂无', imdbId);
            },
            ontimeout: function() {
                displayRatings('暂无', '暂无', imdbId);
            }
        });
    }

    // ============ Rotten Tomatoes 两步法 ============
    // Step 1: 搜索 RT 获取电影 slug
    // Step 2: 访问 RT 电影详情页提取 Tomatometer
    function getEnglishTitle() {
        // 方法1（最可靠）：从"又名"字段提取纯英文别名
        const infoEl = document.getElementById('info');
        if (infoEl) {
            const infoText = infoEl.textContent;
            const aliasMatch = infoText.match(/又名:\s*(.+)/);
            if (aliasMatch) {
                const aliases = aliasMatch[1].split('/').map(s => s.trim());
                for (const alias of aliases) {
                    if (/^[A-Za-z0-9][A-Za-z0-9\s:',\-\.!?&]+$/.test(alias)) {
                        return alias;
                    }
                }
            }
        }
        // 方法2：从 h1 标题提取英文部分
        const titleEl = document.querySelector('h1 span[property="v:itemreviewed"]') || document.querySelector('h1');
        const fullTitle = titleEl ? titleEl.textContent.trim() : '';
        const engMatch = fullTitle.match(/[A-Za-z][A-Za-z0-9\s:',\-\.!?&]{2,}/);
        return engMatch ? engMatch[0].trim() : '';
    }

    function fetchRTScore(imdbId, imdbRating) {
        const searchQuery = getEnglishTitle();
        if (!searchQuery) {
            console.log('[DBHelper] No English title found, skipping RT');
            displayRatings(imdbRating, '暂无', imdbId);
            return;
        }

        console.log('[DBHelper] RT search query:', searchQuery);
        GM_xmlhttpRequest({
            method: "GET",
            url: `https://www.rottentomatoes.com/search?search=${encodeURIComponent(searchQuery)}`,
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            timeout: 12000,
            onload: function(response) {
                console.log('[DBHelper] RT search status:', response.status, 'length:', response.responseText.length);
                if (response.status === 200) {
                    const html = response.responseText;
                    // 从搜索结果中提取第一个电影的 /m/slug URL
                    const slugMatch = html.match(/rottentomatoes\.com\/m\/([^"\s]+)"/);
                    if (slugMatch) {
                        const slug = slugMatch[1];
                        console.log('[DBHelper] RT slug found:', slug);
                        fetchRTMoviePage(slug, imdbId, imdbRating);
                    } else {
                        console.warn('[DBHelper] No RT slug in search HTML. First 500 chars:', html.substring(0, 500));
                        displayRatings(imdbRating, '暂无', imdbId);
                    }
                } else {
                    console.warn('[DBHelper] RT search HTTP error:', response.status);
                    displayRatings(imdbRating, '暂无', imdbId);
                }
            },
            onerror: function(e) {
                console.error('[DBHelper] RT search network error:', e.error || e);
                displayRatings(imdbRating, '暂无', imdbId);
            },
            ontimeout: function() {
                console.warn('[DBHelper] RT search timeout (12s)');
                displayRatings(imdbRating, '暂无', imdbId);
            }
        });
    }

    // Step 2: 从 RT 电影详情页提取 Tomatometer 评分
    function fetchRTMoviePage(slug, imdbId, imdbRating) {
        console.log('[DBHelper] Fetching RT movie page:', slug);
        GM_xmlhttpRequest({
            method: "GET",
            url: `https://www.rottentomatoes.com/m/${slug}`,
            headers: {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            },
            timeout: 15000,
            onload: function(response) {
                console.log('[DBHelper] RT page status:', response.status, 'length:', response.responseText.length);
                if (response.status === 200) {
                    const html = response.responseText;
                    let rtScore = null;

                    // 方法1（最可靠）: JSON-LD 中的 aggregateRating.ratingValue
                    const ldBlocks = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi);
                    if (ldBlocks) {
                        for (const block of ldBlocks) {
                            try {
                                const jsonStr = block.replace(/<script[^>]*>/, '').replace(/<\/script>/i, '');
                                const ld = JSON.parse(jsonStr);
                                if (ld.aggregateRating && ld.aggregateRating.ratingValue) {
                                    rtScore = String(ld.aggregateRating.ratingValue);
                                    console.log('[DBHelper] RT score from JSON-LD:', rtScore);
                                    break;
                                }
                            } catch (e) { /* try next block */ }
                        }
                    }

                    // 方法2: tomatometerScore 属性
                    if (!rtScore) {
                        const m1 = html.match(/tomatometerScore["']?\s*[:=]\s*["']?(\d+)/i);
                        if (m1) { rtScore = m1[1]; console.log('[DBHelper] RT score from tomatometerScore:', rtScore); }
                    }

                    // 方法3: scoreboard 或 media-scorecard 组件内的百分比
                    if (!rtScore) {
                        const m2 = html.match(/(?:score-board|media-scorecard|scoreboard)[\s\S]*?(\d{1,3})%/);
                        if (m2) { rtScore = m2[1]; console.log('[DBHelper] RT score from scorecard:', rtScore); }
                    }

                    // 方法4: critics-score 附近的百分比
                    if (!rtScore) {
                        const m3 = html.match(/critics-score[\s\S]{0,200}?(\d{1,3})%/);
                        if (m3) { rtScore = m3[1]; console.log('[DBHelper] RT score from critics-score:', rtScore); }
                    }

                    // 方法5: 宽松匹配 — 页面中第一个合理的百分比
                    if (!rtScore) {
                        const m4 = html.match(/Tomatometer[\s\S]{0,300}?(\d{1,3})%/);
                        if (m4) { rtScore = m4[1]; console.log('[DBHelper] RT score from Tomatometer:', rtScore); }
                    }

                    console.log('[DBHelper] RT final score:', rtScore);
                    displayRatings(imdbRating, rtScore ? rtScore + '%' : '暂无', imdbId, slug);
                } else {
                    console.warn('[DBHelper] RT page returned status:', response.status);
                    displayRatings(imdbRating, '暂无', imdbId, slug);
                }
            },
            onerror: function(e) {
                console.warn('[DBHelper] RT page network error:', e);
                displayRatings(imdbRating, '暂无', imdbId, slug);
            },
            ontimeout: function() {
                console.warn('[DBHelper] RT page timeout');
                displayRatings(imdbRating, '暂无', imdbId, slug);
            }
        });
    }

    function displayRatings(imdbRating, rtRating, imdbId, rtSlug) {
        const ratingWrap = document.querySelector('.rating_wrap');
        if (!ratingWrap) return;

        // 防止重复渲染
        if (document.querySelector('.dbhelper-ratings')) return;

        // 注入样式（只注入一次）
        if (!document.getElementById('dbhelper-style')) {
            const style = document.createElement('style');
            style.id = 'dbhelper-style';
            style.textContent = `
                .dbhelper-ratings {
                    margin-top: 12px;
                    padding: 10px 0 2px;
                    border-top: 1px solid #eaeaea;
                }
                .dbhelper-row {
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    line-height: 1;
                }
                .dbhelper-badge {
                    display: inline-block;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 0.3px;
                    flex-shrink: 0;
                    text-align: center;
                    min-width: 36px;
                    box-sizing: border-box;
                }
                .dbhelper-badge-imdb {
                    background: #f5c518;
                    color: #000;
                    font-family: Arial, sans-serif;
                }
                .dbhelper-badge-rt {
                    background: #FA320A;
                    color: #fff;
                    font-family: Arial, sans-serif;
                }
                .dbhelper-score {
                    font-size: 17px;
                    font-weight: bold;
                    margin-left: 8px;
                    color: #494949;
                    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                }
                .dbhelper-score-na {
                    color: #bbb;
                    font-size: 13px;
                    font-weight: normal;
                }
                .dbhelper-sub {
                    font-size: 11px;
                    color: #9b9b9b;
                    margin-left: 1px;
                }
                .dbhelper-link {
                    margin-left: auto;
                    font-size: 12px;
                    color: #9b9b9b;
                    text-decoration: none;
                    flex-shrink: 0;
                    padding-left: 10px;
                }
                .dbhelper-link:hover {
                    color: #37a;
                }
            `;
            document.head.appendChild(style);
        }

        const isImdbNum = imdbRating && imdbRating !== '暂无' && /[\d.]/.test(imdbRating);
        const isRtNum = rtRating && rtRating !== '暂无' && /\d/.test(rtRating);

        // RT 链接：有 slug 则直接链到电影页，否则用英文标题搜索
        let rtLink;
        if (rtSlug) {
            rtLink = `https://www.rottentomatoes.com/m/${rtSlug}`;
        } else {
            const rtQuery = getEnglishTitle() || imdbId;
            rtLink = `https://www.rottentomatoes.com/search?search=${encodeURIComponent(rtQuery)}`;
        }

        const ratingsDiv = document.createElement('div');
        ratingsDiv.className = 'dbhelper-ratings';

        ratingsDiv.innerHTML = `
            <div class="dbhelper-row">
                <span class="dbhelper-badge dbhelper-badge-imdb">IMDb</span>
                <span class="dbhelper-score ${isImdbNum ? '' : 'dbhelper-score-na'}">${imdbRating}</span>
                ${isImdbNum ? '<span class="dbhelper-sub"> / 10</span>' : ''}
                <a class="dbhelper-link" href="https://www.imdb.com/title/${imdbId}/" target="_blank" rel="noopener">↗</a>
            </div>
            <div class="dbhelper-row">
                <span class="dbhelper-badge dbhelper-badge-rt">RT</span>
                <span class="dbhelper-score ${isRtNum ? '' : 'dbhelper-score-na'}">${isRtNum ? '🍅 ' + rtRating : rtRating}</span>
                <a class="dbhelper-link" href="${rtLink}" target="_blank" rel="noopener">↗</a>
            </div>
        `;
        ratingWrap.appendChild(ratingsDiv);
    }


    // ==========================================
    // 功能 2：在各种列表页 (Top250, 分类排行榜等) 标记“看过/已读”及“打分”
    // ==========================================
    function handleListPages() {
        const CACHE_KEY = 'douban_watched_cache_v6'; // v6: 缓存统一3天，修复想看误判为已看
        const NOW = Date.now();
        // 缓存策略：已看/想看缓存3天，未标记的缓存3天
        const EXPIRE_MARKED = 3 * 24 * 60 * 60 * 1000;
        const EXPIRE_UNMARKED = 3 * 24 * 60 * 60 * 1000;

        let cache = GM_getValue(CACHE_KEY, {});

        function getCache(typeId) {
            const entry = cache[typeId];
            if (!entry) return null;
            const age = NOW - entry.time;
            if (entry.status && age < EXPIRE_MARKED) return entry;  // watched 或 wish
            if (!entry.status && age < EXPIRE_UNMARKED) return entry; // 未标记
            return null; // 缓存过期
        }

        function setCache(typeId, status, rating) {
            // status: 'watched' | 'wish' | false
            cache[typeId] = { watched: !!status, status: status || false, rating: rating, time: NOW };
            GM_setValue(CACHE_KEY, cache);
        }

        function markStatus(element, status, rating, domainType) {
            // status: 'watched' | 'wish'
            if (element.querySelector('.watched-badge')) return;
            if (element.parentElement && element.parentElement.querySelector('.watched-badge')) return;
            
            const badge = document.createElement('span');
            badge.className = 'watched-badge';
            
            let badgeText, bgColor;
            if (status === 'wish') {
                badgeText = domainType === 'book' ? '📖 想读' : '🎬 想看';
                bgColor = '#f09199'; // 粉色，区别于已看的绿色
            } else {
                badgeText = domainType === 'book' ? '✅ 已读' : '✅ 已看';
                bgColor = '#5ab346';
                if (rating && rating > 0) {
                    const fullStars = '★'.repeat(rating);
                    const emptyStars = '☆'.repeat(5 - rating);
                    badgeText += ` ${fullStars}${emptyStars}`;
                }
            }

            badge.innerText = badgeText;
            badge.style.cssText = `color: #fff; background-color: ${bgColor}; padding: 2px 8px; border-radius: 4px; margin-left: 10px; font-size: 12px; vertical-align: middle; letter-spacing: 1px; display: inline-block;`;
            
            if (element.tagName === 'A') {
                element.parentNode.insertBefore(badge, element.nextSibling);
            } else {
                element.appendChild(badge);
            }
        }

        // 用一个队列来按顺序处理请求，避免并发过高
        const fetchQueue = [];
        let isFetching = false;
        
        function updateProgressUI() {
            let div = document.getElementById('douban-script-progress');
            if (fetchQueue.length === 0) {
                if (div) {
                    div.style.opacity = '0'; 
                    setTimeout(() => div && div.remove(), 500);
                }
                return;
            }
            if (!div) {
                div = document.createElement('div');
                div.id = 'douban-script-progress';
                div.style.cssText = 'position: fixed; bottom: 20px; right: 20px; padding: 10px 15px; background: rgba(0,0,0,0.7); color: #fff; border-radius: 5px; z-index: 9999; font-size: 13px; transition: opacity 0.5s; pointer-events: none;';
                document.body.appendChild(div);
            }
            div.innerText = `正在同步观看状态与评分... 等待队列: ${fetchQueue.length}`;
        }

        function processQueue() {
            if (isFetching || fetchQueue.length === 0) {
                updateProgressUI();
                return;
            }
            isFetching = true;
            updateProgressUI();
            
            const item = fetchQueue.shift();
            
            GM_xmlhttpRequest({
                method: "GET",
                url: `https://${item.domainType}.douban.com/subject/${item.id}/`,
                onload: function(response) {
                    const html = response.responseText;
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, "text/html");

                    let userRating = null;
                    
                    let ratingElem = doc.querySelector('#n_rating') || 
                                     doc.querySelector('#interest_sect_level [class*="stars"]') || 
                                     doc.querySelector('.rating-info [class*="stars"]');

                    if (ratingElem) {
                        const match = ratingElem.className.match(/stars(\d)0/);
                        if (match) {
                            userRating = parseInt(match[1], 10);
                        } else if (ratingElem.getAttribute('value')) {
                            userRating = parseInt(ratingElem.getAttribute('value'), 10);
                        }
                    }

                    if (userRating === null) {
                        const match1 = html.match(/class="[^"]*stars(\d)0[^"]*"[^>]*>[\s\S]{0,150}(?:修改|我看过这部|我的评价)/);
                        if (match1) {
                            userRating = parseInt(match1[1], 10);
                        } else {
                            const match2 = html.match(/(?:修改|我看过这部|我的评价)[\s\S]{0,150}class="[^"]*stars(\d)0[^"]*"/);
                            if (match2) {
                                userRating = parseInt(match2[1], 10);
                            }
                        }
                    }

                    // 区分三种状态：想看/想读、已看/已读、未标记
                    // 注意：必须先检测「想看」，因为 userRating 的宽松提取可能误匹配页面中
                    // 非用户评分的 stars 元素，导致想看条目被错误判定为已看
                    const isWish = 
                        html.includes('<span class="a_saved">想看</span>') || 
                        html.includes('<span class="a_saved">想读</span>') ||
                        html.includes('我想看这部电影') ||
                        html.includes('我想读这本书');
                    
                    const isWatched = !isWish && (
                        userRating !== null || 
                        html.includes('<span class="a_saved">看过</span>') || 
                        html.includes('<span class="a_saved">读过</span>') || 
                        html.includes('我看过这部电影') ||
                        html.includes('我读过这本书')
                    );

                    // 想看状态下不应有用户评分
                    if (isWish) userRating = null;

                    const status = isWatched ? 'watched' : (isWish ? 'wish' : false);
                    setCache(item.typeId, status, userRating);

                    if (status) {
                        markStatus(item.element, status, userRating, item.domainType);
                    }

                    // 延迟 800 毫秒后再请求下一个
                    setTimeout(() => {
                        isFetching = false;
                        processQueue();
                    }, 800);
                },
                onerror: function() {
                    // 失败时，等一会再继续，不把这条重新加进队列以防死循环，只忽略它
                    setTimeout(() => {
                        isFetching = false;
                        processQueue();
                    }, 1500);
                }
            });
        }

        // 定时扫描页面中新出现的电影/书籍节点（适配瀑布流和动态加载）
        setInterval(() => {
            const links = document.querySelectorAll('a[href*="movie.douban.com/subject/"], a[href*="book.douban.com/subject/"]');
            
            links.forEach(link => {
                // 确定要标记的 DOM 元素。
                let elementToMark = link;

                // 排除带有图片的海报链接，避免标签盖在海报上破坏样式
                if (link.querySelector('img')) {
                    if (link.classList.contains('item')) {
                        // 针对 explore(选电影) 页面，整个卡片是个 a.item
                        // 标签应当加在它内部的标题标签 p 上
                        const pTag = link.querySelector('p');
                        if (pTag) {
                            elementToMark = pTag;
                        } else {
                            return;
                        }
                    } else {
                        // Top250 或豆列的海报链接直接跳过（会处理对应的标题链接）
                        return;
                    }
                } else {
                    // 放宽过滤条件：有些列表页的标题链接内部可能有奇怪的排版导致 trim() 后为空，或者有别的内容
                    const text = link.innerText.trim();
                    const parentClass = link.parentNode ? link.parentNode.className : '';
                    
                    // 只要有文字，或者是属于“标题”区的链接（比如 class 为 title 或 pl2）
                    if (!text && !parentClass.includes('title') && !parentClass.includes('pl2')) return;
                }

                const match = link.href.match(/(movie|book)\.douban\.com\/subject\/(\d+)/);
                if (!match) return;
                const domainType = match[1]; // 'movie' or 'book'
                const id = match[2];
                const typeId = domainType + '_' + id;

                // 避免重复处理
                if (link.dataset.watchedChecked) return;
                link.dataset.watchedChecked = "true";

                const cachedEntry = getCache(typeId);
                if (cachedEntry) {
                    const st = cachedEntry.status || (cachedEntry.watched ? 'watched' : false);
                    if (st) {
                        markStatus(elementToMark, st, cachedEntry.rating, domainType);
                    }
                } else {
                    // 加入队列
                    // 检查是否已经在队列中
                    if (!fetchQueue.some(i => i.typeId === typeId)) {
                        fetchQueue.push({ id: id, typeId: typeId, domainType: domainType, element: elementToMark });
                        if (!isFetching) processQueue();
                    }
                }
            });
        }, 1500); // 每 1.5 秒扫描一次新节点
    }
})();