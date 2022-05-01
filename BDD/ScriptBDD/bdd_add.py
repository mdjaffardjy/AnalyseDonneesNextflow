import json
from .bdd_person import *
from .bdd_workflow import *
from .bdd_process import *
from .bdd_tools import *
from .bdd_channel import *
from .bdd_operation import * 

def addGlobalInformation(name_wf,tabAdressJson, dsl,cur,conn):
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

    info_workflow['dsl'] = dsl

    info_workflow['login_owner_wf'] =wf[name_wf]['owner']

    info_workflow['topics'] = wf[name_wf]['topics']

    info_workflow['contributors'] = wf[name_wf]['contributors']

    wf = WorkflowBD(info_workflow)
    idWf = wf.insertBDWorkflow(cur)

    conn.commit()
    return idWf

# -----------------------------------------------------
def addProcessExtracted(name_wf, idWf, cur,conn, dicoAllProcess):
    with open('processes_info.json') as json_processes:
        process = json.load(json_processes)
    
    """with open('channels_extracted.json') as json_channels:
        channel = json.load(json_channels)"""

    for p in process:
        info_process = {}
        info_process['name_wf'] = name_wf
        info_process['name_process'] = process[p]['name_process']
        info_process['string_process'] = process[p]['string_process']
        info_process['nb_lignes_process'] = process[p]['nb_lignes_process']
        info_process['string_script'] = process[p]['string_script']
        info_process['language_script'] = process[p]['language_script']
        info_process['nb_lignes_script'] = process[p]['nb_lignes_script']
        info_process['tools'] = process[p]['tools']
        info_process['nb_inputs'] = process[p]['nb_inputs']
        info_process['nb_outputs'] = process[p]['nb_outputs']

        proc = ProcessBD(info_process, idWf)
        id_proc = proc.insertBDProcess(cur)

        channel = {}
        channel['inputs'] = process[p]['inputs']
        channel['outputs'] = process[p]['outputs']

        cha = ChannelBD(channel, id_proc, idWf)
        cha.insertBDChannel(cur)


        temp = process[p]
        key = str(idWf) + "/" + str(id_proc)
        temp['name_workflow'] = key
        dicoAllProcess.update({key:temp})
    
    conn.commit()
    return dicoAllProcess

# ---------------------------------------------------------------------------------------------------------------------
def addOperation(idWf,cur,conn):
    with open('operations_extracted.json') as json_ope:
        operation = json.load(json_ope)

    for o in operation:
        ope = {}
        ope['string'] = operation[o]['string']
        ope['origin'] = operation[o]['origin']
        ope['gives'] = operation[o]['gives'] 

        oo = OperationBD(ope, idWf)
        oo.insertBDOperation(cur)
        
    conn.commit()

# ---------------------------------------------------------------------------------------------------------------------
def addTools(name_wf,idWf,cur,conn):
    with open('processes_info.json') as json_processes:
        process = json.load(json_processes)
    
    for name_process in process:
        tools = process[name_process]['tools_url']
        dicoTools = process[name_process]['tools_dico']

        for t, dico in zip(tools,dicoTools):
            info_tool = {}
            info_tool['url_biotools'] = t
            info_tool['name_tool'] = dico['name']
            info_tool['description'] = dico['description']
            info_tool['homepage'] = dico['homepage']

            info_tool['topics'] = dico['topic']

            info_tool['operation'] = dico['function'][0]['operation']

            info_tool['input'] = dico['function'][0]['input']

            info_tool['output'] = dico['function'][0]['output']

            tool = ToolsBDD(info_tool)
            tool.insertBDTool(cur)
            tool.insertBDTopics(cur)
            tool.insertBDOperation(cur)
            tool.insertBDInput_Output(cur, 'input')
            tool.insertBDInput_Output(cur, 'output')
            tool.insertBDToolWf(cur, idWf)

    for name_process in process:
        big_name = name_wf + '/' + name_process
        little_name = name_process
        string =  process[name_process]['string_process']  
        verif = f"""
            SELECT id_process FROM process
            WHERE name_process = %(name_process)s AND little_name = %(little_name)s AND string = %(string)s
            """ 
        cur.execute(verif, {'name_process':big_name, 'little_name':little_name, 'string':string})
        raw = cur.fetchall()
        idProc = raw[0][0]
        tools = process[name_process]['tools_url']
        
        for t in tools:
            verif = f"""
                SELECT url_biotools from tool_in_process
                WHERE url_biotools = %(url)s AND id_proc = %(idP)s
                """
            cur.execute(verif, {'url':t, 'idP':idProc})
            raw = cur.fetchall()
            if raw != []:
                None
            else:
                requete = f"""
                    INSERT INTO tool_in_process
                    (url_biotools, id_proc)
                    VALUES
                    (%(url)s, %(idP)s)
                    """
                cur.execute(requete, {'url':t, 'idP':idProc})

    conn.commit()

