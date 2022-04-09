
import json


class ToolsBDD :
    def __init__(self, info_tool):
        self.url_biotools = info_tool['url_biotools']
        self.name_tool = info_tool['name_tool']
        self.description = info_tool['description']
        self.homepage = info_tool['homepage']

        self.topics = info_tool['topics']

        self.operation = info_tool['operation']

        self.input = info_tool['input']

        self.output = info_tool['output']

    #----------------------------------------------------
    def insertBDTool(self, cur):
        verif = f"""
                SELECT url_biotools FROM tool 
                WHERE url_biotools = %(url_biotools)s AND name_tool = %(n)s
                """
        cur.execute(verif, {'url_biotools': self.url_biotools, 'n': self.name_tool})
        raw = cur.fetchall()
        if raw != []:
            return True
        else: 
            requete = f"""
                    INSERT INTO tool 
                    (url_biotools, name_tool, description_tool, homepage)
                    VALUES
                    (%(url_biotools)s, %(name_tool)s, %(description)s, %(homepage)s)
                    """
            cur.execute(requete, {'url_biotools':self.url_biotools, 'name_tool':self.name_tool,
                                    'description':self.description, 'homepage':self.homepage})
            return False

    # ----------------------------------------------------------
    def insertBDTopics(self,cur):
        for topic in self.topics:
            for t in topic:
                uri = t['uri']
                term = t['term']

                verif = f"""
                        SELECT id_topic FROM topic_tools 
                        WHERE topic_uri = %(uri)s AND term = %(t)s
                        """
                cur.execute(verif, {'uri': uri, 't': term})
                raw = cur.fetchall()
                if raw != []:
                    #print("Already in the database : ", raw)
                    idTopic = raw[0][0]
                else: 
                    requete = f"""
                        INSERT INTO topic_tools
                        (id_topic, topic_uri, term)
                        VALUES
                        (nextval('seq_id_topic_tools'), %(uri)s, %(term)s)
                        RETURNING id_topic
                        """
                    cur.execute(requete, {'uri':uri, 'term':term})
                    idTopic = cur.fetchone()[0]

                verif = f"""
                    SELECT url_biotools FROM tools_have_topic 
                    WHERE url_biotools = %(url_biotools)s AND id_topic = %(idT)s 
                    """
                cur.execute(verif, {'url_biotools': self.url_biotools, 'idT': idTopic})
                raw = cur.fetchall()
                if raw != []:
                    #print("Already in the database : ", raw)
                    None
                else:
                    requete = f"""
                        INSERT INTO tools_have_topic
                        (url_biotools, id_topic)
                        VALUES
                        (%(url_biotools)s, %(idT)s)
                        """
                    cur.execute(requete, {'url_biotools': self.url_biotools, 'idT': idTopic})
 
    # ----------------------------------------------------------
    def insertBDOperation(self,cur):
        for o in self.operation[0]:
            uri = o['uri']
            term = o['term']
            verif = f"""
                SELECT id_operation FROM operation_tool
                WHERE operation_uri = %(uri)s AND term = %(term)s
                """
            cur.execute(verif, {'uri':uri, 'term':term})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                idOpe = raw[0][0]
            else:
                requete = f"""
                    INSERT INTO operation_tool
                    (id_operation, operation_uri, term)
                    VALUES
                    (nextval('seq_id_operation_tools'),%(ope)s, %(term)s)
                    RETURNING id_operation
                    """
                cur.execute(requete, {'ope':uri, 'term':term})
                idOpe = cur.fetchone()[0]

            verif = f"""
                SELECT url_biotools FROM tools_have_operation
                WHERE url_biotools = %(url)s AND id_operation = %(idO)s
                """
            cur.execute(verif, {'url':self.url_biotools, 'idO':idOpe})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                None
            else:
                requete = f"""
                    INSERT INTO tools_have_operation
                    (url_biotools, id_operation)
                    VALUES 
                    (%(url_biotools)s, %(idO)s)
                    """
                cur.execute(requete, {'url_biotools':self.url_biotools, 'idO':idOpe})

    def insertBDInput_Output(self,cur, what):
        if what == 'input':
            dicoInfo = self.input
        else:
            dicoInfo = self.output

        for in_out in dicoInfo:
            uri = in_out['uri']
            term = in_out['term']

            verif = f"""
                SELECT id_in_out FROM in_out_data
                WHERE in_out_uri = %(uri)s AND term = %(term)s AND  in_or_out = %(type)s 
                """
            cur.execute(verif, {'uri':uri, 'term': term, 'type':what})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                id_in_out = raw[0][0]
            else:
                requete = f"""
                    INSERT INTO in_out_data
                    (id_in_out, in_out_uri, term, in_or_out)
                    VALUES
                    (nextval('seq_id_in_out_tool'), %(uri)s,%(term)s, %(type)s)
                    RETURNING id_in_out
                    """
                cur.execute(requete, {'uri':uri, 'term':term, 'type':what})
                id_in_out = cur.fetchone()[0]

            verif = f"""
                SELECT url_biotools FROM tools_have_in_out
                WHERE url_biotools = %(url)s AND id_in_out = %(idIO)s
                """
            cur.execute(verif, {'url':self.url_biotools, 'idIO':id_in_out})
            raw = cur.fetchall()
            if raw != []:
                #print("Already in the database : ", raw)
                None
            else:
                requete = f"""
                    INSERT INTO tools_have_in_out
                    (url_biotools, id_in_out)
                    VALUES 
                    (%(url_biotools)s, %(idIO)s)
                    """
                cur.execute(requete, {'url_biotools':self.url_biotools, 'idIO':id_in_out})

    # ---------------------------------------------------
    def insertBDToolWf(self,cur, idWf):
        #link between the tool and the wf
        verif = f"""
            SELECT url_biotools, id_wf FROM tool_in_workflow
            WHERE url_biotools = %(url)s AND id_wf = %(idW)s
            """
        cur.execute(verif, {'url':self.url_biotools, 'idW':idWf})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
        else:
            requete = f"""
                INSERT INTO tool_in_workflow
                (url_biotools, id_wf)
                VALUES
                (%(url)s, %(idW)s)
                """
            cur.execute(requete, {'url':self.url_biotools, 'idW':idWf})

