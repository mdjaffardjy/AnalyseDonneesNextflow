from os import path
from rdflib import ConjunctiveGraph
from rdflib.namespace import Namespace, RDF, RDFS
import jellyfish

import glob
import os

from threading import Thread
from queue import Queue
import time
import sys

import functools

printf = functools.partial(print, end="")

current_adress = os.getcwd()
os.chdir(".")
root = os.getcwd()
bioschemas_dump = glob.glob( "**/data/bioschemas-dump.ttl", recursive = True)
EDAM = glob.glob( "**/data/EDAM_1.25.owl", recursive = True)
os.chdir(current_adress)

bioschemas_dump = root+'/'+bioschemas_dump[0]
EDAM = root+'/'+EDAM[0]


#setting the namespaces as constants
sc = Namespace('http://schema.org/')
edam = Namespace('http://edamontology.org/')
oboInOwl = Namespace('http://www.geneontology.org/formats/oboInOwl#')

#loading the edam data
kg = ConjunctiveGraph()

def thread1(threadname, q):
    i=0
    a = q.get()
    while True:
        a = q.get()
        if a is None: 
            sys.stdout.flush()
            sys.stdout.write("\r{0}".format("Loading Biotools and EDAM libraries. Status : COMPLETED \n"))
            return # Poison pill
        q.put(True)
        if(int(i)%2==0):
            sys.stdout.write("\r{0}".format("Loading Biotools and EDAM libraries. Status : Working   "))
        if(int(i)%4==1):
            sys.stdout.write("\r{0}".format("Loading Biotools and EDAM libraries. Status : Working.  "))
        if(int(i)%4==2):
            sys.stdout.write("\r{0}".format("Loading Biotools and EDAM libraries. Status : Working.. "))
        if(int(i)%4==3):
            sys.stdout.write("\r{0}".format("Loading Biotools and EDAM libraries. Status : Working..."))
        sys.stdout.flush()
        time.sleep(0.3)
        i+=1
    



def thread2(threadname, q):
    a = 0
    q.put(True)
    q.put(True)
    kg.load(bioschemas_dump, format="turtle")
    kg.load(EDAM)
    #kg.load('http://edamontology.org/EDAM_dev.owl')
    q.put(None) # Poison pill

queue = Queue()
thread1 = Thread( target=thread1, args=("Thread-1", queue) )
thread2 = Thread( target=thread2, args=("Thread-2", queue) )

thread1.start()
thread2.start()
thread1.join()
thread2.join()


def get_sorted_matches(toolname):
    #input : string tool name
    #output : a list of matches in the dump with their distance if the toolname is contained in the target name : tuples of the uri, and the distance and name
    matching_tools = {}
    tool_name = toolname[0]
    for s, p, target_name in kg.triples((None, sc.name, None)):
        if tool_name.lower() in target_name.lower():
            dist = jellyfish.levenshtein_distance(tool_name.lower(), target_name.lower())
            # print(tool_name.lower(),target_name.lower(),dist)
            matching_tools[s] = {'dist': dist, 'name': str(target_name)}

    sorted_matchs = sorted(matching_tools.items(), key=lambda x: x[1]['dist'])
    return sorted_matchs

def get_sorted_matches_tuple(toolname):
    #input : tuple string tool name
    #output : a list of matches in the dump with their distance if the toolname is contained in the target name : tuples of the uri, and the distance and name
    tool_name = toolname[0]+" "+toolname[1]
    matching_tools = {}
    #try with two keywords
    for s, p, target_name in kg.triples((None, sc.name, None)):
        if tool_name.lower() in target_name.lower():
            dist = jellyfish.levenshtein_distance(tool_name.lower(), target_name.lower())
            # print(tool_name.lower(),target_name.lower(),dist)
            matching_tools[s] = {'dist': dist, 'name': str(target_name)}
    #try with one keyword
    for s, p, target_name in kg.triples((None, sc.name, None)):
        if toolname[0].lower() in target_name.lower():
            dist = jellyfish.levenshtein_distance(toolname[0].lower(), target_name.lower())
            # print(tool_name.lower(),target_name.lower(),dist)
            matching_tools[s] = {'dist': dist, 'name': str(target_name)}

    #we then sort the whole list in order to get the best result//with one or two keywords
    sorted_matchs = sorted(matching_tools.items(), key=lambda x: x[1]['dist'])
    return sorted_matchs


def extract_match_info(sorted_matchs, treshold = 5):
    # TODO : mettre en option l'enrichissement via les synonimes pour voir si c'est utile ou pas
    #input : a list of matches for a given toolname in the dump : tuples comprised of URI, {distance, name}
    #output : a list of dict for the matches of the following structure :
    # {toolnames, biotools ID, URI, topic[{term, uri}], function[operation [{term, uri}] input[{data: {'term',uri} format:[{'term',uri}]], output:[{data: {'term',uri} format:[{'term',uri}]]}]}

    liste_dict_tools=[]
    distance = []

    for tool in sorted_matchs:
        # Threshold for syntactic distance
        if tool[1]['dist'] > treshold:
            break
        distance.append(tool[1]['dist'])
        #initializing the variables for the different var
        topics = []
        topics_syn = []
        operations = []
        operations_syn = []
        inputs = []
        outputs = []
        dict_tools = {'name': tool[1]['name']}
        dict_tools.update({'uri': str(tool[0])})
        #TODO : get biotools ID
        #dict_tools.update({'biotoolsID': TRUC})

        # we search for topics in bio.tools knowledge graph
        for s, p, o in kg.triples((tool[0], sc.applicationSubCategory, None)):
            # we search for topic labels in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, RDFS.label, None)):
                topics.append({'uri': str(s2), 'term': str(o2)})
            # we search for topic synonyms in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, oboInOwl.hasExactSynonym, None)):
                topics_syn.append({'uri': str(s2), 'term': str(o2)})

        dict_tools.update({'topic': [topics, topics_syn]})

        #REFAIRE UNE FONCTION POUR TROUVER ÇA ?
        # we search for operation labels in the EDAM ontology
        for s, p, o in kg.triples((tool[0], sc.featureList, None)):
            # we search for operation labels in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, RDFS.label, None)):
                operations.append({'uri': str(s2), 'term': str(o2)})
            # we search for operation synonyms in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, oboInOwl.hasExactSynonym, None)):
                operations_syn.append({'uri': str(s2), 'term': str(o2)})

        #TODO : look up a way to find inputs and outputs -- for now we are ignoring them
                # we search for inputs
        for s, p, o in kg.triples((tool[0], edam.has_input, None)):
            # we search for labels in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, RDFS.label, None)):
                inputs.append({'uri': str(s2), 'term': str(o2)})

        for s, p, o in kg.triples((tool[0], edam.has_output, None)):
            # we search for labels in the EDAM ontology
            for s2, p2, o2 in kg.triples((o, RDFS.label, None)):
                outputs.append({'uri': str(s2), 'term': str(o2)})

        # we save the synonyms separately from the original annotations [original, synonyms]
        function = {'operation': [operations,operations_syn], 'input' : inputs, 'output' : outputs}
        dict_tools.update({'function':[function]})

        liste_dict_tools.append(dict_tools)

        return liste_dict_tools



def get_annotations_tool_dump(toolname, treshold = 5):
    #input : toolnames : either a tuple of 2 keywords (strings), either just one word (string)
    #output : a dictionnary of the best matching tool annotations

    if len(toolname) == 1 : #if we have a toolname
        sorted_matches = get_sorted_matches(toolname)
    else : #if we have a tuple
        sorted_matches = get_sorted_matches_tuple(toolname)
    if (extract_match_info(sorted_matches, treshold) == None):
        return None
    if (len(extract_match_info(sorted_matches, treshold)) == 0):
        return None
    else:
        return extract_match_info(sorted_matches, treshold)[0]  # only return the best match