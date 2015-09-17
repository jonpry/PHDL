#!/usr/bin/python

import ply.lex as lex

reserved = {
   'struct' : 'STRUCT',
   'component' : 'COMPONENT',
   'port' : 'PORT',
   'pin' : 'PIN',
   'footprint' : 'FOOTPRINT',
   'symbol' : 'SYMBOL', 
   'module' : 'MODULE',
   'generate' : 'GENERATE',
   'inout' : 'INOUT',
   'in' : 'IN',
   'out' : 'OUT',
   'id' : 'ID',
   'generic' : 'GENERIC',
   'for' : 'FOR',
   'to' : 'TO',
   'constant' : 'CONSTANT'
}

# List of token names.   This is always required
tokens = [
   'NUMBER',
   'PLUS',
   'MINUS',
   'TIMES',
   'DIVIDE',
   'EQUALS',
   'LPAREN',
   'RPAREN',
   'COLON',
   'SEMICOLON',
   'PERIOD',
   'COMMA',
   'LBRACE',
   'RBRACE',
   'LBRACKET',
   'RBRACKET',
   'QUOTE',
   'STRING',
] + list(reserved.values());

# Regular expression rules for simple tokens
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS  = r'='
t_PERIOD  = r'\.'
t_COLON   = r':'
t_SEMICOLON = r';'
t_COMMA   = r','
t_LBRACE  = r'\{'
t_RBRACE  = r'\}'
t_QUOTE   = r'\"'

def t_STRING(t):
    r'\"[a-zA-Z0-9_,]*\"'
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value,'ID')    # Check for reserved words
    return t

# A regular expression rule with some action code
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
    print("Illegal character '%s' at line %d" % (t.value[0], t.lexer.lineno))
    exit(0)

# Build the lexer
lexer = lex.lex()




