def add(tab, kind, idO, idWf, cur):
    for ope in tab:
        extractC = f"""
                SELECT id_channel FROM channel
                WHERE name_channel = %(name)s AND id_in_wf = %(idW)s
                """
        cur.execute(extractC, {'name':ope[0], 'idW':idWf})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            idC =  raw[0][0]
            #rajouter type 
            updateC = f"""
                    UPDATE channel
                    SET type_channel = %(type)s
                    WHERE id_channel = %(idC)s
                    """
            cur.execute(updateC, {'type':ope[1], 'idC':idC})
        else:
            #creer le channel
            requete = f"""
                    INSERT INTO channel
                    (id_channel, name_channel, id_in_wf, type_channel)
                    VALUES
                    (nextval('seq_id_process'), %(name)s, %(idW)s, %(type)s)
                    RETURNING id_channel
                    """
            cur.execute(requete, {'name':ope[0], 'idW':idWf, 'type':ope[1]})
            idC = cur.fetchone()[0]
    
        #Add link between process and channel
        verif = f"""
                SELECT id_ope, id_channel FROM link_channel_operation
                WHERE id_ope = %(idO)s AND  id_channel = %(idC)s AND kind_ope = %(kind)s
                """
        cur.execute(verif, {'idO':idO, 'idC':idC, 'kind':kind}) 
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
        else:
            requete = f"""
                    INSERT INTO link_channel_operation 
                    (id_ope, id_channel, kind_ope)
                    VALUES
                    (%(idO)s,%(idC)s, %(kind)s)
                    """
            cur.execute(requete, {'idO':idO, 'idC':idC, 'kind':kind})

class OperationBD:
    def __init__(self, info_ope, idWf):
        self.string = info_ope['string']
        self.origin = info_ope['origin']
        self.gives = info_ope['gives']

        self.idWf = idWf

    def insertBDOperation(self,cur):
        #Add in databse
        verif = f"""
                SELECT id_ope FROM operation_wf
                WHERE id_in_wf = %(idW)s AND string_ope = %(str)s
                """
        cur.execute(verif, {'idW':self.idWf, 'str':self.string})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            idO =  raw[0][0]
        else:
            requete = f"""
                    INSERT INTO operation_wf
                    (id_ope, id_in_wf, string_ope)
                    VALUES
                    (nextval('seq_id_operation_wf'), %(idWf)s, %(str)s)
                    RETURNING id_ope
                    """
            cur.execute(requete, {'idWf':self.idWf, 'str':self.string})
            idO = cur.fetchone()[0]

        #Add link between channel and ope
        add(self.origin, 'input', idO, self.idWf, cur)
        add(self.gives, 'output', idO, self.idWf, cur)

#pour retrouver le channel on a nom + idWf