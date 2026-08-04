# CANN Recipes 文档静态元数据规范

更新时间：2026-07-31

## 1. 目标

每篇技术文档通过少量、稳定、可校验的静态元数据描述其核心技术属性。元数据用于 Blog 的侧栏标题、分组筛选和封面；不在文档正文中重复展示。

本规范将静态元数据分为两类：公共字段和场景小类扩展字段。

公共字段适用于所有技术文档，目前仅允许维护以下 8 个字段：

- `sidebarTitle`
- `quantization`
- `parallelism`
- `operator`
- `cannFeatures`
- `hardware`
- `frameworks`
- `cover`

场景小类扩展字段只允许在指定目录下使用，其他目录不得填写：

- `llmSpeculativeInference`：仅限 `infer/llm/**`
- `multimodalDitCache`：仅限 `infer/multimodal/**`

文档 H1、目录层级、文件名、来源仓库和全文搜索内容均由构建过程派生，禁止重复写入元数据。

## 2. 通用规则

- 元数据放在 Markdown 文档末尾，使用 HTML 注释包裹 JSON，方便 agent 从尾部扫描和校验。
- 除 `sidebarTitle` 外，所有机器可读值均使用小写 ASCII `kebab-case`；数值精度可使用 `int8`、`fp8` 等行业通用写法。
- 数组字段使用受控枚举；数组中不得重复，空数组应直接省略。
- 对 `quantization`、`parallelism`、`operator`、`cannFeatures`、`hardware` 和 `frameworks`，没有任何适用枚举值时必须填写 `["none"]`；`none` 只能单独出现，不能与其他值并列。
- 不允许 `null`、空字符串、未知顶层字段或不在枚举中的值。
- 场景小类扩展字段只在对应目录下填写；不属于该目录的文档必须省略该字段，不填写 `["none"]`。
- 属于对应目录但未涉及该能力的文档，扩展字段填写 `["none"]`，便于前端在该小类内形成完整筛选项。
- 每篇文档最多有一个 `cann-meta` 块。字段校验失败时，CI 必须停止发布。

```markdown
# DeepSeek-R1 Decode 阶段推理优化

正文内容……

<!-- cann-meta
{
  "sidebarTitle": "Decode 阶段推理优化",
  "quantization": ["int8"],
  "parallelism": ["tensor-parallel", "context-parallel"],
  "operator": ["ascendc", "tilelang"],
  "cannFeatures": ["multi-stream", "prefetch"],
  "hardware": ["atlas-a3"],
  "frameworks": ["cann-recipes"],
  "cover": {"type": "auto"}
}
-->
```

## 3. 字段总览

### 3.1 公共字段

| 字段 | 类型 | 必填 | 数量限制 | 用途 |
|---|---|---:|---:|---|
| `sidebarTitle` | string | 是 | 1 | 侧边栏和紧凑导航标题 |
| `quantization` | string[] | 否 | 0～6 | 按量化数据类型筛选 |
| `parallelism` | string[] | 否 | 0～6 | 按并行切分类型筛选 |
| `operator` | string[] | 否 | 0～4 | 按算子开发/优化方式筛选 |
| `cannFeatures` | string[] | 否 | 0～4 | 按固定 CANN 原子特性筛选 |
| `hardware` | string[] | 否 | 0～4 | 已验证或明确适配的硬件 |
| `frameworks` | string[] | 否 | 0～5 | 直接相关的软件框架 |
| `cover` | object | 否 | 1 | 控制封面来源；缺省等价于 `auto` |

### 3.2 场景小类扩展字段

| 字段 | 适用目录 | 类型 | 必填规则 | 数量限制 | 用途 |
|---|---|---|---|---:|---|
| `llmSpeculativeInference` | `infer/llm/**` | string[] | 目录内填写；目录外禁止 | 1～3 | 按 LLM 投机推理方案筛选 |
| `multimodalDitCache` | `infer/multimodal/**` | string[] | 目录内填写；目录外禁止 | 1～5 | 按多模态 DiT Cache 方案筛选 |

新增场景字段规则：

- 字段名使用 `<小类><技术主题>` 的 camelCase，例如 `llmSpeculativeInference`。
- 字段必须服务于该小类下可复用的筛选能力，不为单篇文章新增字段。
- 字段值必须集中放入 `metadata_enums.py`，展示标签集中放入 `metadata_labels.py`，不得在文档中临时扩展。
- 前端只在用户进入或筛选到对应小类后展示该字段，避免其他场景出现无意义筛选项。

### 3.3 中文标签规范

前端中文页面不得直接展示机器字段名或枚举 ID，应使用本节维护的中文标签。专有英文名词、技术缩写、框架名、硬件名保持英文不变，例如 `superkernel`、MTP、AscendC、NPUGraph、Atlas A3。

字段中文标签如下：

| 字段 | 中文标签 | 说明 |
|---|---|---|
| `sidebarTitle` | 侧栏标题 | 仅作为文档侧栏短标题，不作为筛选项 |
| `quantization` | 量化 | 按权重数据类型筛选 |
| `parallelism` | 并行切分 | 按模型、序列或数据切分方式筛选 |
| `operator` | 算子种类 | 按算子开发或优化方式筛选 |
| `cannFeatures` | CANN 特性 | 按固定 CANN 原子特性筛选 |
| `hardware` | 硬件 | 按已验证或明确适配硬件筛选 |
| `frameworks` | 框架 | 按直接相关框架或工具链筛选 |
| `cover` | 封面 | 控制技术文章封面来源 |
| `llmSpeculativeInference` | 投机推理 | 仅用于 `infer/llm/**` |
| `multimodalDitCache` | DiT Cache | 仅用于 `infer/multimodal/**` |

公共枚举值中文标签如下：

| 字段 | ID | 中文标签 |
|---|---|---|
| `quantization` | `bf16` | BF16 |
| `quantization` | `int8` | INT8 |
| `quantization` | `int4` | INT4 |
| `quantization` | `float8` | Float8 |
| `quantization` | `fp8` | FP8 |
| `quantization` | `mxfp8` | MXFP8 |
| `quantization` | `hif8` | HiF8 |
| `quantization` | `mxfp4` | MXFP4 |
| `quantization` | `none` | 未涉及量化 |
| `parallelism` | `data-parallel` | 数据并行 |
| `parallelism` | `tensor-parallel` | 张量并行 |
| `parallelism` | `pipeline-parallel` | 流水并行 |
| `parallelism` | `context-parallel` | 上下文并行 |
| `parallelism` | `sequence-parallel` | 序列并行 |
| `parallelism` | `expert-parallel` | 专家并行 |
| `parallelism` | `zero` | ZeRO |
| `parallelism` | `none` | 不涉及并行切分 |
| `operator` | `ascendc` | AscendC |
| `operator` | `tilelang` | TileLang |
| `operator` | `pypto` | PyPTO |
| `operator` | `autofuse` | AutoFuse |
| `operator` | `none` | 不涉及算子方式 |
| `cannFeatures` | `multi-stream` | 多流 |
| `cannFeatures` | `superkernel` | superKernel |
| `cannFeatures` | `prefetch` | 预取 |
| `cannFeatures` | `npugraph` | NPUGraph |
| `cannFeatures` | `none` | 无适用 CANN 特性 |
| `hardware` | `atlas-a2` | Atlas A2 / Ascend 910B |
| `hardware` | `atlas-a3` | Atlas A3 |
| `hardware` | `ascend-950` | Ascend 950 |
| `hardware` | `none` | 未指定硬件 |
| `frameworks` | `cann-recipes` | CANN Recipes |
| `frameworks` | `mindspore` | MindSpore |
| `frameworks` | `torchtitan` | TorchTitan |
| `frameworks` | `megatron` | Megatron |
| `frameworks` | `onnx` | ONNX |
| `frameworks` | `atb` | ATB |
| `frameworks` | `none` | 未指定框架 |
| `cover.type` | `auto` | 自动封面 |
| `cover.type` | `image` | 图片封面 |
| `cover.type` | `mermaid` | Mermaid 封面 |
| `cover.type` | `placeholder` | 占位封面 |

场景小类扩展枚举值中文标签如下：

| 字段 | ID | 中文标签 |
|---|---|---|
| `llmSpeculativeInference` | `mtp` | MTP |
| `llmSpeculativeInference` | `dspark` | DSpark |
| `llmSpeculativeInference` | `dflash` | DFlash |
| `llmSpeculativeInference` | `none` | 未涉及投机推理 |
| `multimodalDitCache` | `dit-block-cache` | DiT Block Cache |
| `multimodalDitCache` | `attention-cache` | Attention Cache |
| `multimodalDitCache` | `feature-cache` | Feature Cache |
| `multimodalDitCache` | `teacache` | TeaCache |
| `multimodalDitCache` | `magcache` | MagCache |
| `multimodalDitCache` | `none` | 未涉及 DiT Cache |

维护规则：

- 中文标签只用于前端展示、筛选面板和属性卡片，不写入每篇文档的 `cann-meta`。
- 新增或修改枚举值时，必须同步更新本节中文标签、`metadata_enums.py` 和 `metadata_labels.py`。
- 如果枚举值本身是专有英文名词或行业通用缩写，中文标签保持英文；如果枚举值是通用概念，中文标签使用简洁中文。

## 4. `sidebarTitle`

侧边栏和紧凑导航使用的中文短标题，不使用枚举。

- 必填，建议 4～16 个汉字或等效长度，最长不超过 24 个字符。
- 描述文章的核心技术点或优化目标，避免重复完整 H1。
- 原则上省略模型名、NPU、CANN、昇腾和硬件型号；无法区分时可保留必要术语。
- 避免“实践”“说明”“指南”“文档”等低信息量后缀。
- 同一目录下不得重复。

## 5. `quantization`

`quantization` 按文档实际使用、转换或优化的**权重数据类型**分类，不描述激活数据类型、缓存数据类型、校准算法或单独的中间计算精度。

| ID | 展示名称 |
|---|---|
| `bf16` | BF16 |
| `int8` | INT8 |
| `int4` | INT4 |
| `float8` | Float8 |
| `fp8` | FP8 |
| `mxfp8` | MXFP8 |
| `hif8` | HiF8 |
| `mxfp4` | MXFP4 |
| `none` | 未提供清晰的说明 |

- 仅在正文明确说明该类型用于模型权重、权重量化或权重检查点时填写。
- `float8` 仅表示正文中明确写出的泛化 Float8 表述；若正文已明确写出 FP8、MXFP8 或 HiF8，应分别标注对应枚举值。
- `mxfp4` 单独表示 MXFP4 权重格式。
- 仅出现在激活、KV Cache、中间张量或示例代码中的精度不作为本字段取值。
- 文档不涉及上述权重类型时填写 `["none"]`。

## 6. `parallelism`

`parallelism` 按模型、序列或数据的**切分类型**分类，不描述并行度数值、Rank 数或集群规模。

| ID | 展示名称 |
|---|---|
| `data-parallel` | 数据并行 |
| `tensor-parallel` | 张量并行 |
| `pipeline-parallel` | 流水并行 |
| `context-parallel` | 上下文并行 |
| `sequence-parallel` | 序列并行 |
| `expert-parallel` | 专家并行 |
| `zero` | ZeRO |
| `none` | 不涉及并行切分 |

- 只填写正文中有明确实现、调优或性能分析的切分类型。

## 7. `operator`

`operator` 按文档使用的**算子开发或优化方式**分类，例如 AscendC、TileLang、PyPTO 和 AutoFuse；不按 Attention、MatMul 等计算算子名称分类。

| ID | 展示名称 |
|---|---|
| `ascendc` | AscendC |
| `tilelang` | TileLang |
| `pypto` | PyPTO |
| `autofuse` | AutoFuse |
| `none` | 不涉及上述算子开发方式 |

- 仅在正文包含对应方式的独立实现、性能分析或优化方案时填写。
- Attention、MatMul 等计算算子名称不作为 `operator` 枚举值；如后续确有筛选需求，应新增独立字段，不与本字段混用。
- CANN 原子特性仍填写到 `cannFeatures`；例如算子融合不作为 `operator` 值。

## 8. `cannFeatures`

`cannFeatures` 仅使用以下固定原子特性总类别。新增或改名必须先修改本规范和 `metadata_enums.py`，不得在文档中自行扩展。

| ID | 展示名称 | 含义 |
|---|---|---|
| `multi-stream` | MultiStream | 多流并行与通信计算重叠 |
| `superkernel` | superkernel | superkernel 融合与执行优化 |
| `prefetch` | Prefetch | 数据预取能力 |
| `npugraph` | NPUGraph | NPU 图模式与图优化能力 |
| `none` | 无适用 CANN 原子特性 | 不涉及上述固定特性 |

- `multi-stream` 是 MultiStream 的规范 ID；不使用 `multistram`、`multi_stream` 等拼写变体。
- 每篇文档只填写实际作为核心方案或优化点的特性；仅出现名词不应添加。
- 切分与量化不再作为 `cannFeatures` 取值；具体切分方式填写在 `parallelism` 字段，权重数据类型填写在 `quantization` 字段。

## 9. `hardware` 与 `frameworks`

### 9.1 Hardware

`hardware` 表示报告已验证或明确适配的硬件，而非理论支持范围。

| ID | 展示名称 |
|---|---|
| `atlas-a2` | Atlas A2, Ascend 910B |
| `atlas-a3` | Atlas A3 |
| `ascend-950` | Ascend 950 |
| `none` | 未指定硬件 |

### 9.2 Frameworks

`frameworks` 仅填写对方案实现有直接影响的框架或工具链。

| ID | 展示名称 |
|---|---|
| `cann-recipes` | cann-recipes |
| `mindspore` | MindSpore |
| `torchtitan` | TorchTitan |
| `megatron` | Megatron |
| `onnx` | ONNX |
| `atb` | ATB |
| `none` | 未指定框架或工具链 |

## 10. `cover`

```json
{"type": "auto"}
```

自动选择顺序为：文档第一张 Markdown/HTML 图片、文档第一个 Mermaid 图表、分类占位封面。

支持的类型：

- `auto`
- `image`：必须提供相对于当前文档的 `source`，或允许的 HTTPS URL。
- `mermaid`：必须提供从 `1` 开始的 `index`。
- `placeholder`

构建阶段必须验证指定图片或 Mermaid 图表存在且可用。

## 11. 场景小类扩展字段

### 11.1 `llmSpeculativeInference`

`llmSpeculativeInference` 仅用于 `infer/llm/**` 文档，描述 LLM 推理文档是否涉及投机推理以及具体方案。

| ID | 展示名称 | 含义 |
|---|---|---|
| `mtp` | MTP | Multi-Token Prediction 或基于多 token 预测的投机推理 |
| `dspark` | DSpark | DSpark 投机推理方案 |
| `dflash` | DFlash | DFlash 投机推理方案 |
| `none` | 未涉及投机推理 | 文档不涉及该类方案 |

规则：

- 只在 `infer/llm/**` 文档中填写。
- 如果文档同时对比或实现多个投机推理方案，可以多选。
- 仅提到推理性能优化、并行或量化，但没有投机推理方案时填写 `["none"]`。
- `none` 只能单独出现。

示例：

```json
"llmSpeculativeInference": ["mtp", "dflash"]
```

### 11.2 `multimodalDitCache`

`multimodalDitCache` 仅用于 `infer/multimodal/**` 文档，描述多模态生成或理解任务中 DiT 结构相关的缓存复用方案。

| ID | 展示名称 | 含义 |
|---|---|---|
| `dit-block-cache` | DiT Block Cache | 复用 DiT block 级中间结果 |
| `attention-cache` | Attention Cache | 复用 Attention 或 KV 相关中间结果 |
| `feature-cache` | Feature Cache | 复用 latent、feature map 或 token feature |
| `teacache` | TeaCache | TeaCache 类 timestep-aware 缓存方案 |
| `magcache` | MagCache | MagCache 类幅值/变化量感知缓存方案 |
| `none` | 未涉及 DiT Cache | 文档不涉及该类方案 |

规则：

- 只在 `infer/multimodal/**` 文档中填写；当前仓库目录使用 `multimodal`，不使用 `multimodel` 拼写。
- 如果正文只泛泛提到缓存，但没有说明 DiT 结构或多模态生成链路中的缓存复用，不填写具体值，使用 `["none"]`。
- 如果文档实现的是未命名的 DiT block 级缓存，使用 `dit-block-cache`；只有明确提到 TeaCache、MagCache 时才使用对应专名。
- `none` 只能单独出现。

示例：

```json
"multimodalDitCache": ["dit-block-cache", "teacache"]
```

## 12. 构建校验与前端使用

构建脚本必须校验字段名、类型、数组重复值、枚举值和封面引用。任一校验失败时停止发布，保留上一版可用站点。

| 页面或模块 | 使用字段 |
|---|---|
| 侧边栏与紧凑导航 | `sidebarTitle` |
| 分类筛选 | 场景范围仅包含 `Infer`、`Train`、`Embodie_AI`；技术属性包含 `quantization`、`parallelism`、`operator`、`cannFeatures`、`hardware`、`frameworks` |
| 报告页属性区 | `quantization`、`parallelism`、`operator`、`cannFeatures`、`hardware`、`frameworks` |
| 封面 | `cover` |

场景小类扩展字段仅在路径匹配时参与筛选和报告页属性展示。例如用户筛选 `infer/llm` 后，前端再展示 `llmSpeculativeInference`；用户筛选 `infer/multimodal` 后，前端再展示 `multimodalDitCache`。

## 13. 后续落地

1. 更新 `metadata_enums.py`，删除旧字段和枚举，加入本文规定的字段和受控值。
2. 按本文规范迁移现有文档的 `cann-meta`。
3. 更新 Blog 构建校验、索引生成和分类筛选逻辑。
4. 在 CI 中校验所有元数据。
