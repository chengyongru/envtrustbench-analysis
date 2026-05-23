#!/usr/bin/env python3
"""Compute per-vector and per-scenario stats from verified results."""

import json
from pathlib import Path
from collections import defaultdict

SCRIPT_DIR = Path(__file__).resolve().parent

def main():
    for model in ("glm", "deepseek"):
        verified_file = SCRIPT_DIR / f"experiment-results-{model}" / "verified.json"
        with open(verified_file, encoding="utf-8") as f:
            data = json.load(f)

        cases = data["cases"]

        # Per-vector stats
        vec_stats = defaultdict(lambda: {"pass": 0, "total": 0})
        # Per-scenario stats
        scn_stats = defaultdict(lambda: {"pass": 0, "total": 0})
        # Per-scenario-vector matrix
        matrix = defaultdict(lambda: defaultdict(lambda: {"pass": 0, "total": 0}))

        for c in cases:
            v = c["verified_verdict"]
            vec_stats[c["vector"]]["total"] += 1
            scn_stats[c["scenario"]]["total"] += 1
            matrix[c["scenario"]][c["vector"]]["total"] += 1
            if v == "PASS":
                vec_stats[c["vector"]]["pass"] += 1
                scn_stats[c["scenario"]]["pass"] += 1
                matrix[c["scenario"]][c["vector"]]["pass"] += 1

        print(f"\n{'='*60}")
        print(f"Model: {model}")
        stats = data["stats"]
        print(f"Overall: {stats['verified_pass']}/{stats['total']} = {stats['verified_pass']/stats['total']*100:.1f}% FPCR")

        print(f"\nPer-Vector FPCR:")
        for vec in ["dmm", "eam", "pop", "rfm", "tsm"]:
            s = vec_stats[vec]
            pct = s["pass"]/s["total"]*100 if s["total"] else 0
            print(f"  {vec}: {s['pass']}/{s['total']} = {pct:.1f}%")

        print(f"\nPer-Scenario FPCR:")
        for scn in sorted(scn_stats.keys()):
            s = scn_stats[scn]
            pct = s["pass"]/s["total"]*100 if s["total"] else 0
            print(f"  {scn}: {s['pass']}/{s['total']} = {pct:.1f}%")

        print(f"\nMatrix (scenario × vector):")
        vectors = ["dmm", "eam", "pop", "rfm", "tsm"]
        header = f"{'Scenario':<40} " + " ".join(f"{v:>6}" for v in vectors) + f" {'Avg':>6}"
        print(header)
        for scn in sorted(matrix.keys()):
            row = f"{scn:<40} "
            total_pass = 0
            total_count = 0
            for vec in vectors:
                m = matrix[scn][vec]
                if m["total"]:
                    pct = m["pass"]/m["total"]*100
                    row += f" {pct:>5.0f}%"
                    total_pass += m["pass"]
                    total_count += m["total"]
                else:
                    row += f"    N/A"
            avg = total_pass/total_count*100 if total_count else 0
            row += f" {avg:>5.0f}%"
            print(row)


if __name__ == "__main__":
    main()
