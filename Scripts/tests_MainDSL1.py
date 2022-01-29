from typeMainDSL1 import *
import os

#============
# SET UP
#============
current_dirct= os.getcwd()
os.chdir(__file__[:-len('tests_MainDSL1.py')])
file_name= 'temp.nf'


#======================
# Test Double Dots
#======================
test= "betastats_reportok = params.stats_beta_enable ? process_beta_report.concat( process_beta_report_CSS, process_beta_report_DESeq2, process_beta_report_rarefied ) : Channel.empty()"
with open(file_name, 'w') as f:
    f.write(test)
m= TypeMainDSL1(file_name, "")
m.initialise_basic_main()
m.clean_up_if_double_dots_question_2()
value_expected='''if (params.stats_beta_enable ) { 
betastats_reportok  =  process_beta_report.concat( process_beta_report_CSS, process_beta_report_DESeq2, process_beta_report_rarefied ) 
 } else { 
betastats_reportok  =  Channel.empty()
 } '''
assert(m.string==value_expected)


test= "SAMBAtemplate_ch = params.report_enable ? Channel.fromPath(params.SAMBAtemplate, checkIfExists:true) : Channel.empty()"
with open(file_name, 'w') as f:
    f.write(test)
m= TypeMainDSL1(file_name, "")
m.initialise_basic_main()
m.clean_up_if_double_dots_question_2()
value_expected='''if (params.report_enable ) { 
SAMBAtemplate_ch  =  Channel.fromPath(params.SAMBAtemplate, checkIfExists:true) 
 } else { 
SAMBAtemplate_ch  =  Channel.empty()
 } '''
assert(m.string==value_expected)


#======================
# TEST BRANCH
#======================
test_branch= """
    Channel
        .from(1,2,3,40,50)
        .branch {
            small: it < 10
            large: it > 10
        }
        .set { result }
"""
with open(file_name, 'w') as f:
    f.write(test_branch)
m= TypeMainDSL1(file_name, "")
m.initialise()
assert(m.get_added_operators()==['small', 'large'])



#======================
# TEST MULTIMAP
#======================
test_branch= """
    Channel
        .from(1,2,3,4)
        .multiMap { it ->
            foo: it + 1
            bar: it * it
            }
        .set { result }
"""
with open(file_name, 'w') as f:
    f.write(test_branch)
m= TypeMainDSL1(file_name, "")
m.initialise()
assert(m.get_added_operators()==['foo', 'bar'])


#======================
# TEST CHANNELS
#======================

test= '''
Channel.empty()
Channel.empty()

newick_ch = Channel.fromPath(params.innewick, checkIfExists:true)
                   .set { newick_only }

ch_branched_input = ch_input_sample_downstream.branch{
    fastq: it[8] != 'NA' //These are all fastqs
    bam: it[10] != 'NA' //These are all BAMs
}



ch_fastq_channel = ch_branched_input.fastq.map {
  samplename, libraryid, lane, colour, seqtype, organism, strandedness, udg, r1, r2, bam ->
    [samplename, libraryid, lane, colour, seqtype, organism, strandedness, udg, r1, r2]
}


a = Channel
    .from(1,2,3,40,50)
    .branch {
        small: it < 10
        large: it < 50
        other: true
    }

inasv_table_ch = Channel.fromPath(params.inasv_table, checkIfExists:true)
                        .set { tsv_only }

Channel.small
    .set(poo)


ezrz.other.set{yo}

p.small.set{yo}

inasv_table_ch = Channel.empty()
newick_ch = Channel.empty()

dada2merge_repseqsdir_ch = Channel.fromPath(params.merge_repseqsdir, checkIfExists:true)


Channel.from(summary.collect{ [it.key, it.value] })
    .map { k,v -> "<dt>$k</dt><dd><samp>${v ?: '<span style=\"color:#999999;\">N/A</a>'}</samp></dd>" }
    .reduce { a, b -> return [a, b].join("\n            ") }
    .map { x -> """
    id: 'samba-summary'
    description: " - this information is collected when the pipeline is started."
    section_name: 'samba Workflow Summary'
    section_href: 'https://github.com/ifremer-bioinformatics/samba'
    plot_type: 'html'
    data: |
        <dl class=\"dl-horizontal\">
            $x
        </dl>
    """.stripIndent() }
    .set { ch_workflow_summary }




testmetadata.set { metadata4stats } 

testmanifest.into { manifest ; manifest4integrity }
testmetadata.into { metadata4dada2 ; metadata4dbotu3 ; metadata_filtering_tax ; metadata4stats ; metadata4integrity ; metadata4picrust2 ; metadata4ancom }

data_ready = Channel.value("none")
data_ready.into { ready_integrity ; ready_import ; ready_lr}

Channel.fromPath(params.input_manifest, checkIfExists:true)
       .into { manifest ; manifest4integrity }

Channel.empty().into { manifest ; manifest4integrity }

metadata_sort.into { metadata4dada2 ; metadata4dbotu3 ; metadata4stats ; metadata4picrust2 ; metadata4ancom }
manifest_sort.set { manifest }

Channel.fromPath(params.input_metadata, checkIfExists:true)
       .set { metadata_merge_ch }

longreadsmanifest = testmanifest.splitCsv(header: true, sep:'\t')
                                    .map { row -> tuple( row."sample-id", 
                                    file(row."absolute-filepath")) }
longreadstofasta = testmanifest.splitCsv(header: true, sep:'\t')
                                    .map { row -> file(row."absolute-filepath") }

lr_sequences.collectFile(name : 'lr_sequences.fasta', newLine : false, storeDir : "${params.outdir}/${params.lr_mapping_dirname}")
               .subscribe {       println "Fasta sequences are saved to file : $it"       }



Channel
  .from(params.beta_div_var)
  .splitCsv(sep : ',', strip : true)
  .flatten()
  .into { beta_var_nn ; beta_var_rare ; beta_var_deseq ; beta_var_css }

Channel
     .from(params.picrust_var)
     .splitCsv(sep : ',', strip : true)
     .flatten()
     .set { var_picrust2 }

reference_genome = file(params.fasta, checkIfExists: true)
'''

excepted= '''CHANNEL_1 string : Channel.empty()\nCHANNEL_1 origin : []\nCHANNEL_1 gives  : []\n\n\nCHANNEL_2 string : Channel.empty()\nCHANNEL_2 origin : []\nCHANNEL_2 gives  : []\n\n\nCHANNEL_3 string : newick_ch = Channel.fromPath(params.innewick, checkIfExists:true)\n                   .set { newick_only }\nCHANNEL_3 origin : [[\'params.innewick, checkIfExists:true\', \'A\']]\nCHANNEL_3 gives  : [[\'newick_ch\', \'P\'], [\'newick_only\', \'P\']]\n\n\nCHANNEL_4 string : a = Channel\n    .from(1,2,3,40,50)\n    .branch {\n        small: it < 10\n        large: it < 50\n        other: true\n    }\nCHANNEL_4 origin : [[\'1,2,3,40,50\', \'V\']]\nCHANNEL_4 gives  : [[\'a\', \'P\']]\n\n\nCHANNEL_5 string : inasv_table_ch = Channel.fromPath(params.inasv_table, checkIfExists:true)\n                        .set { tsv_only }\nCHANNEL_5 origin : [[\'params.inasv_table, checkIfExists:true\', \'A\']]\nCHANNEL_5 gives  : [[\'inasv_table_ch\', \'P\'], [\'tsv_only\', \'P\']]\n\n\nCHANNEL_6 string : Channel.small().set(poo)\nCHANNEL_6 origin : []\nCHANNEL_6 gives  : []\n\n\nCHANNEL_7 string : inasv_table_ch = Channel.empty()\nCHANNEL_7 origin : []\nCHANNEL_7 gives  : [[\'inasv_table_ch\', \'P\']]\n\n\nCHANNEL_8 string : newick_ch = Channel.empty()\nCHANNEL_8 origin : []\nCHANNEL_8 gives  : [[\'newick_ch\', \'P\']]\n\n\nCHANNEL_9 string : dada2merge_repseqsdir_ch = Channel.fromPath(params.merge_repseqsdir, checkIfExists:true)\nCHANNEL_9 origin : [[\'params.merge_repseqsdir, checkIfExists:true\', \'A\']]\nCHANNEL_9 gives  : [[\'dada2merge_repseqsdir_ch\', \'P\']]\n\n\nCHANNEL_10 string : Channel.from(summary.collect{ [it.key, it.value] })\n    .map { k,v -> "<dt>$k</dt><dd><samp>${v ?: \'<span style="color:#999999;">N/A</a>\'}</samp></dd>" }\n    .reduce { a, b -> return [a, b].join("\n            ") }\n    .map { x -> """\n    id: \'samba-summary\'\n    description: " - this information is collected when the pipeline is started."\n    section_name: \'samba Workflow Summary\'\n    section_href: \'https://github.com/ifremer-bioinformatics/samba\'\n    plot_type: \'html\'\n    data: |\n        <dl class="dl-horizontal">\n            $x\n        </dl>\n    """.stripIndent() }\n    .set { ch_workflow_summary }\nCHANNEL_10 origin : [[\'summary.collect{ [it.key, it.value] }\', \'V\']]\nCHANNEL_10 gives  : [[\'ch_workflow_summary\', \'P\']]\n\n\nCHANNEL_11 string : data_ready = Channel.value("none")\nCHANNEL_11 origin : [[\'"none"\', \'V\']]\nCHANNEL_11 gives  : [[\'data_ready\', \'P\']]\n\n\nCHANNEL_12 string : Channel.fromPath(params.input_manifest, checkIfExists:true)\n       .into { manifest ; manifest4integrity }\nCHANNEL_12 origin : [[\'params.input_manifest, checkIfExists:true\', \'A\']]\nCHANNEL_12 gives  : [[\'manifest\', \'P\'], [\'manifest4integrity\', \'P\']]\n\n\nCHANNEL_13 string : Channel.empty().into { manifest ; manifest4integrity }\nCHANNEL_13 origin : []\nCHANNEL_13 gives  : [[\'manifest\', \'P\'], [\'manifest4integrity\', \'P\']]\n\n\nCHANNEL_14 string : Channel.fromPath(params.input_metadata, checkIfExists:true)\n       .set { metadata_merge_ch }\nCHANNEL_14 origin : [[\'params.input_metadata, checkIfExists:true\', \'A\']]\nCHANNEL_14 gives  : [[\'metadata_merge_ch\', \'P\']]\n\n\nCHANNEL_15 string : Channel\n  .from(params.beta_div_var)\n  .splitCsv(sep : \',\', strip : true)\n  .flatten()\n  .into { beta_var_nn ; beta_var_rare ; beta_var_deseq ; beta_var_css }\nCHANNEL_15 origin : [[\'params.beta_div_var\', \'V\']]\nCHANNEL_15 gives  : [[\'beta_var_nn\', \'P\'], [\'beta_var_rare\', \'P\'], [\'beta_var_deseq\', \'P\'], [\'beta_var_css\', \'P\']]\n\n\nCHANNEL_16 string : Channel\n     .from(params.picrust_var)\n     .splitCsv(sep : \',\', strip : true)\n     .flatten()\n     .set { var_picrust2 }\nCHANNEL_16 origin : [[\'params.picrust_var\', \'V\']]\nCHANNEL_16 gives  : [[\'var_picrust2\', \'P\']]\n\n\nCHANNEL_17 string : ch_branched_input = ch_input_sample_downstream.branch{\n    fastq: it[8] != \'NA\'                       \n    bam: it[10] != \'NA\'                     \n}\nCHANNEL_17 origin : [[\'ch_input_sample_downstream\', \'P\']]\nCHANNEL_17 gives  : [[\'ch_branched_input\', \'P\']]\n\n\nCHANNEL_18 string : ch_fastq_channel = ch_branched_input.fastq().map {\n  samplename, libraryid, lane, colour, seqtype, organism, strandedness, udg, r1, r2, bam ->\n    [samplename, libraryid, lane, colour, seqtype, organism, strandedness, udg, r1, r2]\n}\nCHANNEL_18 origin : [[\'ch_branched_input\', \'P\']]\nCHANNEL_18 gives  : [[\'ch_fastq_channel\', \'P\']]\n\n\nCHANNEL_19 string : ezrz.other().set{yo}\nCHANNEL_19 origin : [[\'ezrz\', \'P\']]\nCHANNEL_19 gives  : [[\'yo\', \'P\']]\n\n\nCHANNEL_20 string : p.small().set{yo}\nCHANNEL_20 origin : [[\'p\', \'P\']]\nCHANNEL_20 gives  : [[\'yo\', \'P\']]\n\n\nCHANNEL_21 string : testmetadata.set { metadata4stats }\nCHANNEL_21 origin : [[\'testmetadata\', \'P\']]\nCHANNEL_21 gives  : [[\'metadata4stats\', \'P\']]\n\n\nCHANNEL_22 string : testmanifest.into { manifest ; manifest4integrity }\nCHANNEL_22 origin : [[\'testmanifest\', \'P\']]\nCHANNEL_22 gives  : [[\'manifest\', \'P\'], [\'manifest4integrity\', \'P\']]\n\n\nCHANNEL_23 string : testmetadata.into { metadata4dada2 ; metadata4dbotu3 ; metadata_filtering_tax ; metadata4stats ; metadata4integrity ; metadata4picrust2 ; metadata4ancom }\nCHANNEL_23 origin : [[\'testmetadata\', \'P\']]\nCHANNEL_23 gives  : [[\'metadata4dada2\', \'P\'], [\'metadata4dbotu3\', \'P\'], [\'metadata_filtering_tax\', \'P\'], [\'metadata4stats\', \'P\'], [\'metadata4integrity\', \'P\'], [\'metadata4picrust2\', \'P\'], [\'metadata4ancom\', \'P\']]\n\n\nCHANNEL_24 string : data_ready.into { ready_integrity ; ready_import ; ready_lr}\nCHANNEL_24 origin : [[\'data_ready\', \'P\']]\nCHANNEL_24 gives  : [[\'ready_integrity\', \'P\'], [\'ready_import\', \'P\'], [\'ready_lr\', \'P\']]\n\n\nCHANNEL_25 string : metadata_sort.into { metadata4dada2 ; metadata4dbotu3 ; metadata4stats ; metadata4picrust2 ; metadata4ancom }\nCHANNEL_25 origin : [[\'metadata_sort\', \'P\']]\nCHANNEL_25 gives  : [[\'metadata4dada2\', \'P\'], [\'metadata4dbotu3\', \'P\'], [\'metadata4stats\', \'P\'], [\'metadata4picrust2\', \'P\'], [\'metadata4ancom\', \'P\']]\n\n\nCHANNEL_26 string : manifest_sort.set { manifest }\nCHANNEL_26 origin : [[\'manifest_sort\', \'P\']]\nCHANNEL_26 gives  : [[\'manifest\', \'P\']]\n\n\nCHANNEL_27 string : longreadsmanifest = testmanifest.splitCsv(header: true, sep:\'\t\')\n                                    .map { row -> tuple( row."sample-id", \n                                    file(row."absolute-filepath")) }\nCHANNEL_27 origin : [[\'testmanifest\', \'P\']]\nCHANNEL_27 gives  : [[\'longreadsmanifest\', \'P\']]\n\n\nCHANNEL_28 string : longreadstofasta = testmanifest.splitCsv(header: true, sep:\'\t\')\n                                    .map { row -> file(row."absolute-filepath") }\nCHANNEL_28 origin : [[\'testmanifest\', \'P\']]\nCHANNEL_28 gives  : [[\'longreadstofasta\', \'P\']]\n\n\nCHANNEL_29 string : lr_sequences.collectFile(name : \'lr_sequences.fasta\', newLine : false, storeDir : "${params.outdir}/${params.lr_mapping_dirname}")\n               .subscribe {       println "Fasta sequences are saved to file : $it"       }\nCHANNEL_29 origin : [[\'lr_sequences\', \'P\']]\nCHANNEL_29 gives  : []\n\n\n'''

with open(file_name, 'w') as f:
    f.write(test)
m= TypeMainDSL1(file_name, "")
m.initialise()
assert(excepted==m.get_channels_formated())
#print(m.get_channels_formated())




#==================================
# SETTING BACK ORIGINAL PARAMETERS
#==================================
os.remove(file_name)
os.chdir(current_dirct)