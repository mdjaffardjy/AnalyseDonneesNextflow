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
def split(lists, txt):
    listEnd = []
    work = "a \n" + txt
    index = []
    for pattern in lists:
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

"""
Prepare the string for the extraction of tools after
"""
def justScript(txt):
    study = ''
    work = txt
    #Long - several lines
    pattern = [r'(""")', r"(''')"]  
    idx = []
    for pat in pattern:
        for match in re.finditer(pat, txt):
            idx.append([match.span()[0], match.span()[1]])
    idx.sort()
    for i in range (0, len(idx),2):
        study += txt[idx[i][1]:idx[i+1][0]]
        work = work.replace(txt[idx[i][0]:idx[i+1][1]], "\n")
    
    #Short - one line
    pattern = [r'(\n+\s*".*"\n*)', r"(\n+\s*'.*'\n*)"]
    for pat in pattern:
        for match in re.finditer(pat,work):
            temp = work[match.span()[0]: match.span()[1]].lstrip().rstrip()
            study += "\n" + temp[1:-1]
            #little = work[match.span()[0]: match.span()[1]]
            #work = work.replace(little, "\n")
    #print("STUDY : ",study)
    #print("WORK : ", work)
    return study
