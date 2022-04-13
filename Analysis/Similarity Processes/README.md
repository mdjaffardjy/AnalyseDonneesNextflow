# ProSim

In this repository is presented the tool __ProSim__, which allows users to compare processes (in the forme of a json file : output of __Nextflow Analyzer__) folowing different hypotheses. These different hypotheses are presente in the [Jupyter notebook](mesure_similarity.ipynb).

The results of __Prosim__ are presented in different _csv(s)_ files in the form of matrixes.

## Install and Run

### <ins>To install</ins> :
```
sudo python3 setup.py install
```

### <ins>To run</ins> :

#### __Single mode :__ 
```
ProSim --mode "single" --results_directory "some/adress" --processA "address/to/json/A" --processB "address/to/json/B"
```
#### __Multi mode :__
```
ProSim --mode "multi" --results_directory "some/adress" --processes "address/to/the/json/of/the/processes/"
```
