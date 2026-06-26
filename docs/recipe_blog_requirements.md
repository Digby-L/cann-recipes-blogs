# CANN Recipes Blog — 需求分析与方案设计

> 版本：v1.0 | 更新日期：2026-06-26

---

## 1. 需求背景

### 1.1 项目定位

CANN Recipes Blog 是一个面向 **Ascend 开发者社区** 的技术报告浏览平台。它将散落在多个 GitCode 仓库中的模型优化技术报告（Markdown 格式）聚合呈现为一个统一的、可搜索的、具有良好阅读体验的静态网站。

**核心价值：**
1. 让开发者无需逐个翻看仓库，即可快速发现、阅读和分享 CANN recipe 生态中的最佳实践和优化指南。
2. 将文档和图片从 recipe 代码仓中剥离——原仓库因大量 Markdown 和图片导致体积膨胀，clone 慢、IDE 打开卡顿。文档迁移到 Blog 站点后，代码仓可瘦身为纯代码，开发者日常操作不再被文档资产拖累。
3. 作为多仓库的统一门户——将 Infer、Train、Spatial Intelligence、Embodied Intelligence 四个仓库的信息聚合呈现，用户先在门户中总览全貌、搜索定位，再按需跳转到具体仓库深入了解代码实现，实现"信息聚焦，再分流"。

### 1.2 目标用户

| 角色 | 需求 |
|------|------|
| **报告浏览者** | 快速查找某模型的优化方案，阅读完整报告，复制代码片段 |
| **内容维护者** | 在 GitCode 仓库中添加/更新 Markdown 即可自动上线，无需手动部署 |
| **网站维护者** | 清晰的架构和文档，方便后续功能迭代 |

### 1.3 内容来源

报告内容来自 4 个 GitCode 仓库，按 AI 场景分类：

| 分类 | 仓库 | 扫描路径 | 说明 |
|------|------|----------|------|
| 推理 (Infer) | `cann/cann-recipes-infer` | `docs/models` | 大模型推理优化（DeepSeek、Qwen、Hunyuan 等） |
| 训练 (Train) | `cann/cann-recipes-train` | `docs` | 预训练、RL 训练优化 |
| 空间智能 (Spatial Intelligence) | `cann/cann-recipes-spatial-intelligence` | `docs/models` | 3D 生成、视觉几何 |
| 具身智能 (Embodied Intelligence) | `cann/cann-recipes-embodied-intelligence` | `docs` | 机器人 VLA 推理 |

### 1.4 部署形态

- **静态站点**，无后端服务
- 当前部署在 **GitHub Pages**（通过 GitHub Actions 自动构建）
- 计划支持 **GitCode Pages** 部署（基于 GitLab CI）
- 内容在 CI 构建时预拉取为静态 JSON，运行时无外部 API 依赖

---

## 2. 需求分解

按功能域拆分为以下模块：

| 功能域 | 子项 | 状态 |
|--------|------|------|
| **内容展示** | 分类浏览（四大类 → 模型 → 报告） | ✅ 已完成 |
| | 报告 Markdown 渲染 | ✅ 已完成 |
| | 侧边栏层级导航 | ✅ 已完成 |
| | 首页推荐（最新 + 热门） | ✅ 已完成 |
| | 代码高亮 + 复制 | ✅ 已完成 |
| | 图片 Base64 嵌入 | 🔲 TODO |
| | 报告目录导航 (TOC) | 🔲 TODO |
| | 上一篇 / 下一篇导航 | 🔲 TODO |
| | 阅读进度条 | 🔲 TODO |
| **搜索发现** | 关键词搜索（标题/模型名） | ✅ 已完成 |
| | 全文检索（报告正文） | 🔲 TODO |
| | 标签筛选 | 🔲 TODO |
| **构建部署** | GitHub Pages 自动部署 | ✅ 已完成 |
| | GitCode Pages 部署 | 🔲 TODO |
| | 定时刷新（每日 cron） | ✅ 已完成 |
| | 内容预拉取（build_content.py） | ✅ 已完成 |
| **视觉设计** | 配色方案（玻璃拟态 + 橙色主题） | ✅ 已完成 |
| | 关键图标选型（Material Icons） | ✅ 已完成 |
| | **[技术文章封面图选择与生成 — 待讨论](#discuss-cover-image)** | 🔲 TODO |
| | 暗色模式 | 🔲 TODO |
| | 移动端适配 | 🔲 TODO |
| | 打印友好样式 | 🔲 TODO |
| **国际化** | 中英文 UI 切换 | 🔲 TODO |
| **订阅通知** | **[邮件列表订阅 — 待讨论](#discuss-subscribe)** | ✅ 已完成 |
| | RSS 订阅源（优先级低） | 🔲 TODO |
| **反馈互动** | 提交 Issue，反馈与建议（引流到 GitCode Issue） | 🔲 TODO |
| **数据驱动** | 访问统计（驱动热门排序） | 🔲 TODO |
| **路由与子页面** | **[子页面路径支持（如 `/infer/`、`/train/`）— 待讨论](#discuss-routing)** | 🔲 TODO |
| **内容质量** | 技术文章润色与查虫（Agent 任务） | 🔲 TODO |
| | 文章规范制定（格式、命名、结构标准） | 🔲 TODO |
| | 报告关联仓库可执行 README 链接 | 🔲 TODO |
| **开发者体验** | 本地代理（proxy.py） | ✅ 已完成 |
| | 零依赖构建（纯 Python 标准库） | ✅ 已完成 |
| | **[技术文档分类及整理 — 待讨论](#discuss-docs-organize)** | 🔲 TODO |

---

## 3. 需求及方案设计

### 3.1 内容展示模块

#### 3.1.1 分类浏览（已完成）

**需求：** 用户可按 4 大分类 → 模型 → 报告三级层次浏览所有技术报告。

**方案设计：**
- 左侧固定侧边栏，使用 `<details>` 实现树形折叠
- 分类用 Material Icon 区分视觉
- 侧边栏可收起/展开，收起后内容区自动填满宽度
- 数据来源：`content/index.json` manifest 文件（构建时生成）

**技术选型：**
- 纯 HTML `<details>/<summary>` — 无需 JS 状态管理，语义化且可访问
- 宽度动画通过 CSS `transition: width 0.3s` 实现

---

#### 3.1.2 报告渲染（已完成）

**需求：** 完整呈现 Markdown 报告，包括标题层级、代码块、表格、引用块。

**方案设计：**
- 使用 marked.js 解析 Markdown
- highlight.js 提供代码语法高亮（Atom One Dark 主题）
- 代码块增加"复制"按钮
- Heading 生成 anchor ID（`slugify()` 支持中英文），为 TOC 预留

**Markdown 渲染流水线：**
```
报告 JSON → renderMarkdownWithImages(替换图片路径为 base64)
          → renderMarkdown(marked.js 自定义 renderer)
          → enhanceCodeBlocks(语法高亮 + 复制按钮)
```

---

#### 3.1.3 图片渲染（TODO — 待修复）

**需求：** 报告中的图片正确显示，无论是相对路径还是绝对路径引用。

**当前方案：** 构建时通过 GitCode API 拉取图片，编码为 base64 data URI 嵌入报告 JSON，渲染时替换路径。

**已知问题：**
- 部分图片渲染异常，base64 替换逻辑存在 bug
- 某些路径格式（如 `../common/images/`）匹配不到对应的 base64 数据

**修复方向：**
- 排查 `renderMarkdownWithImages()` 中路径匹配逻辑
- 对比 Markdown 中实际引用路径与 `images` 字典中的 key，确认是否一致
- 增加路径归一化处理（去掉 `./`、解析 `../`）

**修改文件：** `index.html`（`renderMarkdownWithImages` 函数）、`build_content.py`（图片路径采集逻辑）

**验证方法：**
1. 运行 `python build_content.py`，检查输出 JSON 中 `images` 字典的 key 列表
2. 打开含有多种路径格式图片的报告（如 `../common/`、`./figures/`）
3. 确认所有图片正常渲染，无 broken image 图标
4. 浏览器 DevTools Console 无 404 或 base64 解码错误

---

#### 3.1.4 报告目录导航 / TOC（TODO）

**需求：** 阅读长报告时，用户可通过目录快速跳转到目标章节。

**方案设计：**
- 报告渲染后，从 DOM 中提取所有 h2/h3 生成目录列表
- 右侧固定面板展示 TOC（宽屏），窄屏可收起为浮动按钮
- Scroll-spy：监听滚动事件，高亮当前可视区域对应的 TOC 条目
- 点击条目调用 `scrollIntoView({ behavior: 'smooth' })`

**前置条件：** heading anchor 已实现（`slugify()`），TOC 直接引用 `#id`。

**修改文件：** `index.html`（新增 TOC 面板 DOM + CSS + scroll-spy JS）

**验证方法：**
1. 打开一篇含有 5+ 个 h2/h3 标题的长报告
2. 确认右侧 TOC 面板正确列出所有章节标题
3. 点击 TOC 条目，页面平滑滚动到对应标题位置
4. 手动滚动页面，确认 TOC 高亮跟随变化
5. 缩小浏览器宽度至 < 768px，确认 TOC 收起/隐藏

---

#### 3.1.5 上一篇 / 下一篇导航（TODO）

**需求：** 报告底部显示同分类内相邻报告链接，方便连续阅读。

**方案设计：**
- 从 `repoModels` 中获取当前分类的所有报告，按模型字母序 + 文件名排序
- 定位当前报告的索引，取前后各一篇
- 在报告底部渲染 "← 上一篇 | 下一篇 →" 按钮
- 首/尾篇时隐藏对应方向的按钮

**修改文件：** `index.html`（`showReport()` 末尾追加导航 DOM）

**验证方法：**
1. 打开某分类中非首非尾的一篇报告，确认底部同时显示"上一篇"和"下一篇"
2. 打开该分类的第一篇报告，确认只显示"下一篇"
3. 打开该分类的最后一篇报告，确认只显示"上一篇"
4. 点击导航按钮，确认跳转正确

---

#### 3.1.6 阅读进度条（TODO）

**需求：** 页面顶部显示一条细进度条，指示当前报告阅读进度。

**方案设计：**
- 固定定位 `<div>` 在页面最顶部，高度 3px，背景色 `#E77A1D`
- 监听 `scroll` 事件，宽度 = `scrollTop / (scrollHeight - clientHeight) * 100%`
- 仅在 report 视图可见，切换到 home/category 时隐藏

**修改文件：** `index.html`（进度条 DOM + scroll listener）

**验证方法：**
1. 打开一篇长报告，确认顶部出现橙色进度条
2. 滚动到底部，确认进度条填满 100%
3. 切换到 Home 或 Category 视图，确认进度条消失
4. 回到报告视图，进度条重新出现

---

#### 3.1.7 首页（已完成）

**需求：** 首页展示最新报告和热门报告，引导用户进入阅读。

**方案设计：**
- "Recent Reports" 区：按 commitDate 排序取最新 6 篇，以卡片形式展示
- "Popular Reports" 区：展示推荐报告（当前为手动配置，未来接入真实访问数据）
- 卡片包含：缩略图、分类标签、标题、模型名

---

#### 3.1.5 面包屑导航（已完成）

**需求：** 在报告详情页显示路径 `Home > Category > Model > Report`，可点击回退。

**方案设计：** 纯 HTML 渲染，每个层级绑定 `onclick` 调用对应的 `showHome()`/`showCategory()`。

---

### 3.2 搜索发现模块

#### 3.2.1 关键词搜索（已完成）

**需求：** 按模型名、报告标题、分类名进行过滤。

**方案设计：**
- 顶部搜索框实时触发 `filterContent()`
- 遍历 `repoModels` 做字符串匹配
- 结果以卡片网格展示，显示匹配数

**局限：** 当前只搜索标题/模型名，不搜索报告正文内容。

---

#### 3.2.2 全文搜索（TODO）

**需求：** 支持搜索报告正文中的关键词，返回上下文片段。

**方案设计（建议）：**
- 在 `build_content.py` 构建时生成搜索索引（纯文本 + 位置映射）
- 客户端使用 Fuse.js 或 lunr.js 加载索引
- 搜索结果高亮匹配词、显示上下文

**修改文件：** `build_content.py`（生成索引）、`index.html`（搜索 UI + 加载索引逻辑）

**验证方法：**
1. 选择某篇报告正文中的一个特有词（不出现在标题中）
2. 在搜索框输入该词，确认能匹配到该报告
3. 确认结果中显示包含该词的上下文片段，且关键词高亮
4. 搜索一个不存在的词，确认显示"无结果"

---

#### 3.2.3 标签筛选（TODO）

**需求：** 为报告打标签（如 "Prefill"、"Decode"、"RL"），支持按标签过滤。

**方案设计：**
- `build_content.py` 从报告文件名或首行标题中提取关键词作为 tag
- 写入 manifest 的 reports 条目中
- 前端在卡片上渲染 tag 标签，点击即可按该 tag 过滤

**修改文件：** `build_content.py`（提取 tags）、`index.html`（tag 展示 + 过滤逻辑）

**验证方法：**
1. 运行 `python build_content.py`，检查 `content/index.json` 中报告条目是否包含 `tags` 字段
2. 打开 Category 视图，确认卡片上显示彩色 tag 标签
3. 点击某个 tag，确认列表过滤为只含该 tag 的报告
4. 清除 tag 过滤，确认恢复全部显示

---

### 3.3 构建部署模块

#### 3.3.1 内容预拉取 — `build_content.py`（已完成）

**需求：** 自动从 4 个 GitCode 仓库拉取所有 Markdown 报告及图片，生成可直接 serve 的静态 JSON。

**方案设计：**
```
build_content.py
├── discover_models() — 通过 GitCode tree API 递归发现模型目录
├── find_md_files_recursive() — 在模型目录下找到所有 .md 文件
├── fetch_file() — 拉取 Markdown 内容
├── fetch_binary_file_base64() — 拉取图片并编码为 base64
├── fetch_commit_date() — 获取文件最后提交日期
└── 输出 → content/index.json + content/reports/**/*.json
```

**设计约束：**
- 零 pip 依赖（只用 Python 标准库）
- 容错：单个文件拉取失败不影响整体构建
- 幂等：重复运行结果一致

---

#### 3.3.2 GitHub Pages 部署（已完成）

**需求：** Push 到 main 分支或每日定时自动部署最新内容。

**方案设计：**
- `.github/workflows/deploy.yml`
- 触发条件：push main / cron `17 2 * * *` / 手动 dispatch
- 流程：checkout → python build_content.py → upload artifact → deploy-pages
- 失败兜底：若 build_content.py 失败，使用仓库中已提交的 `content/` 作为 baseline

---

#### 3.3.3 GitCode Pages 部署（TODO）

**需求：** 支持部署到 GitCode Pages，作为 GitHub Pages 的替代或并行部署。

**方案设计：**
- 新增 `.gitlab-ci.yml`
- `pages` job 将产物输出到 `public/` 目录
- 定时任务通过 GitCode Web UI → CI/CD → Schedules 配置
- 详细操作指南见 `recipe_blog_skill.md` 的 "Deploying to GitCode Pages" 章节

**修改文件：** 新增 `.gitlab-ci.yml`、更新 README

**验证方法：**
1. 将代码推送到 GitCode 仓库 main 分支
2. 进入 CI/CD → Pipelines，确认 `build_content` 和 `pages` job 均绿色通过
3. 进入 Settings → Pages，获取部署 URL
4. 打开 URL，验证首页加载、侧边栏、报告渲染、搜索均正常
5. 在 Schedules 中创建定时任务，等待触发确认自动刷新生效

---

### 3.4 视觉设计模块

#### 3.4.1 配色方案（已完成）

**需求：** 统一的视觉风格，科技感但不冷硬，适合技术文档阅读。

**当前方案：**
- 主色：`#E77A1D`（活力橙）
- 背景：`#F9F8F6`（暖白米色）
- 文字：`#3E2723`（咖啡深棕）
- 效果：玻璃拟态（backdrop-filter blur + 半透明白色卡片）

---

#### 3.4.2 图标选型（已完成）

**需求：** 统一的图标体系，清晰表达分类和操作含义。

**当前方案：** Google Material Symbols Outlined（CDN 引入），每个分类有对应图标：
- Infer → `memory`（芯片）
- Train → `model_training`
- Spatial Intelligence → `view_in_ar`
- Embodied Intelligence → `smart_toy`

---

#### 3.4.3 暗色模式（TODO）

**需求：** 支持 Light/Dark 模式切换，适合夜间阅读。

**方案设计：**
- 默认跟随系统 `prefers-color-scheme`
- Header 添加切换按钮（太阳/月亮图标）
- 使用 CSS 变量定义颜色 token，dark 模式切换变量值
- 玻璃拟态调整：暗色背景 + 低透明度卡片
- highlight.js 代码块主题随模式切换（亮色用 GitHub Light，暗色保持 Atom One Dark）
- 用户选择持久化到 `localStorage`

**修改文件：** `index.html`（CSS 变量 + toggle 按钮 + 各组件 dark 样式）

**验证方法：**
1. 点击切换按钮，确认整体配色切换（背景、文字、卡片、侧边栏）
2. 检查代码块主题是否跟随切换
3. 刷新页面，确认选择被持久化（localStorage）
4. 修改系统暗色偏好，首次访问时确认自动跟随系统设置
5. 检查玻璃拟态效果在暗色下是否清晰可读

---

#### 3.4.4 移动端适配（TODO）

**需求：** 手机/平板上有良好的浏览体验。

**方案设计：**
- 断点：`@media (max-width: 768px)`
- 侧边栏改为 `position: fixed` 全屏覆盖层（slide-over），默认隐藏
- 卡片网格单列显示
- 触摸目标最小 44px × 44px
- 浮动按钮缩小并避免遮挡正文
- 搜索框自适应宽度

**修改文件：** `index.html`（CSS media queries + sidebar toggle 逻辑）

**验证方法：**
1. 使用 Chrome DevTools → Device Toolbar 模拟 375px (iPhone) 和 768px (iPad)
2. 确认侧边栏为全屏覆盖层，点击外部可关闭
3. 确认卡片网格变为单列
4. 确认所有按钮/链接可轻松点击（无需精确瞄准）
5. 确认浮动按钮不遮挡正文阅读

---

#### 3.4.5 打印友好（TODO）

**需求：** 用户可直接 Ctrl+P 打印报告，输出干净无干扰。

**方案设计：**
- `@media print` 隐藏：侧边栏、浮动按钮、搜索栏、header 操作区
- 保留：报告标题、面包屑、正文内容（代码块、表格、图片）
- 添加页眉：报告标题 + 来源 URL
- 代码块不截断，允许分页

**修改文件：** `index.html`（追加 print media 样式块）

**验证方法：**
1. 打开一篇报告，按 Ctrl+P 打开打印预览
2. 确认侧边栏、浮动按钮、搜索栏不出现在打印内容中
3. 确认代码块、表格、图片正常显示
4. 确认页眉有报告标题和来源 URL

---

<a id="discuss-cover-image"></a>

#### 3.4.6 技术文章封面图（TODO — 待讨论）

**需求：** 每篇报告卡片有一张有辨识度的封面图，提升浏览体验。

**方案设计（待选型）：**
- 方案 A：从报告 Markdown 中提取第一张图片作为封面
- 方案 B：按模型/分类生成风格统一的占位图（如带模型名的渐变色块）
- 方案 C：维护一组预设封面图素材，按分类轮换

**当前状态：** 使用固定的 placeholder 图片轮换（`thumbs` 数组），辨识度低。

**修改文件：** `build_content.py`（提取/生成封面）、`index.html`（卡片图片展示逻辑）

**验证方法：**
1. 运行 `python build_content.py`，检查 manifest 中报告是否有 `coverImage` 字段
2. 打开 Category 视图，确认卡片封面图不再千篇一律
3. 对比有/无真实图片的报告，确认 fallback 占位图风格一致
4. 检查不同分类的封面图是否有视觉区分度

---

### 3.5 国际化模块（TODO）

#### 3.5.1 中英文 UI 切换

**需求：** 界面文案支持中文/英文切换，方便国内外开发者使用。

**方案设计：**
- 定义 `i18n = { en: {...}, zh: {...} }` 翻译字典
- Header 区域添加语言切换按钮（CN / EN）
- 切换时批量替换 DOM 中所有 UI 文案（按钮、placeholder、标签、提示语）
- 报告正文内容不翻译（保持原文）
- 用户选择持久化到 `localStorage`

**修改文件：** `index.html`（新增 i18n 字典 + 切换按钮 + 替换逻辑）

**验证方法：**
1. 点击语言切换按钮 EN → CN，确认所有 UI 文案变为中文（按钮、搜索 placeholder、分类标签等）
2. 再次点击 CN → EN，确认全部恢复英文
3. 刷新页面，确认语言选择被持久化
4. 打开一篇报告，确认报告正文内容未被翻译（保持原文）
5. 检查切换后是否有文案遗漏（侧边栏、footer、浮动按钮提示）

---

### 3.6 订阅通知模块

<a id="discuss-subscribe"></a>

#### 3.6.1 邮件列表订阅（已完成 — 待讨论）

**需求：** 用户可订阅最新报告更新通知。

**当前方案：** Header 和首页底部的 "Subscribe" 按钮，跳转到 CANN 邮件列表（mailman3）。

---

#### 3.6.2 RSS 订阅源（TODO，优先级低）

**需求：** 提供 RSS feed，供习惯使用 RSS 阅读器的用户订阅。

**方案设计：**
- `build_content.py` 构建时生成 `feed.xml`（Atom 格式）
- 包含：标题、摘要（前 200 字）、commitDate、报告链接
- `index.html` 添加 `<link rel="alternate" type="application/atom+xml">`

**修改文件：** `build_content.py`（生成 feed.xml）、`index.html`（link 标签）

**验证方法：**
1. 运行 `python build_content.py`，确认根目录生成 `feed.xml`
2. 用浏览器直接打开 `feed.xml`，确认 XML 格式合法
3. 将 feed URL 添加到 RSS 阅读器（如 Feedly），确认能解析出文章列表
4. 检查每篇条目的标题、摘要、日期、链接是否正确

---

### 3.7 反馈互动模块（TODO）

#### 3.7.1 提交 Issue，反馈与建议

**需求：** 用户在阅读报告后可方便地提交反馈或建议。

**方案设计：**
- 在报告底部和页面 footer 添加"反馈建议"按钮
- 点击后跳转到对应 GitCode 仓库的 Issue 页面（按分类路由到对应仓库）
- Issue 模板预填报告标题，方便定位上下文

**路由逻辑：**
| 分类 | 跳转目标 |
|------|----------|
| Infer | `https://gitcode.com/cann/cann-recipes-infer/issues/new` |
| Train | `https://gitcode.com/cann/cann-recipes-train/issues/new` |
| Spatial Intelligence | `https://gitcode.com/cann/cann-recipes-spatial-intelligence/issues/new` |
| Embodied Intelligence | `https://gitcode.com/cann/cann-recipes-embodied-intelligence/issues/new` |

**修改文件：** `index.html`（`showReport()` 末尾添加反馈按钮 + 跳转逻辑）

**验证方法：**
1. 打开 Infer 分类的某篇报告，确认底部出现"反馈建议"按钮
2. 点击按钮，确认跳转到 `gitcode.com/cann/cann-recipes-infer/issues/new`
3. 确认 Issue 标题中预填了当前报告名
4. 分别测试 4 个分类的报告，确认跳转到各自对应的仓库

---

<a id="discuss-routing"></a>

### 3.8 路由与子页面模块（TODO — 待讨论）

#### 3.8.1 子页面路径支持

**需求：** 支持类似 `/cann-recipes-blogs/infer/`、`/cann-recipes-blogs/infer/deepseek-r1` 的可分享直链，用户刷新或直接访问子路径不会 404。

**候选方案：**

| 方案 | 思路 | 优点 | 缺点 |
|------|------|------|------|
| **A. SPA 路由 + 404.html** | 保持单文件 `index.html`；新增 `404.html`（内容同 index.html），利用 GitHub/GitCode Pages 的 404 fallback 机制，JS 解析 URL path 路由到对应视图 | 零文件膨胀；URL 可读可分享；架构改动最小 | 依赖平台 404 行为；SEO 不友好（搜索引擎看到 404 状态码） |
| **B. 物理子目录** | `build_content.py` 构建时为每个分类/模型生成独立的 `infer/index.html`、`train/index.html` 等静态页面 | 真正的 200 状态码；SEO 友好；每个子页面可独立定制 | 构建复杂度增加；多文件维护；需模板引擎或字符串拼接生成 HTML |
| **C. Hash 路由** | URL 改为 `/#/infer/deepseek-r1` 形式，JS 监听 `hashchange` 事件 | 最简单实现；无需 404.html；所有平台兼容 | URL 不够美观；hash 部分不发送到服务端；SEO 不可用 |

**当前倾向：** 方案 A（SPA + 404.html）改动最小且效果好。但需确认：
- GitCode Pages 是否支持自定义 404.html fallback（GitLab Pages 默认支持）
- 是否有 SEO 需求（技术报告是否需要被搜索引擎收录）

**待讨论事项：**
1. 是否需要 SEO（决定方案 A vs B）
2. URL 风格偏好：`/infer/deepseek-r1` vs `/#/infer/deepseek-r1`
3. 子路径粒度：到分类级（`/infer/`）还是到报告级（`/infer/deepseek-r1/report`）

**修改文件（方案 A 为例）：**
- 新增 `404.html`（内容与 index.html 相同或重定向脚本）
- `index.html`（新增 URL path 解析逻辑，页面加载时根据路径调用对应 show 函数）
- `build_content.py`（若方案 B，需生成子目录 HTML）

---

### 3.9 内容质量模块（TODO）


#### 3.9.1 技术文章润色与查虫（Agent 任务）

**需求：** 对已有技术报告进行质量审查，修正错别字、语法错误、格式问题，提升可读性。

**方案设计：**
- 由 Agent 逐篇扫描 GitCode 仓库中的 Markdown 报告
- 检查项：
  - 错别字和语法错误（中英文混排场景）
  - 代码块语言标注是否正确
  - 图片引用是否有效（路径存在）
  - 标题层级是否合理（不跳级）
  - 链接是否可达
- 生成修改建议，提交 PR 到对应仓库

**执行方式：** Agent 自动化任务，批量处理，人工 review PR。

**验证方法：**
1. Agent 输出每篇报告的问题清单（文件名 + 行号 + 问题描述）
2. 修复后的报告通过 Markdown lint 检查（无 warning）
3. 修复不改变技术含义，仅修正表述和格式

---

#### 3.9.2 文章规范制定

**需求：** 制定统一的技术报告撰写规范，供后续新增报告参照，保证质量一致性。

**规范内容（建议）：**
- 文件命名：`<model>_<scenario>_optimization.md`（小写、下划线分隔）
- 标题结构：一级标题为报告名，二级为章节（背景、方案、性能数据、总结）
- 图片放置：统一放在同级 `figures/` 目录下
- 代码块：必须标注语言（```python / ```bash 等）
- 性能数据：使用表格呈现，注明硬件环境和测试条件
- 链接：关联的可执行代码必须提供 README 链接（见 3.8.3）

**输出物：** `docs/writing_guide.md`（撰写规范文档），放在 recipe 仓库中

**验证方法：**
1. 新增一篇报告按规范撰写，确认无需额外调整即可在 Blog 上正确渲染
2. 现有报告逐步按规范整改（配合 3.8.1 润色任务）

---

#### 3.9.3 报告关联仓库可执行 README 链接

**需求：** 每篇技术报告中必须包含指向 GitCode 仓库中对应可执行代码 README 的链接，方便读者从"读文档"直接跳转到"跑代码"。

**方案设计：**
- 在报告 Markdown 头部或末尾固定位置添加"快速开始"链接区：
  ```markdown
  ## 快速开始
  
  > 可执行代码及环境配置详见：[README](<gitcode仓库对应目录>/README.md)
  ```
- `build_content.py` 构建时检测每篇报告是否包含指向仓库 README 的链接
- 对于缺失链接的报告，输出警告清单，Agent 负责补充

**检测逻辑（build_content.py 中添加）：**
```python
# 检查报告中是否包含 README 链接
has_readme_link = bool(re.search(r'\[.*README.*\]\(.*\)', markdown_content, re.IGNORECASE))
if not has_readme_link:
    warnings.append(f"WARN: {report_path} 缺少 README 链接")
```

**修改文件：** 
- `build_content.py`（添加链接检测 + 警告输出）
- 各 GitCode 仓库中缺失链接的报告（由 Agent 提交 PR 补充）

**验证方法：**
1. 运行 `python build_content.py`，确认输出中无 "缺少 README 链接" 警告
2. 在网站上打开报告，确认"快速开始"区域有可点击的 README 链接
3. 点击链接，确认跳转到 GitCode 仓库对应目录且 README 存在
4. 对于新增报告，若未包含链接，构建时能输出明确提示

---

### 3.10 数据驱动模块（TODO）

#### 3.10.1 访问统计

**需求：** 统计各报告访问量，用真实数据驱动首页"热门报告"排序。

**方案设计：**
- 接入轻量级、隐私友好的统计服务（无 cookie）
- 候选方案：Umami（自托管）/ Plausible / Cloudflare Web Analytics（免费）
- 统计数据通过 API 拉取，写入 manifest 或单独 JSON，前端读取排序
- 首页 "Popular Reports" 改为按真实 PV 排序（当前为手动配置）

**约束：** 静态站无后端，统计服务必须是外部托管或 CDN 级别的分析。

**修改文件：** `index.html`（嵌入统计脚本 + Popular 排序逻辑）

**验证方法：**
1. 部署后打开网站，在统计服务后台确认有访问数据上报
2. 访问不同报告若干次，确认后台按报告粒度记录 PV
3. 确认首页 "Popular Reports" 排序与真实 PV 数据一致
4. 打开浏览器 DevTools → Application → Cookies，确认无 cookie 写入

---

### 3.11 开发者体验模块

#### 3.11.1 本地开发（已完成）

**需求：** 网站维护者可在本地快速启动网站，修改后立即预览。

**方案设计：**
- 方式 1（推荐）：`python -m http.server 8080`，使用已提交的 `content/` 静态文件
- 方式 2：启动 `proxy.py`（localhost:8081），实时从 GitCode API 拉取内容
- 4 级 fallback 保证在各种环境下都能加载内容

---

#### 3.11.2 零构建工具（已完成）

**需求：** 前端不使用 webpack/vite/npm，保持零构建、单文件部署的简洁性。

**设计决策：**
- 所有前端代码在 `index.html` 一个文件中
- 外部库通过 CDN 引入（Tailwind、marked.js、highlight.js）
- 好处：部署简单、无 node_modules、任何 HTTP server 都能 serve
- 代价：单文件体量较大（~1600 行），编辑需要按功能块定位

---

<a id="discuss-docs-organize"></a>

#### 3.11.3 技术文档分类及整理（TODO — 待讨论）

**需求：** 项目配套文档结构清晰，方便新维护者快速上手。

**方案设计：**
- 整理 `docs/` 目录下的文档职责划分：
  - `recipe_blog_requirements.md` — 需求分析（本文档，面向决策者和开发者）
  - `recipe_blog_skill.md` — 技术实现细节（面向维护者）
  - `recipe_blog_design.md` — 功能清单速查（面向 agent）
- 确保三份文档无重复、互相引用而非复制
- README.md 作为入口，指引到各文档

**修改文件：** `docs/` 下各文档、`README.md`

**验证方法：**
1. 新人视角：仅通过 README → docs/ 的引导，能否在 5 分钟内理解项目结构和如何本地运行
2. 检查三份文档无重复段落（搜索相同句子）
3. 文档间的交叉引用链接均可正确跳转
4. 每份文档有明确的目标读者声明

---

## 4. 已完成功能清单

以下是当前 v1 版本已上线且稳定运行的全部功能：

### 4.1 内容展示

| # | 功能 | 说明 |
|---|------|------|
| 1 | 四分类浏览 | Infer / Train / Spatial Intelligence / Embodied Intelligence |
| 2 | 层级侧边栏 | 可折叠，分类 → 模型 → 报告三级展开 |
| 3 | 动态模型发现 | build_content.py 通过 tree API 自动发现新模型，无需手动维护列表 |
| 4 | 三视图切换 | Home（首页推荐）、Category（分类网格）、Report（文章详情） |
| 5 | Markdown 渲染 | 标题、表格、列表、引用块、链接完整支持 |
| 6 | 代码高亮 + 复制 | highlight.js 语法着色，每个代码块带 Copy 按钮 |
| 7 | 图片 Base64 嵌入 | 构建时编码，运行时零外部请求，图片永不失效 |
| 8 | Heading Anchor | slugify() 支持中英文，为 TOC/深链接预留 |
| 9 | 面包屑导航 | Category → Model → Report 路径可点击 |
| 10 | 报告提交日期 | 显示每篇报告在 GitCode 的最后 commit 时间 |

### 4.2 搜索与发现

| # | 功能 | 说明 |
|---|------|------|
| 11 | 关键词搜索 | 按模型名、标题、分类名过滤 |
| 12 | 搜索结果网格 | 卡片展示，带匹配数量提示 |
| 13 | 首页最新报告 | 按 commitDate 排序的卡片 |
| 14 | 首页热门报告 | 推荐位展示 |

### 4.3 UI/UX

| # | 功能 | 说明 |
|---|------|------|
| 15 | 玻璃拟态设计 | backdrop-filter blur + 半透明背景 |
| 16 | 响应式卡片网格 | 2-3 列自适应 |
| 17 | 侧边栏动画 | 宽度渐变 + 透明度过渡 |
| 18 | 浮动导航按钮 | 回到顶部 / 跳到底部 |
| 19 | 自定义滚动条 | 橙色细滚动条（WebKit） |
| 20 | Hover 动效 | 卡片阴影放大、颜色渐变 |
| 21 | Fade-in 过渡 | 视图切换淡入动画 |

### 4.4 部署与运维

| # | 功能 | 说明 |
|---|------|------|
| 22 | GitHub Pages 部署 | Actions 自动化 |
| 23 | 每日定时刷新 | Cron 2:17 AM UTC |
| 24 | 构建失败兜底 | 使用已提交的 content/ 作为 baseline |
| 25 | 手动触发构建 | workflow_dispatch |
| 26 | 4 级内容加载 | 静态 JSON → 本地代理 → CORS 代理 → Raw URL |

### 4.5 其他

| # | 功能 | 说明 |
|---|------|------|
| 27 | 订阅按钮 | 跳转 CANN 邮件列表 |
| 28 | Browse Repo 链接 | 无独立报告的模型直接链到 GitCode 仓库 |
| 29 | 外部链接安全 | target="_blank" + rel="noopener" |
| 30 | 本地开发代理 | proxy.py 零依赖 Python 代理 |

---

## 5. 未来 TODO

### 优先级说明

| 级别 | 含义 |
|------|------|
| **P0** | 影响核心体验，建议近期完成 |
| **P1** | 体验提升，中期迭代 |
| **P2** | 锦上添花，有余力时完成 |

---

### P0 — 高优先级

#### TODO-01: 报告目录导航 (TOC)

| 项目 | 内容 |
|------|------|
| **目标** | 在报告详情页展示文章目录，支持点击跳转和滚动高亮 |
| **验收标准** | ① 自动从 h2/h3 生成目录 ② 点击条目平滑滚动到对应章节 ③ 滚动时高亮当前章节 ④ 移动端可收起 |
| **实现要点** | heading anchor 已实现（`slugify()`）；需新增右侧 TOC 面板 + scroll-spy 逻辑 |
| **修改文件** | `index.html`（新增 TOC DOM + CSS + JS） |

---

#### TODO-02: 全文搜索

| 项目 | 内容 |
|------|------|
| **目标** | 支持搜索报告正文内容，返回匹配片段 |
| **验收标准** | ① 输入关键词可搜到正文中包含该词的报告 ② 结果显示匹配上下文（前后 50 字） ③ 关键词高亮 |
| **实现要点** | 方案 A：构建时在 `build_content.py` 生成轻量索引 JSON；方案 B：客户端加载所有报告文本用 Fuse.js 搜索 |
| **修改文件** | `build_content.py`（生成索引）、`index.html`（搜索 UI + 逻辑） |

---

#### TODO-03: 暗色模式

| 项目 | 内容 |
|------|------|
| **目标** | 添加 Light/Dark 模式切换 |
| **验收标准** | ① 默认跟随系统 `prefers-color-scheme` ② 手动切换按钮在 header ③ 选择持久化到 localStorage ④ 代码块主题随之切换 |
| **实现要点** | Tailwind `dark:` 变体；玻璃拟态背景色需调整；highlight.js 提供多套主题 |
| **修改文件** | `index.html`（CSS 变量 + toggle JS + 各组件 dark 样式） |

---

#### TODO-04: GitCode Pages 部署

| 项目 | 内容 |
|------|------|
| **目标** | 支持一键部署到 GitCode Pages |
| **验收标准** | ① `.gitlab-ci.yml` 可直接在 GitCode 上跑通 ② Pages URL 可正常访问所有功能 ③ 定时刷新正常工作 |
| **实现要点** | 详见 `recipe_blog_skill.md` "Deploying to GitCode Pages" 章节 |
| **修改文件** | 新增 `.gitlab-ci.yml`、更新 README |

---

### P1 — 中优先级

#### TODO-05: 移动端适配

| 项目 | 内容 |
|------|------|
| **目标** | 优化手机/平板浏览体验 |
| **验收标准** | ① 侧边栏变为 slide-over 覆盖层 ② 卡片网格单列显示 ③ 触摸目标 ≥ 44px ④ 浮动按钮不遮挡内容 |
| **实现要点** | 增加 `@media (max-width: 768px)` 断点样式；侧边栏改为 `position: fixed` overlay |
| **修改文件** | `index.html`（CSS media queries + sidebar toggle 逻辑调整） |

---

#### TODO-06: 上一篇 / 下一篇导航

| 项目 | 内容 |
|------|------|
| **目标** | 报告底部显示同分类内的前后报告链接 |
| **验收标准** | ① 显示 "← 上一篇" / "下一篇 →" ② 按分类内模型字母序排列 ③ 到达首/尾篇时隐藏对应按钮 |
| **实现要点** | 从 `repoModels` 中计算当前报告的前后位置 |
| **修改文件** | `index.html`（`showReport()` 函数末尾追加导航 DOM） |

---

#### TODO-07: 阅读进度条

| 项目 | 内容 |
|------|------|
| **目标** | 页面顶部显示当前报告的阅读进度 |
| **验收标准** | ① 仅在 report 视图可见 ② 随滚动实时更新 ③ 使用主题橙色 |
| **实现要点** | 监听 `scroll` 事件，计算 `scrollTop / (scrollHeight - clientHeight)` |
| **修改文件** | `index.html`（固定定位的 `<div>` + scroll listener） |

---

#### TODO-08: 报告标签 / Tags

| 项目 | 内容 |
|------|------|
| **目标** | 为报告卡片添加分类标签（如 "Prefill", "Decode", "RL"） |
| **验收标准** | ① 标签显示在卡片上方 ② 点击标签可按该标签过滤 ③ 标签来源：从报告文件名或首行标题提取 |
| **实现要点** | `build_content.py` 提取关键词 → 写入 manifest → 前端读取渲染 |
| **修改文件** | `build_content.py`（提取 tags）、`index.html`（tag 展示 + 过滤逻辑） |

---

### P2 — 低优先级

#### TODO-09: 打印友好

| 项目 | 内容 |
|------|------|
| **目标** | 支持干净的报告打印输出 |
| **验收标准** | ① `@media print` 隐藏侧边栏、浮动按钮 ② 保留代码块、表格、图片 ③ 添加标题和 URL 页眉 |
| **修改文件** | `index.html`（追加 print media 样式） |

---

#### TODO-10: 中英文 UI 切换

| 项目 | 内容 |
|------|------|
| **目标** | 界面文案支持中/英文切换 |
| **验收标准** | ① 语言按钮在 header ② 切换后所有 UI 文案（按钮、placeholder、标签）变更 ③ 报告正文不翻译 ④ 持久化到 localStorage |
| **实现要点** | 定义 `i18n = { en: {...}, zh: {...} }` 对象，切换时 DOM 批量替换 |
| **修改文件** | `index.html` |

---

#### TODO-11: RSS 订阅源

| 项目 | 内容 |
|------|------|
| **目标** | 生成 RSS/Atom feed 供用户在阅读器中订阅 |
| **验收标准** | ① 构建时生成 `feed.xml` ② 包含标题、摘要（前 200 字）、日期、链接 ③ `index.html` 添加 `<link rel="alternate">` |
| **修改文件** | `build_content.py`（生成 feed.xml）、`index.html`（link 标签） |

---

#### TODO-12: 访问统计

| 项目 | 内容 |
|------|------|
| **目标** | 统计报告访问量，驱动"热门报告"排序 |
| **验收标准** | ① 接入轻量统计（Umami / Plausible / 自建） ② 无 cookie ③ 首页"Popular"基于真实数据排序 |
| **实现要点** | 静态站限制下需第三方统计服务或 Cloudflare Analytics |
| **修改文件** | `index.html`（嵌入统计脚本）、首页 Popular 逻辑 |

---

## 附录

### A. 技术架构总览

```
┌────────────────────────────────────────────────────────────────────┐
│                      CI/CD (GitHub Actions / GitLab CI)             │
│                                                                    │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐  │
│  │  build_content.py │───▶│  content/index.json                  │  │
│  │  (Python 3.11)    │    │  content/reports/**/*.json            │  │
│  └──────────────────┘    └──────────────────────────────────────┘  │
│          │                              │                          │
│          │ GitCode tree API             │ Static files             │
│          ▼                              ▼                          │
│  ┌──────────────────┐    ┌──────────────────────────────────────┐  │
│  │  GitCode Repos    │    │  GitHub/GitCode Pages (CDN)           │  │
│  │  (4 repositories) │    │  └── index.html (SPA)                │  │
│  └──────────────────┘    └──────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                                        │
                                        │ HTTPS
                                        ▼
                               ┌──────────────────┐
                               │    Browser        │
                               │  (零后端依赖)     │
                               └──────────────────┘
```

### B. 文件清单

| 文件 | 用途 |
|------|------|
| `index.html` | 前端单页应用（HTML + CSS + JS） |
| `build_content.py` | 构建脚本，拉取内容生成静态 JSON |
| `content/index.json` | Manifest（模型列表 + 报告元数据） |
| `content/reports/**/*.json` | 预拉取的报告内容（markdown + images + commitDate） |
| `.github/workflows/deploy.yml` | GitHub Pages 部署流水线 |
| `.gitlab-ci.yml` | GitCode Pages 部署流水线（TODO） |
| `proxy.py` | 本地开发用 CORS 代理 |
| `docs/recipe_blog_skill.md` | 技术文档（架构、API、部署指南） |
| `docs/recipe_blog_design.md` | 设计文档（已完成/TODO 快速索引） |
| `docs/recipe_blog_requirements.md` | 本文档（需求分析与方案设计） |

### C. 给其他 Agent 的开发指引

#### 文档体系与协作流程

本项目有三份核心文档，各司其职：

| 文档 | 角色 | 什么时候读 |
|------|------|-----------|
| **`recipe_blog_requirements.md`**（本文档） | 需求源 — "做什么"和"为什么" | 接到任务时第一份读：了解需求背景、方案设计、验收标准、验证方法 |
| **`recipe_blog_skill.md`** | 技术规范 — "怎么做"和"不能做什么" | 动手写代码前必读：了解架构、API 调用链、开发约束、测试规范 |
| **`recipe_blog_design.md`** | 速查索引 — "做了哪些/还差哪些" | 快速定位状态，不做深入阅读 |

**协作流程：**
```
1. 接到任务（如 "实现 TOC"）
2. 在 requirements.md 中找到对应章节（3.1.4），阅读：
   - 需求描述 → 理解目标
   - 方案设计 → 理解技术方向
   - 验证方法 → 理解完成标准
3. 在 skill.md 中阅读：
   - 开发约束 → 知道什么不能做
   - 测试规范 → 知道怎么验证
   - 相关技术细节（如渲染流水线、API 格式）
4. 实现 → 按 skill.md 的测试规范自测 → 按 requirements.md 的验证方法逐条确认
```

#### 开发红线（DO NOT）

以下是硬性约束，违反将导致 PR 被拒：

| 禁止事项 | 原因 |
|----------|------|
| 引入 npm/node/webpack/vite 构建工具 | 项目定位为零构建静态站，所有环境只需 `python -m http.server` |
| 拆分 `index.html` 为多个文件 | 单文件 SPA 是设计决策，简化部署和维护 |
| 给 `build_content.py` 添加 pip 依赖 | CI 环境无 pip install 步骤，必须纯标准库 |
| 引入需要后端的功能（数据库、服务端渲染） | 纯静态站，GitHub/GitCode Pages 无服务端 |
| 修改已有功能的行为但不验证回归 | 必须确认修改不破坏现有功能（见测试规范） |
| 硬编码模型列表（绕过 manifest） | 动态发现是核心设计，不退化为手动维护 |
| 删除 4 级 fallback 中的任何一级 | 保证各种环境下内容可加载 |

#### 测试规范（每次提交前必须通过）

**基础验证（所有改动）：**
1. `python build_content.py` 无报错退出
2. `python -m http.server 8080` 启动后，浏览器打开 `http://localhost:8080`
3. 首页加载正常：sidebar 展示、卡片渲染、无 console error
4. 至少打开 1 篇报告确认 Markdown 渲染正常（标题、代码块、图片）
5. 搜索功能输入关键词有结果返回

**回归验证（修改已有功能时额外执行）：**
6. 侧边栏折叠/展开动画流畅
7. 分类视图切换正常（Home → Category → Report → Home）
8. 面包屑导航每级可点击跳转
9. 代码块 "Copy" 按钮可用
10. 浮动按钮（回到顶部/底部）正常工作

**功能专项验证（新功能）：**
- 执行该功能在 `requirements.md` 中对应的"验证方法"章节，逐条通过

#### 修改范围速查

| 改动类型 | 涉及文件 |
|----------|----------|
| 前端 UI / 交互 / 样式 | `index.html` |
| 内容构建 / 数据处理 | `build_content.py` |
| GitHub 部署 | `.github/workflows/deploy.yml` |
| GitCode 部署 | `.gitlab-ci.yml` |
| 文档 | `docs/` 下对应文件 |

#### 任务分配

第 5 章的每个 TODO 均已标注"修改文件"，可直接作为独立任务卡分配。接到任务后按上述协作流程执行即可。
