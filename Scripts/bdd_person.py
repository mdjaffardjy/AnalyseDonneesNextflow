import datetime

class PersonBD:
    def __init__(self, info_person, info_person_comp):
        self.login_git = info_person['login_git']
        self.node_id = info_person['node_id']
        self.git_url = info_person['git_url']
        self.type_person = info_person['type_person']
        self.nb_public_repos = info_person['nb_public_repos']
        self.nb_followers = info_person['nb_followers']
        self.nb_following = info_person['nb_following']
        self.date_creation = info_person['date_creation']
        self.date_updated = info_person['date_updated']

        self.login_git = info_person_comp['login_git']
        self.name_person = info_person_comp['name_person']
        self.email = info_person_comp['email']
        self.bio = info_person_comp['bio']
        self.location_person = info_person_comp['location_person']
        self.company = info_person_comp['company']

    # -------------------------------------------------------------------------   
    def insertBDPerson(self, cur):
        verif = f"""
                SELECT login_git FROM person_git
                WHERE login_git = %(login)s AND node_id = %(id)s
                """
        cur.execute(verif, {'login': self.login_git, 'id': self.node_id})
        raw = cur.fetchall()
        if raw != []:
            #print("Already in the database : ", raw)
            None
        else: 
                dateC = self.date_creation
                dateC = dateC.split('-')
                dateU = self.date_updated
                dateU = dateU.split('-')

                requete = f"""
                    INSERT INTO person_git 
                    (login_git, node_id, git_url, type_person, nb_public_repos,nb_followers,
                    nb_following,date_creation,date_updated)
                    VALUES
                    (%(login)s, %(id)s, %(git)s, %(type)s, %(nbR)s, %(nbFollowers)s,
                    %(nbFollowing)s, %(dateC)s, %(dateU)s)
                    """
                
                cur.execute(requete, {'login':self.login_git, 'id':self.node_id, 'git': self.git_url,
                            'type':self.type_person, 'nbR':self.nb_public_repos,
                            'nbFollowers':self.nb_followers, 'nbFollowing':self.nb_following,
                            'dateC':datetime.date(int(dateC[0]), int(dateC[1]), int(dateC[2])),
                            'dateU':datetime.date(int(dateU[0]), int(dateU[1]), int(dateU[2]))})
                

    def insertDBPersonComp(self,cur):
        verif = f"""
                SELECT login_git FROM person_git_comp
                WHERE login_git = %(login)s
                """
        cur.execute(verif, {'login': self.login_git})
        raw = cur.fetchall()
        if raw != []:
            None
        else: 
            if self.name_person != None or self.email != None or self.bio != None or self.location_person != None or self.company != None:
                requete = f"""
                                INSERT INTO person_git_comp 
                                (login_git, name_person, email, bio, location_person, company)
                                VALUES
                                (%(login)s, %(name)s, %(email)s, %(bio)s, %(location)s, %(company)s)
                                """
                cur.execute(requete, {'login':self.login_git, 'name':self.name_person, 'email':self.email, 
                                        'bio':self.bio, 'location':self.location_person, 'company':self.company})