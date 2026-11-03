from pathlib import Path
import json, re, html, shutil
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
POSTS = json.loads((ROOT / 'content/posts.json').read_text(encoding='utf-8'))
BASE = 'https://zijunsong.github.io'
SCHOLAR = 'https://scholar.google.com/citations?user=oCGK2GoAAAAJ&hl=en'
E = lambda s: html.escape(str(s), quote=True)
BLOG_POSTS = [p for p in POSTS if not p.get('example', False)]

RESEARCH_PAPERS = [
    {
        'title': 'Benchmarking Diffusion Models for Predicting Perturbed Cellular Responses',
        'authors': 'Zijun Song, Chuxiong Zheng, Jiangmeng Li, Linhai Xie, Yujia Xiang',
        'venue': 'NeurIPS 2025 Workshop on Biosecurity Safeguards for Generative AI',
        'note': 'First author · Accepted workshop',
        'url': SCHOLAR,
    },
    {
        'title': 'CriticSearch: Fine-Grained Credit Assignment for Search Agents via a Retrospective Critic',
        'authors': 'Yaocheng Zhang*, Haohuan Huang*, Zijun Song, Zijie Zhao, Qichao Zhang, Yuanheng Zhu, Dongbin Zhao',
        'venue': 'Findings of ACL 2026',
        'note': 'Accepted',
        'url': 'https://aclanthology.org/2026.findings-acl.596/',
    },
    {
        'title': 'TSRL: Trigger-based Supervised Reinforcement Learning for Continual Agent Training',
        'authors': 'Yuqian Fu, Kaiwen Jiang, Zijun Song, Jiawei Wang, Yuanheng Zhu, Dongbin Zhao',
        'venue': 'Findings of EMNLP 2026',
        'note': 'Accepted',
        'url': 'https://aclanthology.org/2026.findings-emnlp.19/',
    },
    {
        'title': 'PertDiffBench: Benchmarking Diffusion Models for Single-Cell Perturbation Response Prediction',
        'authors': 'Zijun Song*, Yujia Xiang*, Zhi Song, Wenyi Jin, Jiangmeng Li, Chuxiong Sun, Linhai Xie',
        'venue': 'bioRxiv 2026',
        'note': 'First author · Preprint',
        'url': 'https://www.biorxiv.org/content/10.64898/2026.06.13.732013v1',
    },
    {
        'title': 'ToLeaP: Rethinking Development of Tool Learning with Large Language Models',
        'authors': 'Haotian Chen, Zijun Song, Boye Niu, Ke Zhang, Litu Ou, Yaxi Lu, Zhong Zhang, Xin Cong, Yankai Lin, et al.',
        'venue': 'arXiv 2025',
        'note': 'Preprint',
        'url': 'https://arxiv.org/abs/2505.11833',
    },
    {
        'title': 'TIDE-Bench: Task-Aware and Diagnostic Evaluation of Tool-Integrated Reasoning',
        'authors': 'Y. Li, J. Li, Zijun Song, C. Sun, R. Wang, C. Zheng',
        'venue': 'arXiv 2026',
        'note': 'Preprint',
        'url': 'https://arxiv.org/abs/2605.09544',
    },
]

TECH_REPORTS = [
    {
        'title': 'MiniCPM4: Ultra-Efficient LLMs on End Devices',
        'authors': 'MiniCPM Team, including Zijun Song',
        'venue': 'arXiv 2025',
        'note': 'Technical report',
        'url': 'https://arxiv.org/abs/2506.07900',
    },
    {
        'title': 'AgentCPM-Explore: Realizing Long-Horizon Deep Exploration for Edge-Scale Agents',
        'authors': 'Haotian Chen, Xin Cong, Shengda Fan, Yuyang Fu, Ziqin Gong, Yaxi Lu, Yishan Li, Boye Niu, Chengjun Pan, Zijun Song, et al.',
        'venue': 'arXiv 2026',
        'note': 'Technical report',
        'url': 'https://arxiv.org/abs/2602.06485',
    },
]

def inline(s):
    s = E(s)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', s)
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
                out.append('<div class="code-wrap"><div class="code-head"><span>' + E(code or 'text') + '</span><button class="copy-code">Copy</button></div><pre><code>' + E('\n'.join(buf)) + '</code></pre></div>')
                code = None
            continue
        if code is not None:
            buf.append(line)
            continue
        if listing and not line.startswith('- '):
            out.append('</ul>')
            listing = False
        img = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img:
            flush()
            alt, src = img.group(1), img.group(2)
            out.append(f'<figure><img src="{E(src)}" alt="{E(alt)}" loading="lazy"><figcaption>{inline(alt)}</figcaption></figure>')
            continue
        if line.startswith('# '):
            flush()
            continue
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

def shell(title, body, active='home', desc='Zijun Song’s homepage: search-agent post-training and research notes.', path=''):
    depth = '../' if path.startswith('posts/') else './'
    items = [('home', '', 'About'), ('blog', 'blog.html', 'Blog'), ('projects', 'projects.html', 'Projects')]
    nav = ''.join(
        f'<a href="{depth}{p}"' + (' aria-current="page"' if active == key else '') + f'>{label}</a>'
        for key, p, label in items
    )
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · Zijun Song</title><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#f8f7f4"><meta property="og:title" content="{E(title)} · Zijun Song"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{'article' if path.startswith('posts/') else 'website'}"><link rel="icon" href="{depth}assets/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Zijun Song · Blog" href="{depth}feed.xml"><link rel="stylesheet" href="{depth}assets/style.css"><script src="{depth}assets/app.js" defer></script></head><body><a class="skip" href="#main">Skip to content</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="brand" href="{depth}"><span class="monogram">zs<span>·</span></span><span>Zijun Song <span class="brand-sub">/ 宋子骏</span></span></a><nav aria-label="Primary">{nav}<a class="github-nav" href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub ↗</a><button class="theme-switch" aria-label="Switch to dark mode" title="Switch theme">◐</button></nav></header>{body}<footer class="site-footer"><div><a class="footer-name" href="{depth}">Zijun Song<span> / Purple Nightmare</span></a><p>Write ideas clearly. Test them carefully.</p></div><div class="footer-right"><a href="{depth}feed.xml">RSS ↗</a><a href="mailto:2949203143@qq.com">Email ↗</a><a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">Scholar ↗</a><span>© 2026 · An open research notebook.</span></div></footer></body></html>'''

def card(p, featured=False, prefix='posts/'):
    tags = ''.join('<span>' + E(t) + '</span>' for t in p['tags'])
    return (
        f'<a class="note-card {"featured-card" if featured else ""}" href="{prefix}{E(p["slug"])}.html" '
        f'data-tags="{E(" ".join(p["tags"]))}" data-search="{E(p["title"] + " " + p["summary"] + " " + " ".join(p["tags"]))}">'
        f'<div class="note-meta"><span>{E(p["kind"])}</span><span>{p["date"].replace("-", ".")} · {p["minutes"]} MIN READ</span></div>'
        f'<h3>{E(p["title"])}<span class="card-arrow">↗</span></h3><p>{E(p["summary"])}</p>'
        f'<div class="card-bottom"><div class="tags">{tags}</div>'
        f'{"<span class=\"draft-status\">Draft</span>" if p.get("example", True) else "<span class=\"draft-status\">Research note</span>"}'
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
  <img class="profile-photo" src="Pics/ZijunSong.jpg" alt="Portrait of Zijun Song" width="200" height="240">
  <div>
    <div class="eyebrow"><span class="tiny-dot"></span> ABOUT</div>
    <h1>Zijun Song<span class="profile-en">宋子骏</span></h1>
    <p class="profile-role">PhD student · School of Advanced Interdisciplinary Sciences, UCAS<br>Jointly trained with the Institute of Automation, CAS · Beijing</p>
    <div class="profile-links">
      <a href="mailto:2949203143@qq.com">Email</a>
      <a href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">Scholar</a>
      <a href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub</a>
      <a href="blog.html">Blog</a>
    </div>
    <div class="profile-bio">
      <p>I am Zijun Song. I received my B.Eng. in Network Engineering from the School of Software, Dalian University of Technology, in 2025. As an undergraduate, I worked on wireless sensing with Wi-Fi, UWB, and millimeter-wave radar.</p>
      <p>I am now a PhD student at the School of Advanced Interdisciplinary Sciences, University of the Chinese Academy of Sciences, jointly trained with the <a href="https://www.ia.ac.cn/" target="_blank" rel="noopener noreferrer">Institute of Automation, CAS</a>. I am advised by <a href="https://scholar.google.com/citations?user=RxvYlNQAAAAJ&amp;hl=en" target="_blank" rel="noopener noreferrer">Prof. Dongbin Zhao</a>.</p>
      <p>My current research focuses on <strong>post-training for search agents</strong>. At ModelBest (面壁智能), I worked on post-training for MiniCPM4 and AgentCPM-Explore. At Xiaomi, I worked on post-training for MiSearchAgent.</p>
    </div>
    <div class="hero-topics"><span>SEARCH AGENT</span><i></i><span>POST-TRAINING</span><i></i><span>WIRELESS SENSING</span></div>
  </div>
</section>
<section class="home-section" id="experience">
  <div class="home-kicker">EXPERIENCE</div>
  <h2>Internships</h2>
  <div class="timeline">
    <div class="timeline-item"><span class="when">TBD</span><div><h3>Research Intern, ModelBest (面壁智能)</h3><p>Post-training for MiniCPM4 and AgentCPM-Explore.</p></div></div>
    <div class="timeline-item"><span class="when">TBD</span><div><h3>Research Intern, Xiaomi</h3><p>Post-training for MiSearchAgent.</p></div></div>
  </div>
</section>
<section class="home-section notes-section" id="blog">
  <div class="section-heading"><div><div class="home-kicker">BLOG</div><h2>Selected posts</h2></div><a class="text-link" href="blog.html">All posts ↗</a></div>
  <div class="notes-grid home-notes">{''.join(card(p, i==0) for i,p in enumerate(BLOG_POSTS))}</div>
</section>
<section class="home-section" id="publications">
  <div class="section-heading"><div><div class="home-kicker">PUBLICATIONS</div><h2>Papers</h2></div><a class="text-link" href="{SCHOLAR}" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a></div>
  <p class="home-lead">Author lists follow the original papers. <span class="pub-me">Zijun Song</span> is me. Accepted first-author work is listed first, then accepted co-authored papers, then other manuscripts.</p>
  <h3 class="pub-group">Research Papers</h3>
  <div class="pub-list">{''.join(pub_item(p) for p in RESEARCH_PAPERS)}</div>
  <h3 class="pub-group">Technical Reports</h3>
  <div class="pub-list">{''.join(pub_item(p) for p in TECH_REPORTS)}</div>
</section>
<section class="projects-preview" id="open-source">
  <div class="section-heading"><div><div class="home-kicker">OPEN SOURCE</div><h2>From papers to code</h2></div><a class="text-link" href="projects.html">All projects ↗</a></div>
  <div class="project-strip">
    <a href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer"><span class="project-number">01</span><div><h3>PertDiffBench ↗</h3><p>A unified benchmark for perturbation response prediction.</p></div><span class="project-type">AI4SCIENCE</span></a>
    <a href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer"><span class="project-number">02</span><div><h3>Capability Evolution ↗</h3><p>Agent capability, self-evolution, and training.</p></div><span class="project-type">AGENTS</span></a>
    <a href="https://github.com/ZijunSong/On-Policy-Context-Distillation" target="_blank" rel="noopener noreferrer"><span class="project-number">03</span><div><h3>On-Policy Context Distillation ↗</h3><p>An open implementation of on-policy distillation.</p></div><span class="project-type">POST-TRAINING</span></a>
  </div>
</section>
<section class="closing-note"><span class="handwritten">A work in progress.</span><p>Research is more than papers.<br>Some of the process belongs here too.</p><a href="mailto:2949203143@qq.com">Get in touch <span>↗</span></a></section>
</main>'''

blog_body = f'''<main id="main"><section class="notes-section page-notes" id="blog"><div class="section-heading"><div><div class="eyebrow">BLOG</div><h2>Posts<span class="section-count"> / {str(len(BLOG_POSTS)).zfill(2)}</span></h2></div><p>Method notes from ongoing research.</p></div><div class="notes-tools"><div class="filters" role="group" aria-label="Filter by topic">{''.join(f'<button data-filter="{t}" aria-pressed="{str(t=="All").lower()}">{t}</button>' for t in ['All','Agent','Post-training'])}</div><label class="search-box"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8" cy="8" r="5.5"/><path d="m12 12 5 5"/></svg><input id="search" type="search" placeholder="Search posts…" aria-label="Search posts"><kbd>/</kbd></label></div><div class="notes-grid">{''.join(card(p, i==0) for i,p in enumerate(BLOG_POSTS))}</div><p class="no-results" hidden>No matching posts. Try another keyword or topic.</p></section></main>'''

(OUT / 'index.html').write_text(shell('About', home, 'home'), encoding='utf-8')
(OUT / 'blog.html').write_text(shell('Blog', blog_body, 'blog', 'Research notes by Zijun Song on agents, post-training, and tool learning.'), encoding='utf-8')
(OUT / 'notes.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=blog.html"><link rel="canonical" href="blog.html"><title>Blog · Zijun Song</title></head><body><p><a href="blog.html">Go to the blog</a></p></body></html>', encoding='utf-8')
(OUT / 'about.html').write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=./"><link rel="canonical" href="./"><title>About · Zijun Song</title></head><body><p><a href="./">Go to the homepage</a></p></body></html>',
    encoding='utf-8',
)

(OUT / 'posts').mkdir(exist_ok=True)
for p in BLOG_POSTS:
    body, toc = markdown((ROOT / 'content/posts' / f"{p['slug']}.md").read_text(encoding='utf-8'))
    article_notice = ''
    citation = f"Zijun Song. {p['title']}. Blog, {p['date']}. {BASE}/posts/{p['slug']}.html"
    article = f'''<main id="main" class="article-main"><a class="back-link" href="../blog.html">← Back to blog</a><header class="article-header"><div class="eyebrow">{E(p['kind'])} / {E(' · '.join(p['tags']))}</div><h1>{E(p['title'])}</h1><p class="article-deck">{E(p['summary'])}</p><div class="author-line"><span class="author-mark">ZS</span><span>Zijun Song<br><small>{p['date']} · {p['minutes']} min read · {E(p.get('version', 'v1.0'))}</small></span></div></header><div class="article-layout"><article class="prose">{article_notice}{body}<div class="citation-box"><span class="eyebrow">CITE</span><p id="citation">{E(citation)}</p><button class="copy-citation">Copy citation</button><span class="copy-feedback" role="status"></span></div><nav class="article-nav" aria-label="Keep reading"><span>Keep reading</span>{''.join(f'<a href="{E(other["slug"])}.html">{E(other["title"])} ↗</a>' for other in BLOG_POSTS if other != p)}</nav></article><aside class="toc"><span class="eyebrow">ON THIS PAGE</span>{''.join(f'<a href="#{anchor}">{E(label)}</a>' for anchor, label in toc)}<a class="back-top" href="#main">Back to top ↑</a></aside></div></main>'''
    (OUT / 'posts' / f"{p['slug']}.html").write_text(shell(p['title'], article, 'blog', p['summary'], path='posts/' + p['slug'] + '.html'), encoding='utf-8')

project_body = '''<main id="main" class="page-main"><div class="eyebrow">SELECTED PROJECTS</div><h1>Let ideas meet practice.</h1><p class="page-deck">Selected open-source work from GitHub. Code and latest results live in each repository.</p>
<div class="project-full"><span class="project-number">01 / AI FOR SCIENCE</span><h2>PertDiffBench</h2><p>A benchmark for perturbation response prediction, with a shared interface across models and tasks, including unseen cell types, species, and drugs.</p><a class="primary-button" href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer">View GitHub repo ↗</a></div>
<div class="project-full"><span class="project-number">02 / AGENTS</span><h2>Capability Evolution</h2><p>Research code on agent capability, self-evolution, and training, including harness internalization.</p><a class="primary-button" href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer">View GitHub repo ↗</a></div>
<div class="project-full"><span class="project-number">03 / POST-TRAINING</span><h2>On-Policy Context Distillation</h2><p>An open reimplementation of on-policy context distillation.</p><a class="primary-button" href="https://github.com/ZijunSong/On-Policy-Context-Distillation" target="_blank" rel="noopener noreferrer">View GitHub repo ↗</a></div>
<div class="project-full"><span class="project-number">04 / TOOL LEARNING</span><h2>ToLeaP</h2><p>Code around evaluating and developing tool learning for large language models.</p><a class="primary-button" href="https://github.com/ZijunSong/ToLeaP" target="_blank" rel="noopener noreferrer">View GitHub repo ↗</a></div>
</main>'''
(OUT / 'projects.html').write_text(shell('Projects', project_body, 'projects'), encoding='utf-8')
(OUT / '404.html').write_text(shell('Page not found', '<main id="main" class="page-main"><div class="eyebrow">404 / A SMALL DETOUR</div><h1>This note is not written yet.</h1><p class="page-deck">The link may have moved. Head back to the homepage.</p><a class="primary-button" href="./">Back home ↗</a></main>'), encoding='utf-8')
(OUT / '.nojekyll').touch()
(OUT / 'feed.xml').write_text(
    '<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Zijun Song · Blog</title><link>' + BASE + '</link><description>Research notes on agents and post-training</description>' +
    ''.join('<item><title>' + xml_escape(p['title']) + '</title><link>' + BASE + '/posts/' + p['slug'] + '.html</link><guid>' + BASE + '/posts/' + p['slug'] + '.html</guid><description>' + xml_escape(p['summary']) + '</description></item>' for p in BLOG_POSTS) +
    '</channel></rss>',
    encoding='utf-8',
)
pages = ['', 'blog.html', 'projects.html'] + ['posts/' + p['slug'] + '.html' for p in BLOG_POSTS]
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join('<url><loc>' + BASE + '/' + p + '</loc></url>' for p in pages) + '</urlset>', encoding='utf-8')
(OUT / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: ' + BASE + '/sitemap.xml\n', encoding='utf-8')
for name in ('Papers', 'Pics'):
    src, dst = ROOT / name, OUT / name
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
print('Built homepage, notes, projects, RSS, sitemap. Assets retained.')
