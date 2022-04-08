import datetime
import json
import os
from .bdd_person import *
from .bdd_workflow import *
from .bdd_process import *
from .bdd_tools import *

def addGlobalInformation(name_wf,tabAdressJson,cur,conn):
    """
    In this fonction : add the global information on a workflow
    Information extract from github
    Information on Workflow, Person   
    """
    with open(tabAdressJson[0]) as wf_json:
            wf = json.load(wf_json)

    with open(tabAdressJson[1]) as author_json:
            author = json.load(author_json)
        
    people = [wf[name_wf]['owner']]
    for p in wf[name_wf]['contributors']:
        if not p in people:
            people.append(p)

    for p in people :
        info_person = {}
        info_person_comp = {}
        info_person['login_git'] = p
        info_person['node_id'] = author[p]['node_id']
        info_person['git_url'] = author[p]['html_url']
        info_person['type_person'] = author[p]['type']
        info_person['nb_public_repos'] = author[p]['nb_public_repos']
        info_person['nb_followers'] = author[p]['nb_followers']
        info_person['nb_following'] = author[p]['nb_following']
        info_person['date_creation'] = author[p]['creation_date']
        info_person['date_updated'] = author[p]['updated_date']

        info_person_comp['login_git'] = p
        info_person_comp['name_person'] = author[p]['name']
        info_person_comp['email'] = author[p]['email']
        info_person_comp['bio'] = author[p]['bio']
        info_person_comp['location_person'] = author[p]['location']
        info_person_comp['company'] = author[p]['company']

        person = PersonBD(info_person, info_person_comp)
        person.insertBDPerson(cur)
        person.insertDBPersonComp(cur)
   
    info_workflow = {}
    info_workflow['name_wf'] = name_wf    
    info_workflow['id_git'] =wf[name_wf]['id']
    info_workflow['files'] = wf[name_wf]['files']
    info_workflow['git_url'] = wf[name_wf]['git_url']
    info_workflow['date_creation'] =  wf[name_wf]['creation_date']
    info_workflow['date_last_push'] = wf[name_wf]['last_push']
    info_workflow['date_updated'] = wf[name_wf]['update_date']
    info_workflow['date_download_json'] = wf[name_wf]['actual_date']
    info_workflow['description_wf'] =wf[name_wf]['description']
    info_workflow['nb_forks'] =  wf[name_wf]['forks']
    info_workflow['nb_stars'] =wf[name_wf]['stars']
    info_workflow['nb_watchers'] = wf[name_wf]['watchers']
    info_workflow['nb_subscribers'] = wf[name_wf]['subscribers']
    info_workflow['system_wf'] =wf[name_wf]['languages']
    info_workflow['archived'] =wf[name_wf]['archived']

    info_workflow['login_owner_wf'] =wf[name_wf]['owner']

    info_workflow['topics'] = wf[name_wf]['topics']

    info_workflow['contributors'] = wf[name_wf]['contributors']

    wf = WorkflowBD(info_workflow)
    idWf = wf.insertBDWorkflow(cur)

    conn.commit()
    return idWf

# -----------------------------------------------------
def addWorkflowExtracted(name_wf, idWf, cur,conn):
    with open('processes_info.json') as json_processes:
        process = json.load(json_processes)
    
    with open('channels_extracted.json') as json_channels:
        channel = json.load(json_channels)

    for p in process:
        info_process = {}
        info_process['name_wf'] = name_wf
        info_process['name_process'] = process[p]['name_process']
        info_process['string_process'] = process[p]['string_process']
        info_process['nb_lignes_process'] = process[p]['nb_lignes_process']
        info_process['string_script'] = process[p]['string_script']
        info_process['language_script'] = process[p]['language_script']
        info_process['nb_lignes_script'] = process[p]['nb_lignes_script']

        proc = ProcessBD(info_process, idWf)
        id_proc = proc.insertBDProcess(cur)
    
    conn.commit()

# ---------------------------------------------------------------------------------------------------------------------
def addTools(name_wf,idWf,cur,conn, adressJson):
    with open('processes_info.json') as json_processes:
        process = json.load(json_processes)
    
    list_tools = []
    name_tools = []
    for name_process in process:
        tools = process[name_process]['tools']
        toolsUrl = process[name_process]['tools_url']
        all_tools = zip(tools, toolsUrl)
        for t_name, t_url in all_tools:
            if not t_name in name_tools:
                list_tools.append(t_url)
                name_tools.append(t_name)

    currentPath = os.getcwd()
    try : 
        os.chdir(adressJson + "ToolsJson")
    except:
        os.chdir(adressJson)
        os.mkdir('ToolsJson')
        os.chdir(adressJson + "ToolsJson")

    for t in list_tools:
        tool = t.split('/')[-1]
        name = tool + '.json'
        try:
            with open(name) as tool_json:
                tool_information = json.load(tool_json)
        except:
            req = 'curl -X GET "https://bio.tools/api/tool/' + tool + '/?format=json" > '  + name
            os.system(req)
            with open(name) as tool_json:
                tool_information = json.load(tool_json)

        try:
            info_tool = {}

            info_tool['biotoolsID'] = tool_information['biotoolsID']
            info_tool['name'] = tool_information['name']
            info_tool['description'] = tool_information['description']
            info_tool['homepage'] = tool_information['homepage']
            info_tool['url_biotools'] = t

            info_tool['version'] = tool_information['version']
            info_tool['license'] = tool_information['license']
            info_tool['accessibility'] = tool_information['accessibility']
            info_tool['elixirNode'] = tool_information['elixirNode']
            info_tool['elixirPlatform'] = tool_information['elixirPlatform']

            try:
                info_tool['topic'] = tool_information['topic']
            except:
                info_tool['topic'] = []

            info_tool['collectionID'] = tool_information['collectionID']

            try:
                info_tool['operation'] = tool_information['function'][0]['operation']
            except:
                info_tool['operation'] = []

            info_tool['credit'] = tool_information['credit']

            try:
                info_tool['input'] = tool_information['function'][0]['input']
            except:
                info_tool['input'] = []

            try:
                info_tool['output'] = tool_information['function'][0]['output']
            except:
                info_tool['output'] = []
            
            tool_study = ToolsBDD(info_tool)
            already = tool_study.insertBDTool(cur)
            if not already:
                #tool_study.insertDBToolComp(cur)
                tool_study.insertBDToolCollectionID(cur)
                tool_study.insertBDTopics(cur)
                tool_study.insertBDOperation(cur)
                tool_study.insertBDInput_Output(cur, 'input')
                tool_study.insertBDInput_Output(cur, 'output')
                tool_study.insertBDCredit(cur)
            tool_study.insertBDToolWf(cur,idWf) 
        except  Exception as inst:
            print(print('This tool has a problem :', tool , ' : ', inst))

    for p in process:
        toolsInThisProcess = process[p]['tools_url']
        if len(toolsInThisProcess) != 0:
            bignameProcess = name_wf + "/" + p
            littlenameProcess = p
            string_process = process[p]['string_process']
            #on cherche le id du process dans la base
            verif = f"""
                SELECT id_process FROM process
                WHERE name_process = %(np)s AND little_name = %(ns)s AND string = %(string)s
                """
            cur.execute(verif, {'np':bignameProcess, 'ns':littlenameProcess, 'string':string_process})
            idProc = cur.fetchall()[0][0]

        for tool_url in toolsInThisProcess:
            try:
                tool = tool_url.split('/')[-1]
                with open(tool + '.json') as tool_json:
                    tool_info = json.load(tool_json)
                bI = tool_info['biotoolsID']

                #on verifie que le lien n'existe pas deja
                verif = f"""
                        SELECT biotoolsID FROM tool_in_process
                        WHERE biotoolsID = %(bi)s AND id_proc = %(idP)s
                        """
                cur.execute(verif, {'bi':bI, 'idP':idProc})
                raw = cur.fetchall()
                if raw != []:
                    #print("Already in the database : ", raw)
                    None
                else:
                    requete = f"""
                            INSERT INTO tool_in_process
                            (biotoolsID, id_proc)
                            VALUES
                            (%(bI)s, %(idP)s)
                            """
                    cur.execute(requete, {'bI':bI, 'idP':idProc})

            except Exception as inst:
                #print(print('This tool has a problem :', tool , ' : ', inst))
                None

    conn.commit()
    os.chdir(currentPath)