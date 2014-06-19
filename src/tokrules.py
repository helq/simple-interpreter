# module: tokrules.py
# author: helq
# license: wtfpl
# This module just contains the lexing rules

reserved = {
   'exec' : 'EXEC',      'let'  : 'LET',
   'func' : 'FUNC',      'in'   : 'IN',
   'end'  : 'END',       'if'   : 'IF',
   'val'  : 'VAL',       'then' : 'THEN',
   'true' : 'TRUE',      'else' : 'ELSE',
   'false' : 'FALSE',    'nil'  : 'NIL',
}

tokens = [
   'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'COMMA', 'NUMBER', 'PLUS', 'MINUS',
   'TIMES', 'DIVIDE', 'DOT', 'EQUAL', 'LESSTHAN', 'GREATERTHAN', 'ASSIG',
   'AND', 'OR', 'ID', 'ID_FUNC', 'STRING',
] + list(reserved.values())

# Regular expression rules for simple tokens
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_LBRACE      = r'\['
t_RBRACE      = r'\]'
t_ASSIG       = r':='
t_COMMA       = r','

t_PLUS        = r'\+'
t_MINUS       = r'-'
t_TIMES       = r'\*'
t_DIVIDE      = r'/'
t_DOT         = r'\.'
t_LESSTHAN    = r'<'
t_GREATERTHAN = r'>'
t_EQUAL       = r'='
t_AND         = r'&'
t_OR          = r'\|'

def t_ID(t):
    r'[a-z][a-zA-Z_0-9\']*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    if t.value == "true":  t.value = True
    if t.value == "false": t.value = False
    return t

def t_ID_FUNC(t):
    r'[A-Z][a-zA-Z_0-9\']*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = eval(t.value)
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# a comment
def t_ignore_comments(t):
    r'\#[^\n]*'


# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)
