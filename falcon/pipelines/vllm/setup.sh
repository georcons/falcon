#!/bin/bash
#SBATCH --job-name=vllm
#SBATCH --partition=batch       # Specify the partition
#SBATCH --constraint=type-gpu   # Or type-gpu for GPU nodes
#SBATCH --mem=120G              # Memory limit
#SBATCH --time=00:30:00         # Job timeout
#SBATCH --mail-type=ALL         # Send updates via Slack