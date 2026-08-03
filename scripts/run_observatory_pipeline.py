#!/usr/bin/env python3
"""
================================================================================
BLOC-RELOC-V2: DYNAMICS OBSERVATORY MASTER ORCHESTRATOR
================================================================================
Automated pipeline execution and verification runner.
Sequential execution flow:
  1. scripts/dynamics_observatory.py
  2. scripts/observatory_advanced_analysis.py
  3. scripts/observatory_final_summary.py

Author: Bloc-Reloc Laboratory
================================================================================
"""

import os
import sys
import datetime
import subprocess
from pathlib import Path

# ------------------------------------------------------------------------------
# 1. PATH RESOLUTION & CHECKPOINTS CONFIGURATION
# ------------------------------------------------------------------------------
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parent.parent

OBSERVATORY_DIR = REPO_ROOT / 'results' / 'observatory'
LOG_FILE = OBSERVATORY_DIR / 'pipeline_execution.log'
SUCCESS_FLAG = OBSERVATORY_DIR / 'PIPELINE_COMPLETE.txt'

STEPS = [
    {
        'name': 'Dynamics Observatory Baseline Engine',
        'script': REPO_ROOT / 'scripts' / 'dynamics_observatory.py',
        'expected_files': [
            'relaxation_models.csv',
            'best_relaxation_models.csv',
            'hazard_curve.csv',
            'survival_analysis.csv',
            'avalanche_distribution.csv',
            'observatory_summary.csv'
        ]
    },
    {
        'name': 'Observatory Advanced Analysis',
        'script': REPO_ROOT / 'scripts' / 'observatory_advanced_analysis.py',
        'expected_files': [
            'relaxation_regime.csv',
            'avalanche_statistics.csv',
            'avalanche_tail_models.csv',
            'master_relaxation_curves.csv',
            'topology_dynamics_correlation.csv'
        ]
    },
    {
        'name': 'Final Dynamic Regime Summary Generator',
        'script': REPO_ROOT / 'scripts' / 'observatory_final_summary.py',
        'expected_files': [
            'dynamic_regime_summary.csv'
        ]
    }
]

# ------------------------------------------------------------------------------
# 2. LOGGING HELPER
# ------------------------------------------------------------------------------
def log_message(log_fp, msg):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    formatted = f"{timestamp} {msg}\n"
    print(msg)
    log_fp.write(formatted)
    log_fp.flush()

# ------------------------------------------------------------------------------
# 3. MAIN ORCHESTRATOR EXECUTION
# ------------------------------------------------------------------------------
def main():
    # Ensure results/observatory directory exists
    OBSERVATORY_DIR.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, 'w', encoding='utf-8') as log_fp:
        log_message(log_fp, "============================================================")
        log_message(log_fp, "STARTING BLOC-RELOC OBSERVATORY PIPELINE EXECUTION")
        log_message(log_fp, f"Repository Root: {REPO_ROOT}")
        log_message(log_fp, "============================================================")

        all_generated_files = []

        for step_idx, step in enumerate(STEPS, start=1):
            script_path = step['script']
            script_name = script_path.name
            desc = step['name']

            log_message(log_fp, f"\n[STEP {step_idx}/{len(STEPS)}] Executing: {script_name} ({desc})")

            # Check script existence
            if not script_path.exists():
                log_message(log_fp, f"\n[FATAL ERROR] Script not found: {script_path}")
                sys.exit(1)

            # Execute step via subprocess
            proc = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(REPO_ROOT)
            )

            step_output = []
            for line in iter(proc.stdout.readline, ''):
                step_output.append(line)
                log_fp.write(f"[{script_name}] {line}")
                log_fp.flush()

            proc.wait()

            if proc.returncode != 0:
                log_message(log_fp, f"\n[FATAL ERROR] Execution failed for {script_name} with exit code {proc.returncode}")
                log_message(log_fp, "--- LAST 50 LINES OF ERROR LOG ---")
                tail_lines = step_output[-50:] if len(step_output) >= 50 else step_output
                for line in tail_lines:
                    sys.stderr.write(line)
                log_message(log_fp, "------------------------------------")
                sys.exit(proc.returncode)

            log_message(log_fp, f" -> Success: {script_name} completed cleanly (exit code 0).")

            # Verify expected artifacts at checkpoint
            missing_files = []
            for fname in step['expected_files']:
                target_file = OBSERVATORY_DIR / fname
                if not target_file.exists():
                    missing_files.append(fname)
                else:
                    all_generated_files.append(fname)

            if missing_files:
                log_message(log_fp, f"\n[FATAL ERROR] Checkpoint verification failed after {script_name}.")
                log_message(log_fp, "Missing expected artifact(s):")
                for mf in missing_files:
                    log_message(log_fp, f"  - {OBSERVATORY_DIR / mf}")
                sys.exit(1)

            log_message(log_fp, f" -> Checkpoint verified: All {len(step['expected_files'])} expected file(s) present.")

        # Write PIPELINE_COMPLETE.txt completion flag
        completion_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(SUCCESS_FLAG, 'w', encoding='utf-8') as sf:
            sf.write("====================================================\n")
            sf.write("BLOC-RELOC OBSERVATORY PIPELINE EXECUTION REPORT\n")
            sf.write("====================================================\n")
            sf.write(f"Timestamp:        {completion_time}\n")
            sf.write(f"Status:           SUCCESS\n\n")
            sf.write("Scripts Executed:\n")
            for step in STEPS:
                sf.write(f"  - {step['script'].name}\n")
            sf.write("\nGenerated Artifacts:\n")
            for fname in all_generated_files:
                sf.write(f"  - results/observatory/{fname}\n")
            sf.write("====================================================\n")

        log_message(log_fp, "\nPipeline completion record written to PIPELINE_COMPLETE.txt")

    # Output final summary to terminal
    print("\n================================================")
    print("BLOC-RELOC OBSERVATORY PIPELINE COMPLETE")
    print("================================================")
    print("\nSTATUS: SUCCESS\n")
    print("Generated:")
    print("  - dynamic_regime_summary.csv")
    print("  - observatory artifacts")
    print("================================================\n")

if __name__ == '__main__':
    main()
