"""Inspect the RSNA knee competition image layout on Kaggle.

This script is intentionally read-only. It scans the training image tree, joins
the discovered series with train_series.csv, and reads only a sample of DICOM
headers (not pixel arrays). Reports are written to a small output directory so
they can be downloaded and reviewed without downloading the MRI dataset.

Kaggle usage:
    python scripts/inspect_kaggle_train_images.py \
        --input-root /kaggle/input/rsna-knee-abnormality-detection \
        --output-dir /kaggle/working/rsna_structure_report
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

try:
    import pydicom
except ImportError as exc:  # pragma: no cover - informative Kaggle error
    raise SystemExit(
        "pydicom is required. In a Kaggle cell, run: !pip install -q pydicom"
    ) from exc


DICOM_TAGS = [
    "SOPInstanceUID",
    "StudyInstanceUID",
    "SeriesInstanceUID",
    "SeriesDescription",
    "ProtocolName",
    "SequenceName",
    "ScanningSequence",
    "SequenceVariant",
    "ScanOptions",
    "MRAcquisitionType",
    "MagneticFieldStrength",
    "Manufacturer",
    "ManufacturerModelName",
    "Rows",
    "Columns",
    "PixelSpacing",
    "SliceThickness",
    "SpacingBetweenSlices",
    "InstanceNumber",
    "ImagePositionPatient",
    "ImageOrientationPatient",
    "SliceLocation",
    "PhotometricInterpretation",
    "BitsAllocated",
    "BitsStored",
    "HighBit",
    "PixelRepresentation",
    "RescaleSlope",
    "RescaleIntercept",
    "WindowCenter",
    "WindowWidth",
    "NumberOfFrames",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-root",
        type=Path,
        default=Path("/kaggle/input/rsna-knee-abnormality-detection"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("/kaggle/working/rsna_structure_report"),
    )
    parser.add_argument(
        "--metadata-sample-size",
        type=int,
        default=300,
        help="Number of series for which one DICOM header is read.",
    )
    parser.add_argument(
        "--ordering-sample-size",
        type=int,
        default=30,
        help="Number of series for which all slice headers are checked.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def find_file(root: Path, filename: str) -> Path:
    direct = root / filename
    if direct.exists():
        return direct
    matches = list(root.rglob(filename))
    if len(matches) != 1:
        raise FileNotFoundError(
            f"Expected exactly one {filename!r} under {root}, found {len(matches)}"
        )
    return matches[0]


def find_image_root(input_root: Path) -> Path:
    candidates = [
        input_root / "train_images",
        input_root / "train",
        input_root / "images" / "train",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate

    first_dicom = next(input_root.rglob("*.dcm"), None)
    if first_dicom is None:
        raise FileNotFoundError(
            f"No .dcm files found under {input_root}. Make sure the competition "
            "dataset is attached to the Kaggle Notebook."
        )

    # Typical layout is root/train_images/study_uid/series_uid/image.dcm.
    # Walk upward and prefer an ancestor whose name contains 'train'.
    for ancestor in first_dicom.parents:
        if ancestor == input_root:
            break
        if "train" in ancestor.name.lower():
            return ancestor
    return first_dicom.parents[2]


def dicom_files_in_directory(directory: Path, filenames: Iterable[str]) -> list[Path]:
    return sorted(
        directory / name
        for name in filenames
        if Path(name).suffix.lower() == ".dcm"
    )


def scan_series(image_root: Path, series_table: pd.DataFrame) -> tuple[pd.DataFrame, Counter]:
    expected_series = set(series_table["SeriesInstanceUID"].astype(str))
    expected_study_by_series = dict(
        zip(
            series_table["SeriesInstanceUID"].astype(str),
            series_table["StudyInstanceUID"].astype(str),
        )
    )
    extension_counts: Counter = Counter()
    records: list[dict[str, Any]] = []

    for current, _, filenames in os.walk(image_root):
        if not filenames:
            continue

        current_path = Path(current)
        for name in filenames:
            suffix = Path(name).suffix.lower() or "<no_extension>"
            extension_counts[suffix] += 1

        dicoms = dicom_files_in_directory(current_path, filenames)
        if not dicoms:
            continue

        relative = current_path.relative_to(image_root)
        parts = relative.parts
        directory_series_uid = current_path.name
        matched_series_uid = (
            directory_series_uid if directory_series_uid in expected_series else None
        )
        study_uid = (
            expected_study_by_series.get(matched_series_uid)
            if matched_series_uid is not None
            else (parts[-2] if len(parts) >= 2 else None)
        )

        records.append(
            {
                "StudyInstanceUID": study_uid,
                "SeriesInstanceUID": matched_series_uid or directory_series_uid,
                "series_dir": str(current_path),
                "relative_series_dir": str(relative),
                "path_depth_below_image_root": len(parts),
                "slice_count": len(dicoms),
                "first_dicom": str(dicoms[0]),
                "last_dicom": str(dicoms[-1]),
                "first_filename": dicoms[0].name,
                "last_filename": dicoms[-1].name,
                "series_uid_matched_csv": matched_series_uid is not None,
            }
        )

    inventory = pd.DataFrame.from_records(records)
    if inventory.empty:
        raise RuntimeError(
            f"Directories were scanned under {image_root}, but no .dcm series were found."
        )
    return inventory, extension_counts


def dicom_value(dataset: pydicom.Dataset, keyword: str) -> Any:
    value = getattr(dataset, keyword, None)
    if value is None:
        return None
    if isinstance(value, (str, int, float)):
        return value
    try:
        return list(value)
    except TypeError:
        return str(value)


def read_header(path: Path) -> dict[str, Any]:
    dataset = pydicom.dcmread(
        path,
        stop_before_pixels=True,
        force=True,
        specific_tags=DICOM_TAGS,
    )
    return {tag: dicom_value(dataset, tag) for tag in DICOM_TAGS}


def balanced_sample(
    table: pd.DataFrame,
    sample_size: int,
    seed: int,
) -> pd.DataFrame:
    if len(table) <= sample_size:
        return table.copy()

    group_columns = [
        column
        for column in ["Anatomical_Plane", "Fluid_Sensitive", "Fat_Suppression"]
        if column in table.columns
    ]
    if not group_columns:
        return table.sample(sample_size, random_state=seed)

    groups = list(table.groupby(group_columns, dropna=False, sort=False))
    per_group = max(1, math.ceil(sample_size / len(groups)))
    pieces = [
        group.sample(min(per_group, len(group)), random_state=seed + index)
        for index, (_, group) in enumerate(groups)
    ]
    sampled = pd.concat(pieces, ignore_index=True).drop_duplicates(
        subset=["SeriesInstanceUID"]
    )
    if len(sampled) > sample_size:
        sampled = sampled.sample(sample_size, random_state=seed)
    return sampled


def sample_series_metadata(
    inventory: pd.DataFrame,
    sample_size: int,
    seed: int,
) -> pd.DataFrame:
    sampled = balanced_sample(inventory, sample_size, seed)
    records: list[dict[str, Any]] = []

    for row in sampled.to_dict("records"):
        record = {
            "inventory_StudyInstanceUID": row.get("StudyInstanceUID"),
            "inventory_SeriesInstanceUID": row.get("SeriesInstanceUID"),
            "Anatomical_Plane": row.get("Anatomical_Plane"),
            "Fluid_Sensitive": row.get("Fluid_Sensitive"),
            "Fat_Suppression": row.get("Fat_Suppression"),
            "slice_count": row.get("slice_count"),
            "sample_dicom": row.get("first_dicom"),
            "read_error": None,
        }
        try:
            record.update(read_header(Path(row["first_dicom"])))
        except Exception as exc:  # keep scanning and report malformed files
            record["read_error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)

    return pd.DataFrame.from_records(records)


def check_slice_ordering(
    inventory: pd.DataFrame,
    sample_size: int,
    seed: int,
) -> pd.DataFrame:
    sampled = balanced_sample(inventory, sample_size, seed + 10_000)
    records: list[dict[str, Any]] = []

    for row in sampled.to_dict("records"):
        series_dir = Path(row["series_dir"])
        files = sorted(series_dir.glob("*.dcm"))
        instance_numbers: list[int] = []
        image_positions: list[str] = []
        shapes: list[str] = []
        errors: list[str] = []

        for path in files:
            try:
                header = pydicom.dcmread(
                    path,
                    stop_before_pixels=True,
                    force=True,
                    specific_tags=[
                        "InstanceNumber",
                        "ImagePositionPatient",
                        "Rows",
                        "Columns",
                    ],
                )
                instance = getattr(header, "InstanceNumber", None)
                if instance is not None:
                    instance_numbers.append(int(instance))
                position = getattr(header, "ImagePositionPatient", None)
                if position is not None:
                    image_positions.append("|".join(str(value) for value in position))
                rows = getattr(header, "Rows", None)
                columns = getattr(header, "Columns", None)
                if rows is not None and columns is not None:
                    shapes.append(f"{int(rows)}x{int(columns)}")
            except Exception as exc:
                errors.append(f"{path.name}: {type(exc).__name__}: {exc}")

        records.append(
            {
                "StudyInstanceUID": row.get("StudyInstanceUID"),
                "SeriesInstanceUID": row.get("SeriesInstanceUID"),
                "Anatomical_Plane": row.get("Anatomical_Plane"),
                "Fluid_Sensitive": row.get("Fluid_Sensitive"),
                "Fat_Suppression": row.get("Fat_Suppression"),
                "file_count": len(files),
                "headers_read": len(files) - len(errors),
                "instance_number_count": len(instance_numbers),
                "instance_number_unique": len(set(instance_numbers)),
                "instance_number_min": min(instance_numbers, default=None),
                "instance_number_max": max(instance_numbers, default=None),
                "image_position_count": len(image_positions),
                "image_position_unique": len(set(image_positions)),
                "unique_shapes": ";".join(sorted(set(shapes))),
                "error_count": len(errors),
                "errors": " || ".join(errors[:5]),
            }
        )

    return pd.DataFrame.from_records(records)


def quantiles(series: pd.Series) -> dict[str, Any]:
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return {}
    return {
        "min": int(values.min()),
        "p01": float(values.quantile(0.01)),
        "p05": float(values.quantile(0.05)),
        "p25": float(values.quantile(0.25)),
        "median": float(values.quantile(0.50)),
        "p75": float(values.quantile(0.75)),
        "p95": float(values.quantile(0.95)),
        "p99": float(values.quantile(0.99)),
        "max": int(values.max()),
        "mean": float(values.mean()),
    }


def json_ready(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    train_csv_path = find_file(args.input_root, "train.csv")
    series_csv_path = find_file(args.input_root, "train_series.csv")
    image_root = find_image_root(args.input_root)

    train = pd.read_csv(train_csv_path)
    series_table = pd.read_csv(series_csv_path)
    inventory, extension_counts = scan_series(image_root, series_table)

    inventory = inventory.merge(
        series_table,
        on=["StudyInstanceUID", "SeriesInstanceUID"],
        how="left",
        validate="one_to_one",
        indicator="series_csv_join",
    )

    metadata = sample_series_metadata(
        inventory,
        sample_size=args.metadata_sample_size,
        seed=args.seed,
    )
    ordering = check_slice_ordering(
        inventory,
        sample_size=args.ordering_sample_size,
        seed=args.seed,
    )

    expected_series = set(series_table["SeriesInstanceUID"].astype(str))
    found_series = set(inventory["SeriesInstanceUID"].astype(str))
    expected_studies = set(train["StudyInstanceUID"].astype(str))
    found_studies = set(inventory["StudyInstanceUID"].dropna().astype(str))

    series_per_study = inventory.groupby("StudyInstanceUID").size()
    report = {
        "input_root": args.input_root,
        "train_csv": train_csv_path,
        "train_series_csv": series_csv_path,
        "detected_train_image_root": image_root,
        "train_rows": len(train),
        "train_unique_studies": train["StudyInstanceUID"].nunique(),
        "train_series_csv_rows": len(series_table),
        "train_series_csv_unique_series": series_table["SeriesInstanceUID"].nunique(),
        "found_studies": len(found_studies),
        "found_series_directories": len(inventory),
        "found_dicom_files": int(inventory["slice_count"].sum()),
        "missing_study_count": len(expected_studies - found_studies),
        "missing_study_examples": sorted(expected_studies - found_studies)[:20],
        "missing_series_count": len(expected_series - found_series),
        "missing_series_examples": sorted(expected_series - found_series)[:20],
        "unexpected_series_count": len(found_series - expected_series),
        "unexpected_series_examples": sorted(found_series - expected_series)[:20],
        "series_csv_join_counts": inventory["series_csv_join"].value_counts().to_dict(),
        "file_extension_counts": dict(extension_counts),
        "path_depth_counts": inventory[
            "path_depth_below_image_root"
        ].value_counts().sort_index().to_dict(),
        "slice_count_quantiles": quantiles(inventory["slice_count"]),
        "series_per_study_quantiles": quantiles(series_per_study),
        "plane_counts": inventory["Anatomical_Plane"].value_counts(dropna=False).to_dict(),
        "acquisition_group_counts": (
            inventory.groupby(
                ["Anatomical_Plane", "Fluid_Sensitive", "Fat_Suppression"],
                dropna=False,
            )
            .size()
            .sort_values(ascending=False)
            .rename("count")
            .reset_index()
            .to_dict("records")
        ),
        "sampled_metadata_rows": len(metadata),
        "sampled_metadata_read_errors": int(metadata["read_error"].notna().sum()),
        "ordering_sample_rows": len(ordering),
        "ordering_sample_error_series": int((ordering["error_count"] > 0).sum()),
    }

    inventory.to_csv(args.output_dir / "series_inventory.csv", index=False)
    metadata.to_csv(args.output_dir / "dicom_sample_metadata.csv", index=False)
    ordering.to_csv(args.output_dir / "slice_ordering_sample.csv", index=False)
    with (args.output_dir / "dataset_structure_report.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(json_ready(report), handle, indent=2, ensure_ascii=False)

    print(json.dumps(json_ready(report), indent=2, ensure_ascii=False))
    print("\nCreated:")
    for path in sorted(args.output_dir.iterdir()):
        print(f"  {path} ({path.stat().st_size / 1024:.1f} KiB)")


if __name__ == "__main__":
    main()
