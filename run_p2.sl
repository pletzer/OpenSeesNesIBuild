#!/bin/bash -e
#SBATCH --job-name=run_p2
#SBATCH --ntasks=1
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task 2
## END HEADER
#
echo "Running file $1"
srun python $1