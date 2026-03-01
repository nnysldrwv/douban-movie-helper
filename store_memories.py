import urllib.request, json, datetime

token = open(r'C:\Users\fengxing.chen\.notion_token').read().strip()
db_id = '3147c2c7-a522-8123-927e-d260346e402b'
today = str(datetime.date.today())

memories = [
    {
        'title': 'Sean 基础信息',
        'category': '用户偏好',
        'importance': '高',
        'tags': ['基础信息', '沟通'],
        'content': '用户称呼 Sean，偏好中文沟通，回复风格偏好简洁优先、结构清晰。',
        'source': '系统提示词 + 对话观察'
    },
    {
        'title': 'Douban Movie Helper 项目',
        'category': '项目上下文',
        'importance': '高',
        'tags': ['油猴脚本', '豆瓣', 'GitHub'],
        'content': ('豆瓣电影助手油猴脚本(Tampermonkey)，功能包括：OMDb/IMDb 评分获取、'
                    '烂番茄(RT)评分抓取、已看/想看状态标记(绿色/粉色徽章)。'
                    'GitHub 仓库：nnysldrwv/douban-movie-helper。'
                    '当前版本 v4.9，缓存版本 v5。脚本目标页面 movie.douban.com/subject/*。'),
        'source': '对话 - 2026-02-28'
    },
    {
        'title': '油猴脚本技术细节',
        'category': '技术栈',
        'importance': '中',
        'tags': ['Tampermonkey', 'JavaScript', '豆瓣'],
        'content': ('使用 GM_xmlhttpRequest 跨域请求，DOMParser 解析 HTML，正则匹配 RT 评分。'
                    '缓存使用 GM_setValue/GM_getValue，key 为 douban_watched_cache_v5，'
                    '包含 status 字段(watched|wish|false)。'
                    '状态检测在 handleListPages 函数中，UI 标记在 markStatus 函数中。'),
        'source': '对话 - 2026-02-28'
    },
    {
        'title': 'RT 评分抓取方案',
        'category': '项目上下文',
        'importance': '中',
        'tags': ['烂番茄', '爬虫', '豆瓣'],
        'content': ('两步法抓取烂番茄评分：1.用搜索API获取slug 2.抓取详情页提取评分。'
                    '优先从豆瓣"又名"字段提取英文标题作为搜索词。'
                    '需在 @connect 白名单中添加 rottentomatoes.com。'),
        'source': '对话 - 2026-02-28'
    },
    {
        'title': 'Notion 工作空间结构',
        'category': '常用资源',
        'importance': '高',
        'tags': ['Notion', '配置'],
        'content': ('Diary DB: 2ca7c2c7-a522-813b-a409-eec1c75bf2a4。'
                    'Todo List DB: 3107c2c7-a522-814a-9a3d-000b75336965。'
                    '提示词页面: 3107c2c7-a522-8096-bd55-d2698dd3ae79。'
                    'Echo Memory 页面: 3147c2c7-a522-8168-9d91-ef5df7493015。'
                    '父级页面(workspace root): 2de7c2c7-a522-80fb-bbe5-d26fca450ec9。'),
        'source': '对话 - 2026-02-28'
    },
    {
        'title': 'Agent Memory 系统配置',
        'category': '常用资源',
        'importance': '高',
        'tags': ['Notion', '配置', 'Echo'],
        'content': ('Memory Store 数据库 ID: 3147c2c7-a522-8123-927e-d260346e402b。'
                    'Token 文件路径: C:\\Users\\fengxing.chen\\.notion_token。'
                    'Skill 路径: C:\\Users\\fengxing.chen\\.agents\\skills\\agent-memory\\SKILL.md。'
                    '所有直接 REST 调用需使用 API 版本 2022-06-28。'),
        'source': '对话 - 2026-02-28'
    },
    {
        'title': 'Notion MCP 版本限制',
        'category': '技术栈',
        'importance': '中',
        'tags': ['Notion', 'MCP', 'Bug'],
        'content': ('Notion MCP 工具默认绑定 API 版本 2025-09-03，'
                    '该版本不支持通过 create-a-data-source 端点创建数据库。'
                    '需通过 Python urllib 直接调用 Notion REST API 并指定版本 2022-06-28 来绕过。'
                    '查询(query)操作不受影响。'),
        'source': '对话 - 2026-02-28'
    }
]

url = 'https://api.notion.com/v1/pages'
headers = {
    'Authorization': f'Bearer {token}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

for i, m in enumerate(memories):
    data = json.dumps({
        'parent': {'database_id': db_id},
        'properties': {
            '记忆': {'title': [{'text': {'content': m['title']}}]},
            '类别': {'select': {'name': m['category']}},
            '重要性': {'select': {'name': m['importance']}},
            '标签': {'multi_select': [{'name': t} for t in m['tags']]},
            '内容': {'rich_text': [{'text': {'content': m['content']}}]},
            '来源': {'rich_text': [{'text': {'content': m['source']}}]},
            '最后验证': {'date': {'start': today}}
        }
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        print(f'[{i+1}/7] {m["title"]} -> {result["id"][:8]}...')

print('\nDone! All 7 memories stored.')
