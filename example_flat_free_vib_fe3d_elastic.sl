#!/bin/bash -e
#SBATCH --job-name=flat_free_vib_fe3d_elastic
#SBATCH --ntasks=16
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task 1
#SBATCH --account=nesi03638
## END HEADER
#
method="$1"
size="$2"
srun python example_flat_free_vib_fe3d_elastic.py $method $size "out-folder-$SLURM_JOBID"
