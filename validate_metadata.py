#!/usr/bin/env python3
"""Validate cann-meta blocks in all content documents."""

import json
import re
import sys
from pathlib import Path

from metadata_enums import (
    CannFeature,
    CoverType,
    Framework,
    Hardware,
    LlmSpeculativeInference,
    MetadataField,
    MultimodalDitCache,
    Operator,
    Parallelism,
    Quantization,
    enum_values,
)
from metadata_labels import FIELD_LABELS, LABEL_LANGUAGES, VALUE_LABELS


ROOT = Path(__file__).resolve().parent
CONTENT_ROOTS = ("infer", "train", "embodied", "cann_features")
META_PATTERN = re.compile(r"<!--\s*cann-meta\s*\n([\s\S]*?)\n\s*-->")
ALLOWED_FIELDS = enum_values(MetadataField)
ENUM_FIELDS = {
    "quantization": enum_values(Quantization),
    "parallelism": enum_values(Parallelism),
    "operator": enum_values(Operator),
    "cannFeatures": enum_values(CannFeature),
    "hardware": enum_values(Hardware),
    "frameworks": enum_values(Framework),
}
SCOPED_ENUM_FIELDS = {
    "llmSpeculativeInference": {
        "roots": ("infer/llm/",),
        "allowed": enum_values(LlmSpeculativeInference),
        "limits": (1, 3),
    },
    "multimodalDitCache": {
        "roots": ("infer/multimodal/",),
        "allowed": enum_values(MultimodalDitCache),
        "limits": (1, 5),
    },
}
LIMITS = {
    "quantization": (1, 6),
    "parallelism": (1, 6),
    "operator": (1, 4),
    "cannFeatures": (1, 6),
    "hardware": (0, 4),
    "frameworks": (0, 5),
}


def validate_label_entry(name, labels):
    errors = []
    if not isinstance(labels, dict):
        return [f"{name} must define localized labels"]
    missing = [lang for lang in LABEL_LANGUAGES if not isinstance(labels.get(lang), str) or not labels[lang].strip()]
    if missing:
        errors.append(f"{name} is missing labels for languages: {missing}")
    return errors


def validate_metadata_labels():
    """Ensure every machine enum has front-end display labels."""

    errors = []
    unknown_field_labels = sorted(set(FIELD_LABELS) - ALLOWED_FIELDS)
    if unknown_field_labels:
        errors.append(f"FIELD_LABELS contains unknown metadata fields: {unknown_field_labels}")
    for field in sorted(ALLOWED_FIELDS):
        errors.extend(validate_label_entry(f"FIELD_LABELS[{field!r}]", FIELD_LABELS.get(field)))

    value_specs = {
        **ENUM_FIELDS,
        **{field: spec["allowed"] for field, spec in SCOPED_ENUM_FIELDS.items()},
        "cover.type": enum_values(CoverType),
    }
    unknown_value_fields = sorted(set(VALUE_LABELS) - set(value_specs))
    if unknown_value_fields:
        errors.append(f"VALUE_LABELS contains unknown enum fields: {unknown_value_fields}")
    for field, allowed_values in value_specs.items():
        labels = VALUE_LABELS.get(field)
        if not isinstance(labels, dict):
            errors.append(f"VALUE_LABELS[{field!r}] must define labels for enum values")
            continue
        missing = sorted(allowed_values - set(labels))
        if missing:
            errors.append(f"VALUE_LABELS[{field!r}] is missing enum values: {missing}")
        unknown = sorted(set(labels) - allowed_values)
        if unknown:
            errors.append(f"VALUE_LABELS[{field!r}] contains unknown enum values: {unknown}")
        for value in sorted(allowed_values & set(labels)):
            errors.extend(validate_label_entry(f"VALUE_LABELS[{field!r}][{value!r}]", labels[value]))
    return errors


def content_documents():
    return sorted(path for name in CONTENT_ROOTS for path in (ROOT / name).rglob("*.md"))


def validate_array(path, field, value, allowed=None, limits=None):
    errors = []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        return [f"{path}: {field} must be an array of non-empty strings"]
    if len(value) != len(set(value)):
        errors.append(f"{path}: {field} contains duplicate values")
    minimum, maximum = limits or LIMITS[field]
    if not minimum <= len(value) <= maximum:
        errors.append(f"{path}: {field} must contain {minimum} to {maximum} values")
    if allowed is not None:
        unknown = sorted(set(value) - allowed)
        if unknown:
            errors.append(f"{path}: {field} contains unknown values: {unknown}")
        if len(value) > 1 and "none" in value:
            errors.append(f"{path}: {field} cannot mix none with other values")
    return errors


def validate_cover(path, cover, markdown):
    if not isinstance(cover, dict):
        return [f"{path}: cover must be an object"]
    cover_type = cover.get("type")
    if cover_type not in enum_values(CoverType):
        return [f"{path}: invalid cover type: {cover_type!r}"]
    keys = set(cover)
    if cover_type == CoverType.IMAGE:
        source = cover.get("source")
        if keys != {"type", "source"} or not isinstance(source, str) or not source.strip():
            return [f"{path}: image cover requires only a non-empty source"]
        if not source.startswith(("http://", "https://")):
            resolved = (path.parent / source.split("?", 1)[0]).resolve()
            if not resolved.is_file():
                return [f"{path}: cover image does not exist: {source}"]
    elif cover_type == CoverType.MERMAID:
        index = cover.get("index")
        diagrams = re.findall(r"^\s*```\s*mermaid\s*$", markdown, re.IGNORECASE | re.MULTILINE)
        if keys != {"type", "index"} or not isinstance(index, int) or not 1 <= index <= len(diagrams):
            return [f"{path}: Mermaid cover index is invalid"]
    elif keys != {"type"}:
        return [f"{path}: {cover_type} cover only accepts the type field"]
    return []


def main():
    documents = content_documents()
    errors = validate_metadata_labels()
    for path in documents:
        markdown = path.read_text(encoding="utf-8")
        matches = list(META_PATTERN.finditer(markdown))
        relative = path.relative_to(ROOT)
        if len(matches) != 1:
            errors.append(f"{relative}: expected exactly one cann-meta block, found {len(matches)}")
            continue
        if not re.search(r"<!--\s*cann-meta\s*\n[\s\S]*?\n\s*-->\s*$", markdown):
            errors.append(f"{relative}: cann-meta block must be at the end of the document")
        try:
            metadata = json.loads(matches[0].group(1))
        except json.JSONDecodeError as error:
            errors.append(f"{relative}: invalid cann-meta JSON: {error}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{relative}: cann-meta must be an object")
            continue
        unknown = sorted(set(metadata) - ALLOWED_FIELDS)
        if unknown:
            errors.append(f"{relative}: unknown metadata fields: {unknown}")
        sidebar_title = metadata.get("sidebarTitle")
        if not isinstance(sidebar_title, str) or not sidebar_title.strip():
            errors.append(f"{relative}: sidebarTitle is required")
        elif len(sidebar_title) > 24:
            errors.append(f"{relative}: sidebarTitle must not exceed 24 characters")
        for field, allowed in ENUM_FIELDS.items():
            if field not in metadata:
                errors.append(f"{relative}: {field} is required")
            else:
                errors.extend(validate_array(relative, field, metadata[field], allowed))
        relative_posix = relative.as_posix()
        for field, spec in SCOPED_ENUM_FIELDS.items():
            applies = relative_posix.startswith(spec["roots"])
            if field not in metadata:
                if applies:
                    errors.append(f"{relative}: {field} is required under {spec['roots']}")
                continue
            if not applies:
                errors.append(f"{relative}: {field} is only allowed under {spec['roots']}")
                continue
            errors.extend(validate_array(relative, field, metadata[field], spec["allowed"], spec["limits"]))
        if "cover" in metadata:
            errors.extend(validate_cover(relative, metadata["cover"], markdown))
        if not re.search(r"^#\s+\S", markdown, re.MULTILINE):
            errors.append(f"{relative}: document is missing an H1")

    if errors:
        print("Metadata validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"Validated metadata for {len(documents)} documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
