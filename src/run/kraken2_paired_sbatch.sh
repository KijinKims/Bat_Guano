#!/bin/bash

#SBATCH --time=00:15:00
#SBATCH --job-name=kraken2
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=2G

# parse arguments
input_file=$1
outdir=$2
db=$3

# read input file as array
#readarray ARRAY < $input_file

# parse sample metadata by task ID
while IFS=',' read sample path1 path2; do
#sample=$(echo ${ARRAY[$SLURM_ARRAY_TASK_ID]} | cut -f1 -d',')
#path1=$(echo ${ARRAY[$SLURM_ARRAY_TASK_ID]} | cut -f2 -d',')
#path2=$(echo ${ARRAY[$SLURM_ARRAY_TASK_ID]} | cut -f3 -d',')

# create sample output dir
mkdir -p $outdir/$sample

# call tool
kraken2 --db $db \
    --threads 16 \
    --output $outdir/$sample/kraken.out \
    --report $outdir/$sample/kraken.report \
    --paired \
    $path1 $path2

# create Krona input
cat $outdir/$sample/kraken.out | cut -f2,3 > $outdir/$sample/$sample.krona
done < $input_file
