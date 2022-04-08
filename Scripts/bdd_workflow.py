import datetime

class WorkflowBD:
    def __init__(self, info_workflow):
        self.name_full = info_workflow['login_owner_wf'] + '/' + info_workflow['name_wf']         
        self.name_wf = info_workflow['name_wf']     
        self.id_git = info_workflow['id_git'] 
        self.files = info_workflow['files'] 
        self.git_url = info_workflow['git_url'] 
        self.date_creation = info_workflow['date_creation'] 
        self.date_last_push = info_workflow['date_last_push'] 
        self.date_updated  = info_workflow['date_updated'] 
        self.date_download_json  = info_workflow['date_download_json'] 
        self.description_wf = info_workflow['description_wf'] 
        self.nb_forks  = info_workflow['nb_forks']           
        self.nb_stars  = info_workflow['nb_stars'] 
        self.nb_watchers = info_workflow['nb_watchers'] 
        self.nb_subscribers = info_workflow['nb_subscribers'] 
        self.system_wf = info_workflow['system_wf'] 
        self.archived  = info_workflow['archived'] 

        self.login_owner_wf = info_workflow['login_owner_wf']

        self.topics = info_workflow['topics']

        self.contributors = info_workflow['contributors']


    def insertBDWorkflow(self, cur):
        #add in the bdd the workflow if not already inside
        verif = f"""
                SELECT id_wf FROM workflow  
                WHERE name_full = %(name)s AND id_git = %(id)s
                """
        cur.execute(verif, {'name': self.name_full, 'id': self.id_git})
        raw = cur.fetchall()
        if raw != []:
            idWf = raw[0][0]
        else : 
            dateC = self.date_creation
            dateC = dateC.split('-')
            dateU = self.date_updated
            dateU = dateU.split('-')
            dateP = self.date_last_push
            dateP = dateP.split('-')
            dateJ = self.date_download_json
            dateJ = dateJ.split('-')
            language = 'SnakeMake'
            for l in self.system_wf:
                if l == 'Nextflow':
                    language = 'Nextflow'
            #add in the database
            requete = f"""
                    INSERT INTO workflow 
                    (name_full, id_wf, name_wf, id_git, files, git_url,
                    date_creation, date_last_push,date_updated,date_download_json,
                    description_wf, nb_forks, nb_stars, nb_watchers, nb_subscribers,
                    system_wf, archived, login_owner_wf)
                    VALUES
                    (%(nameF)s, nextval('seq_id_wf'), %(nameW)s, %(idG)s, %(files)s, %(git_url)s, 
                    %(dateC)s, %(dateP)s, %(dateU)s, %(dateJ)s, %(description)s, %(nbF)s, %(nbStars)s,
                    %(nbW)s, %(nbS)s, %(system)s, %(archived)s, %(login)s)
                    RETURNING id_wf;
                    """
            cur.execute(requete, {'nameF':self.name_full,'nameW':self.name_wf, 'idG':self.id_git, 
                            'files':self.files, 'git_url':self.git_url,
                            'dateC':datetime.date(int(dateC[0]), int(dateC[1]), int(dateC[2])),
                            'dateP':datetime.date(int(dateP[0]), int(dateP[1]), int(dateP[2])),
                            'dateU':datetime.date(int(dateU[0]), int(dateU[1]), int(dateU[2])),
                            'dateJ':datetime.date(int(dateJ[0]), int(dateJ[1]), int(dateJ[2])),
                            'description':self.description_wf, 'nbF':self.nb_forks, 'nbStars':self.nb_stars, 
                            'nbW':self.nb_watchers,'nbS':self.nb_stars, 'system': language,
                            'archived':self.archived, 'login':self.login_owner_wf})
            #extract the id of the wf
            idWf = cur.fetchone()[0]

            #create the table topics and had information
            for t in self.topics:
                requete = f"""
                            INSERT INTO topic_wf 
                            (id_wf, name_topic)
                            VALUES
                            (%(id)s, %(name)s)
                            """
                cur.execute(requete, {'id':idWf, 'name':t})

            #last : add the contributor information 
            for p in self.contributors:
                requete = f"""
                            INSERT INTO contributor
                            (id_wf, login_git)
                            VALUES
                            (%(idW)s, %(login)s)
                            """
                cur.execute(requete, {'idW':idWf, 'login':p})
        return idWf