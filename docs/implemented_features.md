# CANN Recipes Blog 已实现功能清单

更新时间：2026-07-21

本文档记录 `new_docs` 分支当前已经实现的功能。详细需求与设计决策请参阅 `recipe_blog_requirements.md`。

## 内容与导航

- 支持分类、子分类、模型、报告四级内容导航。
- 根据 `content/index.json` 动态生成可展开的侧边栏目录树。
- 本地开发从 GitCode 远程加载 Markdown，不在仓库中持久化报告正文。
- GitHub Pages 从 CI 生成的同源静态正文缓存加载报告，避免 GitCode CORS/WAF 导致正文不可用。
- 支持 Markdown 标题、列表、链接、引用、代码块、图片和表格。
- 支持代码语法高亮和一键复制。
- 支持 Mermaid 图表渲染。
- 支持 KaTeX 数学公式渲染。
- 报告面包屑支持点击返回上级目录。
- 报告目录支持章节高亮和滚动跟踪。
- 支持上一篇和下一篇报告导航。
- 支持阅读进度条。
- 宽表格限制在报告正文区域内，并支持横向滚动。

## 首页

- 根据 manifest 数据生成 Recent Reports 列表。
- 从远程 Markdown 的第一张图片提取报告封面。
- 报告没有图片或图片加载失败时，显示按分类设计的 CSS 占位封面。
- 提供 Infer、Train、Embodied Intelligence 和 Docs 仓库快捷入口。
- 侧边栏提供唯一的 `Browse Docs Repo` 入口。

## 搜索与发现

- 支持按报告文件名标题、模型名称和分类实时搜索。
- 不修改关键词时，可以按 Enter 重新执行搜索。
- 搜索结果使用全宽响应式卡片。
- 搜索结果中的报告封面完整显示，不裁切技术图表。
- 根据文件名生成报告标签，并写入 manifest。
- 搜索框旁提供便捷的 Tags 筛选面板。
- 支持仅按标签筛选，以及关键词与标签组合筛选。
- 报告卡片和搜索结果卡片中的标签可以直接点击。
- 结果页显示当前活动筛选条件，并支持一键清除。

## 报告封面

- `build_content.py` 临时读取 Markdown，定位首个 Markdown 或 HTML 图片。
- manifest 只保存 GitCode 远程封面 URL，不保存 Base64 图片数据。
- 封面使用 `object-fit: contain`，避免裁切技术图表。
- 浏览器加载 manifest 时绕过旧缓存。
- 远程封面加载失败时自动重试一次，再回退到分类占位封面。

## 反馈与互动

- 每篇真实报告底部提供反馈入口。
- 报告视图提供浮动反馈快捷按钮。
- 支持内容纠错、Bug 报告、功能建议和技术讨论四种 Issue 类型。
- 自动预填 Issue 标题、报告路径、阅读地址和 Markdown 模板。
- 根据报告分类自动路由到 Infer、Train、Embodied AI 或 Docs 仓库。
- 同时兼容 `title` / `body` 和 GitLab 风格的 Issue 查询参数。
- 支持通过关闭按钮、点击遮罩或按 Escape 关闭反馈弹窗。

## 视觉与可访问性

- 使用玻璃拟态界面和克制的橙色强调色。
- 支持浅色和深色主题。
- 导航与操作按钮使用 Material Symbols 图标。
- 报告卡片和搜索结果支持响应式布局。
- 长标题和仓库名称可以在容器内自动换行。
- 宽表格支持键盘聚焦和横向滚动。
- 纯图标控件提供工具提示或无障碍标签。

## 构建与部署

- manifest 生成器只依赖 Python 标准库。
- 支持动态发现 GitCode 目录结构。
- manifest 包含文件路径、标签、封面和来源仓库路由元数据。
- 支持 GitHub Pages 自动部署。
- 支持定时刷新内容。
- CI 会校验正文缓存数量；构建不完整时停止部署并保留上一版可用站点。
- `content/reports/` 只存在于 Pages 部署产物，并通过 `.gitignore` 排除在仓库之外。
- 提供本地静态服务器和可选的只读 GitCode 代理。

## 明确取消的功能

- Popular Reports 排行和访问统计：可靠排行需要持久化 PV、访问去重、数据库以及后端聚合接口。
- 邮件列表订阅：已从当前产品范围中移除。

## 主要文件

- `index.html`：应用界面、内容渲染、搜索、筛选、报告阅读、封面和反馈功能。
- `build_content.py`：GitCode 内容发现和 manifest 元数据生成。
- `content/index.json`：生成后的报告元数据。
- `docs/recipe_blog_requirements.md`：详细需求和设计决策。
