"""
Author : Clemence SEBE
"""
import re
"""
This file contains all the functions which could be use in different Class
"""

"""
DIRECTIVE - INPUT - OUTPUT
"""

"""
Clean an element : no \n and no \
"""
def clean(txt):
    antiSlash = []
    for match in re.finditer(r"(\\)", txt):
        antiSlash.append(match.span())
    antiSlash.sort(reverse = True)
    for j in range(len(antiSlash)):
        txt = txt.replace(txt[antiSlash[j][0]:antiSlash[j][1]], " ")
    txt =" ".join(txt.split())
    return txt

"""
Split 
"""
def split(list, txt):
    listEnd = []
    work = "a \n" + txt
    index = []
    for pattern in list:
        for match in re.finditer(pattern, work):
            index.append(match.span()[0]+1)
    index.sort()
    for i in range (len(index)):
        if i == len(index)-1:
            study = work[index[i]:].lstrip().rstrip()
        else:   
            study = work[index[i]:index[i+1]].lstrip().rstrip()
        study = clean(study)
        listEnd.append(study)
    return listEnd

"""
Extract 
"""
def extractQ(txt):
    listEnd = []
    for i in range (len(txt)):
        cut = re.split("[^\w]",txt[i])
        key = cut[0] 
        listEnd.append([i,key])
    return listEnd


"""
SCRIPT - STUB
"""
"""
Analyse Language
"""
def whichLanguage(txt):
    language =""
    pattern = r'(#!/)'
    start = -1
    nb = -1
    for match in re.finditer(pattern, txt):
        start = match.span()[0]
        nb = 1
    if nb < 0:
        language = 'bash'
    else:
        patternEnd = r'(\n)'
        end = len(txt)
        for match in re.finditer(patternEnd, txt):
            if match.span()[0] < end and match.span()[0] > start:
                end = match.span()[0]
        work =txt[start:end].lstrip().rstrip()
        test1 = work.split()
        if len(test1) > 1:
            language = test1[-1]
        else:
            test2 = work.split('/')
            language = test2[-1]
    return language