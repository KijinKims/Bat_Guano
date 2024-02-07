final_df <- read.table(input_file, header = TRUE)

TAX <- tax_table(final_df[,1:7])

otumat<- as.matrix(final_df[,8:ncol(final_df)])
mode(otumat) <- "integer"
OTU <- otu_table(otumat, taxa_are_rows=TRUE)

sample_table <- read.csv("sintax_result_visualization/sample_table_1st_run.csv")
sampledata <- sample_data(data.frame(Location=sample_table$Location, Primer=sample_table$Primer, Sample.No=sample_table$Sample, row.names=sample_table$Library, stringsAsFactors = FALSE))

SAM <- sample_data(sampledata)

physeq = phyloseq(OTU, TAX, SAM)
sample_order <- c("sample1","sample2","sample3","sample26","sample27","sample45","sample46","sample47")
sample_data(physeq)$Sample.No <- factor(sample_data(physeq)$Sample.No, levels = sample_order)


bats = subset_taxa(physeq, Order=="Chiroptera")
bats <- ps_filter(bats, Primer == "Bats")

# Species
bats_species <- tax_glom(bats, NArm = FALSE, taxrank="Species")
taxtab = cbind(tax_table(bats_species), species = NA)
taxtab[,"species"] = as(tax_table(bats_species)[,"Species"], 
                        "character")
narows = rownames(tax_table(bats_species))[is.na(data.frame(tax_table(bats_species))$Species)]
taxtab[narows, "species"] <- "Unclassified"
for (i in 1:length(taxtab[,"species"])){
  query_res <- sci2comm(taxtab[i,"species"])
  if(!identical(query_res[[1]], character(0))){
    taxtab[i,"species"] <- paste0(taxtab[i,"species"], "(", query_res[[1]], ")")
  }
}
tax_table(bats_species) <- tax_table(taxtab)
colours <- MakePalette(bats_species, "species")
png("bat_species.png", width=1000)
plot_bar(bats_species, x = "Sample.No", fill = "species")+ facet_grid(~Location, scale = 'free_x')+ geom_bar(stat="identity") + scale_fill_manual("", breaks=names(colours), values=colours) + guides(fill = guide_legend(title = "Species")) + ggtitle("Bat species taxons (Bats primer)")
dev.off()