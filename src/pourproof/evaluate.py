"""Reproducible benchmark and evaluation script for PourProof vision pipeline.

Runs a controlled evaluation set with independently known ground truth, computes:
1. True measurement error against ground truth (|detected - ground_truth|).
2. Specification deviation from user-entered nominal (|detected - nominal|).
3. Pipeline gate dispositions and stage latency.

NOTE: All fixtures in this evaluation are synthetic fixtures with known
mathematical provenance. They establish pipeline reproducibility and do not
substitute for physical on-site construction validation.
"""

import json
import os
import sys
import time
from typing import Dict, Any, List, Optional
import numpy as np

# Ensure src and project roots are importable
_src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_project_root = os.path.abspath(os.path.join(_src_dir, ".."))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from pourproof.vision.runtime import get_opencv_runtime_info
from pourproof.vision.pipeline import run_inspection_pipeline
from tests.fixtures.synthetic_generator import (
    generate_synthetic_rebar_grid,
    generate_blurry_fixture,
    generate_underexposed_fixture,
    generate_overexposed_fixture,
    generate_missing_marker_fixture,
)


def run_benchmark() -> Dict[str, Any]:
    """Execute evaluation benchmark on the controlled synthetic suite."""
    runtime = get_opencv_runtime_info()
    test_cases: List[Dict[str, Any]] = [
        {
            "case_id": "SYNTH-001-STANDARD-PLANAR",
            "description": "Clean planar rebar grid, 150.0mm nominal spacing, 50.0mm marker",
            "generator": lambda: generate_synthetic_rebar_grid(nominal_spacing_mm=150.0, marker_dimension_mm=50.0),
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 15.0,
            "marker_mm": 50.0,
            "expected_status": "measured",
        },
        {
            "case_id": "SYNTH-002-TIGHT-SPACING",
            "description": "Clean planar grid, 100.0mm nominal spacing, 50.0mm marker",
            "generator": lambda: generate_synthetic_rebar_grid(nominal_spacing_mm=100.0, marker_dimension_mm=50.0),
            "nominal_spacing_mm": 100.0,
            "tolerance_mm": 10.0,
            "marker_mm": 50.0,
            "expected_status": "measured",
        },
        {
            "case_id": "SYNTH-003-OUT-OF-TOLERANCE",
            "description": "Grid with middle bar offset by +35mm (GT spacings: 185mm & 115mm vs nominal 150mm)",
            "generator": lambda: generate_synthetic_rebar_grid(nominal_spacing_mm=150.0, irregular_spacing_mm=35.0),
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 10.0,
            "marker_mm": 50.0,
            "expected_status": "needs_review",
        },
        {
            "case_id": "SYNTH-004-DEFECT-BLUR",
            "description": "Severe camera motion/focus blur (negative test for sharpness gate)",
            "generator": generate_blurry_fixture,
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 15.0,
            "marker_mm": 50.0,
            "expected_status": "needs_recapture",
            "expected_reason": "IMAGE_TOO_BLURRY",
        },
        {
            "case_id": "SYNTH-005-DEFECT-UNDEREXPOSED",
            "description": "Severe underexposure / darkness (negative test for lighting gate)",
            "generator": generate_underexposed_fixture,
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 15.0,
            "marker_mm": 50.0,
            "expected_status": "needs_recapture",
            "expected_reason": "IMAGE_UNDEREXPOSED",
        },
        {
            "case_id": "SYNTH-006-DEFECT-OVEREXPOSED",
            "description": "Severe overexposure / clipping (negative test for lighting gate)",
            "generator": generate_overexposed_fixture,
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 15.0,
            "marker_mm": 50.0,
            "expected_status": "needs_recapture",
            "expected_reason": "IMAGE_OVEREXPOSED",
        },
        {
            "case_id": "SYNTH-007-DEFECT-NO-MARKER",
            "description": "Clean rebar grid lacking calibration marker (abstention gate)",
            "generator": generate_missing_marker_fixture,
            "nominal_spacing_mm": 150.0,
            "tolerance_mm": 15.0,
            "marker_mm": 50.0,
            "expected_status": "needs_recapture",
            "expected_reason": "CALIBRATION_MARKER_NOT_FOUND",
        },
    ]

    case_results: List[Dict[str, Any]] = []
    all_gt_errors_mm: List[float] = []
    all_nominal_devs_mm: List[float] = []
    correct_disposition_count = 0

    print("=" * 100)
    print(f"PourProof Numerical Accuracy Benchmark — OpenCV {runtime['version']}")
    print("=" * 100)
    print(f"{'Case ID':<28} {'Expected':<16} {'Actual':<16} {'GT Err(mm)':<12} {'Nom Dev(mm)':<12} {'Status'}")
    print("-" * 100)

    for case in test_cases:
        img, gt = case["generator"]()
        t0 = time.perf_counter()
        res = run_inspection_pipeline(
            image_input=img,
            nominal_spacing_mm=case["nominal_spacing_mm"],
            tolerance_mm=case["tolerance_mm"],
            calibration_marker_mm=case["marker_mm"],
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 1)

        actual_status = res["status"]
        expected_status = case["expected_status"]
        disposition_correct = actual_status == expected_status

        case_gt_errors: List[float] = []
        case_nominal_devs: List[float] = []
        detailed_measurements = []

        # If measurements were produced, pair each with its known ground truth
        if res["status"] in ("measured", "needs_review") and res["measurements"]:
            gt_h_spacings = gt.get("ground_truth_horizontal_spacings_mm", [])
            gt_v_spacings = gt.get("ground_truth_vertical_spacings_mm", [])

            h_idx = 0
            v_idx = 0
            for m in res["measurements"]:
                is_horiz = m["direction"] == "horizontal_spacing"
                gt_val: Optional[float] = None
                if is_horiz and h_idx < len(gt_h_spacings):
                    gt_val = gt_h_spacings[h_idx]
                    h_idx += 1
                elif not is_horiz and v_idx < len(gt_v_spacings):
                    gt_val = gt_v_spacings[v_idx]
                    v_idx += 1

                detected_spacing = m["spacing_mm"]
                nominal_spacing = m["nominal_spacing_mm"]
                nom_dev = abs(m["deviation_mm"])
                case_nominal_devs.append(nom_dev)
                all_nominal_devs_mm.append(nom_dev)

                gt_err = abs(detected_spacing - gt_val) if gt_val is not None else None
                if gt_err is not None:
                    case_gt_errors.append(gt_err)
                    all_gt_errors_mm.append(gt_err)

                detailed_measurements.append({
                    "id": m["measurement_id"],
                    "direction": m["direction"],
                    "detected_spacing_mm": detected_spacing,
                    "ground_truth_spacing_mm": gt_val,
                    "absolute_error_vs_gt_mm": round(gt_err, 3) if gt_err is not None else None,
                    "nominal_spacing_mm": nominal_spacing,
                    "deviation_from_nominal_mm": round(m["deviation_mm"], 3),
                    "in_tolerance": m["in_tolerance"],
                })

        mean_case_gt_err = round(float(np.mean(case_gt_errors)), 3) if case_gt_errors else None
        mean_case_nom_dev = round(float(np.mean(case_nominal_devs)), 3) if case_nominal_devs else None

        if disposition_correct:
            correct_disposition_count += 1
            status_symbol = "PASS"
        else:
            status_symbol = "FAIL"

        gt_err_str = f"{mean_case_gt_err:.3f}" if mean_case_gt_err is not None else "N/A (abstained)"
        nom_dev_str = f"{mean_case_nom_dev:.3f}" if mean_case_nom_dev is not None else "N/A (abstained)"

        print(
            f"{case['case_id']:<28} {expected_status:<16} {actual_status:<16} {gt_err_str:<12} {nom_dev_str:<12} {status_symbol}"
        )

        case_results.append({
            "case_id": case["case_id"],
            "description": case["description"],
            "expected_status": expected_status,
            "actual_status": actual_status,
            "disposition_correct": disposition_correct,
            "next_action": res["next_action"],
            "elapsed_ms": elapsed_ms,
            "measurements_count": len(res["measurements"]),
            "mean_ground_truth_error_mm": mean_case_gt_err,
            "mean_nominal_deviation_mm": mean_case_nom_dev,
            "measurements": detailed_measurements,
        })

    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "dataset": "synthetic_controlled_v1",
        "provenance_note": (
            "All fixtures generated programmatically with known ground truth geometry. "
            "Verification proves algorithmic correctness and metric consistency, not physical jobsite certification."
        ),
        "opencv_version": runtime["version"],
        "opencv_module_path": runtime["module_path"],
        "total_cases": len(test_cases),
        "correct_dispositions": correct_disposition_count,
        "disposition_accuracy_pct": round((correct_disposition_count / len(test_cases)) * 100, 1),
        "metric_distinction": {
            "ground_truth_error": "Absolute difference between detected physical spacing and known fixture ground truth.",
            "nominal_specification_deviation": "Difference between detected physical spacing and user-entered nominal design specification.",
        },
        "mean_absolute_ground_truth_error_mm": round(float(np.mean(all_gt_errors_mm)), 4) if all_gt_errors_mm else None,
        "max_absolute_ground_truth_error_mm": round(float(np.max(all_gt_errors_mm)), 4) if all_gt_errors_mm else None,
        "mean_absolute_nominal_deviation_mm": round(float(np.mean(all_nominal_devs_mm)), 4) if all_nominal_devs_mm else None,
        "cases": case_results,
    }

    print("-" * 100)
    print(f"Summary: {correct_disposition_count}/{len(test_cases)} dispositions correct ({summary['disposition_accuracy_pct']}%)")
    if all_gt_errors_mm:
        print(f"True Mean Ground-Truth Error: {summary['mean_absolute_ground_truth_error_mm']} mm (Max: {summary['max_absolute_ground_truth_error_mm']} mm)")
    if all_nominal_devs_mm:
        print(f"Mean Specification Deviation from Nominal: {summary['mean_absolute_nominal_deviation_mm']} mm")
    print("=" * 100)

    # Save report to local-results/
    os.makedirs("local-results", exist_ok=True)
    report_path = os.path.join("local-results", "evaluation_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Machine-readable evaluation saved to: {report_path}")

    return summary


if __name__ == "__main__":
    run_benchmark()
