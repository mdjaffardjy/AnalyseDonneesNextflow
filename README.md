[![Actions Status](https://github.com/IFB-ElixirFr/fair-checker/workflows/Build%20and%20test/badge.svg)](https://github.com/IFB-ElixirFr/fair-checker/actions) [![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Version 1.0.1](https://img.shields.io/badge/version-v1.0.1-blue)]()


# AnalyseDonneesNextflow

In this repository are presented multiple tools :

- The main one __'Nextflow analyzer'__ allows users to extract information (info on processes or and the structure) of a single or multiple Nextflow workflows. This tool is found here at the root.
- The second one __'ProSim'__ allows users to compare processes following different hypotheses, it is presented and is found [here](/Analysis/Similarity%20Processes/) 
- The final one _#TODO -> Clémence_

Main contributors are: 
- [Clémence Sebe](https://github.com/ClemenceS)
- [George Marchment](https://github.com/George-Marchment)
 

## Main features



## Known bugs

  - None

## Contribute
Please submit GitHub issues to provide feedback or ask for new features, and contact us for any related question.


## Install and Run

### To install :
```
sudo python3 setup.py install
```

### To run :

See [here](Docs/Examples%20Nextflow%20Analyzer.pdf) for a more explicit explanation on how to run the analyzer

#### __Single mode (DSL1 workflow) :__

When analyzing a single DSL1 workflow, the analyzer needs as input the address of the main of the workflow.

```
NFanalyzer --input 'address/to_folder/to_workflow.nf' --results_directory 'address/to_save' --name 'New_Analysis' --mode 'single'
```
![Example](Pictures/1.png)

#### __Single mode (DSL2 workflow) :__

When analyzing a single DSL2 workflow, the analyzer needs as input the address of a folder containing the nextflow files of the workflow.

```
NFanalyzer --input 'address/to_folder/to_workflow' --results_directory 'address/to_save' --name 'New_Analysis' --mode 'single'
```
![Example](Pictures/2.png)

#### __Multi mode :__

When analyzing a multiple workflows, the analyzer needs as input the address of a folder containing the all the workflows wanting to be analyzed.

```
NFanalyzer --input 'address/to_folder/to_workflows' --results_directory 'address/to_save' --name 'New_Analysis' --mode 'multi'
```
![Example](Pictures/3.png)


### Requirements 

Your software environment needs the following Python packages : 

- setuptools
- argparse
- pathlib
- os
- glob2
- re
- graphviz
- json
- rdflib
- jellyfish
- glob
- threading
- queue
- time
- sys
- functools
- ntpath 

## License
FAIR-Checker is released under the [MIT License](LICENSE). Some third-party components are included. They are subject to their own licenses. All of the license information can be found in the included [LICENSE](LICENSE) file.

## Funding
#TODO
