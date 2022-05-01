import psycopg
from .bdd_add import *

def addInDatabase(tabAdressJson, name_wf, dsl, dicoAllProcess):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        #print('\nConnecting to the PostgreSQL database...')
        conn = psycopg.connect()  # TODO file pour se connecter a une bd
        cur = conn.cursor()

        #Add global information about the workflow 
        # workflow , topic_wf, person_git, person_git_comp et contributor
        idWf = addGlobalInformation(name_wf,tabAdressJson, dsl,cur,conn)

        #Add information process, channel ...
        dicoAllProcess = addProcessExtracted(name_wf, idWf, cur,conn, dicoAllProcess)

        #Add operation  
        if dsl == 1:
            addOperation(idWf,cur,conn)

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
