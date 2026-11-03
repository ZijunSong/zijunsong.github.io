from pathlib import Path
import json, re, html, shutil
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
POSTS = json.loads((ROOT / 'content/posts.json').read_text(encoding='utf-8'))
BASE = 'https://zijunsong.github.io'
SCHOLAR = 'https://scholar.google.com/citations?user=oCGK2GoAAAAJ&hl=zh-CN'
E = lambda s: html.escape(str(s), quote=True)

PUBLICATIONS = [
    {
        'title': 'CriticSearch: Fine-Grained Credit Assignment for Search Agents via a Retrospective Critic',
        'authors': 'Yaocheng Zhang*, Haohuan Huang*, Zijun Song, Zijie Zhao, Qichao Zhang, Yuanheng Zhu, Dongbin Zhao',
        'venue': 'Findings of ACL 2026',
        'note': 'Search Agent · Credit Assignment',
        'url': 'https://aclanthology.org/2026.findings-acl.596/',
    },
    {
        'title': 'TSRL: Trigger-based Supervised Reinforcement Learning for Continual Agent Training',
        'authors': 'Yuqian Fu, Kaiwen Jiang, Zijun Song, Jiawei Wang, Yuanheng Zhu, Dongbin Zhao',
        'venue': 'Findings of EMNLP 2026',
        'note': 'Continual Agent Training',
        'url': 'https://aclanthology.org/2026.findings-emnlp.19/',
    },
    {
        'title': 'PertDiffBench: Benchmarking Diffusion Models for Single-Cell Perturbation Response Prediction',
        'authors': 'Zijun Song*, Yujia Xiang*, Zhi Song, Wenyi Jin, Jiangmeng Li, Chuxiong Sun, Linhai Xie',
        'venue': 'bioRxiv 2026',
        'note': 'First author · AI for Science',
        'url': 'https://www.biorxiv.org/content/10.64898/2026.06.13.732013v1',
    },
    {
        'title': 'MiniCPM4: Ultra-Efficient LLMs on End Devices',
        'authors': 'MiniCPM Team, including Zijun Song',
        'venue': 'arXiv 2025',
        'note': 'On-device LLM',
        'url': 'https://arxiv.org/abs/2506.07900',
    },
    {
        'title': 'AgentCPM-Explore: Realizing Long-Horizon Deep Exploration for Edge-Scale Agents',
        'authors': 'Haotian Chen, Xin Cong, Shengda Fan, Yuyang Fu, Ziqin Gong, Yaxi Lu, Yishan Li, Boye Niu, Chengjun Pan, Zijun Song, et al.',
        'venue': 'arXiv 2026',
        'note': 'Edge-scale Agent',
        'url': 'https://arxiv.org/abs/2602.06485',
    },
    {
        'title': 'ToLeaP: Rethinking Development of Tool Learning with Large Language Models',
        'authors': 'Haotian Chen, Zijun Song, Boye Niu, Ke Zhang, Litu Ou, Yaxi Lu, Zhong Zhang, Xin Cong, Yankai Lin, et al.',
        'venue': 'arXiv 2025',
        'note': 'Tool Learning',
        'url': 'https://arxiv.org/abs/2505.11833',
    },
    {
        'title': 'TIDE-Bench: Task-Aware and Diagnostic Evaluation of Tool-Integrated Reasoning',
        'authors': 'Y. Li, J. Li, Zijun Song, C. Sun, R. Wang, C. Zheng',
        'venue': 'arXiv 2026',
        'note': 'Tool-Integrated Reasoning',
        'url': 'https://arxiv.org/abs/2605.09544',
    },
    {
        'title': 'Benchmarking Diffusion Models for Predicting Perturbed Cellular Responses',
        'authors': 'Zijun Song, Chuxiong Zheng, Jiangmeng Li, Linhai Xie, Yujia Xiang',
        'venue': 'NeurIPS 2025 Workshop on Biosecurity Safeguards for Generative AI',
        'note': 'Workshop',
        'url': SCHOLAR,
    },
    {
        'title': 'Wind Speed Prediction with Deep Learning Method',
        'authors': 'Xianli Li, Zijun Song, Ze Jin',
        'venue': 'IEEE ICIPCA 2023',
        'note': 'EI',
        'url': SCHOLAR,
    },
    {
        'title': 'A Rotation Speed Measurement System based on Millimeter Wave',
        'authors': 'Zijun Song, Qiwei Wang',
        'venue': 'IEEE CCCI 2022',
        'note': 'EI',
        'url': SCHOLAR,
    },
]

def inline(s):
    s = E(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1 ↗</a>', s)
    return s

def markdown(text):
    out = []
    toc = []
    para = []
    code = None
    buf = []
    listing = False
    def flush():
        if para:
            out.append('<p>' + inline(' '.join(para)) + '</p>')
            para.clear()
    for line in text.splitlines() + ['']:
        if line.startswith('```'):
            flush()
            if code is None:
                code = line[3:].strip()
                buf = []
            else:
                out.append('<div class="code-wrap"><div class="code-head"><span>' + E(code or 'text') + '</span><button class="copy-code">复制代码</button></div><pre><code>' + E('\n'.join(buf)) + '</code></pre></div>')
                code = None
            continue
        if code is not None:
            buf.append(line)
            continue
        if listing and not line.startswith('- '):
            out.append('</ul>')
            listing = False
        if line.startswith('## '):
            flush()
            label = line[3:]
            anchor = 'section-' + str(len(toc) + 1)
            toc.append((anchor, label))
            out.append(f'<h2 id="{anchor}">{inline(label)}</h2>')
        elif line.startswith('### '):
            flush()
            out.append('<h3>' + inline(line[4:]) + '</h3>')
        elif line.startswith('> '):
            flush()
            out.append('<blockquote>' + inline(line[2:]) + '</blockquote>')
        elif line.startswith('- '):
            flush()
            if not listing:
                out.append('<ul>')
                listing = True
            out.append('<li>' + inline(line[2:]) + '</li>')
        elif not line.strip():
            flush()
        else:
            para.append(line)
    return '\n'.join(out), toc

def mark_me(authors):
    return re.sub(r'(Zijun Song|宋子骏)', r'<span class="pub-me">\1</span>', E(authors))

def shell(title, body, active='home', desc='宋子骏的个人主页：Agent 强化学习、工具学习、后训练与 AI for Science。', path=''):
    depth = '../' if path.startswith('posts/') else './'
    items = [('home', '', '关于'), ('notes', 'notes.html', '研究笔记'), ('projects', 'projects.html', '项目')]
    nav = ''.join(
        f'<a href="{depth}{p}"' + (' aria-current="page"' if active == key else '') + f'>{label}</a>'
        for key, p, label in items
    )
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · Zijun Song</title><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#f8f7f4"><meta property="og:title" content="{E(title)} · Zijun Song"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{'article' if path.startswith('posts/') else 'website'}"><link rel="icon" href="{depth}assets/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Zijun Song · Research Notes" href="{depth}feed.xml"><link rel="stylesheet" href="{depth}assets/style.css"><script src="{depth}assets/app.js" defer></script></head><body><a class="skip" href="#main">跳到正文</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="brand" href="{depth}"><span class="monogram">zs<span>·</span></span><span>Zijun Song <span class="brand-sub">/ 宋子骏</span></span></a><nav aria-label="主导航">{nav}<a class="github-nav" href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub ↗</a><button class="theme-switch" aria-label="切换深色模式" title="切换深色模式">◐</button></nav></header>{body}<footer class="site-footer"><div><a class="footer-name" href="{depth}">Zijun Song<span> / 紫色噩梦</span></a><p>把想法写清楚，把实验做扎实。</p></div><div class="footer-right"><a href="{depth}feed.xml">RSS ↗</a><a href="mailto:2949203143@qq.com">Email ↗</a><a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">Scholar ↗</a><span>© 2026 · An open research notebook.</span></div></footer></body></html>'''

def card(p, featured=False, prefix='posts/'):
    tags = ''.join('<span>' + E(t) + '</span>' for t in p['tags'])
    return (
        f'<a class="note-card {"featured-card" if featured else ""}" href="{prefix}{E(p["slug"])}.html" '
        f'data-tags="{E(" ".join(p["tags"]))}" data-search="{E(p["title"] + " " + p["summary"] + " " + " ".join(p["tags"]))}">'
        f'<div class="note-meta"><span>{E(p["kind"])}</span><span>{p["date"].replace("-", ".")} · {p["minutes"]} MIN READ</span></div>'
        f'<h3>{E(p["title"])}<span class="card-arrow">↗</span></h3><p>{E(p["summary"])}</p>'
        f'<div class="card-bottom"><div class="tags">{tags}</div>'
        f'{"<span class=\"draft-status\">示例文章 · 待审阅</span>" if p.get("example", True) else "<span class=\"draft-status\">研究文章</span>"}'
        f'</div></a>'
    )

def pub_item(p):
    title = f'<a href="{E(p["url"])}" target="_blank" rel="noopener noreferrer">{E(p["title"])} ↗</a>' if p.get('url') else E(p['title'])
    return (
        f'<article class="pub-item"><div class="pub-venue">{E(p["venue"])} · {E(p["note"])}</div>'
        f'<h3>{title}</h3><p class="pub-meta">{mark_me(p["authors"])}</p></article>'
    )

home = f'''<main id="main" class="home-main">
<section class="profile" id="about">
  <img class="profile-photo" src="Pics/ZijunSong.jpg" alt="宋子骏 Zijun Song 的照片" width="200" height="240">
  <div>
    <div class="eyebrow"><span class="tiny-dot"></span> ABOUT</div>
    <h1>宋子骏<span class="profile-en">Zijun Song</span></h1>
    <p class="profile-role">博士生 · 中国科学院大学前沿交叉科学学院<br>School of Advanced Interdisciplinary Sciences, UCAS · Beijing</p>
    <div class="profile-links">
      <a href="mailto:2949203143@qq.com">Email</a>
      <a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">Scholar</a>
      <a href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub</a>
      <a href="notes.html">研究笔记</a>
    </div>
    <div class="profile-bio">
      <p>你好，我是宋子骏，也叫紫色噩梦。我是中国科学院大学前沿交叉科学学院的博士生，研究工作同时在<a href="https://www.ia.ac.cn/" target="_blank" rel="noopener noreferrer">中国科学院自动化研究所</a>展开。</p>
      <p>我的研究关注 <strong>AI Agent</strong>，尤其是 Agent 强化学习、工具学习与后训练：当模型借助搜索、工具和外部执行系统把任务做得更好时，哪些能力可以留在模型里，并迁移到新的任务上。近期工作包括搜索 Agent 的细粒度信用分配、持续学习中的监督触发，以及端侧 Agent 的长程探索。</p>
      <p>我也关注 <strong>AI for Science</strong>。我作为第一作者完成了 PertDiffBench，用于评测扩散模型在单细胞扰动响应预测中的适用范围。</p>
      <p>本科毕业于大连理工大学软件学院。欢迎围绕研究方法、复现和开源项目来信交流。</p>
    </div>
    <div class="hero-topics"><span>AGENT RL</span><i></i><span>TOOL LEARNING</span><i></i><span>POST-TRAINING</span><i></i><span>AI4SCIENCE</span></div>
  </div>
</section>
<section class="home-section" id="experience">
  <div class="home-kicker">EDUCATION &amp; EXPERIENCE</div>
  <h2>经历</h2>
  <div class="timeline">
    <div class="timeline-item"><span class="when">2025.09 – 至今</span><div><h3>中国科学院大学 · 前沿交叉科学学院</h3><p>博士生。研究方向为 Agent 强化学习、工具学习与后训练。论文署名单位还包括中国科学院自动化研究所。</p></div></div>
    <div class="timeline-item"><span class="when">2021.09 – 2025.06</span><div><h3>大连理工大学 · 软件学院</h3><p>本科。期间关注强化学习、AI for Science，以及相关系统实现。</p></div></div>
    <div class="timeline-item"><span class="when">实习经历</span><div><h3>中国科学院软件研究所</h3><p>曾在天基综合信息系统重点实验室实习，从事强化学习相关工作。</p></div></div>
  </div>
</section>
<section class="home-section" id="publications">
  <div class="section-heading"><div><div class="home-kicker">SELECTED PUBLICATIONS</div><h2>论文</h2></div><a class="text-link" href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">在 Google Scholar 查看全部 ↗</a></div>
  <p class="home-lead">以下为公开可核验的论文与预印本。作者列表按原论文列出，<span class="pub-me">Zijun Song</span> 为本人。</p>
  <div class="pub-list">{''.join(pub_item(p) for p in PUBLICATIONS)}</div>
</section>
<section class="home-section" id="honors">
  <div class="home-kicker">HONORS</div>
  <h2>荣誉</h2>
  <ul class="honor-list">
    <li><span class="honor-year">2023 – 2024</span><span>国家励志奖学金；校优秀三好学生；文体活动奖学金；社会实践奖学金；精神文明奖学金</span></li>
    <li><span class="honor-year">2022 – 2023</span><span>国家励志奖学金；校优秀三好学生；文体活动奖学金；社会工作奖学金；精神文明奖学金</span></li>
    <li><span class="honor-year">2021 – 2022</span><span>文体活动奖学金；校优秀团员</span></li>
  </ul>
</section>
<section class="home-section notes-section" id="notes">
  <div class="section-heading"><div><div class="home-kicker">RESEARCH NOTES</div><h2>最近的笔记</h2></div><a class="text-link" href="notes.html">查看全部笔记 ↗</a></div>
  <div class="notes-grid home-notes">{''.join(card(p, False) for p in POSTS[:3])}</div>
</section>
<section class="projects-preview" id="open-source">
  <div class="section-heading"><div><div class="home-kicker">OPEN SOURCE</div><h2>从论文到代码</h2></div><a class="text-link" href="projects.html">查看全部项目 ↗</a></div>
  <div class="project-strip">
    <a href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer"><span class="project-number">01</span><div><h3>PertDiffBench ↗</h3><p>细胞扰动响应预测的统一评测框架。</p></div><span class="project-type">AI4SCIENCE</span></a>
    <a href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer"><span class="project-number">02</span><div><h3>Capability Evolution ↗</h3><p>探索 Agent 能力、自进化与训练。</p></div><span class="project-type">AGENTS</span></a>
    <a href="https://github.com/ZijunSong/On-Policy-Context-Distillation" target="_blank" rel="noopener noreferrer"><span class="project-number">03</span><div><h3>On-Policy Context Distillation ↗</h3><p>On-policy 蒸馏相关的开源实现。</p></div><span class="project-type">POST-TRAINING</span></a>
  </div>
</section>
<section class="closing-note"><span class="handwritten">A work in progress.</span><p>研究不止于论文。<br>一些值得留下的过程，也在这里。</p><a href="mailto:2949203143@qq.com">欢迎交流想法 <span>↗</span></a></section>
</main>'''

notes_notice = ''
if any(p.get('example', True) for p in POSTS):
    notes_notice = '<div class="editorial-notice"><span>初次见面</span> 下面是用于预览排版的示例文章，尚未经作者审阅；正式稿件可用 Markdown 持续发布。</div>'
notes_body = f'''<main id="main"><section class="notes-section page-notes" id="notes"><div class="section-heading"><div><div class="eyebrow">THE NOTEBOOK</div><h2>研究笔记<span class="section-count"> / {str(len(POSTS)).zfill(2)}</span></h2></div><p>方法拆解、实验记录与开放思考。</p></div>{notes_notice}<div class="notes-tools"><div class="filters" role="group" aria-label="按主题筛选">{''.join(f'<button data-filter="{t}" aria-pressed="{str(t=="全部").lower()}">{t}</button>' for t in ['全部','Agent','后训练','AI4Science'])}</div><label class="search-box"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8" cy="8" r="5.5"/><path d="m12 12 5 5"/></svg><input id="search" type="search" placeholder="搜索笔记…" aria-label="搜索研究笔记"><kbd>/</kbd></label></div><div class="notes-grid">{''.join(card(p, i==0) for i,p in enumerate(POSTS))}</div><p class="no-results" hidden>没有找到相关笔记，试试其他关键词或主题。</p></section></main>'''

(OUT / 'index.html').write_text(shell('宋子骏', home, 'home'), encoding='utf-8')
(OUT / 'notes.html').write_text(shell('研究笔记', notes_body, 'notes', '宋子骏的研究笔记：Agent、自进化、后训练与 AI for Science。'), encoding='utf-8')
(OUT / 'about.html').write_text(
    '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=./"><link rel="canonical" href="./"><title>关于我 · Zijun Song</title></head><body><p><a href="./">前往个人介绍</a></p></body></html>',
    encoding='utf-8',
)

(OUT / 'posts').mkdir(exist_ok=True)
for p in POSTS:
    body, toc = markdown((ROOT / 'content/posts' / f"{p['slug']}.md").read_text(encoding='utf-8'))
    article_notice = '<div class="article-notice"><strong>关于这篇示例</strong><p>此文用于展示博客的阅读体验，是依据研究主题撰写的概念性示例，尚未经作者审阅，不代表正式研究报告或实验结论。</p></div>' if p.get('example', True) else ''
    citation = f"宋子骏. {p['title']}. Research Notes, {p['date']}. {BASE}/posts/{p['slug']}.html"
    article = f'''<main id="main" class="article-main"><a class="back-link" href="../notes.html">← 返回研究笔记</a><header class="article-header"><div class="eyebrow">{E(p['kind'])} / {E(' · '.join(p['tags']))}</div><h1>{E(p['title'])}</h1><p class="article-deck">{E(p['summary'])}</p><div class="author-line"><span class="author-mark">ZS</span><span>宋子骏 · Zijun Song<br><small>{p['date']} · {p['minutes']} 分钟阅读 · {('v0.1 示例稿' if p.get('example', True) else E(p.get('version', 'v1.0')))}</small></span></div></header><div class="article-layout"><article class="prose">{article_notice}{body}<div class="citation-box"><span class="eyebrow">引用与分享</span><p id="citation">{E(citation)}</p><button class="copy-citation">复制引用</button><span class="copy-feedback" role="status"></span></div><nav class="article-nav" aria-label="继续阅读"><span>继续阅读</span>{''.join(f'<a href="{E(other["slug"])}.html">{E(other["title"])} ↗</a>' for other in POSTS if other != p)}</nav></article><aside class="toc"><span class="eyebrow">ON THIS PAGE</span>{''.join(f'<a href="#{anchor}">{E(label)}</a>' for anchor, label in toc)}<a class="back-top" href="#main">回到顶部 ↑</a></aside></div></main>'''
    (OUT / 'posts' / f"{p['slug']}.html").write_text(shell(p['title'], article, 'notes', p['summary'], path='posts/' + p['slug'] + '.html'), encoding='utf-8')

project_body = '''<main id="main" class="page-main"><div class="eyebrow">SELECTED PROJECTS</div><h1>让想法经受实践。</h1><p class="page-deck">部分开源项目来自 GitHub。代码、实现细节与项目进展，以各仓库为准。</p>
<div class="project-full"><span class="project-number">01 / AI FOR SCIENCE</span><h2>PertDiffBench</h2><p>面向细胞扰动响应预测的评测框架，提供多类模型与任务的统一运行接口，关注跨细胞类型、跨物种和未见药物等泛化场景。</p><a class="primary-button" href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div>
<div class="project-full"><span class="project-number">02 / AGENTS</span><h2>Capability Evolution</h2><p>围绕 Agent 能力演化与训练展开的研究代码。当前关注 Harness、自进化与能力内化之间的关系。</p><a class="primary-button" href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div>
<div class="project-full"><span class="project-number">03 / POST-TRAINING</span><h2>On-Policy Context Distillation</h2><p>对 On-Policy Context Distillation 的开源复现与实验记录。</p><a class="primary-button" href="https://github.com/ZijunSong/On-Policy-Context-Distillation" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div>
<div class="project-full"><span class="project-number">04 / TOOL LEARNING</span><h2>ToLeaP</h2><p>围绕大模型工具学习评测与开发流程的相关研究代码。</p><a class="primary-button" href="https://github.com/ZijunSong/ToLeaP" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div>
</main>'''
(OUT / 'projects.html').write_text(shell('开源项目', project_body, 'projects'), encoding='utf-8')
(OUT / '404.html').write_text(shell('页面未找到', '<main id="main" class="page-main"><div class="eyebrow">404 / A SMALL DETOUR</div><h1>这页笔记还没写到。</h1><p class="page-deck">链接可能已经更新，回到首页继续阅读。</p><a class="primary-button" href="./">返回首页 ↗</a></main>'), encoding='utf-8')
(OUT / '.nojekyll').touch()
(OUT / 'feed.xml').write_text(
    '<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Zijun Song · Research Notes</title><link>' + BASE + '</link><description>研究笔记与方法分享</description>' +
    ''.join('<item><title>' + xml_escape(p['title']) + '</title><link>' + BASE + '/posts/' + p['slug'] + '.html</link><guid>' + BASE + '/posts/' + p['slug'] + '.html</guid><description>' + xml_escape(('[示例文章·待审阅] ' if p.get('example', True) else '') + p['summary']) + '</description></item>' for p in POSTS) +
    '</channel></rss>',
    encoding='utf-8',
)
pages = ['', 'notes.html', 'projects.html'] + ['posts/' + p['slug'] + '.html' for p in POSTS]
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + BASE + '/' + p + '</loc></url>' for p in pages) + '</urlset>', encoding='utf-8')
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
for name in ('Papers', 'Pics'):
    src, dst = ROOT / name, OUT / name
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
print('Built homepage, notes, projects, RSS, sitemap. Assets retained.')
