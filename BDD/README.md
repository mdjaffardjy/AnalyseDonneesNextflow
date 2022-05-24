# AddInDatabase

In this directory is presented the tool __AddInDatabase__, which allows to fill a database implemented with Postgresql.

<ins>Database Schema :</ins>
![Schema](Pictures/0.png)

To launch this tool, you need to have the folder containing the results of the __Nextflow analyser__ and a folder with the __global information__ (author and information about the workflow from github)

1. The folder containing the results of the __Nextflow analyser__  must contain all the workflow results folder :

Obtain with the command : 
```
NFanalyzer --input "/home/clemence/AnalyseDonneesNextflow/bddFiles" --results_directory "/home/clemence/AnalyseDonneesNextflow"  --name 'Result_Nfanalyser' --mode 'multi'
```

![Example](Pictures/5.png)

* A workflow written in DSL1 must contain in it repository 7 files:

![Example](Pictures/6.png)

* And a DSL2 workflow contain only 1 file : 

![Example](Pictures/7.png)

2. The __global information__ folder must contain at least 2 files : one with the *wf* in it name and a second with the word *author*. **Warning** : not two distinct files in this directory must contain in their names *wf* or *author*

![Example](Pictures/8.png)

## Install and Run

To install and run this tool, you first need to be __in this directory__.

### <ins>Postgrsql Connection file configuration</ins> :

This file is located in the [resources](/BDD/resources/) folder. How find the information to complete the documentation :

* In a terminal open a postgresql session: ```psql```
* Then type the command: ```\conninfo```
* To finish, put your parameters in the config file and add your password.

![Example](Pictures/1.png)

### <ins>To install</ins> :

```
sudo python3 setup.py install
```

### <ins>Before running </ins> :

In the postgresql session launch the [script](/BDD/TablesSql/createTables.sql) to create the tables :

Command : 
```\i address_to_the_script_if_not_in_the_same_directory/createTables.sql ```

![Example](Pictures/3.png)
![Example](Pictures/4.png)


### <ins>To run</ins> :

* The option *--system* : 'N' (Nextflow) 

```
AddInDatabase --system 'N' --results_directory 'address/to_folder/to_result' --json_directory 'address/to_folder/to_json_information'
```

![Example](Pictures/2.png)

### Requirements 
Your software environment needs the following Python packages : 
* configparser
* argparse
* psycopg
* pathlib
* datetime
* glob
* json
* os