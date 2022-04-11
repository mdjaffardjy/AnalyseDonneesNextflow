from utility import *

#==========================================================
#Test check_containing
#==========================================================
tab=['a', 'r', 't']
assert(check_containing('r', tab))
assert(not check_containing('g', tab))

#==========================================================
#Test create_empty
#==========================================================
temp= "George and the penguin"
assert(len(create_empty(temp, 0, len(temp)))==len(temp))
assert(len(create_empty(temp, 5, len(temp)))==len(temp[5:]))
assert(len(list(set(list(create_empty(temp, 0, len(temp)-1)))))==1)
assert(list(set(list(create_empty(temp, 0, len(temp)-1))))[0]==' ')

#==========================================================
#get_next_element_caracter
#==========================================================
temp= "George and the penguin"
assert(get_next_element_caracter(temp, 0)==('e', 1))
assert(get_next_element_caracter(temp, 5)==('a', 7))
temp= """George
 and the penguin"""
assert(get_next_element_caracter(temp, 5)==('a', 8))

#==========================================================
#get_next_element_word
#==========================================================
temp= "George and the penguin"
assert(get_next_element_word(temp, 0)==('eorge', 1))
assert(get_next_element_word(temp, 0, True)==('George', 0))
assert(get_next_element_word(temp, 5)==('and', 7))
assert(get_next_element_word(temp, 5, True)==(' and', 6))
assert(get_next_element_word(temp, 6, True)==(' and', 6))

#==========================================================
#extract_curly
#==========================================================
temp= """if(George and the penguin) {
            test...1...2...3
        }"""
assert(temp[extract_curly(temp, 27)-1]=='}')
assert(temp[extract_curly(temp, 28)-1]=='}')
temp= """if(George and the penguin) {
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
temp2= """{
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
assert(temp[27:extract_curly(temp, 27)]==temp2)
assert(temp[27:extract_curly(temp, 28)]==temp2)

#==========================================================
#get_next_line
#==========================================================
temp= """
    George and the penguin
    George and the armadillo
    Clemence and the penguin
    """
assert(get_next_line(temp,0)==('George and the penguin', 5, 26))
assert(get_next_line(temp,26)==('George and the armadillo', 32, 55))
assert(get_next_line(temp,27)==('George and the armadillo', 32, 55))
assert(get_next_line(temp,55)==('Clemence and the penguin', 61, 84))

#==========================================================
#extract_condition_2
#==========================================================
temp= """if(George and the penguin) {
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
assert(extract_condition_2(temp)=='George and the penguin')
temp= """if(George && (the) || penguin) {
            test...1...2...3
        }"""
assert(extract_condition_2(temp)=='George && (the) || penguin')

#==========================================================
#get_index_next_curly
#==========================================================
temp= """if(George and the penguin) {
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
assert(temp[get_index_next_curly(temp, 0)]=='{')
assert(temp[get_index_next_curly(temp, 29)]=='{')

temp= """if(George and the penguin) '{'
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
assert(temp[get_index_next_curly(temp, 0, True)]=='{')
assert(get_index_next_curly(temp, 0, True)==72)

#==========================================================
#get_index_next_curly_close
#==========================================================
temp= """if(George and the penguin) {
            if(George and the penguin 2) {
                test...1...2...3
            }
        }"""
assert(temp[get_index_next_curly_close(temp, 0)]=='}')
assert(temp[get_index_next_curly_close(temp, 118)]=='}')

temp= """if(George and the penguin) {
            if(George and the penguin 2) {
                test...1...2...3
            '}'
        }"""
assert(temp[get_index_next_curly_close(temp, 0, True)]=='}')
assert(get_index_next_curly_close(temp, 0, True)==129)

#==========================================================
#link_conditions
#==========================================================
temp= ['A', 'B', 'C', 'D']
assert(link_conditions(temp)=='A && B && C && D')
assert(link_conditions(temp, True)=='!(A) && !(B) && !(C) && !(D)')
temp= ['A']
assert(link_conditions(temp)=='A')
assert(link_conditions(temp, True)=='!(A)')

#==========================================================
#add_spaces
#==========================================================
expected= 'if (George & the penguin) {'
temp= 'if(George & the penguin) {'
assert(add_spaces(temp)==expected)
temp= 'if (George & the penguin){'
assert(add_spaces(temp)==expected)
temp= 'if(George & the penguin){'
assert(add_spaces(temp)==expected)
assert(add_spaces(expected)==expected)
temp= '\nelse{'
assert(add_spaces(temp)=='\n else {')

#==========================================================
#format_if_recursif_3
#==========================================================
temp="""if (c) {
    boo
}
"""
assert(format_if_recursif_3(temp, 0, len(temp), [], [], '')[1]=='<< boo ;; c >>\n')
assert(format_if_recursif_3(temp, 0, len(temp), [], [], '')[0]==['c'])
temp="""if (c) {
    if (c1) {
        boo
    } else {
        not boo
    }
}
"""
assert(format_if_recursif_3(temp, 0, len(temp), [], [], '')[1]=='<< boo ;; c && c1 >>\n<< not boo ;; c && !(c1) >>\n')
temp="""if (c) {
    if (c1) {
        if (c2) {
            boo2
        }
        boo1
    } else if (c3) {
        boo3 
    } else if (c4) {
        boo4 
    } else {
        not boo134
    }
}
"""
expected= '<< boo2 ;; c && c1 && c2 >>\n<< boo1 ;; c && c1 >>\n<< boo3 ;; c && c3 && !(c1) >>\n<< boo4 ;; c && c4 && !(c3) && !(c1) >>\n<< not boo134 ;; c && !(c4) && !(c3) && !(c1) >>\n'
assert(format_if_recursif_3(temp, 0, len(temp), [], [], '')[1]==expected)

#==========================================================
#add_curly
#==========================================================
expected='if (c) { \n  boo  \n}'
temp="""if(c) boo """
assert(add_curly(temp)==expected)
temp="""if(c) boo """
assert(add_curly(temp)==expected)
temp="""if (c) { 
  boo  
}"""
assert(add_curly(temp)==expected)
expected='else { \n  boo  \n}'
temp="""else boo """
assert(add_curly(temp)==expected)



print("All good!")



