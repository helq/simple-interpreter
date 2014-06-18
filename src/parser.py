# module: parser.py
# author: helq
# license: wtfpl
# This module just grammatical rules

from tokrules import tokens

precedence = (
    ('left', 'AND', 'OR'),
    ('nonassoc', 'LESSTHAN', 'GREATERTHAN', 'EQUAL'),  # Nonassociative operators
    ('right', 'DOT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
#    ('right', 'UMINUS'),                      # Unary minus operator
)

def p_global_facts(p):
    'global_facts : facts exec_line'
    p[0] = { 'facts': p[1], 'stm': p[2] }

# facts
def p_facts1(p):
    '''facts : func_def facts
             | assign   facts'''
    name = p[1]['name']
    p[2].update( {name: p[1]} )
    p[0] = p[2]
def p_facts2(p):
    'facts : '
    p[0] = {}

# func_def
def p_func_def(p):
    'func_def : FUNC ID_FUNC LBRACE params RBRACE ASSIG stm END'
    p[0] = {'type': 'func', 'name': p[2], 'params': p[4], 'stm': p[7]}

def p_params1(p):
    'params : ID_FUNC COMMA params'
    p[0] = [{'type': 'id_func', 'id_func': p[1]}] + p[3]
def p_params2(p):
    'params : ID COMMA params'
    p[0] = [{'type': 'id', 'id': p[1]}] + p[3]
def p_params3(p):
    'params : ID_FUNC'
    p[0] = [{'type': 'id_func', 'id_func': p[1]}]
def p_params4(p):
    'params : ID'
    p[0] = [{'type': 'id', 'id': p[1]}]

# assign
def p_assign(p):
    'assign : VAL ID ASSIG stm END'
    p[0] = {'type': 'val', 'name': p[2], 'stm': p[4]}

# stm
def p_stm_func_call(p):
    'stm : ID_FUNC LBRACE args RBRACE'
    p[0] = {'type': 'stm_func_call', 'id_func': p[1], 'args': p[3]}
def p_args1(p):
    '''args : ID_FUNC COMMA args'''
    p[0] = [{'type': 'id_func', 'id_func': p[1]}] + p[3]
def p_args2(p):
    '''args : stm     COMMA args'''
    p[0] = [p[1]] + p[3]
def p_args3(p):
    '''args : ID_FUNC'''
    p[0] = [{'type': 'id_func', 'id_func': p[1]}]
def p_args4(p):
    '''args : stm'''
    p[0] = [p[1]]

def p_stm_op(p):
    '''stm : stm PLUS        stm
           | stm MINUS       stm
           | stm TIMES       stm
           | stm DIVIDE      stm
           | stm DOT         stm
           | stm LESSTHAN    stm
           | stm GREATERTHAN stm
           | stm EQUAL       stm
           | stm AND         stm
           | stm OR          stm '''
    p[0] = {'type': 'stm_op', 'op': p[2], 'value1': p[1], 'value2': p[3]}

def p_stm_string(p):
    'stm : STRING'
    p[0] = {'type': 'stm_value', 'type_value': 'string', 'value': p[1]}
def p_stm_number(p):
    'stm : NUMBER'
    p[0] = {'type': 'stm_value', 'type_value': 'number', 'value': p[1]}
def p_stm_boolean(p):
    '''stm : TRUE
           | FALSE'''
    p[0] = {'type': 'stm_value', 'type_value': 'boolean', 'value': p[1]}
def p_stm_nil(p):
    'stm : NIL'
    p[0] = {'type': 'stm_value', 'type_value': 'cons', 'value': 'nil'}

def p_stm_id(p):
    'stm : ID'
    p[0] = {'type': 'stm_id', 'id': p[1]}

def p_stm_enclosed(p):
    'stm : LPAREN stm RPAREN'
    p[0] = p[2]

def p_stm_if_then(p):
    'stm : IF stm THEN stm ELSE stm END'
    p[0] = {'type': 'stm_if_then', 'if': p[2], 'then': p[4], 'else': p[6]}

def p_stm_let(p):
    'stm : LET facts IN stm END'
    p[0] = {'type': 'stm_let', 'facts': p[2], 'stm': p[4]}

# exec_line
def p_exec_line(p):
    'exec_line : EXEC stm'
    p[0] = p[2]

# Error rule for syntax errors
def p_error(p):
    print "Syntax error in input!"
