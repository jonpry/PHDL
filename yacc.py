#!/usr/bin/python

# Yacc codes

import ply.yacc as yacc
import ply.lex as lex

# Get the token map from the lexer.  This is required.
from calclex import tokens,lexer	

def p_program(p):
    '''program : stmt_blocks'''

def p_stmt_blocks(p):
    '''stmt_blocks : stmt_block
	| stmt_blocks stmt_block'''

def p_stmt_block(p):
    '''stmt_block : struct_def SEMICOLON
       | component_def SEMICOLON 
       | module_def SEMICOLON'''

def p_struct_def(p):
    '''struct_def : STRUCT ID LBRACE struct_member_list RBRACE'''

def p_struct_member_list_def(p):
    '''struct_member_list : struct_member
       | struct_member_list COMMA struct_member'''

def p_struct_member_def(p):
    '''struct_member : id_list COLON type'''

def p_id_list(p):
    '''id_list : ID
       | id_list COMMA ID'''

def p_type(p):
    '''type : ID
       | ID LBRACKET NUMBER RBRACKET'''

def p_component_def(p):
    '''component_def : COMPONENT ID COLON component_def_list'''

def p_component_def_list(p):
    '''component_def_list : component_def_elem
       | component_def_list component_def_elem'''

def p_component_def_elem(p):
    '''component_def_elem : decl_port
       | decl_generic
       | decl_pin
       | decl_footprint
       | decl_symbol'''

def p_decl_port(p):
    '''decl_port : PORT LBRACE port_member_list RBRACE'''

def p_port_member_list(p):
    '''port_member_list : port_member
      | port_member_list COMMA port_member'''

def p_port_member(p):
    '''port_member : id_list COLON IN type
       | id_list COLON OUT type
       | id_list COLON INOUT type'''

def p_module_def(p):
    '''module_def : MODULE ID module_def_list'''

def p_module_def_list(p):
    '''module_def_list : module_def_elem
       | module_def_list module_def_elem'''

def p_module_def_elem(p):
    '''module_def_elem : decl_port
       | decl_generic
       | decl_body'''

def p_decl_pin_def(p):
    '''decl_pin : PIN LBRACE pin_list RBRACE'''

def p_pin_list_def(p):
    '''pin_list : pin
       | pin_list COMMA pin'''

def p_pin_def(p):
    '''pin : aderef EQUALS STRING'''

def p_aderef_def(p):
    '''aderef : deref
       | deref LBRACKET NUMBER RBRACKET'''

def p_deref_def(p):
    '''deref : ID
       | deref PERIOD ID'''

def p_decl_footprint_def(p):
    '''decl_footprint : FOOTPRINT LBRACE ID LPAREN expr_list RPAREN RBRACE
       | FOOTPRINT LBRACE ID LPAREN RPAREN RBRACE'''

def p_expr_list_def(p):
    '''expr_list : expr
       | expr_list COMMA expr'''

def p_expr_def(p):
    '''expr : NUMBER
       | STRING
       | ID '''

def p_decl_generic_def(p):
    '''decl_generic : GENERIC LBRACE decl_generic_list RBRACE'''

def p_decl_generic_list(p):
    '''decl_generic_list : decl_generic_item
       | decl_generic_list COMMA decl_generic_item'''

def p_decl_generic_item(p):
    '''decl_generic_item : ID COLON type
       | ID COLON type COLON EQUALS expr'''

def p_decl_symbol_def(p):
    '''decl_symbol : SYMBOL LBRACE ID RBRACE'''

def p_decl_body_def(p):
     '''decl_body : LBRACE instance_list RBRACE'''

def p_instance_list_def(p):
     '''instance_list : instance
        | instance_list instance'''

def p_instance_def(p):
     '''instance : signal_inst
        | component_inst
        | generate_inst'''

#these should not have id_list but causes shift reduce conflict so it will have to be enforced during symantics
def p_component_inst_def(p):
     '''component_inst : id_list COLON COMPONENT ID component_args_list SEMICOLON'''

def p_generate_inst_def(p):
     '''generate_inst : id_list COLON GENERATE LBRACE gen_stmt_list RBRACE'''

def p_gen_stmt_list_def(p):
     '''gen_stmt_list : gen_stmt
        | gen_stmt_list gen_stmt'''

def p_gen_stmt_def(p):
     '''gen_stmt : for_inst
        | component_inst'''

def p_for_inst(p):
     '''for_inst : FOR ID IN expr TO expr LBRACE gen_stmt_list RBRACE'''

def p_component_args_list_def(p):
     '''component_args_list : component_arg
        | component_args_list component_arg'''

def p_component_arg_def(p):
     '''component_arg : use_port
        | use_generic'''

def p_use_port_def(p):
     '''use_port : PORT LPAREN id_list RPAREN'''

def p_use_generic_def(p):
    '''use_generic : GENERIC LPAREN expr_list RPAREN'''

def p_signal_inst_def(p):
     '''signal_inst : id_list COLON type SEMICOLON'''

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()

myfile = open ("example1.phdl", "r")
data=myfile.read().replace('\n', '')
data = lex.input(data)

#for tok in lexer:
#    print(tok)

#print(data)
result = parser.parse(data,debug=0)



