from pathlib import Path
import json, re, html, shutil
from xml.sax.saxutils import escape as xml_escape
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist'; OUT.mkdir(exist_ok=True)
POSTS=json.loads((ROOT/'content/posts.json').read_text(encoding='utf-8'))
BASE='https://zijunsong.github.io'
E=lambda s:html.escape(str(s),quote=True)
def inline(s):
    s=E(s)
    s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2" target="_blank" rel="noopener noreferrer">\1 ↗</a>',s)
    return s

def markdown(text):
    out=[]; toc=[]; para=[]; code=None; buf=[]; listing=False
    def flush():
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para.clear()
    for line in text.splitlines()+['']:
        if line.startswith('```'):
            flush()
            if code is None: code=line[3:].strip(); buf=[]
            else:
                out.append('<div class="code-wrap"><div class="code-head"><span>'+E(code or 'text')+'</span><button class="copy-code">复制代码</button></div><pre><code>'+E('\n'.join(buf))+'</code></pre></div>'); code=None
            continue
        if code is not None: buf.append(line); continue
        if listing and not line.startswith('- '):out.append('</ul>');listing=False
        if line.startswith('## '):
            flush(); label=line[3:]; anchor='section-'+str(len(toc)+1);toc.append((anchor,label));out.append(f'<h2 id="{anchor}">{inline(label)}</h2>')
        elif line.startswith('### '):flush();out.append('<h3>'+inline(line[4:])+'</h3>')
        elif line.startswith('> '):flush();out.append('<blockquote>'+inline(line[2:])+'</blockquote>')
        elif line.startswith('- '):
            flush()
            if not listing:out.append('<ul>');listing=True
            out.append('<li>'+inline(line[2:])+'</li>')
        elif not line.strip():flush()
        else:para.append(line)
    return '\n'.join(out),toc

def shell(title,body,active='notes',desc='宋子骏的研究笔记：Agent、自进化、后训练与 AI for Science。',path=''):
    nav=''.join(f'<a href="/{p}" '+('aria-current="page"' if active==key else '')+f'>{label}</a>' for key,p,label in [('notes','','研究笔记'),('projects','projects.html','项目'),('about','about.html','关于我')])
    # Relative paths also support project Pages under a subdirectory.
    depth='../' if path.startswith('posts/') else './'
    nav=nav.replace('href="/','href="'+depth)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} · Zijun Song</title><meta name="description" content="{E(desc)}"><meta name="theme-color" content="#f8f7f4"><meta property="og:title" content="{E(title)} · Zijun Song"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="{'article' if path.startswith('posts/') else 'website'}"><link rel="icon" href="{depth}assets/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Zijun Song · Research Notes" href="{depth}feed.xml"><link rel="stylesheet" href="{depth}assets/style.css"><script src="{depth}assets/app.js" defer></script></head><body><a class="skip" href="#main">跳到正文</a><div class="reading-progress" aria-hidden="true"></div><header class="site-header"><a class="brand" href="{depth}"><span class="monogram">zs<span>·</span></span><span>Zijun Song <span class="brand-sub">/ Research Notes</span></span></a><nav aria-label="主导航">{nav}<a class="github-nav" href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub ↗</a><button class="theme-switch" aria-label="切换深色模式" title="切换深色模式">◐</button></nav></header>{body}<footer class="site-footer"><div><a class="footer-name" href="{depth}">Zijun Song<span> / 紫色噩梦</span></a><p>把想法写清楚，把实验做扎实。</p></div><div class="footer-right"><a href="{depth}feed.xml">RSS ↗</a><a href="mailto:2949203143@qq.com">Email ↗</a><span>© 2026 · An open research notebook.</span></div></footer></body></html>'''

def card(p,featured=False):
    tags=''.join('<span>'+E(t)+'</span>' for t in p['tags'])
    return f'''<a class="note-card {'featured-card' if featured else ''}" href="posts/{E(p['slug'])}.html" data-tags="{E(' '.join(p['tags']))}" data-search="{E(p['title']+' '+p['summary']+' '+' '.join(p['tags']))}"><div class="note-meta"><span>{E(p['kind'])}</span><span>{p['date'].replace('-','.')} · {p['minutes']} MIN READ</span></div><h3>{E(p['title'])}<span class="card-arrow">↗</span></h3><p>{E(p['summary'])}</p><div class="card-bottom"><div class="tags">{tags}</div>{('<span class="draft-status">示例文章 · 待审阅</span>' if p.get('example', True) else '<span class="draft-status">研究文章</span>')}</div></a>'''

hero='''<section class="hero"><div class="hero-copy"><div class="eyebrow"><span class="tiny-dot"></span> ZIJUN SONG’S RESEARCH NOTEBOOK</div><h1>让想法走出草稿，<br>让研究<span class="purple-title">持续生长。</span></h1><p class="hero-description">你好，我是宋子骏，也叫紫色噩梦。<br>一名研究 AI Agent 的博士生，在这里记录方法、实验，<br class="desktop-break">以及还在形成中的思考。</p><div class="hero-actions"><a class="primary-button" href="#notes">开始阅读 <span>↘</span></a><a class="text-link" href="about.html">更多关于我 ↗</a></div><div class="hero-topics"><span>AI AGENTS</span><i></i><span>SELF-EVOLUTION</span><i></i><span>POST-TRAINING</span></div></div><div class="hero-art" aria-label="从想法到实验再到新问题的研究循环示意图"><div class="art-coordinate">FIG. 01 / THE RESEARCH LOOP</div><svg viewBox="0 0 500 350" role="img" aria-label="想法、实验和证据构成持续迭代的循环"><defs><pattern id="grid" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="currentColor" opacity=".16"/></pattern><marker id="arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="none" stroke="currentColor"/></marker></defs><rect width="500" height="350" fill="url(#grid)"/><ellipse cx="250" cy="179" rx="178" ry="112" fill="none" stroke="currentColor" opacity=".12" transform="rotate(-24 250 179)"/><ellipse cx="250" cy="179" rx="142" ry="142" fill="none" stroke="currentColor" opacity=".09"/><path d="M171 140 C235 56 340 73 371 155 M355 220 C320 290 207 305 158 232 M116 197 C91 164 104 120 128 111" fill="none" stroke="currentColor" stroke-width="1.5" marker-end="url(#arrow)"/><g fill="var(--bg)" stroke="currentColor" stroke-width="1.2"><rect x="95" y="132" width="111" height="57" rx="8"/><rect x="314" y="167" width="111" height="57" rx="8"/><rect x="171" y="267" width="111" height="57" rx="8"/></g><g fill="currentColor" font-size="13" font-family="monospace" text-anchor="middle"><text x="150" y="166">01 / IDEA</text><text x="369" y="201">02 / TEST</text><text x="226" y="301">03 / LEARN</text></g><circle cx="248" cy="186" r="36" fill="var(--purple-soft)"/><path d="M239 174 L251 174 L245 186 L259 186 L239 207 L244 192 L234 192 Z" fill="var(--purple)"/><g fill="var(--purple)"><circle cx="173" cy="84" r="4"/><circle cx="393" cy="265" r="3"/><circle cx="79" cy="258" r="3"/></g></svg><div class="art-caption"><span>好问题 → 可检验的想法 → 新问题</span><span>↺</span></div></div></section>'''
index_body=f'''<main id="main">{hero}<section class="notes-section" id="notes"><div class="section-heading"><div><div class="eyebrow">THE NOTEBOOK</div><h2>研究笔记<span class="section-count"> / 03</span></h2></div><p>方法拆解、实验记录与开放思考。</p></div><div class="editorial-notice"><span>初次见面</span> 下面是用于预览排版的示例文章，尚未经作者审阅；正式稿件可用 Markdown 持续发布。</div><div class="notes-tools"><div class="filters" role="group" aria-label="按主题筛选">{''.join(f'<button data-filter="{t}" aria-pressed="{str(t=="全部").lower()}">{t}</button>' for t in ['全部','Agent','后训练','AI4Science'])}</div><label class="search-box"><svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8" cy="8" r="5.5"/><path d="m12 12 5 5"/></svg><input id="search" type="search" placeholder="搜索笔记…" aria-label="搜索研究笔记"><kbd>/</kbd></label></div><div class="notes-grid">{''.join(card(p,i==0) for i,p in enumerate(POSTS))}</div><p class="no-results" hidden>没有找到相关笔记，试试其他关键词或主题。</p></section><section class="projects-preview"><div class="section-heading"><div><div class="eyebrow">BUILDING IN THE OPEN</div><h2>从笔记到代码</h2></div><a class="text-link" href="projects.html">查看全部项目 ↗</a></div><div class="project-strip"><a href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer"><span class="project-number">01</span><div><h3>Capability Evolution ↗</h3><p>探索 Agent 能力、自进化与训练。</p></div><span class="project-type">AGENTS</span></a><a href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer"><span class="project-number">02</span><div><h3>PertDiffBench ↗</h3><p>面向细胞扰动响应预测的统一评测。</p></div><span class="project-type">AI4SCIENCE</span></a></div></section><section class="closing-note"><span class="handwritten">A work in progress.</span><p>研究不止于论文。<br>一些值得留下的过程，也在这里。</p><a href="mailto:2949203143@qq.com">欢迎交流想法 <span>↗</span></a></section></main>'''
(OUT/'index.html').write_text(shell('研究笔记',index_body.replace(' / 03',' / '+str(len(POSTS)).zfill(2)) if any(p.get('example',True) for p in POSTS) else re.sub(r'<div class="editorial-notice">.*?</div>','',index_body.replace(' / 03',' / '+str(len(POSTS)).zfill(2)))), encoding='utf-8')
(OUT/'posts').mkdir(exist_ok=True)
for p in POSTS:
    body,toc=markdown((ROOT/'content/posts'/f"{p['slug']}.md").read_text(encoding='utf-8'))
    article_notice='<div class="article-notice"><strong>关于这篇示例</strong><p>此文用于展示博客的阅读体验，是依据研究主题撰写的概念性示例，尚未经作者审阅，不代表正式研究报告或实验结论。</p></div>' if p.get('example',True) else ''
    citation=f"宋子骏. {p['title']}. Research Notes, {p['date']}. {BASE}/posts/{p['slug']}.html"
    article=f'''<main id="main" class="article-main"><a class="back-link" href="../#notes">← 返回研究笔记</a><header class="article-header"><div class="eyebrow">{E(p['kind'])} / {E(' · '.join(p['tags']))}</div><h1>{E(p['title'])}</h1><p class="article-deck">{E(p['summary'])}</p><div class="author-line"><span class="author-mark">ZS</span><span>宋子骏 · Zijun Song<br><small>{p['date']} · {p['minutes']} 分钟阅读 · {('v0.1 示例稿' if p.get('example',True) else E(p.get('version','v1.0')))}</small></span></div></header><div class="article-layout"><article class="prose">{article_notice}{body}<div class="citation-box"><span class="eyebrow">引用与分享</span><p id="citation">{E(citation)}</p><button class="copy-citation">复制引用</button><span class="copy-feedback" role="status"></span></div><nav class="article-nav" aria-label="继续阅读"><span>继续阅读</span>{''.join(f'<a href="{E(other["slug"])}.html">{E(other["title"])} ↗</a>' for other in POSTS if other!=p)}</nav></article><aside class="toc"><span class="eyebrow">ON THIS PAGE</span>{''.join(f'<a href="#{anchor}">{E(label)}</a>' for anchor,label in toc)}<a class="back-top" href="#main">回到顶部 ↑</a></aside></div></main>'''
    (OUT/'posts'/f"{p['slug']}.html").write_text(shell(p['title'],article,desc=p['summary'],path='posts/'+p['slug']+'.html'), encoding='utf-8')
project_body='''<main id="main" class="page-main"><div class="eyebrow">SELECTED PROJECTS</div><h1>让想法经受实践。</h1><p class="page-deck">我的部分开源项目。代码、实现细节与项目进展，以各仓库为准。</p><div class="project-full"><span class="project-number">01 / AGENTS</span><h2>Capability Evolution</h2><p>围绕 Agent 能力演化与训练展开的研究代码。当前关注 Harness、自进化与能力内化之间的关系。</p><a class="primary-button" href="https://github.com/ZijunSong/Capability_Evolution" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div><div class="project-full"><span class="project-number">02 / AI FOR SCIENCE</span><h2>PertDiffBench</h2><p>面向细胞扰动响应预测的评测框架，提供多类模型与任务的统一运行接口，关注跨细胞类型、跨物种和未见药物等泛化场景。</p><a class="primary-button" href="https://github.com/ZijunSong/PertDiffBench" target="_blank" rel="noopener noreferrer">查看 GitHub 仓库 ↗</a></div></main>'''
(OUT/'projects.html').write_text(shell('开源项目',project_body,'projects'), encoding='utf-8')
about='''<main id="main" class="page-main about-page"><div class="eyebrow">ABOUT THE AUTHOR</div><h1>宋子骏<span class="serif-name">Zijun Song.</span></h1><div class="about-intro"><div class="about-avatar" aria-hidden="true">宋<span>紫色噩梦 / ZS</span></div><div><p class="page-deck">你好，我是紫色噩梦，<br>一名关注 AI Agent 的计算机领域博士生。</p><p>我对一个问题尤其感兴趣：如何让 Agent 从完成任务的过程里，获得可以保留下来、迁移出去的能力？围绕这个问题，我关注 Harness、自进化、后训练，以及 Search Agent 的实践。</p><p>这里是我的开放研究笔记本。我希望把方法的来龙去脉讲清楚，也留下一些实验过程中值得讨论的问题。</p></div></div><section class="about-section"><h2>我关心的方向</h2><div class="interest-list"><div><span>01</span><h3>Agent & Self-evolution</h3><p>外部执行系统与模型能力如何共同演化。</p></div><div><span>02</span><h3>Search & Post-training</h3><p>如何获得有效证据，并把行为改进沉淀下来。</p></div><div><span>03</span><h3>AI for Science</h3><p>把智能体与建模方法放进真实科研问题。</p></div></div></section><section class="about-section"><h2>保持联系</h2><p>欢迎围绕研究方法、复现与开源项目交流。</p><div class="contact-links"><a href="https://github.com/ZijunSong" target="_blank" rel="noopener noreferrer">GitHub ↗</a><a href="mailto:2949203143@qq.com">Email ↗</a><a href="https://scholar.google.com/citations?user=oCGK2GoAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar ↗</a></div></section></main>'''
(OUT/'about.html').write_text(shell('关于我',about,'about'), encoding='utf-8')
(OUT/'404.html').write_text(shell('页面未找到','<main id="main" class="page-main"><div class="eyebrow">404 / A SMALL DETOUR</div><h1>这页笔记还没写到。</h1><p class="page-deck">链接可能已经更新，回到首页继续阅读。</p><a class="primary-button" href="/">返回首页 ↗</a></main>'), encoding='utf-8')
(OUT/'.nojekyll').touch()
(OUT/'feed.xml').write_text('<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel><title>Zijun Song · Research Notes</title><link>'+BASE+'</link><description>研究笔记与方法分享</description>'+''.join('<item><title>'+xml_escape(p['title'])+'</title><link>'+BASE+'/posts/'+p['slug']+'.html</link><guid>'+BASE+'/posts/'+p['slug']+'.html</guid><description>'+xml_escape(('[示例文章·待审阅] ' if p.get('example',True) else '')+p['summary'])+'</description></item>' for p in POSTS)+'</channel></rss>', encoding='utf-8')
(OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="utf-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+BASE+'/'+p+'</loc></url>' for p in ['','about.html','projects.html']+['posts/'+p['slug']+'.html' for p in POSTS])+'</urlset>', encoding='utf-8')
(OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+BASE+'/sitemap.xml\n', encoding='utf-8')
for name in ('Papers', 'Pics'):
    src, dst = ROOT/name, OUT/name
    if src.exists():
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
print('Built 7 HTML pages, RSS, sitemap. Assets retained.')
