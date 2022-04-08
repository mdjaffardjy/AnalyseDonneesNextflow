
import json


class ToolsBDD :
    def __init__(self, info_tool):
        self.biotoolsID = info_tool['biotoolsID']
        self.name = info_tool['name']
        self.descrition = info_tool['description']
        self.homepage = info_tool['homepage']
        self.url_biotoolsId = info_tool['url_biotools']

        self.version = info_tool['version']
        self.license = info_tool['license']
        self.accessibility =info_tool['accessibility']
        self.elixirNode = info_tool['elixirNode']
        self.elixirPlatform = info_tool['elixirPlatform']

        self.topics = info_tool['topic']

        self.collectionID = info_tool['collectionID']

        self.operation = info_tool['operation']

        self.credit = info_tool['credit']

        self.input = info_tool['input']

        self.output = info_tool['output']

    def insertBDTool(self, cur):
        verif = f"""
                SELECT biotoolsID FROM tool 
                WHERE biotoolsID = %(biotoolsID)s AND name_tool = %(n)s
                """
        cur.execute(verif, {'biotoolsID': self.biotoolsID, 'n': self.name})
        raw = cur.fetchall()
        if raw != []:
            return True
        else: 
            requete = f"""
                    INSERT INTO tool 
                    (biotoolsID,name_tool,description_tool,homepage,url_biotools)
                    VALUES
                    (%(biotoolsId)s, %(name)s, %(description)s, %(urlH)s, %(urlB)s)
                    """
            cur.execute(requete, {'biotoolsId':self.biotoolsID, 'name':self.name, 'description': self.descrition, 
                                'urlH': self.homepage, 'urlB':self.biotoolsID})
            return False

    def insertDBToolComp(self,cur):
        if self.version != [] or self.license != None or self.accessibility != None or self.elixirNode != [] or self.elixirPlatform != []:
            requete = f"""
                INSERT INTO tool_comp
                (biotoolsID,version_tool,license,accessibility,elixirNode,elixirPlatform)
                VALUES
                (%(bI)s, %(version)s, %(license)s, %(access)s, %(eN)s, %(eP)s)
                """
            cur.execute(requete, {'bI':self.biotoolsID, 'version':self.version, 'license':self.license, 
                        'access': self.accessibility, 'eN':self.elixirNode, 'eP':self.elixirPlatform})
                
    def insertBDToolCollectionID(self,cur):
        for c in self.collectionID:
            requete = f"""
                INSERT INTO collectionID
                (biotoolsID, name_collection)
                VALUES
                (%(bI)s, %(name)s)
                """
            cur.execute(requete, {'bI':self.biotoolsID, 'name':c})

    def insertBDTopics(self,cur):
        for t in self.topics:
            uri = t['uri']
            term = t['term']
            verif = f"""
                    SELECT id_topic FROM topic_tools 
                    WHERE topic_url = %(t_url)s AND term = %(t)s
                    """
            cur.execute(verif, {'t_url': uri, 't': term})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                idTopic = raw[0][0]
            else: 
                requete = f"""
                    INSERT INTO topic_tools
                    (id_topic, topic_url, term)
                    VALUES
                    (nextval('seq_id_topic_tools'), %(t_url)s, %(term)s)
                    RETURNING id_topic
                    """
                cur.execute(requete, {'t_url':uri, 'term':term})
                idTopic = cur.fetchone()[0]

            verif = f"""
                SELECT biotoolsID FROM tools_have_topic 
                WHERE biotoolsID = %(bI)s AND id_topic = %(idT)s 
                """
            cur.execute(verif, {'bI': self.biotoolsID, 'idT': idTopic})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                None
            else:
                requete = f"""
                    INSERT INTO tools_have_topic
                    (biotoolsID, id_topic)
                    VALUES
                    (%(bI)s, %(idT)s)
                    """
                cur.execute(requete, {'bI': self.biotoolsID, 'idT': idTopic})

    def insertBDOperation(self,cur):
        for o in self.operation:
            uri = o['uri']
            term = o['term']
            verif = f"""
                SELECT id_operation FROM operation_tool
                WHERE operation_url = %(ope_url)s AND term = %(t)s
                """
            cur.execute(verif, {'ope_url':uri, 't':term})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                idOpe = raw[0][0]
            else:
                requete = f"""
                    INSERT INTO operation_tool
                    (id_operation, operation_url, term)
                    VALUES
                    (nextval('seq_id_operation_tools'),%(ope)s, %(t)s)
                    RETURNING id_operation
                    """
                cur.execute(requete, {'ope':uri, 't':term})
                idOpe = cur.fetchone()[0]
            #tools_have_operation
            verif = f"""
                SELECT biotoolsID FROM tools_have_operation
                WHERE biotoolsID = %(bi)s AND id_operation = %(idO)s
                """
            cur.execute(verif, {'bi':self.biotoolsID, 'idO':idOpe})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                None
            else:
                requete = f"""
                    INSERT INTO tools_have_operation
                    (biotoolsID, id_operation)
                    VALUES 
                    (%(bi)s, %(idO)s)
                    """
            cur.execute(requete, {'bi':self.biotoolsID, 'idO':idOpe})

    def insertBDInput_Output(self,cur, what):
        if what == 'input':
            dicoInfo = self.input
        else:
            dicoInfo = self.output

        for in_out in dicoInfo:
            data = in_out['data']
            format = in_out['format']
                       
            d_url = data['uri']
            d_term = data['term']
            verif = f"""
                SELECT id_in_out FROM in_out_data
                WHERE in_out_url = %(url)s AND term = %(term)s AND  in_or_out = %(type)s 
                """
            cur.execute(verif, {'url':d_url, 'term': d_term, 'type':what})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                id_in_out = raw[0][0]
            else:
                requete = f"""
                    INSERT INTO in_out_data
                    (id_in_out, in_out_url, term, in_or_out)
                    VALUES
                    (nextval('seq_id_in_out_tool'), %(url)s,%(term)s, %(type)s)
                    RETURNING id_in_out
                    """
                cur.execute(requete, {'url':d_url, 'term':d_term, 'type':what})
                id_in_out = cur.fetchone()[0]
                            
                requete = f"""
                    INSERT INTO tools_have_in_out
                    (id_in_out, biotoolsID)
                    VALUES
                    (%(id)s, %(bI)s)
                    """
                cur.execute(requete, {'id':id_in_out, 'bI':self.biotoolsID})

            #format
            for f in format:
                f_url = f['uri']
                f_term = f['term']

                verif = f"""
                    SELECT id_in_out_format FROM in_out_format
                    WHERE url_format = %(url)s AND term = %(term)s
                    """
                cur.execute(verif, {'url':f_url, 'term':f_term})
                raw = cur.fetchall()
                if raw != []:
                    #print("Already in the database : ", raw)
                    idF = raw[0][0]
                else:
                    requete = f"""
                        INSERT INTO in_out_format
                        (id_in_out_format, url_format, term)
                        VALUES
                        (nextval('seq_id_in_out_tool_format'), %(url)s, %(term)s)
                        RETURNING id_in_out_format
                        """
                    cur.execute(requete, {'url':f_url, 'term':f_term})
                    idF = cur.fetchone()[0]
                            
                verif = f"""
                    SELECT id_in_out FROM in_out_link_data_format
                    WHERE id_in_out = %(id)s AND id_in_out_format = %(idF)s
                    """
                cur.execute(verif, {'id':id_in_out, 'idF':idF})
                raw = cur.fetchall()
                if raw != []:
                    #print("Already in the database : ", raw)
                    None
                else:
                    requete = f"""
                        INSERT INTO in_out_link_data_format
                        (id_in_out, id_in_out_format)
                        VALUES
                        (%(id)s, %(idF)s)
                        """
                    cur.execute(requete, {'id':id_in_out, 'idF':idF})


    def insertBDCredit(self,cur):
        for c in self.credit:
            name = c['name']
            typeEntity = c['typeEntity']
            verif = f"""
                SELECT id_credit FROM  credit_tool 
                WHERE name_credit = %(name)s AND type_entity_credit = %(type)s
                """
            cur.execute(verif, {'name':name, 'type': typeEntity})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                idCredit = raw[0][0]
            else:
                email = c['email']
                requete = f"""
                    INSERT INTO credit_tool
                    (id_credit, name_credit, email, type_entity_credit)
                    VALUES
                    (nextval('seq_id_credit'), %(name)s, %(email)s, %(type)s)
                    RETURNING id_credit
                    """
                cur.execute(requete, {"name":name, 'email':email, 'type':typeEntity})
                idCredit = cur.fetchone()[0]

                url = c['url']
                orcidid = c['orcidid']
                if url != None or orcidid != None:
                    requete = f"""
                        INSERT INTO credit_tool_comp
                        (id_credit, credit_url, orcidid)
                        VALUES
                        (%(id)s, %(url)s, %(orcidid)s)
                        """
                    cur.execute(requete, {'id':idCredit, 'url':url, 'orcidid':orcidid})

            #add relation between credit and tools
            verif = f"""
                SELECT biotoolsID FROM tools_contact_credit
                WHERE biotoolsID = %(id)s AND id_credit = %(credit)s
                """
            cur.execute(verif, {'id':self.biotoolsID, 'credit':idCredit})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                None
            else:
                requete = f"""
                    INSERT INTO tools_contact_credit
                    (biotoolsID, id_credit, type_role_entity)
                    VALUES 
                    (%(idB)s, %(idC)s, %(type)s)
                    """ 
                cur.execute(requete, {'idB':self.biotoolsID, 'idC':idCredit, 'type':c['typeRole']})

    def insertBDToolWf(self,cur, idWf):
        #link between the tool and the wf
        verif = f"""
            SELECT biotoolsID, id_wf FROM tool_in_workflow
            WHERE biotoolsID = %(idT)s AND id_wf = %(idW)s
            """
        cur.execute(verif, {'idT':self.biotoolsID, 'idW':idWf})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
        else:
            requete = f"""
                INSERT INTO tool_in_workflow
                (biotoolsID, id_wf)
                VALUES
                (%(idT)s, %(idW)s)
                """
            cur.execute(requete, {'idT':self.biotoolsID, 'idW':idWf})

