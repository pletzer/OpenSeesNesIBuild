#!/bin/bash -e
#SBATCH --job-name=run_p2nt
#SBATCH --ntasks=2
#SBATCH --time=00:05:00
## END HEADER
#
echo "Running file $1"
mpiexec -np 2 python $1