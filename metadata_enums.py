"""Controlled values for CANN Recipes document metadata.

Keep these enums aligned with docs_info.md. Dynamic references such as
cover.source are intentionally not enumerated here.
"""

from enum import StrEnum


class MetadataField(StrEnum):
    """Allowed top-level fields inside a cann-meta block."""

    SIDEBAR_TITLE = "sidebarTitle"
    QUANTIZATION = "quantization"
    PARALLELISM = "parallelism"
    OPERATOR = "operator"
    CANN_FEATURES = "cannFeatures"
    HARDWARE = "hardware"
    FRAMEWORKS = "frameworks"
    COVER = "cover"
    LLM_SPECULATIVE_INFERENCE = "llmSpeculativeInference"
    MULTIMODAL_DIT_CACHE = "multimodalDitCache"


class Quantization(StrEnum):
    """Weight data types and quantized weight formats."""

    BF16 = "bf16"
    INT8 = "int8"
    INT4 = "int4"
    FLOAT8 = "float8"
    FP8 = "fp8"
    MXFP8 = "mxfp8"
    HIF8 = "hif8"
    MXFP4 = "mxfp4"
    NONE = "none"


class Parallelism(StrEnum):
    """Model, sequence, and data partitioning types."""

    DATA_PARALLEL = "data-parallel"
    TENSOR_PARALLEL = "tensor-parallel"
    PIPELINE_PARALLEL = "pipeline-parallel"
    CONTEXT_PARALLEL = "context-parallel"
    SEQUENCE_PARALLEL = "sequence-parallel"
    EXPERT_PARALLEL = "expert-parallel"
    ZERO = "zero"
    NONE = "none"


class Operator(StrEnum):
    """Operator development and optimization approaches."""

    ASCENDC = "ascendc"
    TILELANG = "tilelang"
    PYPTO = "pypto"
    AUTOFUSE = "autofuse"
    NONE = "none"


class CannFeature(StrEnum):
    """Fixed CANN atomic feature categories."""

    MULTI_STREAM = "multi-stream"
    SUPERKERNEL = "superkernel"
    PREFETCH = "prefetch"
    NPUGRAPH = "npugraph"
    NONE = "none"


class Hardware(StrEnum):
    """Hardware platforms covered by the metadata specification."""

    ATLAS_A2 = "atlas-a2"
    ATLAS_A3 = "atlas-a3"
    ASCEND_950 = "ascend-950"
    NONE = "none"


class Framework(StrEnum):
    """Frameworks and toolchains directly relevant to a report."""

    CANN_RECIPES = "cann-recipes"
    MINDSPORE = "mindspore"
    TORCHTITAN = "torchtitan"
    MEGATRON = "megatron"
    ONNX = "onnx"
    ATB = "atb"
    NONE = "none"


class CoverType(StrEnum):
    AUTO = "auto"
    IMAGE = "image"
    MERMAID = "mermaid"
    PLACEHOLDER = "placeholder"


class LlmSpeculativeInference(StrEnum):
    """Speculative inference approaches for infer/llm reports."""

    MTP = "mtp"
    DSPARK = "dspark"
    DFLASH = "dflash"
    NONE = "none"


class MultimodalDitCache(StrEnum):
    """DiT cache approaches for infer/multimodal reports."""

    DIT_BLOCK_CACHE = "dit-block-cache"
    ATTENTION_CACHE = "attention-cache"
    FEATURE_CACHE = "feature-cache"
    TEACACHE = "teacache"
    MAGCACHE = "magcache"
    NONE = "none"


def enum_values(enum_class: type[StrEnum]) -> set[str]:
    """Return the serialized values of a metadata enum."""

    return {item.value for item in enum_class}
