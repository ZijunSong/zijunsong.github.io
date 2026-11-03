# Zijun Song · Research Notes

一套可部署到 `https://zijunsong.github.io` 的个人研究博客。暖白纸感与紫色点缀，包含研究笔记、项目、作者介绍、文章目录、代码复制、引用复制、主题筛选、标题/摘要/标签搜索、深色模式、RSS 与站点地图。搜索不包含文章全文。所有前端资源均在本地，无外部字体、图片或脚本依赖。

## 在线地址

站点已发布到 GitHub Pages：<https://zijunsong.github.io>

本地静态文件在 `dist/`。修改 Markdown 后运行 `python scripts/build.py`，再提交即可更新。

## 部署到你已有的 GitHub Pages

你已经有 `ZijunSong/zijunsong.github.io`，无需再创建仓库。下面两种方法选一种。

### 方法 A：直接上传静态页面，操作最少

1. 先在原仓库中建立一个备份分支，保留现有主页。
2. 将 `dist/` **内部**的所有文件上传到仓库根目录。不是把整个 dist 文件夹放到根目录。`index.html` 会替换旧首页；已有 `Pics/`、`Papers/` 等其他目录不要删除。
3. 仓库 Settings → Pages → Source 选择 Deploy from a branch，选择 main 和 /(root)。
4. 等 GitHub Pages 部署完成后查看 `https://zijunsong.github.io`。此方式以后需本地运行构建，再上传更新的 dist 文件。

### 方法 B：Markdown 自动发布，适合长期使用

1. 先备份现有仓库，然后把本项目的 `content/`、`scripts/build.py`、`dist/assets/` 和 `.github/workflows/pages.yml` 合并进原仓库，提交到 main。原有其他文件可继续保留。
2. 在 Settings → Pages → Source 选择 GitHub Actions。
3. 在 Actions 查看 Publish research notebook 的运行。构建只依赖 Python 3 标准库，不需要安装 npm 或 Python 包。
4. 后续修改 Markdown 并提交，页面会自动构建发布。

注意：方法 B 部署的内容仅来自 dist。原站的 `Papers/`、`Pics/` 与旧 HTML 若需要继续访问，须在构建前复制到 dist，并避免覆盖新首页；当前新版未链接原站的旧文件。正式切换前请检查对外使用的旧论文下载链接。方法 A 则会继续保留仓库根目录原有的这些路径。

GitHub 官方说明：https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 发布一篇文章

1. 在 `content/posts/` 创建 `your-post.md`。
2. 在 `content/posts.json` 的开头增加文章元数据：

```json
{
  "slug": "your-post",
  "title": "你的文章标题",
  "summary": "用一两句话讲清研究问题与核心发现。",
  "tags": ["Agent", "后训练"],
  "kind": "METHOD NOTES",
  "date": "2026-11-03",
  "minutes": 8,
  "example": false,
  "version": "v1.0"
}
```

3. 使用 `##` 作为文章章节标题，目录会自动生成；正文支持段落、`###` 小标题、加粗、行内代码、代码块、无序列表、引用段和 HTTPS 链接。当前是轻量 Markdown 子集，**不支持 LaTeX 渲染、图片与 Markdown 表格**。若需要复杂数学推导或大量图表，可进一步加入完整 Markdown/KaTeX 构建。
4. 本地执行 `python3 scripts/build.py`。方法 B 提交后会自动构建。

标签筛选默认是 Agent / 后训练 / AI4Science；如新增类别，在 `scripts/build.py` 中的筛选列表同步添加。

## 示例内容与个人信息

当前三篇文章是为展示排版而写的概念性示例，均明确标记“示例文章 · 待审阅”，不代表作者正式研究结论。请用自己的稿件替换。设置 `example: false` 后，文章和卡片将移除示例标记；全部文章均为正式稿时，首页提示也会移除。

项目链接来自公开仓库；姓名、研究方向与邮箱以用户提供信息和已有主页为依据。上线前可在 `scripts/build.py` 修改个人介绍与联系方式。

## 文件结构

- `content/posts.json`：文章目录与元数据。
- `content/posts/*.md`：文章正文。
- `scripts/build.py`：静态生成器与页面模板。
- `dist/assets/style.css`：样式与响应式布局。
- `dist/assets/app.js`：搜索、筛选、主题与复制交互。
- `dist/`：可直接部署的静态网站。
- `.github/workflows/pages.yml`：可选的 GitHub Pages 自动发布配置。

构建命令不会删除 dist 中现有资产。移除文章后，如需同时删除旧文章 URL，应手动移除对应 dist/posts 文件。

## 设计参考

借鉴信息组织与阅读体验，不复制文章或源代码：

- Lil'Log：https://lilianweng.github.io/ —— 清晰的文章层级与长期知识积累。
- Andrej Karpathy：https://karpathy.github.io/ —— 直接的问题表达与项目导向写作。
- colah's blog：https://colah.github.io/ —— 以图解辅助理解方法。

## 验证记录

本次已检查静态脚本语法、生成文件与内部链接，使用浏览器检查首页、主题筛选、关键词与空搜索结果、文章阅读、深色主题，以及 390/320 像素容器中的响应式布局。GitHub Actions 未在用户仓库实际运行，需获得写入权限后才能完成原站部署验证。
