import psycopg
from .bdd_add import *

def addInDatabase(tabAdressJson, name_wf, dicoAllProcess):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        #print('\nConnecting to the PostgreSQL database...')
        conn = psycopg.connect()  # TODO file pour se connecter a une bd
        cur = conn.cursor()

        #Add global information about the workflow 
        # workflow , topic_wf, person_git, person_git_comp et contributor
        idWf = addGlobalInformation(name_wf,tabAdressJson,cur,conn)

        #Add information procees, channel ...
        dicoAllProcess = addWorkflowExtracted(name_wf, idWf, cur,conn, dicoAllProcess)

        #Add information about the tool
        addTools(name_wf, idWf, cur,conn) 


        cur.close()
    except (Exception, psycopg.DatabaseError) as error:
        print("ERROR in the bdd : ")
        print(error)
    finally:
        if conn is not None:
            conn.close()
            #print('Database connection closed.\n')
            
    return dicoAllProcess
