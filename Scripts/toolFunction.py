"""
author : marinedjaffardjy 
"""

import ntpath
import re
import requests
from ratelimiter import RateLimiter
import json
from .search_biotools_dump import *

EXCEPTIONS = ["export", 'awk', 'sed', 'grep', "cmd", "module", "cat", "elif", "sort", "cd", "zcat",
              "rm", "for", "find", "java", "forgi", "sleep", "tabix", "zgrep", "wget", "mv", "mkdir", "echo",
              'FS', 'head', 'Rscript', "python", "jekyll","bgzip", "tr", "dot", "tRNA", "header", "fi", "then",
              "read", "do","else","cut", "wc", "tar", "gzip", "cool", "if", "turn", "git", "checkm", "cp", "make", "pour",
              "NR", "melt" , "read", "tail", "genes", "add", "bc", "scp", "scif", "uniq", "ln", "set", "zip", "time", "ls",
              "print","make", "pour", "source", "melt", "paste", "split", "layer", "touch" , "google-chrome", "query"
              "curl", "snps", "def"]

def path_leaf(path):
    """
    author : marinedjaffardjy 
    """
    # extract last word from path -- useful for extracting toolnames
    # input : string path name
    # output string last element of path
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def parse_lines(compil):
    """
    author : marinedjaffardjy 
    """
    # returns a list of lines from the shell data
    # input : shell content (string)
    # output : list of command lines as a list of strings
    lines_list = []
    for whole_line in compil.split('\n'):
        # check if the line has at least one character
        if (re.search('[a-zA-Z]', whole_line) is not None):  # checks that the line contains a character
            # split the line into several lines if there is a |, a ; or a >
            if any(ext in whole_line for ext in ['', '|', ';', '>']):
                whole_line = whole_line.split('|')
                for subline in whole_line:
                    subline = subline.split('>')
                    for subsubline in subline:
                        subsubline = subsubline.split(';')
                        for el in subsubline:
                            lines_list.append(el)
    return lines_list

def get_toolname_from_line(line):
    """
    author : marinedjaffardjy 
    """
    # get command from a line
    # input : a line (string)
    # output : a command word (string) or a tuple of two words (string, string) or none if the toolname is not relevant
    while (len(line) > 1 and line[0] == ' '):
        line = line[1:]
    line = line.replace('cmd ( "', "")
    tool = line.split(' ')[0].replace('\t', '').replace('"', '').replace("'",
                                                                             '')  # just for syntax, take out the tabs
    if ("=" in tool):
        tool.split('=')[0]
    if ("'" in tool):
        tool = tool.replace("'", '')
    # if the tool is in a command with a path ex /home/marine\.outil
    if ('/' in tool):
        tool = path_leaf(tool)
    if ('bowtie-' in tool):
        tool = "bowtie"
    if ('htseq-count' in tool):
        tool = "htseqcount"
    # look for second word :
    if len(line.split(' ')) > 1:
        sec_word = line.split(' ')[1]  # weget the second word
        # if the second word starts with a letter and is bigger than one letter, we take it into account
        if (len(sec_word) > 1):
            if (re.search('[a-zA-Z]', sec_word[0]) is not None and len(sec_word) > 1):
                # if the second word doesn't have an extension, we take it into account
                if ('.' not in sec_word):
                    # print("second word " + sec_word)
                    return [tool, sec_word]
    return [tool]

def get_toolnames(strScript):
    """
    author : marinedjaffardjy 
    Add some little changes : 
    Insteed of working on all Wf -> just the string of the script
    """
    toolnames = []
    scripts_python = []
    scripts_R = []
    scripts_bash = []
      
    lines_list = parse_lines(strScript)
    for line in lines_list:
        # print("line "+line)
        toolname = get_toolname_from_line(line)
        # print(toolname)
        if (re.search('[a-zA-Z]', toolname[0]) is not None and len(
                    toolname[
                            0]) > 1):  # if the toolname is comprised of at least one letter and is of length sup to one
            if (re.search('[a-zA-Z]', toolname[0][
                0]) is not None):  # if the toolname doesn't start with a special character
                    # # on cherche les scripts python
                    # if toolname[0] == "python":
                    #     scripts_python.append(toolname)
                    # # on cherche els scripts R
                    # if toolname [0]== "Rscript":
                    #     scripts_R.append(toolname)
                    # # on cherche les scripts bash
                    # if toolname[0][-3:]== ".sh":
                    #     scripts_bash.append(toolname)

                    if (toolname[0] not in EXCEPTIONS ):
                        if ('(' not in toolname[0] and '{' not in toolname[0] and '#' not in toolname[0] and "=" not in toolname[0] and '\\' not in toolname[0] and '.' not in toolname[0]):
                            toolnames.append(toolname)
                            # print("line " + line)
    #print(toolnames)
    return toolnames   
 #------------------------------------------------------------------------------------------------
 #------------------------------------------------------------------------------------------------
def get_info_biotools_set_of_tools_dump(set_tools, treshold = 5):
    """
    author : marinedjaffardjy 
    """
    # queries the biotools dump for a set of tools
    #we can control the treshold of selectivity for the levensthein distance score
    # intput : a set of strings of toolnames
    # output : a dict of dict of tools annotation, with the key being the given toolname
    dict_tools = {}
    #TODO : faire une fct pour séparer le tri
    for tool in set_tools:
        if (re.search('[a-zA-Z]',tool[0]) is not None):  # checks that the linetoolname contains a character, should be redundant but just in case
            if (tool[0] not in ["module", "cat", "elif", "sort", "cd", "zcat", "rm", "zgrep", "wget", "mv", "mkdir",
                             "echo", "dot", "gunzip", "pandoc", "pdflatex", "python", "sleep", "done", "perl", "egrep", "tr", "rev", "jekyll", "rsync"]):
                # print('tool ' + str(tool))
                tool_info = get_annotations_tool_dump(tool, treshold)
                if tool_info is not None:
                    # print('uri ' + tool_info['uri'])
                    if len(tool)==1:
                        dict_tools.update({tool[0]: tool_info})
                    else :
                        dict_tools.update({tool[0]+" "+tool[1]: tool_info})
    return dict_tools    