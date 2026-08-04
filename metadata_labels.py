"""Display labels for CANN Recipes document metadata.

The Markdown ``cann-meta`` block stays machine-readable and only stores enum
IDs. This module is the single source of truth for UI labels exported to the
static site manifest.
"""

LABEL_LANGUAGES = ("en", "zh")


FIELD_LABELS = {
    "sidebarTitle": {"en": "Sidebar title", "zh": "侧栏标题"},
    "quantization": {"en": "Quantization", "zh": "量化"},
    "parallelism": {"en": "Parallelism", "zh": "并行切分"},
    "operator": {"en": "Operator", "zh": "算子种类"},
    "cannFeatures": {"en": "CANN Features", "zh": "CANN 特性"},
    "hardware": {"en": "Hardware", "zh": "硬件"},
    "frameworks": {"en": "Frameworks", "zh": "框架"},
    "cover": {"en": "Cover", "zh": "封面"},
    "llmSpeculativeInference": {"en": "Speculative inference", "zh": "投机推理"},
    "multimodalDitCache": {"en": "DiT Cache", "zh": "DiT Cache"},
}


VALUE_LABELS = {
    "quantization": {
        "bf16": {"en": "BF16", "zh": "BF16"},
        "int8": {"en": "INT8", "zh": "INT8"},
        "int4": {"en": "INT4", "zh": "INT4"},
        "float8": {"en": "Float8", "zh": "Float8"},
        "fp8": {"en": "FP8", "zh": "FP8"},
        "mxfp8": {"en": "MXFP8", "zh": "MXFP8"},
        "hif8": {"en": "HiF8", "zh": "HiF8"},
        "mxfp4": {"en": "MXFP4", "zh": "MXFP4"},
        "none": {"en": "None", "zh": "未涉及量化"},
    },
    "parallelism": {
        "data-parallel": {"en": "Data parallel", "zh": "数据并行"},
        "tensor-parallel": {"en": "Tensor parallel", "zh": "张量并行"},
        "pipeline-parallel": {"en": "Pipeline parallel", "zh": "流水并行"},
        "context-parallel": {"en": "Context parallel", "zh": "上下文并行"},
        "sequence-parallel": {"en": "Sequence parallel", "zh": "序列并行"},
        "expert-parallel": {"en": "Expert parallel", "zh": "专家并行"},
        "zero": {"en": "ZeRO", "zh": "ZeRO"},
        "none": {"en": "None", "zh": "不涉及并行切分"},
    },
    "operator": {
        "ascendc": {"en": "AscendC", "zh": "AscendC"},
        "tilelang": {"en": "TileLang", "zh": "TileLang"},
        "pypto": {"en": "PyPTO", "zh": "PyPTO"},
        "autofuse": {"en": "AutoFuse", "zh": "AutoFuse"},
        "none": {"en": "None", "zh": "不涉及算子方式"},
    },
    "cannFeatures": {
        "multi-stream": {"en": "MultiStream", "zh": "多流"},
        "superkernel": {"en": "superKernel", "zh": "superKernel"},
        "prefetch": {"en": "Prefetch", "zh": "预取"},
        "npugraph": {"en": "NPUGraph", "zh": "NPUGraph"},
        "none": {"en": "None", "zh": "无适用 CANN 特性"},
    },
    "hardware": {
        "atlas-a2": {"en": "Atlas A2 / Ascend 910B", "zh": "Atlas A2 / Ascend 910B"},
        "atlas-a3": {"en": "Atlas A3", "zh": "Atlas A3"},
        "ascend-950": {"en": "Ascend 950", "zh": "Ascend 950"},
        "none": {"en": "None", "zh": "未指定硬件"},
    },
    "frameworks": {
        "cann-recipes": {"en": "CANN Recipes", "zh": "CANN Recipes"},
        "mindspore": {"en": "MindSpore", "zh": "MindSpore"},
        "torchtitan": {"en": "TorchTitan", "zh": "TorchTitan"},
        "megatron": {"en": "Megatron", "zh": "Megatron"},
        "onnx": {"en": "ONNX", "zh": "ONNX"},
        "atb": {"en": "ATB", "zh": "ATB"},
        "none": {"en": "None", "zh": "未指定框架"},
    },
    "cover.type": {
        "auto": {"en": "Auto cover", "zh": "自动封面"},
        "image": {"en": "Image cover", "zh": "图片封面"},
        "mermaid": {"en": "Mermaid cover", "zh": "Mermaid 封面"},
        "placeholder": {"en": "Placeholder cover", "zh": "占位封面"},
    },
    "llmSpeculativeInference": {
        "mtp": {"en": "MTP", "zh": "MTP"},
        "dspark": {"en": "DSpark", "zh": "DSpark"},
        "dflash": {"en": "DFlash", "zh": "DFlash"},
        "none": {"en": "None", "zh": "未涉及投机推理"},
    },
    "multimodalDitCache": {
        "dit-block-cache": {"en": "DiT Block Cache", "zh": "DiT Block Cache"},
        "attention-cache": {"en": "Attention Cache", "zh": "Attention Cache"},
        "feature-cache": {"en": "Feature Cache", "zh": "Feature Cache"},
        "teacache": {"en": "TeaCache", "zh": "TeaCache"},
        "magcache": {"en": "MagCache", "zh": "MagCache"},
        "none": {"en": "None", "zh": "未涉及 DiT Cache"},
    },
}


def metadata_label_manifest() -> dict[str, dict]:
    """Return labels in the JSON shape consumed by the static site."""

    return {
        "fields": FIELD_LABELS,
        "values": VALUE_LABELS,
    }
