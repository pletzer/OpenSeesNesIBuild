#!/bin/bash -e
#SBATCH --job-name=speed_test
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task 1
## END HEADER
#
method="$1"
width="$2"
output_dir="output-$SLURM_JOBID"
echo "running python speed_test.py $method $width $output_dir with $SLURM_NTASKS cpus"
srun python speed_test.py $method $width
