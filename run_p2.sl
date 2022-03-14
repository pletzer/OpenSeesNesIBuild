#!/bin/bash -e
#SBATCH --job-name=run_p2
#SBATCH --ntasks=1
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task 2
## END HEADER
#
echo "Running file $1"
mpiexec -np 2 python $1