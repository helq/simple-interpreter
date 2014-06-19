#!/usr/bin/env python2
# author: helq
# license: wtfpl

# There is a problem with introspection in the interpreter of python on
# windows.
# This script join the principal files in only one, then the interpreter for
# python for windows can do introspection

tokrules = open("src/tokrules.py", 'r').readlines()[5:]
parser = open("src/parser.py", 'r').readlines()[7:]
interpreter = open("src/interpreter.py", 'r').readlines()
main = open("main.py", 'r').readlines()[13:]

imports = ["\n"
          , "import ply.lex as lex\n"
          , "import ply.yacc as yacc\n"
          , "lexer = lex.lex()\n"]

open("main_Windows.py", 'w').write(
        reduce(lambda x,y: x+y, tokrules + parser + interpreter + imports + main)
    )
