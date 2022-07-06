#!/bin/bash -e
#SBATCH --job-name=example_mpi_paralleltruss_explicit
#SBATCH --ntasks=2
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task 1
## END HEADER
#
srun python example_mpi_paralleltruss_explicit.py
