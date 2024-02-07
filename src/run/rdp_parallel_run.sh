while read sample; do
    rdp_classifier -Xmx16g -t ~/programs/CO1Classifier/mydata/rRNAClassifier.properties -o rdp_output/output/$sample.output trimmed_fasta/$sample.fasta &
done < $1
