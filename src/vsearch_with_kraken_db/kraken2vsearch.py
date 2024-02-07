#!/usr/bin/env python
# Mike Robeson
# quickly hacked / draft code to build a compatable fasta file for use in usearch v8.1
# See: http://www.drive5.com/usearch/manual/utax_user_train.html

from optparse import OptionParser, OptionGroup
from cogent.parse.ncbi_taxonomy import NcbiTaxonomyFromFiles
from cogent.parse.fasta import MinimalFastaParser
import unicodedata

def make_ncbi_taxonomy_tree(nodes_fp, names_fp):
        tree = NcbiTaxonomyFromFiles(open(nodes_fp), open(names_fp))
        return tree

def make_lineage_builder(tree, ranks):#ranks=['superkingdom','phylum','class','order','family','genus','species']):
        """tax_dict is either {gi : taxid} or {acc : taxid}"""
        taxonomy_rank_lookup = dict([(rank,idx) for idx,rank in enumerate(ranks)])
        lr = len(ranks)
        def get_lineage(taxid):
                """returns taxonomic lineage for all ranks as list"""
                lineage = ['NOTAXONOMYRECORD'] * lr # blank this out each time
                try:
                        node = tree.ById[int(taxid)]
                        curr = node
                        while curr.Parent is not None:
                                if curr.Rank in taxonomy_rank_lookup:
                                        lineage[taxonomy_rank_lookup[curr.Rank]] = curr.Name
                                curr = curr.Parent
                        return lineage
                except KeyError:
                        print "tax id \'%s\' was not found." % taxid
                        return ['NOTAXONOMYRECORD'] * len(ranks)
        return get_lineage

def remove_odd_ascii(lin_name):
	"""remove ascii chars, return what remains.
	Some code taken from https://gist.github.com/walterst/0a4d36dbb20c54eeb952
	Also see:
		 http://stackoverflow.com/questions/14118352/how-to-convert-unicode-accented-characters-to-pure-ascii-without-accents
		 http://stackoverflow.com/questions/4182603/python-how-to-convert-a-string-to-utf-8
	WARNING: may result in lineage names missing characters"""
	other_odd_chars = set(["'","{","}","[","]","(",")","_","-","+","=","*","&","^","%","$","#","@","\"","/","|","`","~",':',';',",",".","?"])
	
	lin_utf8 = unicode(lin_name, "utf-8")
	norm_unicode = unicodedata.normalize('NFD', lin_utf8).encode('ascii', 'ignore')
	
	updated_lineage_name = ""
	for char in norm_unicode:
		if ord(char) < 128 and char not in other_odd_chars:
			updated_lineage_name += char
	return updated_lineage_name

def clean_lineage_names(lineage_list):
	"""Tries to remove odd characters and replace extraneous whitespace with
	 '_' in lineage names"""
	updated_lin_list = []
	for lin_name in lineage_list:
		fixed_ascii = remove_odd_ascii(lin_name)
		fixed_ascii_white = '_'.join(fixed_ascii.split())
		updated_lin_list.append(fixed_ascii_white)
	return updated_lin_list

def make_usearch_fasta(short_label, lineage_list, rank_levels, seq):
	clean_lineage_list = clean_lineage_names(lineage_list)
	rl_tup = zip(rank_levels, clean_lineage_list)
	rl_list = [r + ':' + l for (r,l) in rl_tup]
	usearch_lineage = ','.join(rl_list)
	fasta_str = '>' + short_label + ';tax=' + usearch_lineage + ';\n' + seq + '\n'
	return fasta_str


def get_acc(subject_id):
        """Returns gi number from BLAST result line.
                Returns: "7184"
                From: ">kraken:taxid|7184"
        """
        acc = subject_id.split('|')[1]
        return acc

def parse_gb_data(gb_recs, fasta_out, get_lineage_func, rank_levels, get_id_func=get_acc):
    i=0
    fp = MinimalFastaParser(gb_recs.read().split('\n'))
    for label,seq in fp:
        i += 1
        id = get_id_func(label)
        lineage = get_lineage_func(id)
        fasta_str = make_usearch_fasta(str(i), lineage, rank_levels, seq)
        fasta_out.write(fasta_str)
		

def main():
	usage = """
	\n%prog -g gi_taxid_nucl.dmp -n nodes.dmp -m names.dmp -l \'d,k,p,c,o,f,g,s\' -r \'kingdom,phylum,subclass,order,family,subfamily,genus,species\' -i genbank_records.fna -o usearch_formatted.fna
		
		Use \'%prog -h\' for more information.
	"""
	# set up options
	parser = OptionParser(usage=usage)
	parser.add_option("-r", "--ranks",
		default='kingdom,phylum,class,order,family,genus,species', help="Comma separated taxonomic ranks. For plants I suggest: \'kingdom,phylum,subclass,order,family,tribe,genus,species\' [default: %default]")
		# full gb taxonomy list:
		# superkingdom,kingdom,subkingdom,phylum,superclass,class,subclass,infraclass,superorder,order,suborder,infraorder,parvorder,superfamily,family,subfamily,tribe,subtribe,genus,subgenus,species group,species subgroup,species
	parser.add_option("-l", "--rank_levels", default='k,p,c,o,f,g,s', help="Comma separated rank levels. Should have as many entries as \'--ranks\'. [default: %default]")
	req = OptionGroup(parser, "Required Options")
	req.add_option("-i", "--input_fp", action="store", type="string", help="GenBank FASTA records. [REQUIRED]")
	req.add_option("-o", "--output_fp", action="store", type="string", help="usearch formatted FASTA output. [REQUIRED]")
	req.add_option("-n", "--nodes_fp", action="store", type="string", help="The nodes.dmp file from GenBank. [REQUIRED]")
	req.add_option("-m", "--names_fp", action="store", type="string", help="The names.dmp file from GenBank. [REQUIRED]")

	parser.add_option_group(req)
	
	(options, args) = parser.parse_args()
	
	# check for required flags:
	# first dynamically build up required flags
	if parser.option_groups:
		required = []
		for group in parser.option_groups:
			for item in group.option_list:
				if "[REQUIRED]" in item.help:
					required.append(item.dest)
		# print out missing options
		missing = []
		for ro in required:
			if getattr(options, ro) == None:
				missing.append(ro)
		missing_str = ', '.join(['--'+mi for mi in missing])		
		if missing != []:
			parser.error('Required option(s) missing: \'%s\'.' % missing_str)
	else:
		print"No required options found. Are you sure this is correct?"


	# parse ncbi taxonomy files
	nodes = options.nodes_fp
	names = options.names_fp
	print "Building NCBI Taxonomy Tree from %s and %s ..." % (nodes, names)
	tt = make_ncbi_taxonomy_tree(nodes, names)

	# get lists and sanity check
	l = options.rank_levels.split(',')
	r = options.ranks.split(',')
	
	# make taxid-to-lineage search function
	print "Building lineage parser..."
	# need to simply pass these in as a function choise:
        get_lineage_func = make_lineage_builder(tt, r)
	#get_lineage_func = make_lineage_builder(tt, r, gi2tax_dict)

	# set input / output file handles
	fasta_recs = open(options.input_fp, 'U')
	fasta_out = open(options.output_fp, 'w')

	# parse genbank data
	print "Processing GenBank FASTA records..."
	parse_gb_data(fasta_recs, fasta_out, get_lineage_func, l)

	fasta_recs.close()
	fasta_out.close()

	# notify processing is complete
	print "Processing complete!"



if __name__ == '__main__':
	main()
