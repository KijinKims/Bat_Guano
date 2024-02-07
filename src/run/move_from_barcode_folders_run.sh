while read folder; do
cat $folder/*.fastq.gz > $folder.fastq.gz
done < $1
