# PROSIM
# Written by Clémence Sebe and George Marchment
# October 2021 - April 2022

import argparse
from pathlib import Path
import os
import glob2


import json
import pandas as pd
import math
from collections import defaultdict

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
 
print('''
  ____  ____   ___  ____ ___ __  __ 
 |  _ \|  _ \ / _ \/ ___|_ _|  \/  |
 | |_) | |_) | | | \___ \| || |\/| |
 |  __/|  _ <| |_| |___) | || |  | |
 |_|   |_| \_|\___/|____/___|_|  |_|
                                    
''')

print("""________________________________________________

Developped by Clemence Sebe and George Marchment
________________________________________________\n""")


#Definition des fonctions auxiliaires
#==================================================================
#Fonction qui retourne les éléments d'intersection entre 2 ensembles
def intersection(l1, l2):
    return list(set(l1) & set(l2))

#Fonction qui retourne les éléments d'union entre 2 ensembles
def union(l1, l2):
    return list(set(l1 + l2))
#https://stackoverflow.com/questions/29348345/declaring-a-multi-dimensional-dictionary-in-python
def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n-1, type))
#==================================================================


#Definition des fonctions de mesure de similarité entre 2 ensembles
#==================================================================
#Indice de Jaccard
def jaccard(t1, t2):
    num = len(intersection(t1, t2))
    if(num==0):
        return 0
    denum= len(union(t1, t2))
    return num/denum

#Indice de Sørensen-Dice
def soresen(t1, t2):
    num = 2*len(intersection(t1, t2))
    if(num==0):
        return 0
    denum= len(t1) + len(t2)
    return num/denum

#Overlap coefficient
def overlap(t1, t2):
    num = len(intersection(t1, t2))
    if(num==0):
        return 0
    denum= min(len(t1), len(t2))
    return num/denum
#==================================================================


#Definition des fonctions de mesure de similarité entre 2 textes
#==================================================================
#Similarité cosinus
#Fonction inspiré par https://studymachinelearning.com/cosine-similarity-text-similarity-metric/
def similarite_cosinus(doc_1, doc_2):
    data = [doc_1.lower(), doc_2.lower()]
    count_vectorizer = CountVectorizer()
    vector_matrix = count_vectorizer.fit_transform(data)

    tokens = count_vectorizer.get_feature_names_out()
    vector_matrix.toarray()

    def create_dataframe(matrix, tokens):

        doc_names = [f'doc_{i+1}' for i, _ in enumerate(matrix)]
        df = pd.DataFrame(data=matrix, index=doc_names, columns=tokens)
        return(df)

    create_dataframe(vector_matrix.toarray(),tokens)

    cosine_similarity_matrix = cosine_similarity(vector_matrix)

    Tfidf_vect = TfidfVectorizer()
    vector_matrix = Tfidf_vect.fit_transform(data)

    tokens = Tfidf_vect.get_feature_names_out()
    create_dataframe(vector_matrix.toarray(),tokens)

    cosine_similarity_matrix = cosine_similarity(vector_matrix)
    return create_dataframe(cosine_similarity_matrix,['doc_1','doc_2'])['doc_1']['doc_2']

#Indice de Jaccard
def jaccard_texts(s1, s2):
    s1 , s2= s1.lower().split(), s2.lower().split()
    num = len(intersection(s1, s2))
    if(num==0):
        return 0
    denum= len(union(s1, s2))
    return num/denum
#==================================================================


#LES HYPOTHÈSES
#==================================================================
#Hypothèse 1.1 : Identité entre les processes
def H_1_1(p1, p2):
    return p1["string_process"].lower() == p2["string_process"].lower()

#Hypothèse 1.2 : Identité entre les scripts
def H_1_2(p1, p2):
    return p1["string_script"].lower() == p2["string_script"].lower()

#Hypothèse 2.1 : Similarité entre le code des processes
def H_2_1(p1, p2, similarity):
    return similarity(p1["string_process"], p2["string_process"])

#Hypothèse 2.2 : Similarité entre les scripts des processes
def H_2_2(p1, p2, similarity):
    return similarity(p1["string_script"], p2["string_script"])

#Hypothèse 2.3 : Similarité entre les noms des processes
def H_2_3(p1, p2, similarity):
    return similarity(p1['name_process'], p2['name_process'])

#Hypothèse 3 : Identité des outils bio.tools
def H_3(p1, p2):
    return p1['tools'] == p2['tools']

#Hypothèse 4.1 : Similarité entre les outils bio.tools
def H_4_1(p1, p2, similarity):
    return similarity(p1['tools'], p2['tools'])

#Hypothèse 4.2 : Similarité entre les outils bio.tools + Nombre de lignes des scripts
def H_4_2(p1, p2, similarity):
    def score_length_script(p1, p2):
        num = abs(p1['nb_lignes_script'] - p2['nb_lignes_script'])
        denum = max(max(p1['nb_lignes_script'], p2['nb_lignes_script']), 1)
        return 1 - num/denum
    if(similarity(p1['tools'], p2['tools'])!=0):
        return (similarity(p1['tools'], p2['tools']) + score_length_script(p1, p2))/2
    return 0

#Hypothèse 5.1 : Similarité entre nb d'inputs
def H_5_1(p1, p2):
    num = abs(p1['nb_inputs'] - p2['nb_inputs'])
    denum = max(max(p1['nb_inputs'], p2['nb_inputs']), 1)
    return 1 - num/denum

#Hypothèse 5.2 : Similarité entre nb d'output
def H_5_2(p1, p2):
    num = abs(p1['nb_outputs'] - p2['nb_outputs'])
    denum = max(max(p1['nb_outputs'], p2['nb_outputs']), 1)
    return 1 - num/denum

#Mesure euclidienne
def mesure_eclidienne(p1, p2):
    similarity_text = jaccard_texts
    similarity_set = jaccard
    h_2_1 = True
    h_2_2 = True
    h_2_3 = False
    h_4_1 = True
    h_4_2 = True
    h_5_1 = False
    h_5_2 = False

    num = 0
    num += h_2_1 * (1 - H_2_1(p1, p2, similarity_text))**2
    num += h_2_2 * (1 - H_2_2(p1, p2, similarity_text))**2
    num += h_2_3 * (1 - H_2_3(p1, p2, similarity_text))**2
    
    num+= h_4_1 * (1 - H_4_1(p1, p2, similarity_set))**2
    num+= h_4_2 * (1 - H_4_2(p1, p2, similarity_set))**2

    num+= h_5_1 *(1 - H_5_1(p1, p2))**2
    num+= h_5_2 *(1 - H_5_2(p1, p2))**2

    denum = math.sqrt(h_2_1+h_2_2+h_2_3+h_4_1+h_4_2+h_5_1+h_5_2)

    return 1 - (math.sqrt(num)/denum) 
#==================================================================


#Jaccard est la fonction de comparaison par default
def main():
    #Get current directory
    current_directory = os.getcwd()
    
    parser = argparse.ArgumentParser()
    #Obligatory
    #parser.add_argument('results_directory')
    #Facultative
    parser.add_argument('--processA', default='')
    parser.add_argument('--processB', default='')
    parser.add_argument('--mode', default='single') #single mode is the default
    parser.add_argument('--results_directory', default='')
    parser.add_argument('--processes', default='')

    args = parser.parse_args() 
    
    if(args.results_directory == ''):
        args.results_directory= current_directory

    os.chdir(args.results_directory)
    os.system(f"mkdir -p Results_Similarity")
    os.chdir(args.results_directory+'/Results_Similarity')
    #=========
    # SINGLE
    #=========
    if(args.mode == "single"):
        print('')
        print('\x1b[1;37;42m' + 'Single mode was selected' + '\x1b[0m')
        print('')

        dict_H_1_1 = nested_dict(2, float)
        dict_H_1_2 = nested_dict(2, float)
        dict_H_2_1 = nested_dict(2, float)
        dict_H_2_2 = nested_dict(2, float)
        dict_H_2_3 = nested_dict(2, float)
        dict_H_3 = nested_dict(2, float)
        dict_H_4_1 = nested_dict(2, float)
        dict_H_4_2 = nested_dict(2, float)
        dict_H_5_1 = nested_dict(2, float)
        dict_H_5_2 = nested_dict(2, float)
        dict_eclidienne = nested_dict(2, float)


        if Path(args.processA).is_file():
            if Path(args.processB).is_file():
               
                processes1= {}
                with open(args.processA) as json_file:
                    processes1 = json.load(json_file)

                processes2 = {}
                with open(args.processB) as json_file:
                    processes2 = json.load(json_file)

                for A in processes1 :
                    for B in processes2 :
                        proA = processes1[A]
                        proB = processes2[B]
                        workflow1 = proA['name_workflow']
                        workflow2 = proB['name_workflow']
                        nameA = f'{workflow1}:{A}'
                        nameB = f'{workflow2}:{B}'
                        print(f'Comparing {nameA} and {nameB}')
                        #print(f"Identity between processes : {H_1_1(proA, proB)}")
                        dict_H_1_1[nameA][nameB] = H_1_1(proA, proB)
                        #print(f"Identity between scripts : {H_1_2(proA, proB)}")
                        dict_H_1_2[nameA][nameB] = H_1_2(proA, proB)
                        #print(f"Similarity between the process code : {H_2_1(proA, proB, jaccard_texts)}")
                        dict_H_2_1[nameA][nameB] = H_2_1(proA, proB, jaccard_texts)
                        #print(f"Similarity between process scripts : {H_2_2(proA, proB, jaccard_texts)}")
                        dict_H_2_2[nameA][nameB] = H_2_2(proA, proB, jaccard_texts)
                        #print(f"Similarity between process names : {H_2_3(proA, proB, jaccard_texts)}")
                        dict_H_2_3[nameA][nameB] = H_2_3(proA, proB, jaccard_texts)
                        #print(f"Identity of bio.tools : {H_3(proA, proB)}")
                        dict_H_3[nameA][nameB] = H_3(proA, proB)
                        #print(f"Similarity between bio.tools : {H_4_1(proA, proB, jaccard)}")
                        dict_H_4_1[nameA][nameB] = H_4_1(proA, proB, jaccard)
                        #print(f"Similarity between bio.tools + Number of lines in the scripts : {H_4_2(proA, proB, jaccard)}")
                        dict_H_4_2[nameA][nameB] = H_4_2(proA, proB, jaccard)
                        #print(f"Similarity between number of inputs : {H_5_1(proA, proB)}")
                        dict_H_5_1[nameA][nameB] = H_5_1(proA, proB)
                        #print(f"Similarity between number of outputs : {H_5_2(proA, proB)}")
                        dict_H_5_2[nameA][nameB] = H_5_2(proA, proB)
                        #print(f"Eclidean measure : {mesure_eclidienne(proA, proB)}")
                        dict_eclidienne[nameA][nameB] = mesure_eclidienne(proA, proB)
                        #print('\n')

                df_H_1_1= pd.DataFrame.from_dict(dict_H_1_1)
                df_H_1_2= pd.DataFrame.from_dict(dict_H_1_2)
                df_H_2_1= pd.DataFrame.from_dict(dict_H_2_1)
                df_H_2_2= pd.DataFrame.from_dict(dict_H_2_2)
                df_H_2_3= pd.DataFrame.from_dict(dict_H_2_3)
                df_H_3= pd.DataFrame.from_dict(dict_H_3)
                df_H_4_1= pd.DataFrame.from_dict(dict_H_4_1)
                df_H_4_2= pd.DataFrame.from_dict(dict_H_4_2)
                df_H_5_1= pd.DataFrame.from_dict(dict_H_5_1)
                df_H_5_2= pd.DataFrame.from_dict(dict_H_5_2)
                df_eclidienne= pd.DataFrame.from_dict(dict_eclidienne)
                #print(df_eclidienne)
                
                df_H_1_1.to_csv("H_1_1.csv")
                df_H_1_2.to_csv("H_1_2.csv")
                df_H_2_1.to_csv("H_2_1.csv")
                df_H_2_2.to_csv("H_2_2.csv")
                df_H_2_3.to_csv("H_2_3.csv")
                df_H_3.to_csv("H_3.csv")
                df_H_4_1.to_csv("H_4_1.csv")
                df_H_4_2.to_csv("H_4_2.csv")
                df_H_5_1.to_csv("H_5_1.csv")
                df_H_5_2.to_csv("H_5_2.csv")
                df_eclidienne.to_csv("euclidienne.csv")
                             
            else:
                raise Exception('\x1b[1;37;41m' + f'The address given for "processB" is not a file or does not exist!!'+ '\x1b[0m')
        else:
            raise Exception('\x1b[1;37;41m' + f'The address given for "processA" is not a file or does not exist!!'+ '\x1b[0m')

    #=========
    # MULTI
    #=========
    elif(args.mode == 'multi'):
        print('')
        print('\x1b[7;33;40m' + 'Multiple mode was selected' + '\x1b[0m')
        print('')
        if(args.processes != ''):
            
            dict_H_1_1 = nested_dict(2, float)
            dict_H_1_2 = nested_dict(2, float)
            dict_H_2_1 = nested_dict(2, float)
            dict_H_2_2 = nested_dict(2, float)
            dict_H_2_3 = nested_dict(2, float)
            dict_H_3 = nested_dict(2, float)
            dict_H_4_1 = nested_dict(2, float)
            dict_H_4_2 = nested_dict(2, float)
            dict_H_5_1 = nested_dict(2, float)
            dict_H_5_2 = nested_dict(2, float)
            dict_eclidienne = nested_dict(2, float)


            all_header_files = glob2.glob(args.processes+'/*.json')
            print(f'Found {len(all_header_files)} jsons to analyse in {args.processes}')
            for p1 in range(len(all_header_files)):
                for p2 in range(p1+1, len(all_header_files)):

                    processes1= {}
                    with open(all_header_files[p1]) as json_file:
                        processes1 = json.load(json_file)

                    processes2 = {}
                    with open(all_header_files[p2]) as json_file:
                        processes2 = json.load(json_file)

                    for A in processes1 :
                        for B in processes2 :
                            proA = processes1[A]
                            proB = processes2[B]
                            workflow1 = proA['name_workflow']
                            workflow2 = proB['name_workflow']
                            nameA = f'{workflow1}:{A}'
                            nameB = f'{workflow2}:{B}'
                            print(f'Comparing {nameA} and {nameB}')
                            #print(f"Identity between processes : {H_1_1(proA, proB)}")
                            dict_H_1_1[nameA][nameB] = H_1_1(proA, proB)
                            #print(f"Identity between scripts : {H_1_2(proA, proB)}")
                            dict_H_1_2[nameA][nameB] = H_1_2(proA, proB)
                            #print(f"Similarity between the process code : {H_2_1(proA, proB, jaccard_texts)}")
                            dict_H_2_1[nameA][nameB] = H_2_1(proA, proB, jaccard_texts)
                            #print(f"Similarity between process scripts : {H_2_2(proA, proB, jaccard_texts)}")
                            dict_H_2_2[nameA][nameB] = H_2_2(proA, proB, jaccard_texts)
                            #print(f"Similarity between process names : {H_2_3(proA, proB, jaccard_texts)}")
                            dict_H_2_3[nameA][nameB] = H_2_3(proA, proB, jaccard_texts)
                            #print(f"Identity of bio.tools : {H_3(proA, proB)}")
                            dict_H_3[nameA][nameB] = H_3(proA, proB)
                            #print(f"Similarity between bio.tools : {H_4_1(proA, proB, jaccard)}")
                            dict_H_4_1[nameA][nameB] = H_4_1(proA, proB, jaccard)
                            #print(f"Similarity between bio.tools + Number of lines in the scripts : {H_4_2(proA, proB, jaccard)}")
                            dict_H_4_2[nameA][nameB] = H_4_2(proA, proB, jaccard)
                            #print(f"Similarity between number of inputs : {H_5_1(proA, proB)}")
                            dict_H_5_1[nameA][nameB] = H_5_1(proA, proB)
                            #print(f"Similarity between number of outputs : {H_5_2(proA, proB)}")
                            dict_H_5_2[nameA][nameB] = H_5_2(proA, proB)
                            #print(f"Eclidean measure : {mesure_eclidienne(proA, proB)}")
                            dict_eclidienne[nameA][nameB] = mesure_eclidienne(proA, proB)
                            #print('\n')
            
            df_H_1_1= pd.DataFrame.from_dict(dict_H_1_1)
            df_H_1_2= pd.DataFrame.from_dict(dict_H_1_2)
            df_H_2_1= pd.DataFrame.from_dict(dict_H_2_1)
            df_H_2_2= pd.DataFrame.from_dict(dict_H_2_2)
            df_H_2_3= pd.DataFrame.from_dict(dict_H_2_3)
            df_H_3= pd.DataFrame.from_dict(dict_H_3)
            df_H_4_1= pd.DataFrame.from_dict(dict_H_4_1)
            df_H_4_2= pd.DataFrame.from_dict(dict_H_4_2)
            df_H_5_1= pd.DataFrame.from_dict(dict_H_5_1)
            df_H_5_2= pd.DataFrame.from_dict(dict_H_5_2)
            df_eclidienne= pd.DataFrame.from_dict(dict_eclidienne)
            #print(df_eclidienne)
            
            df_H_1_1.to_csv("H_1_1.csv")
            df_H_1_2.to_csv("H_1_2.csv")
            df_H_2_1.to_csv("H_2_1.csv")
            df_H_2_2.to_csv("H_2_2.csv")
            df_H_2_3.to_csv("H_2_3.csv")
            df_H_3.to_csv("H_3.csv")
            df_H_4_1.to_csv("H_4_1.csv")
            df_H_4_2.to_csv("H_4_2.csv")
            df_H_5_1.to_csv("H_5_1.csv")
            df_H_5_2.to_csv("H_5_2.csv")
            df_eclidienne.to_csv("euclidienne.csv")

        else:
            Exception(f"A directory was not given to analyze")
    #=========
    # ERROR
    #=========
    else:
        raise Exception(f"Neither single or multiple workflow analysis was selected, but '{args.mode}'")
    
    os.chdir(current_directory)

