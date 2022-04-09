from .process import *
from .functionsProcess.helpPrint import *
import matplotlib.pyplot as plt
import os
import glob

if __name__ == "__main__":
    print("-----------------------------START-----------------------------")
    """
    #path = "/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/bddProcess"+"/**/*.txt"
    path = "/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/ReJourneedu18Novembre/nextflow-wfs/data-nf/stevekm/nextflow-demos/*.nf"
    bddProcess = glob.glob(path, recursive= True)
    print("Taille de la bdd :", len(bddProcess))
    currentPath = os.getcwd() 

    languageScript = {}
    keyword = {'directives':0, 'input':0, 'output':0, 'when':0, 'script':0, 'stub':0}
    faute = 0
    for i in range (len(bddProcess)):
        try:
            print("******************************************")
            f = open(bddProcess[i],"r")
            process = f.read()
            p = Process(process) 
            p.extractProcess()
            inputs, outputs, emit = p.extractAll()
            #print("FILE : ", bddProcess[i])
            #print(p.script)
            #print("Emit : ", emit)
            dico = p.script.getAnnotations()
            #print(dico.keys())
            #for a in dico.keys():
            #    print(dico[a])
            #print(p.script.annotations)
            #print("Inputs: ", inputs)
            #print("Outputs: ",outputs)
            #print(p.script.script_string)
            informations = p.getAll()
            for part, k in zip(informations[1:], keyword):
                if part != None:
                    keyword[k] += 1
                if k == 'script':
                    l = part.getLanguage()
                    if l in languageScript:
                        languageScript[l] +=1
                    else:
                        languageScript.update({l: 1})
            f.close()
        except:
            print("ERROR ", bddProcess[i])
            faute += 1
            None
    print("NB FAUTES :" , faute)
    os.chdir("/home/clemence/FAC/Master/M1/S1/TER/AnalyseDonneesNextflow/Analyse")
    docs = open("statParts.csv", "w")
    txt = "Database size : {}\n".format(len(bddProcess))
    docs.write(txt)
    txt = "\tPresent\tNot Present\n"
    docs.write(txt)
    #Histogram 
    for k in keyword:
        fig,ax = plt.subplots()
        val = [keyword[k], len(bddProcess)-keyword[k]]
        plt.bar(["Present", "Not Present"], val, color = ['#00429d', '#7f40a2'])
        plt.title(k)
        plt.ylabel('Number')
        name = k + ".png"
        plt.savefig(name)

        nb = keyword[k]
        nb2 = len(bddProcess)-keyword[k]
        txt = "{}\t{}\t{}\n".format(k, nb, nb2)
        docs.write(txt)
    docs.close()

    #Language
    docs = open("statLanguage.csv", "w")
    txt = "Database size : {}\n".format(len(bddProcess))
    docs.write(txt)
    x = []
    y = []
    for l in languageScript:
        fig,ax = plt.subplots()
        x.append(l)
        y.append(languageScript[l])

        txt = "{}\t{}\n".format(l, languageScript[l])
        docs.write(txt)
    docs.close()
    plt.bar(x,y)  
    plt.title("Language Script")
    plt.ylabel("Number")
    plt.savefig("languageScript.png")
    os.chdir(currentPath)

    """
    #print(os.getcwd() )
    """adress = "/home/clemence/FAC/Master/M1/TER/AnalyseDonneesNextflow/Workflows/Tuto_Nextflow/test.txt"
    f = open(adress,"r")
    lines = f.read()"""
    lines = '''
   process trimReads {
    tag "$pair_id"
    afterScript 'mv *-trimmed-pair1* `echo *-trimmed-pair1* | sed s/\\-trimmed\\-pair1/_1_filt/g`; mv *-trimmed-pair2* `echo *-trimmed-pair2* | sed s/\\-trimmed\\-pair2/_2_filt/g`'
    
    input:
    set pair_id, file(reads) from (read_files_for_trimming)

    output:
    set pair_id, file("*_filt.fastq.gz") into filtered_reads_for_assembly
    file("*_filt.fastq.gz") into filtered_read_for_QC
    file("*trimmed.log") into logTrimming_for_QC

    script: 
    def trimmer = new Trimmer(reads:reads, extrapars:"-Q ${params.meanquality} -q ${params.trimquality} -x ${params.adapter}", id:pair_id, min_read_size:params.minsize, cpus:task.cpus)
    trimmer.trimWithSkewer()
    }

    '''

    lines = '''
process runBwaAln {

    tag { sampleName + ' - BWA-aln' }

    publishDir "${params.outDir}/BWA-aln/${sampleName}_${experimentName}", mode: 'copy'

    input:
    set experimentName, 
    sampleName, 
    libraryName, 
    unitName, 
    platformName, 
    runName, 
    file(fastqCollapsed) from result_FastP
    val ref_fasta_basename from params.genome
    file ref_fasta from referenceMap.genomeFile
    file ref_idx from Channel.fromPath.collect() // Copies index files to wd


    output:
    set experimentName, 
        sampleName, 
        libraryName, 
        unitName, 
        platformName, 
        runName, 
        file("${sampleName}_${experimentName}_${libraryName}_${runName}_${ref_fasta_basename}_collapsed_bwaALN_sorted.bam"), 
        file("${sampleName}_${experimentName}_${libraryName}_${runName}_${ref_fasta_basename}_collapsed_bwaALN_sorted.bam.bai") into results_bwa

    // Loading Phoenix modules - separate with colon
    module 'BWA/0.7.15-foss-2017a:SAMtools/1.9-foss-2016b'

    script:
    """
    bwa aln \
    -t 8 \
    ${ref_fasta} \
    ${fastqCollapsed} \
    -n 0.04 \
    -l 1024 \
    -k 2 \
    -f ${sampleName}_${experimentName}_${libraryName}_${runName}.sai

    bwa samse \
    -r "@RG\tID:${runName}\tPL:${platformName}\tPU:${unitName}\tSM:${sampleName}" \
    ${ref_fasta} \
    ${sampleName}_${experimentName}_${libraryName}_${runName}.sai \
    ${fastqCollapsed} | \
    samblaster | \
    samtools sort \
        -@ ${task.cpus} \
        -O BAM  \
        -o ${sampleName}_${experimentName}_${libraryName}_${runName}_${ref_fasta_basename}_collapsed_bwaALN_sorted.bam \
        -

    samtools index \
    ${sampleName}_${experimentName}_${libraryName}_${runName}_${ref_fasta_basename}_collapsed_bwaALN_sorted.bam
"""
}
'''

    p = Process(lines) 
    p.extractProcess()
    inputs, outputs, emit = p.extractAll()
    """print(p.get_name())
    print("Inputs: ", inputs)
    print("Outputs: ",outputs)
    print("Emit : ", emit)
    print("Directives :", p.printDirectives())
    print("Script : ", p.script.script_string)
    print("Script Language : ", p.script.language)
    print("")"""
    dico = p.script.getAnnotations()
    #print("ANNOTATIONS in bio.tools : ", dico.keys())
    """printInformations(p)
    for t in dico:
        print("ANNOTATIONS in bio.tools : ", dico[t])"""
    print("Inputs: ", inputs)
    print("Outputs: ",outputs)
    print("Emit : ", emit)
    #print(p.printDirectives())
    #print(p.numberDirectives())
    #printNameInWorkflow(p)
    #printLanguage(p)
    #printQualifier(p)
    #f.close()
    #"""
    print("-----------------------------END-----------------------------")





    """
    process trimReads {
    tag "$pair_id"
    afterScript 'mv *-trimmed-pair1* `echo *-trimmed-pair1* | sed s/\\-trimmed\\-pair1/_1_filt/g`; mv *-trimmed-pair2* `echo *-trimmed-pair2* | sed s/\\-trimmed\\-pair2/_2_filt/g`'
    
    input:
    set pair_id, file(reads) from (read_files_for_trimming)

    output:
    set pair_id, file("*_filt.fastq.gz") into filtered_reads_for_assembly
    file("*_filt.fastq.gz") into filtered_read_for_QC
    file("*trimmed.log") into logTrimming_for_QC

    script: 
    def trimmer = new Trimmer(reads:reads, extrapars:"-Q ${params.meanquality} -q ${params.trimquality} -x ${params.adapter}", id:pair_id, min_read_size:params.minsize, cpus:task.cpus)
    trimmer.trimWithSkewer()
    }
    """