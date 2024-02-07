while read sample; do
    vsearch --sintax trimmed_fasta/$sample.fasta --db /home/kijin/programs/CO1Classifier/trained/sintax.udb --strand both --tabbedout vsearch_output/$sample.txt &
done < $1
