#!/bin/bash
set -e

export PYTHONPATH=$PWD

python3 experiments/run_generation.py
python3 experiments/run_experiment.py

echo "Done"
