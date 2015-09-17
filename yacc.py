#!/usr/bin/python

# Yacc codes

import ply.yacc as yacc
import ply.lex as lex

# Get the token map from the lexer.  This is required.
from calclex import tokens,lexer

def p_program(p):
    '''program : stmt_blocks'''
    p[0] = p[1]

def p_stmt_blocks(p):
    '''stmt_blocks : stmt_block
	| stmt_blocks stmt_block''' 
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_stmt_block(p):
    '''stmt_block : struct_def SEMICOLON
       | component_def SEMICOLON 
       | module_def SEMICOLON
       | constant_def SEMICOLON
       | function_def SEMICOLON'''
    p[0] = p[1]

def p_function_def(p):
    '''function_def : FUNCTION ID LPAREN id_list RPAREN LBRACE function_stmt_list RBRACE'''
    p[0] = (p[1], p[2], (p[4], p[7]))

def p_function_stmt_list(p):
    '''function_stmt_list : function_stmt
       | function_stmt_list function_stmt'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_function_stmt(p):
   '''function_stmt : return_stmt'''
   p[0] = p[1]

def p_return_stmt(p):
    '''return_stmt : RETURN expr SEMICOLON'''
    p[0] = (p[1], p[2])

def p_constant_def(p):
    '''constant_def : CONSTANT ID COLON type COLON EQUALS expr'''
    p[0] = (p[1], p[2], (p[4], p[7]))

def p_struct_def(p):
    '''struct_def : STRUCT ID LBRACE struct_member_list RBRACE'''
    p[0] = (p[1],p[2],p[4])

def p_struct_member_list_def(p):
    '''struct_member_list : struct_member
       | struct_member_list COMMA struct_member'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_struct_member_def(p):
    '''struct_member : id_list COLON type'''
    p[0] = (p[1], p[3])

def p_id_list(p):
    '''id_list : ID
       | id_list COMMA ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_type_def(p):
    '''type : ID
       | ID LBRACKET NUMBER RBRACKET'''
    if len(p) > 2:
      p[0] = (p[1], p[3])
    else:
      p[0] = (p[1], 1)

def p_component_def(p):
    '''component_def : COMPONENT ID COLON component_def_list'''
    p[0] = (p[1],p[2],p[4])

def p_component_def_list(p):
    '''component_def_list : component_def_elem
       | component_def_list component_def_elem'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_component_def_elem(p):
    '''component_def_elem : decl_port
       | decl_generic
       | decl_pin
       | decl_footprint
       | decl_symbol'''
    p[0] = p[1]

def p_decl_port(p):
    '''decl_port : PORT LBRACE port_member_list RBRACE'''
    p[0] = (p[1], p[3])

def p_port_member_list(p):
    '''port_member_list : port_member
      | port_member_list COMMA port_member'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_port_member(p):
    '''port_member : id_list COLON IN type
       | id_list COLON OUT type
       | id_list COLON INOUT type'''
    p[0] = (p[1],(p[3],p[4]))

def p_module_def(p):
    '''module_def : MODULE ID module_def_list'''
    p[0] = (p[1],p[2],p[3])

def p_module_def_list(p):
    '''module_def_list : module_def_elem
       | module_def_list module_def_elem'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])

def p_module_def_elem(p):
    '''module_def_elem : decl_port
       | decl_generic
       | decl_body'''
    p[0] = p[1]

def p_decl_pin_def(p):
    '''decl_pin : PIN LBRACE pin_list RBRACE'''
    p[0] = (p[1], p[3])

def p_pin_list_def(p):
    '''pin_list : pin
       | pin_list COMMA pin'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_pin_def(p):
    '''pin : aderef EQUALS STRING'''
    p[0] = (p[1], p[3])

def p_aderef_def(p):
    '''aderef : deref
       | deref LBRACKET NUMBER RBRACKET'''
    p[0] = p[1]
    if len(p) > 2:
      p[0] = (p[1], p[3])

def p_deref_def(p):
    '''deref : ID
       | deref PERIOD ID'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_function_call_def(p):
    '''function_call : ID LPAREN expr_list RPAREN
       | ID LPAREN RPAREN'''
    if len(p) > 3:
      p[0] = ('function_call', p[1], p[3])
    else:
      p[0] = ('function_call', p[1], None)

def p_decl_footprint_def(p):
    '''decl_footprint : FOOTPRINT LBRACE function_call RBRACE'''
    p[0] = (p[1], p[3])

def p_expr_list_def(p):
    '''expr_list : expr
       | expr_list COMMA expr'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_expr_def(p):
    '''expr : NUMBER
       | STRING
       | ID 
       | function_call'''
    p[0] = p[1]

def p_decl_generic_def(p):
    '''decl_generic : GENERIC LBRACE decl_generic_list RBRACE'''
    p[0] = (p[1], p[3])

def p_decl_generic_list(p):
    '''decl_generic_list : decl_generic_item
       | decl_generic_list COMMA decl_generic_item'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])

def p_decl_generic_item(p):
    '''decl_generic_item : ID COLON type
       | ID COLON type COLON EQUALS expr'''
    if len(p) > 4:
      p[0] = (p[1],p[3],p[6])
    else:
      p[0] = (p[1],p[3],None)

def p_decl_symbol_def(p):
    '''decl_symbol : SYMBOL LBRACE ID RBRACE'''
    p[0] = (p[1], p[3])


def p_decl_body_def(p):
     '''decl_body : LBRACE instance_list RBRACE'''
     p[0] = ('body', p[2])

def p_instance_list_def(p):
     '''instance_list : instance
        | instance_list instance'''
     if len(p) == 2:
        p[0] = [p[1]]
     else:
        p[0] = p[1]
        p[0].append(p[2])

def p_instance_def(p):
     '''instance : signal_inst
        | component_inst
        | generate_inst'''
     p[0] = p[1]

#these should not have id_list but causes shift reduce conflict so it will have to be enforced during symantics
def p_component_inst_def(p):
     '''component_inst : id_list COLON COMPONENT ID component_args_list SEMICOLON'''
     p[0] = (p[3],p[1][0],p[4],p[5])

def p_generate_inst_def(p):
     '''generate_inst : id_list COLON GENERATE LBRACE gen_stmt_list RBRACE'''
     p[0] = (p[1][0],p[3],p[5])

def p_gen_stmt_list_def(p):
     '''gen_stmt_list : gen_stmt
        | gen_stmt_list gen_stmt'''
     if len(p) == 2:
        p[0] = [p[1]]
     else:
        p[0] = p[1]
        p[0].append(p[2])

def p_gen_stmt_def(p):
     '''gen_stmt : for_inst
        | component_inst'''
     p[0] = p[1]

def p_for_inst(p):
     '''for_inst : FOR ID IN expr TO expr LBRACE gen_stmt_list RBRACE'''
     p[0] = (p[1],p[2],p[4],p[6],p[8])

def p_component_args_list_def(p):
     '''component_args_list : component_arg
        | component_args_list component_arg'''
     if len(p) == 2:
        p[0] = [p[1]]
     else:
        p[0] = p[1]
        p[0].append(p[2])

def p_component_arg_def(p):
     '''component_arg : use_port
        | use_generic'''
     p[0] = p[1]

def p_use_port_def(p):
     '''use_port : PORT LPAREN id_list RPAREN'''
     p[0] = (p[1], p[3])

def p_use_generic_def(p):
    '''use_generic : GENERIC LPAREN expr_list RPAREN'''
    p[0] = (p[1], p[3])

def p_signal_inst_def(p):
     '''signal_inst : id_list COLON type SEMICOLON'''
     p[0] = (p[1], p[3])

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
parser = yacc.yacc()



