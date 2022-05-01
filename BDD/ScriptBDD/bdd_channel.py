def add(tab, kind, idP, idW, cur):
    for cha in tab:
        #Add the channel
        verif = f"""
                    SELECT id_channel FROM channel
                    WHERE name_channel = %(name)s AND id_in_wf = %(idW)s
                    """
        cur.execute(verif, {'name':cha, 'idW':idW})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            idC = raw[0][0]
        else:
            requete = f"""
                    INSERT INTO channel
                    (id_channel, name_channel, id_in_wf)
                    VALUES
                    (nextval('seq_id_process'), %(name)s, %(idW)s)
                    RETURNING id_channel
                    """
            cur.execute(requete, {'name':cha, 'idW':idW})
            idC = cur.fetchone()[0]

        #Add link between process and channel
        verif = f"""
                SELECT id_proc, id_channel FROM link_process_channel
                WHERE id_proc = %(idP)s AND  id_channel = %(idC)s AND kind_channel = %(kind)s
                """
        cur.execute(verif, {'idP':idP, 'idC':idC, 'kind':kind}) 
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
        else:
            requete = f"""
                    INSERT INTO link_process_channel 
                    (id_proc, id_channel, kind_channel)
                    VALUES
                    (%(idP)s,%(idC)s, %(kind)s)
                    """
            cur.execute(requete, {'idP':idP, 'idC':idC, 'kind':kind})
        

class ChannelBD:
    def __init__(self, info_channel, idProc, idWf):
        self.inputs = info_channel['inputs']
        self.outputs = info_channel['outputs']

        self.idProcess = idProc

        self.idWf = idWf

    def insertBDChannel(self,cur):
        add(self.inputs, 'input', self.idProcess,self.idWf, cur)
        add(self.outputs, 'output',self.idProcess, self.idWf, cur)
