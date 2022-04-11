import csv
import json
import pandas as pd
import os

nameSimilarity = ['H_1_1', 'H_3', 'H_5_2', 'H_2_3', 'H_2_1', 'euclidienne', 'H_4_1', 'H_5_1', 'H_4_2', 'H_2_2', 'H_1_2']

class ProcessBD:
    def __init__(self, info_process, idWf):
        self.name = info_process['name_wf'] + '/' + info_process['name_process']
        self.little_name = info_process['name_process']
        self.string_process = info_process['string_process']
        self.nb_lines_process = info_process['nb_lignes_process']
        self.string_script = info_process['string_script']
        self.language_script = info_process['language_script']
        self.nb_lines_script = info_process['nb_lignes_script']
        self.idWf = idWf

        self.idProcess = None

        self.tools = info_process['tools']
        self.nb_inputs = info_process['nb_inputs']
        self.nb_outputs = info_process['nb_outputs']

    def insertBDProcess(self, cur):
        verif = f"""
                SELECT id_process FROM process
                WHERE name_process = %(np)s AND little_name = %(n)s AND
                string = %(s)s AND nb_lines = %(nbl)s AND nb_inputs = %(nbI)s AND nb_outputs = %(nbO)s
                AND string_script = %(scriptString)s 
                AND language_script = %(language)s AND nb_lines_script = %(nbls)s  AND id_wf = %(idW)s
                """
        cur.execute(verif, {'np':self.name, 'n':self.little_name, 's':self.string_process, 'nbl':self.nb_lines_process,
                            'nbI':self.nb_inputs, 'nbO':self.nb_outputs,
                            'scriptString':self.string_script, 'language':self.language_script, 'nbls':self.nb_lines_script,
                            'idW':self.idWf})

        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
            id_process = raw[0][0]
        else:
            requete = f"""
                    INSERT INTO process
                    (name_process, little_name, id_process, string, nb_lines, nb_inputs, nb_outputs, string_script, language_script, nb_lines_script, id_wf)
                    VALUES
                    (%(np)s, %(ln)s, nextval('seq_id_process'), %(stringP)s, %(nbLinesP)s, %(nbI)s, %(nbO)s, %(stringS)s,  %(language)s,
                    %(nbLS)s, %(idW)s)
                    RETURNING id_process 
                    """
            cur.execute(requete, {'np':self.name, 'ln':self.little_name, 'stringP':self.string_process, 'nbLinesP':self.nb_lines_process, 
                                'nbI': self.nb_inputs, 'nbO':self.nb_outputs, 
                                'stringS':self.string_script,'language':self.language_script, 'nbLS':self.nb_lines_script, 'idW':self.idWf})
            id_process = cur.fetchone()[0]
        self.idProcess = id_process
        return id_process

    '''
    def addSimilarity(self, cur):
        #TO CONTINUE
        comparaison = [i for i in range (1, self.idProcess)]
        temp1 = {}
        temp1['string_process'] = self.string_process
        temp1['string_script'] = self.string_script
        temp1['name_process'] = self.little_name
        temp1['tools'] = self.tools
        temp1['nb_lignes_script'] = self.nb_lines_script
        temp1['nb_inputs'] = self.nb_inputs
        temp1['nb_outputs'] = self.nb_outputs
        temp1['name_workflow'] = str(self.idWf) + "/" + str(self.idProcess)

        for i in comparaison:
            ok = True
            for nameSim in nameSimilarity:
                verif = f"""
                SELECT sim_val FROM similarity_process 
                WHERE id_proc_1 = %(id1)s AND id_proc_2 = %(id2)s AND sim_type = %(name)s
                """
                cur.execute(verif, {'id1':self.idProcess, 'id2':i, 'name':nameSim})
                raw = cur.fetchall() 
                if raw != []:
                    ok = False

            if ok:
                # -----
                temp2 = {}
                verif = f"""
                    SELECT name_process, little_name,string,nb_lines,nb_inputs,nb_outputs,string_script,
                        language_script,nb_lines_script,id_wf FROM process
                    WHERE id_process = %(id)s
                    """
                cur.execute(verif, {'id':i})
                raw = cur.fetchall()
                verif = f"""
                        SELECT tool.name_tool FROM tool, tool_in_process WHERE tool_in_process.id_proc = %(idP)s
                        AND tool_in_process.url_biotools = tool.url_biotools
                        """
                cur.execute(verif, {'idP':i})
                raw2 = cur.fetchall()

                temp2['string_process'] = raw[0][2]
                temp2['string_script'] = raw[0][6]
                temp2['name_process'] = raw[0][1]
                temp2['tools'] = []
                for t in raw2:
                    temp2['tools'].append(t[0])
                temp2['nb_lignes_script'] = raw[0][8]
                temp2['nb_inputs'] = raw[0][4]
                temp2['nb_outputs'] = raw[0][5]
                temp2['name_workflow'] = str(raw[0][9]) + "/" + str(i)

                currentPath = os.getcwd()

                os.chdir('/home/clemence/FAC/Master/M1/TER/2/AnalyseDonneesNextflow/clemence_9avril16h45')

                tempA = {}
                tempA['1'] = temp1
                with open("tempA.json", 'w') as dicoP:
                    json.dump(tempA, dicoP, indent=4)

                tempB = {}
                tempB['2'] = temp2
                with open("tempB.json", 'w') as dicoP:
                    json.dump(tempB, dicoP, indent=4)

                inputsA = os.getcwd() + '/' + 'tempA.json'
                inputsB = os.getcwd() + '/' + 'tempB.json'
                where = os.getcwd()
                os.system('ProSim --mode "single" --results_directory ' + where + ' --processA ' + inputsA + ' --processB ' + inputsB)

                os.chdir(where + '/Results_Similarity')
                for file in os.listdir():
                    with open(file, newline='') as f:
                        reader = csv.reader(f)
                        nameSimVal = list(reader)

                    nameSim = file.split('.')[0]
                    val = nameSimVal[1][1]
                    if val == 'False':
                        val = 0
                    elif val == 'True':
                        val = 1

                    requete = f"""
                                INSERT INTO similarity_process 
                                (id_proc_1, id_proc_2, sim_type, sim_val)
                                VALUES
                                (%(id1)s, %(id2)s, %(type)s, %(val)s)
                                """
                    cur.execute(requete, {'id1':self.idProcess, 'id2':i, 'type':nameSim, 'val':val})

                #os.chdir(args.results_directory + "/Results_Similarity")"""
                os.chdir(currentPath)
    '''