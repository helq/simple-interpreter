#!/usr/bin/env python2
# author: helq
# license: wtfpl

import ply.lex as lex
import src.tokrules

import ply.yacc as yacc
from src.parser import *

from src.interpreter import *

lexer = lex.lex(module=src.tokrules)
parser = yacc.yacc()

if __name__ == "__main__":
    from sys import argv, setrecursionlimit
    setrecursionlimit(10000)
    if len(argv) != 2:
        print "how to use:\n "+argv[0]+" file_to_execute"
        exit(1)

    prelude = open('prelude.code', 'r').read()
    filecode = open(argv[1], 'r').read()
    ast = parser.parse(prelude + filecode)
    result = execute_ast(ast)
    toPrint = result[1] if result[0] != 'cons' else cons_to_tuples(result)
    print toPrint
