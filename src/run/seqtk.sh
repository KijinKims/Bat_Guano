#!/bin/sh
#SBATCH --time=10-00:00:00
#SBATCH --job-name=porechop
#SBATCH --cpus-per-task=2
#SBATCH --mem-per-cpu=4G

while IFS=',' read -r input output; do
seqtk seq -A $input > $output
done < $1
