#!/usr/bin/env python2

import src.tokrules
import ply.lex as lex

lexer = lex.lex(module=src.tokrules)

def test(s):
    print "test for:\n   " + repr(i)
    lexer.input(s)
    for tok in lexer:
        print "    | "+ str(tok)

tests = [
    "3 + 4",
    "if i < 15 then F 5 (2*3) else nothing end",
    """
func F a with let a' := 2*a in a*a' end
exec F 15 """,
    'exec "testing this, only one token must be here"',
    r'exec "testing this, only one \"token must be here"',
    r'"aoetnu""""',
    """
func Map[F, xs] :=
    if xs = nil
        then nil
        else CONS[ F[CAR[xs]], CDR[xs] ]
    end
end

func ConcatStrings[xss] :=
    if xss = nil
        then ""
        else (CAR[xss]) . (ConcatStrings[xss])
    end
end

func List[n] :=
    let func Helper[a] :=
                if a > n | a = n
                    then nil
                    else CONS[a, Helper[a+1]]
                end
        end
    in
        Helper[0]
    end
end

exec List[5]
    """,
]

for i in tests:
    test(i)
    print
