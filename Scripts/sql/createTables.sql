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

    string_script TEXT,          -- string of the script extract from the process
    language_script VARCHAR(50), -- language of the script   -> enum ?
    nb_lines_script INT,         -- number of lines of the script

    id_wf  INT,                  -- id of the wf in which the process is

    CONSTRAINT pk_process PRIMARY KEY (id_process),   -- je voudrais aussi rajouter name_process mais j'y arrive pas car je fais une reference dans similarity_process
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

    CONSTRAINT pk_similarity_process PRIMARY KEY (id_proc_1, id_proc_2),
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
    id_channel INT,            -- id of the channel (auto-increment)
    string_channel VARCHAR(100),  -- string of the channel
    type_channel type_c,          -- the channel is a pointer (P), a value (V), an adress (A) or a query for the NCBI SRA (S)
    kind_channel type_kind,       -- if the channel is used to be as an input of a process or an output    

    CONSTRAINT pk_channel PRIMARY KEY (id_channel)
);

/* Sequence pour id automatique channel */
CREATE SEQUENCE seq_id_channel START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table process_have_channel : 
 ************************************************************************
*/
CREATE TABLE process_have_channel(
    id_proc INT,     -- id of the process
    id_channel INT,  -- id of the channel 

    CONSTRAINT pk_process_have_channel PRIMARY KEY (id_proc, id_channel), 
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
    id_ope INT,            -- auto increment  
    id_in_wf INT,             -- id George (id in the wf)
    name_ope type_operation,  -- type of the operation

    CONSTRAINT pk_operation_wf PRIMARY KEY (id_ope)
);

/* Sequence pour id automatique id operation_wf*/
CREATE SEQUENCE seq_id_operation_wf START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table channel_have_operation : 
 ************************************************************************
*/
CREATE TABLE channel_have_operation(
    id_channel INT,  -- id of the channel
    id_ope INT,      -- id of the operation 
    kind type_kind,  -- the type of the channel made

    CONSTRAINT pk_channel_have_operation PRIMARY KEY (id_channel, id_ope),
    CONSTRAINT fk_operation_c FOREIGN KEY(id_ope) REFERENCES operation_wf(id_ope),
    CONSTRAINT fk_channel_o FOREIGN KEY(id_channel) REFERENCES channel(id_channel)

);

/************************************************************************
 * Table Tools : global informations on a tools 
 ************************************************************************
*/
CREATE TABLE tool (
    biotoolsID VARCHAR(100) ,--CHECK (biotoolsID ~* '[_\-.0-9a-zA-Z]*'),            -- biotoolsID
    name_tool VARCHAR(100) ,--CHECK (name_tool ~* '[\p{Zs}A-Za-z0-9+\.,\-_:;()]*'), -- name of the tool 
    description_tool VARCHAR(1000),                                              -- description of the tool
    homepage VARCHAR(200) ,--CHECK (homepage ~* 'http(s?)://[^\s/$.?#].[^\s]*'),    -- url of the tool page
    url_biotools VARCHAR(100),                                                   -- url on biotools

    CONSTRAINT pk_tool PRIMARY KEY (biotoolsID)
);

CREATE TYPE type_accessibility AS ENUM ('[]', 'Open access', 'Open access (with restrictions)', 'Restricted access');
CREATE TYPE type_elixirNode AS ENUM ('[]','Data', 'Tools', 'Compute', 'Interoperability', 'Training');
CREATE TYPE type_elixirPlatform AS ENUM ('[]','Belgium', 'Czech Republic', 'Denmark','EMBL','Estonia', 'Finland',
                                            'France', 'Germany', 'Greece', 'Hungary', 'Ireland', 'Israel', 
                                            'Italy', 'Luxembourg', 'Netherlands', 'Norway', 'Portugal', 'Slovenia',
                                            'Spain', 'Sweden', 'Switzerland','UK');
CREATE TYPE type_license_tool AS ENUM ('None','0BSD', 'AAL', 'ADSL', 'AFL-1.1', 'AFL-1.2', 'AFL-2.0', 'AFL-2.1', 'AFL-3.0', 'AGPL-1.0', 'AGPL-3.0', 'AMDPLPA', 'AML', 'AMPAS', 'ANTLR-PD',
                                        'APAFML', 'APL-1.0', 'APSL-1.0', 'APSL-1.1', 'APSL-1.2', 'APSL-2.0', 'Abstyles', 'Adobe-2006', 'Adobe-Glyph', 'Afmparse', 'Aladdin', 'Apache-1.0',
                                        'Apache-1.1', 'Apache-2.0', 'Artistic-1.0', 'Artistic-1.0-Perl', 'Artistic-1.0-cl8', 'Artistic-2.0', 'BSD-2-Clause', 'BSD-2-Clause-FreeBSD', 
                                        'BSD-2-Clause-NetBSD', 'BSD-3-Clause', 'BSD-3-Clause-Attribution', 'BSD-3-Clause-Clear', 'BSD-3-Clause-LBNL', 'BSD-3-Clause-No-Nuclear-License', 
                                        'BSD-3-Clause-No-Nuclear-License-2014', 'BSD-3-Clause-No-Nuclear-Warranty', 'BSD-4-Clause', 'BSD-4-Clause-UC', 'BSD-Protection', 'BSD-Source-Code', 
                                        'BSL-1.0', 'Bahyph', 'Barr', 'Beerware', 'BitTorrent-1.0', 'BitTorrent-1.1', 'Borceux', 'CATOSL-1.1', 'CC-BY-1.0', 'CC-BY-2.0', 'CC-BY-2.5', 'CC-BY-3.0', 
                                        'CC-BY-4.0', 'CC-BY-NC-1.0', 'CC-BY-NC-2.0', 'CC-BY-NC-2.5', 'CC-BY-NC-3.0', 'CC-BY-NC-4.0', 'CC-BY-NC-ND-1.0', 'CC-BY-NC-ND-2.0', 'CC-BY-NC-ND-2.5', 
                                        'CC-BY-NC-ND-3.0', 'CC-BY-NC-ND-4.0', 'CC-BY-NC-SA-1.0', 'CC-BY-NC-SA-2.0', 'CC-BY-NC-SA-2.5', 'CC-BY-NC-SA-3.0', 'CC-BY-NC-SA-4.0', 'CC-BY-ND-1.0', 
                                        'CC-BY-ND-2.0', 'CC-BY-ND-2.5', 'CC-BY-ND-3.0', 'CC-BY-ND-4.0', 'CC-BY-SA-1.0', 'CC-BY-SA-2.0', 'CC-BY-SA-2.5', 'CC-BY-SA-3.0', 'CC-BY-SA-4.0', 'CC0-1.0', 
                                        'CDDL-1.0', 'CDDL-1.1', 'CECILL-1.0', 'CECILL-1.1', 'CECILL-2.0', 'CECILL-2.1', 'CECILL-B', 'CECILL-C', 'CNRI-Jython', 'CNRI-Python', 
                                        'CNRI-Python-GPL-Compatible', 'CPAL-1.0', 'CPL-1.0', 'CPOL-1.02', 'CUA-OPL-1.0', 'Caldera', 'ClArtistic', 'Condor-1.1', 'Crossword', 'CrystalStacker', 
                                        'Cube', 'D-FSL-1.0', 'DOC', 'DSDP', 'Dotseqn', 'ECL-1.0', 'ECL-2.0', 'EFL-1.0', 'EFL-2.0', 'EPL-1.0', 'EUDatagrid', 'EUPL-1.0', 'EUPL-1.1', 'Entessa', 
                                        'ErlPL-1.1', 'Eurosym', 'FSFAP', 'FSFUL', 'FSFULLR', 'FTL', 'Fair', 'Frameworx-1.0', 'FreeImage', 'GFDL-1.1', 'GFDL-1.2', 'GFDL-1.3', 'GL2PS', 'GPL-1.0', 
                                        'GPL-2.0', 'GPL-3.0', 'Giftware', 'Glide', 'Glulxe', 'HPND', 'HaskellReport', 'IBM-pibs', 'ICU', 'IJG', 'IPA', 'IPL-1.0', 'ISC', 'ImageMagick', 'Imlib2', 
                                        'Info-ZIP', 'Intel', 'Intel-ACPI', 'Interbase-1.0', 'JSON', 'JasPer-2.0', 'LAL-1.2', 'LAL-1.3', 'LGPL-2.0', 'LGPL-2.1', 'LGPL-3.0', 'LGPLLR', 'LPL-1.0', 
                                        'LPL-1.02', 'LPPL-1.0', 'LPPL-1.1', 'LPPL-1.2', 'LPPL-1.3a', 'LPPL-1.3c', 'Latex2e', 'Leptonica', 'LiLiQ-P-1.1', 'LiLiQ-R-1.1', 'LiLiQ-Rplus-1.1', 'Libpng',
                                        'MIT', 'MIT-CMU', 'MIT-advertising', 'MIT-enna', 'MIT-feh', 'MITNFA', 'MPL-1.0', 'MPL-1.1', 'MPL-2.0', 'MPL-2.0-no-copyleft-exception', 'MS-PL', 'MS-RL', 
                                        'MTLL', 'MakeIndex', 'MirOS', 'Motosoto', 'Multics', 'Mup', 'NASA-1.3', 'NBPL-1.0', 'NCSA', 'NGPL', 'NLOD-1.0', 'NLPL', 'NOSL', 'NPL-1.0', 'NPL-1.1', 
                                        'NPOSL-3.0', 'NRL', 'NTP', 'Naumen', 'NetCDF', 'Newsletr', 'Nokia', 'Noweb', 'Nunit', 'OCCT-PL', 'OCLC-2.0', 'ODbL-1.0', 'OFL-1.0', 'OFL-1.1', 'OGTSL', 
                                        'OLDAP-1.1', 'OLDAP-1.2', 'OLDAP-1.3', 'OLDAP-1.4', 'OLDAP-2.0', 'OLDAP-2.0.1', 'OLDAP-2.1', 'OLDAP-2.2', 'OLDAP-2.2.1', 'OLDAP-2.2.2', 'OLDAP-2.3', 
                                        'OLDAP-2.4', 'OLDAP-2.5', 'OLDAP-2.6', 'OLDAP-2.7', 'OLDAP-2.8', 'OML', 'OPL-1.0', 'OSET-PL-2.1', 'OSL-1.0', 'OSL-1.1', 'OSL-2.0', 'OSL-2.1', 'OSL-3.0', 
                                        'OpenSSL', 'PDDL-1.0', 'PHP-3.0', 'PHP-3.01', 'Plexus', 'PostgreSQL', 'Python-2.0', 'QPL-1.0', 'Qhull', 'RHeCos-1.1', 'RPL-1.1', 'RPL-1.5', 'RPSL-1.0', 
                                        'RSA-MD', 'RSCPL', 'Rdisc', 'Ruby', 'SAX-PD', 'SCEA', 'SGI-B-1.0', 'SGI-B-1.1', 'SGI-B-2.0', 'SISSL', 'SISSL-1.2', 'SMLNJ', 'SMPPL', 'SNIA', 'SPL-1.0', 
                                        'SWL', 'Saxpath', 'Sendmail', 'SimPL-2.0', 'Sleepycat', 'Spencer-86', 'Spencer-94', 'Spencer-99', 'SugarCRM-1.1.3', 'TCL', 'TMate', 'TORQUE-1.1', 'TOSL', 
                                        'UPL-1.0', 'Unicode-TOU', 'Unlicense', 'VOSTROM', 'VSL-1.0', 'Vim', 'W3C', 'W3C-19980720', 'WTFPL', 'Watcom-1.0', 'Wsuipa', 'X11', 'XFree86-1.1', 'XSkat', 
                                        'Xerox', 'Xnet', 'YPL-1.0', 'YPL-1.1', 'ZPL-1.1', 'ZPL-2.0', 'ZPL-2.1', 'Zed', 'Zend-2.0', 'Zimbra-1.3', 'Zimbra-1.4', 'Zlib', 'bzip2-1.0.5', 
                                        'bzip2-1.0.6', 'curl', 'diffmark', 'dvipdfm', 'eGenix', 'gSOAP-1.3b', 'gnuplot', 'iMatix', 'libtiff', 'mpich2', 'psfrag', 'psutils', 'xinetd', 'xpp', 
                                        'zlib-acknowledgement', 'Proprietary', 'Freeware', 'Other', 'Not licensed');


/************************************************************************
 * Table Tool complement = entite faible (existe pas sans tool) : more information about the tool
 ************************************************************************
*/
CREATE TABLE tool_comp (
    biotoolsID VARCHAR(100) CHECK (biotoolsID ~* '[_\-.0-9a-zA-Z]*'),                       -- biotools ID
    version_tool VARCHAR(100)[],                                                            -- tab of the version which already exists
    license VARCHAR(25),                                                                    -- under which license
    accessibility type_accessibility[],                                                       -- if the tool is under restrictions or not
    elixirNode type_elixirNode[],                                                             -- elixir Node
    elixirPlatform type_elixirPlatform[],                                                     -- elixir platform (which country)

    CONSTRAINT pk_tool_comp PRIMARY KEY (biotoolsID), -- il y a que ca ou autre chose ?
    CONSTRAINT fk_tool_comp FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID)
);

CREATE TABLE collectionID(
    biotoolsID VARCHAR(100),                                                                 -- id of the tool
    name_collection VARCHAR(100),-- CHECK (name_collection ~* '[\p{Zs}A-Za-z0-9+\.,\-_:;()]*'), -- a collection that the software has been assigned in bio.tools 
    
    CONSTRAINT pk_collectionID PRIMARY KEY (biotoolsID,name_collection),
    CONSTRAINT fk_tool_collection FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID)
);

/************************************************************************
 * Table tool_in_workflow
 ************************************************************************
 */
CREATE TABLE tool_in_workflow (
    biotoolsID VARCHAR(100),  -- id of the tool
    id_wf INT,                -- id of the wf

    CONSTRAINT pk_tool_in_workflow PRIMARY KEY (biotoolsID,id_wf),
    CONSTRAINT fk_tool_id_wf FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID),
    CONSTRAINT fk_id_wf FOREIGN KEY(id_wf) REFERENCES workflow(id_wf)
);

/************************************************************************
 * Table tool_in_process
 ************************************************************************
 */
CREATE TABLE tool_in_process (
    biotoolsID VARCHAR(100), -- id of the tool
    id_proc INT,  -- id of the process

    CONSTRAINT pk_tool_in_process PRIMARY KEY (biotoolsID,id_proc),
    CONSTRAINT fk_tool_id_proc FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID),
    CONSTRAINT fk_id_proc FOREIGN KEY(id_proc) REFERENCES process(id_process)
);

/************************************************************************
 * Table Topic 
 ************************************************************************
 */
CREATE TABLE topic_tools (
    id_topic INT,
    topic_url VARCHAR(100), -- url of edam
    term VARCHAR(100),      -- little words on the topic

    CONSTRAINT pk_topic_tools PRIMARY KEY (id_topic) -- il y a que ca ou autre chose car cardinalite bizarre?

);

CREATE SEQUENCE seq_id_topic_tools START WITH 1 INCREMENT BY 1;


/*
        uri
                Required: No (if term present), Yes (otherwise)
                Cardinality: 0 or 1
                Type: URL

        term
                Required: No (if URI present), Yes (otherwise)
                Cardinality: 0 or 1
                Type: String

=> si il nous en manque un requete edam pour avoir le second ?
*/

/************************************************************************
 * Table tools_have_topic
 ************************************************************************
 */
CREATE TABLE tools_have_topic (   
    biotoolsID VARCHAR(100), -- id of the tool
    id_topic INT,  -- edam url

    CONSTRAINT pk_tools_have_topic PRIMARY KEY (biotoolsID,id_topic),
    CONSTRAINT fk_tools_id_tools_topic FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID),
    CONSTRAINT fk_topic_id FOREIGN KEY(id_topic) REFERENCES topic_tools(id_topic)
);

/************************************************************************
 * Table operation_tool
 ************************************************************************
 */
CREATE TABLE operation_tool (  -- comme topic_tools je peux avoir que l'un des deux
    id_operation INT,
    operation_url VARCHAR(100), -- edam url
    term VARCHAR(100),          -- little words on the topic

    CONSTRAINT pk_operation_url PRIMARY KEY (id_operation)
);

CREATE SEQUENCE seq_id_operation_tools START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table tools_have_operation
 ************************************************************************
 */
CREATE TABLE tools_have_operation (
    biotoolsID VARCHAR(100),    -- id of the tools
    id_operation INT,

    CONSTRAINT pk_tools_have_operation PRIMARY KEY (biotoolsID,id_operation),
    CONSTRAINT fk_tools_id_tool_ope FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID),
    CONSTRAINT fk_ope_id FOREIGN KEY(id_operation) REFERENCES operation_tool(id_operation)
);

/************************************************************************
 * Table in_out_data  
 ************************************************************************
*/
CREATE TABLE in_out_data (
    id_in_out INT,           -- auto-increment
    in_out_url VARCHAR(100), -- EDAM url
    term VARCHAR(100),       -- little explanation
    in_or_out type_kind,     -- used as input or output 
    
    CONSTRAINT pk_in_out_data PRIMARY KEY (id_in_out) 
);

/* Sequence pour id automatique in_out_tool */
CREATE SEQUENCE seq_id_in_out_tool START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table in_out_format 
 ************************************************************************
*/
CREATE TABLE in_out_format (
    id_in_out_format INT,           -- auto-increment
    url_format VARCHAR(100), --edam url
    term VARCHAR(100), -- little explanation

    CONSTRAINT pk_in_out_format PRIMARY KEY (id_in_out_format)
);

CREATE SEQUENCE seq_id_in_out_tool_format START WITH 1 INCREMENT BY 1;


/************************************************************************
 * Table in_out_link_data_format 
 ************************************************************************
*/
CREATE TABLE in_out_link_data_format(
    id_in_out INT,              -- id of the tool data
    id_in_out_format INT,    -- url of the tool format

    CONSTRAINT pk_in_out_link_data_format PRIMARY KEY (id_in_out,id_in_out_format),
    CONSTRAINT fk_id_in_out FOREIGN KEY(id_in_out) REFERENCES in_out_data(id_in_out),
    CONSTRAINT fk_id_format FOREIGN KEY(id_in_out_format) REFERENCES in_out_format(id_in_out_format)
);


/************************************************************************
 * Table tools_have_in_out 
 ************************************************************************
*/
CREATE TABLE tools_have_in_out(
    id_in_out INT,            --  id input or output
    biotoolsID VARCHAR(100),  -- biotoolsID

    CONSTRAINT pk_tools_have_in_out PRIMARY KEY (id_in_out,biotoolsID),
    CONSTRAINT fk_tools_have_id_in_out FOREIGN KEY(id_in_out) REFERENCES in_out_data(id_in_out),
    CONSTRAINT fk_tools_have_biotoolsID FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID)
);


/************************************************************************
 * Table Credit : information about the contact of a tool 
 ************************************************************************
 */
CREATE TYPE type_entity AS ENUM ('Person', 'Project', 'Division', 'Institute', 'Consortium', 'Funding agency');

CREATE TABLE credit_tool (
    id_credit INT,                                                                                                                               -- key auto-increment : il n'y a aucun element qu'on est sur a 100% de retrouver chez tout le monde
    name_credit VARCHAR(100),                                                                                                                       --name 
    email VARCHAR(100) , --CHECK (email ~* '[A-Za-z0-9_]+([-+.’][A-Za-z0-9_]+)*@[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*.[A-Za-z0-9_]+([-.][A-Za-z0-9_]+)*'),  -- email
    type_entity_credit type_entity,                                                                                                                 -- type of the credit if it's a person, a project ...

    CONSTRAINT pk_credit_tool PRIMARY KEY (id_credit)
);

/* Sequence pour id automatique id_credit */
CREATE SEQUENCE seq_id_credit START WITH 1 INCREMENT BY 1;

/************************************************************************
 * Table Credit complement = entite faible (existe pas sans credit_tool) : more information about the credits
 ************************************************************************
 */
CREATE TABLE credit_tool_comp (
    id_credit INT,                                                                                  -- id of the credit
    credit_url VARCHAR(200), -- CHECK (credit_url ~* 'http(s?)://[^s/$.?#].[^s]*'),                     -- page web
    orcidid VARCHAR(100), -- CHECK (orcidid ~* 'http://orcid.org/[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}'), -- orcid (identify of a researcher)
 
    CONSTRAINT pk_credit_tool_comp PRIMARY KEY (id_credit), -- il y a que ca ou autre chose ?
    CONSTRAINT fk_credit_tool_comp FOREIGN KEY(id_credit) REFERENCES credit_tool(id_credit)
    --CONSTRAINT unique_orcidid UNIQUE (orcidid)
);

/************************************************************************
 * Table tools_contact_credit
 ************************************************************************
 */
CREATE TYPE type_role AS ENUM ('Developer', 'Maintainer', 'Provider', 'Documentor', 'Contributor', 'Support', 'Primary contact');

CREATE TABLE tools_contact_credit (
    biotoolsID VARCHAR(100),        -- id of the tools
    id_credit INT,                  -- id of the credit
    type_role_entity  type_role[],  -- type of the credit    -- modif on supprime la tab ???

    CONSTRAINT pk_tools_contact_credit PRIMARY KEY (biotoolsID, id_credit),
    CONSTRAINT fk_tools_contact_credit_tool FOREIGN KEY(biotoolsID) REFERENCES tool(biotoolsID),
    CONSTRAINT fk_tools_contact_credit_id FOREIGN KEY(id_credit) REFERENCES credit_tool(id_credit)
);

