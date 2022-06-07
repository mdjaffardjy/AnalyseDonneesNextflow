/************************************************************************
 * Table Person = all the informations about 
 ************************************************************************
 */

-- Enum about the type of the person
CREATE TYPE type_p AS ENUM ('User', 'Organization', 'Bot');

CREATE TABLE person_git (
    login_git VARCHAR(100),  -- login of the person on github
    node_id VARCHAR(50),     -- id on github
    git_url VARCHAR(500),    -- git page
    type_person type_p,      -- type of the user on github
    nb_public_repos INT,     -- number of public repositories 
    nb_followers INT,        -- number of followers
    nb_following INT,        -- number of following
    date_creation DATE,      -- when the account was created
    date_updated DATE,       -- when the account was updated by the person

    CONSTRAINT pk_person_git PRIMARY KEY (login_git),
    CONSTRAINT unique_person_git UNIQUE(node_id)
);

/************************************************************************
 * Table Person complement = entite faible (existe pas sans person_git) : more information about the user
 ************************************************************************
 */
CREATE TABLE person_git_comp (
    login_git VARCHAR(100),          -- login of the person on github
    name_person VARCHAR(200),        -- name of the person
    email VARCHAR(100),              -- email of the person
    bio TEXT,                        -- little presentation of the user
    location_person VARCHAR(100),    -- where the person is
    company VARCHAR(100),            -- in which company

    CONSTRAINT pk_person_git_comp PRIMARY KEY (login_git), 
    CONSTRAINT fk_person_git_comp FOREIGN KEY(login_git) REFERENCES person_git(login_git)
);

/************************************************************************
 * Table Workflow = all the informations about the workflow in general
 ************************************************************************
 */

-- Enum about the wf system
CREATE TYPE type_system AS ENUM ('Nextflow', 'SnakeMake');


CREATE TABLE workflow (
    name_full VARCHAR(200),   -- name of the owner + / + name of the workflow
    id_wf INT,                -- auto-increment 
    name_wf VARCHAR(100),     -- name_full but without the name of the owner and the /
    id_git INT,               -- id github of the workflow
    files VARCHAR(500)[],     -- tab with the url 'raw.githubusercontent.com' for all the .nf 
    git_url VARCHAR(100),     -- git url of the wf
    date_creation DATE,       -- date when the wf was created
    date_last_push DATE,      -- date of the last-push 
    date_updated DATE,        -- 
    date_download_json DATE,  -- date when the information of the wf were download 
    description_wf TEXT,      -- description given on the wf
    nb_forks INT,             -- numbers of people who fork the project
    nb_stars INT,             -- numbers of people who star the project
    nb_watchers INT,          -- numbers of people who watch the project
    nb_subscribers INT,       -- numbers of people who subscribe the project
    system_wf type_system,    -- nextflow or snakemake
    archived BOOLEAN,         -- if the wf is archived or not

    login_owner_wf VARCHAR(100), -- git login of the owner of the project

    CONSTRAINT pk_workflow PRIMARY KEY (id_wf),
    CONSTRAINT unique_full_name UNIQUE (name_full),
    CONSTRAINT unique_id_git UNIQUE (id_git),
    CONSTRAINT unique_git_url UNIQUE (git_url),
    CONSTRAINT fk_wf_owner FOREIGN KEY (login_owner_wf) REFERENCES person_git(login_git)
);

/************************************************************************
 * Table wf_Nextflow : dsl 1 or 2 + structure if we know
 ************************************************************************
*/
CREATE TYPE type_dsl AS ENUM ('1','2');

CREATE TABLE wf_nextflow(
    id_wf INT,        -- id of the wf
    dsl type_dsl,     -- to know if the dsl is written in dsl 1 or 2
    structure TEXT,   -- if we know the text of the wf structure (dsl1 in Nextflow)
    CONSTRAINT pk_wf_nextflow PRIMARY KEY (id_wf)
);

/* Sequence pour id automatique id of the worflow */
CREATE SEQUENCE seq_id_wf START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table topics_wf : topic related to the wf
 ************************************************************************
*/
CREATE TABLE topic_wf(
    id_wf INT,
    name_topic VARCHAR(50),

    CONSTRAINT pk_wf_have_topic PRIMARY KEY (id_wf,name_topic),
    CONSTRAINT fk_topic_wf_id FOREIGN KEY(id_wf) REFERENCES workflow(id_wf)
);


/************************************************************************
 * Table Contributor 
 ************************************************************************
 */
CREATE TABLE contributor (
    id_wf INT,   -- id of the workflow
    login_git VARCHAR(100),   -- login of the user

    CONSTRAINT pk_contributor PRIMARY KEY (id_wf,login_git),
    CONSTRAINT fk_id_wf FOREIGN KEY(id_wf) REFERENCES workflow(id_wf),
    CONSTRAINT fk_login_git FOREIGN KEY(login_git) REFERENCES person_git(login_git)
);

/************************************************************************
 * Table Process : : all the information on a process
 ************************************************************************
 */
CREATE TABLE process (
    name_process VARCHAR(300),   -- name_full of the wf and the name of the process
    little_name VARCHAR(100),    -- just the name of the process   ????
    id_process INT,           -- id of the process (auto-increment)
    string TEXT,                 -- the string of the process
    nb_lines INT,                -- the number of lines of the process

    nb_inputs INT,
    nb_outputs INT,

    string_script TEXT,          -- string of the script extract from the process
    language_script VARCHAR(50), -- language of the script   -> enum ?
    nb_lines_script INT,         -- number of lines of the script

    id_wf  INT,                  -- id of the wf in which the process is

    CONSTRAINT pk_process PRIMARY KEY (id_process),   
    CONSTRAINT fk_process FOREIGN KEY(id_wf) REFERENCES workflow(id_wf)
    --CONSTRAINT unique_name_process unique (name_process)
);

/* Sequence pour id automatique process */
CREATE SEQUENCE seq_id_process START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table similarity_process : value of similarity_process between two process 
 ************************************************************************
 */
CREATE TABLE similarity_process (
    id_proc_1 INT,         -- id of the process 1
    id_proc_2 INT,         -- id of the process 2 
    sim_type VARCHAR(25),  -- type of the similarity_process   -> faire un enum avec les differents types
    sim_val NUMERIC,       -- val of the similarity_process

    CONSTRAINT pk_similarity_process PRIMARY KEY (id_proc_1, id_proc_2, sim_type),
    CONSTRAINT fk_id_proc_1 FOREIGN KEY(id_proc_1) REFERENCES process(id_process),
    CONSTRAINT fk_id_proc_2 FOREIGN KEY(id_proc_2) REFERENCES process(id_process)
);

/************************************************************************
 * Table Channel : 
 ************************************************************************
 */
CREATE TYPE type_kind AS ENUM ('input', 'output');
CREATE TYPE type_c AS ENUM ('P', 'A', 'V', 'S');

CREATE TABLE channel (
    id_channel INT,             -- id of the channel (auto-increment)
    name_channel VARCHAR(1000), -- name of the channel
    id_wf INT,                  -- id of the wf
    type_channel type_c,        -- the channel is a pointer (P), a value (V), an adress (A) or a query for the NCBI SRA (S) or Null if we don't know

    CONSTRAINT pk_channel PRIMARY KEY (id_channel)
    CONSTRAINT fk_channel FOREIGN KEY (id_wf) REFERENCES workflow(id_wf)
);

/* Sequence pour id automatique channel */
CREATE SEQUENCE seq_id_channel START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table process_have_channel : 
 ************************************************************************
*/
CREATE TABLE link_process_channel(
    id_proc INT,             -- id of the process
    id_channel INT,          -- id of the channel 
    kind_channel type_kind,  -- if the channel is used to be as an input of a process or an output    

    CONSTRAINT pk_process_have_channel PRIMARY KEY (id_proc, id_channel, kind_channel), 
    CONSTRAINT fk_id_proc FOREIGN KEY(id_proc) REFERENCES process(id_process),
    CONSTRAINT fk_id_channel FOREIGN KEY(id_channel) REFERENCES channel(id_channel)
);

/************************************************************************
 * Table operation_wf : 
 ************************************************************************
*/
CREATE TYPE type_operation AS ENUM ('distinct', 'filter', 'first', 'last', 'randomSample', 'take', 'unique', 'until', -- filtering operators
                                    'buffer', 'collate', 'collect', 'flatten', 'flatMap', 'groupBy', 'groupTuple', 'map', 'reduce', 'toList', 'toSortedList', 'transpose', -- transforming operators
                                    'splitCSV', 'splitFasta', 'splitFastq', 'splitText', -- splitting operators
                                    'cross', 'collectFile', 'combine', 'concat', 'join', 'merge', 'mix', 'phase', 'spread', 'tap', -- combining operators
                                    'branch', 'choise', 'multiMap', 'into', 'separate',  -- forking operators  + have also tap in their operatos but already in combining
                                    'count', 'countBy', 'min', 'max', 'sum', 'toInteger',  -- maths operators
                                    'close', 'dump', 'ifEmpty', 'print', 'println', 'set', 'view');  -- other operators
             
CREATE TABLE operation_wf(
    id_ope INT,                 -- auto increment  
    id_wf INT,                  -- id in the wf
    string_ope VARCHAR(65000),  -- string of the operation

    CONSTRAINT pk_operation_wf PRIMARY KEY (id_ope)
    CONSTRAINT fk_operation_wf REFERENCES workflow(id_wf)
);

/* Sequence pour id automatique id operation_wf*/
CREATE SEQUENCE seq_id_operation_wf START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table channel_have_operation : 
 ************************************************************************
*/
CREATE TABLE link_channel_operation(
    id_channel INT,  -- id of the channel
    id_ope INT,      -- id of the operation 
    kind_ope type_kind,  -- the type of the channel made

    CONSTRAINT pk_channel_have_operation PRIMARY KEY (id_channel, id_ope, kind_ope),
    CONSTRAINT fk_operation_c FOREIGN KEY(id_ope) REFERENCES operation_wf(id_ope),
    CONSTRAINT fk_channel_o FOREIGN KEY(id_channel) REFERENCES channel(id_channel)

);

/************************************************************************
 * Table Tools : global informations on a tools 
 ************************************************************************
*/
CREATE TABLE tool (
    url_biotools VARCHAR(200),
    name_tool VARCHAR(100),
    description_tool VARCHAR(1000), 
    homepage VARCHAR(200) ,

    CONSTRAINT pk_tool PRIMARY KEY (url_biotools),
    CONSTRAINT unique_name_tool UNIQUE (name_tool)  -- a revoir
);

/************************************************************************
 * Table tool_in_workflow
 ************************************************************************
 */
CREATE TABLE tool_in_workflow (
    url_biotools VARCHAR(200),  
    id_wf INT,                -- id of the wf

    CONSTRAINT pk_tool_in_workflow PRIMARY KEY (url_biotools,id_wf),
    CONSTRAINT fk_tool_in_wf FOREIGN KEY(url_biotools) REFERENCES tool(url_biotools),
    CONSTRAINT fk_id_wf FOREIGN KEY(id_wf) REFERENCES workflow(id_wf)
);

/************************************************************************
 * Table tool_in_process
 ************************************************************************
 */
CREATE TABLE tool_in_process (
    url_biotools VARCHAR(200), -- id of the tool
    id_proc INT,  -- id of the process

    CONSTRAINT pk_tool_in_process PRIMARY KEY (url_biotools,id_proc),
    CONSTRAINT fk_tool_in_process FOREIGN KEY(url_biotools) REFERENCES tool(url_biotools),
    CONSTRAINT fk_id_proc FOREIGN KEY(id_proc) REFERENCES process(id_process)
);

/************************************************************************
 * Table Topic 
 ************************************************************************
 */
CREATE TABLE topic_tools (
    id_topic INT,
    topic_uri VARCHAR(100), -- uri of edam
    term VARCHAR(100),      -- little words on the topic

    CONSTRAINT pk_topic_tools PRIMARY KEY (id_topic) 

);

CREATE SEQUENCE seq_id_topic_tools START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table tools_have_topic
 ************************************************************************
 */
CREATE TABLE tools_have_topic (   
    url_biotools VARCHAR(200), -- id of the tool
    id_topic INT,  

    CONSTRAINT pk_tools_have_topic PRIMARY KEY (url_biotools,id_topic),
    CONSTRAINT fk_tools_id_tools_topic FOREIGN KEY(url_biotools) REFERENCES tool(url_biotools),
    CONSTRAINT fk_topic_id FOREIGN KEY(id_topic) REFERENCES topic_tools(id_topic)
);

/************************************************************************
 * Table operation_tool
 ************************************************************************
 */
CREATE TABLE operation_tool (  
    id_operation INT,
    operation_uri VARCHAR(100), 
    term VARCHAR(100),          -- little words on the topic

    CONSTRAINT pk_operation_tool PRIMARY KEY (id_operation)
);

CREATE SEQUENCE seq_id_operation_tools START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table tools_have_operation
 ************************************************************************
 */
CREATE TABLE tools_have_operation (
    url_biotools VARCHAR(200),    -- id of the tools
    id_operation INT,

    CONSTRAINT pk_tools_have_operation PRIMARY KEY (url_biotools,id_operation),
    CONSTRAINT fk_tools_id_tool_ope FOREIGN KEY(url_biotools) REFERENCES tool(url_biotools),
    CONSTRAINT fk_ope_id FOREIGN KEY(id_operation) REFERENCES operation_tool(id_operation)
);

/************************************************************************
 * Table in_out_data  
 ************************************************************************
*/
CREATE TABLE in_out_data (
    id_in_out INT,           -- auto-increment
    in_out_uri VARCHAR(100), -- EDAM uri
    term VARCHAR(100),       -- little explanation
    in_or_out type_kind,     -- used as input or output 
    
    CONSTRAINT pk_in_out_data PRIMARY KEY (id_in_out) 
);

/* Sequence pour id automatique in_out_tool */
CREATE SEQUENCE seq_id_in_out_tool START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table tools_have_in_out 
 ************************************************************************
*/
CREATE TABLE tools_have_in_out(
    id_in_out INT,            --  id input or output
    url_biotools VARCHAR(200),

    CONSTRAINT pk_tools_have_in_out PRIMARY KEY (id_in_out,url_biotools),
    CONSTRAINT fk_tools_have_id_in_out FOREIGN KEY(id_in_out) REFERENCES in_out_data(id_in_out),
    CONSTRAINT fk_tools_have_url_biotools FOREIGN KEY(url_biotools) REFERENCES tool(url_biotools)
);