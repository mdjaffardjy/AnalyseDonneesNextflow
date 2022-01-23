from process import *
from functionsProcess.helpPrint import *
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
process INTERPROSCAN {
    tag "$meta.id"
    label 'process_medium'
    publishDir "${params.outdir}",
        mode: params.publish_dir_mode,
        saveAs: { filename -> saveFiles(filename:filename, options:params.options, publish_dir:getSoftwareName(task.process), meta:meta, publish_by_meta:['id']) }

    
    container "annotater/interproscan:5.36-0.9"

    input:
    tuple val(meta), path(fasta)

    output:
    tuple val(meta), path("*.{tsv,xml,gff,json,html,svg}"), emit: outfiles
    path "versions.yml"           , emit: version

    script:
    def software = getSoftwareName(task.process)
    def prefix   = options.suffix ? "${meta.id}${options.suffix}" : "${meta.id}_interpro"
    """
    /usr/local/interproscan/interproscan.sh \\
          --input $fasta \\
          --cpu $task.cpus \\
          --output-file-base ${prefix} \\
          $options.args

    cat <<-END_VERSIONS > versions.yml
    ${getProcessName(task.process)}:
        ${getSoftwareName(task.process)}: \$(/usr/local/interproscan/interproscan.sh -version 2>&1 | head -n 1 | sed 's/^InterProScan version //')
    END_VERSIONS
    """
}
    '''

    p = Process(lines) 
    p.extractProcess()
    inputs, outputs, emit = p.extractAll()
    #print(p.get_name())
    #print(p.output.list_output)
    """print("Inputs: ", inputs)
    print("Outputs: ",outputs)
    print("Emit : ", emit)"""
    """print("Script : ", p.script.script_string)
    print(p.script.language)
    print("")
    print("TOOLS : ", p.script.tools)
    dico = p.script.getAnnotations()
    #print("ANNOTATIONS in bio.tools : ", dico.keys())
    print("ANNOTATIONS in bio.tools : ", dico)"""
    #printInformations(p)
    print(p.printDirectives())
    print(p.numberDirectives())
    #printNameInWorkflow(p)
    #printLanguage(p)
    #printQualifier(p)
    #f.close()
    #"""
    print("-----------------------------END-----------------------------")
