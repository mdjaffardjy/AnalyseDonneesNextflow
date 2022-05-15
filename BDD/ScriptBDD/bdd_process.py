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
