#!/usr/bin/env python2

import ply.lex as lex
import src.tokrules

import ply.yacc as yacc
from src.parser import *

from src.interpreter import *

lexer = lex.lex(module=src.tokrules)
parser = yacc.yacc()

#while True:
#   try:
#       s = raw_input('input > ')
#   except EOFError:
#       break
#   if not s: continue
#   result = parser.parse(s)
#   print result

prelude = open('prelude.code', 'r').read()
tests = [
    "exec 5",
    "exec 5/2 + 6 * 9 - 6",
    "exec (2 < 5) | false",
    'exec "aboen" . "yes"',
    "exec 5/2 + 6 * 9 - 6 > 42",
    'exec 4 = 6 | "yes" = "y"."es"',
    'exec if true then "yes" else "no" end',
    'exec if 4=6 then "yes" else "no" end',
    'exec 4 * if 4=6 then 2 else 0 end',
    'val a := 15 end exec a',
    '''
    val a :=
        if true
            then 15
            else panc
        end
    end
    exec a - 6''',
    "exec let val a := 15 end in a end",
    '''
    val a :=
        if true
            then 15
            else panc
        end
    end
    exec let val a := 6 end
            in a - 6
         end''',
    '''
    func F[a,R] := R[3*a] end
    func G[a] := if 6 > a then "casa" else "carro" end end
    exec F[5,G]
    ''',
    'exec nil = nil',
    r'exec "uertno\n\n"',
    '''
    func G[b] := if b > 2 then "a" else "b" end end
    val b := 15 end
    exec let func X[A, b] := A[b] end in X[G, b] end
    ''',
    '''
    func CONS[a,b] := primitive end
    func CAR[a] := primitive end
    val a := CONS["a", nil] end
    exec CAR[a] = "a"
    ''',
] + [ prelude+x for x in [
    '''
    val a := CONS["a", nil] end
    exec CAR[a] = "b"
    ''',
    '''
    val a := CONS["a", nil] end
    exec CDR[a] = nil
    ''',
    'exec List[0,10]',
    '''
func F[n] := 2*n end
exec Map[F, List[0,10]]
    ''',
] ]


for s in tests:
    print "==="
    print repr(s)

    print
    ast = parser.parse(s)

    print ast
    print

    result = execute_ast(ast)
    toPrint = result[1] if result[0] != 'cons' else cons_to_tuples(result)
    print "result > ", toPrint
    print
