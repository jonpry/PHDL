#!/usr/bin/python

from yacc import parser;
from copy import deepcopy;

def extract(stmts,v):
  ret = {}
  for s in filter(lambda t: t[0] == v, stmts) :
    if s[1] in ret.keys():
      raise Exception("duplicate " + v + " definition")
    ret[s[1]] = s[2]
  return (filter(lambda t: t[0] != v, stmts),ret)

def swapify(s):
   members = {}
   for m in s:
     for w in m[0]:
        members[w] = m[1]
   return members

def swap_part(whole):
  for c in whole:
    nlist = []
    for d in filter(lambda t: t[0] == 'port', whole[c]):
      nlist.append( (d[0],swapify(d[1]) ))
    whole[c] = filter(lambda t: t[0] != 'port', whole[c])  + nlist

def any_union(l):
  for i in l:
    for j in l:
      if i==j:
        continue
      if i.keys() & j.viewkeys() :
        return True
  return False 

def resolve_function(name, args,context):
  if not name in functions:
    raise Exception("Function not found")
  f = functions[name]
  if len(f[0]) != len(args):
    raise Exception("Wrong number of arguments")
  for a,b in zip(f[0],args):
    context[a] = b

  for s in f[1]:
    e = resolve_expr(s[1],context)
    if s[0] == 'return':
      return e
    elif s[0] == 'assignment':
      context[s[2]] = e
    else:
      raise Exception("Unknown statements")

def is_number(s): 
  try:
    float(s)
    return True
  except ValueError:
    pass
  return False

def is_string(s):
  if not type(s) is str:
    return False
  if not s.startswith("\"") or not s.endswith("\""):
    return False
  return True

def resolve_expr(expr,context):
  if not type(expr) is tuple:
    if is_number(expr) or is_string(expr):
      return expr;
    if not expr in context:
      raise Exception("Undefined variable")
    return context[expr]
  if expr[0] == 'function_call':
    args = []
    for e in expr[2]:
      args.append(resolve_expr(e,context))
    return resolve_function(expr[1],args,deepcopy(context))
  if expr[0] == "*":
    return resolve_expr(expr[1],context) * resolve_expr(expr[2],context)    
  if expr[0] == "/":
    return resolve_expr(expr[1],context) / resolve_expr(expr[2],context)    
  if expr[0] == "+":
    return resolve_expr(expr[1],context) + resolve_expr(expr[2],context)    
  if expr[0] == "-":
    return resolve_expr(expr[1],context) - resolve_expr(expr[2],context)    
  if expr[0] == "(":
    return resolve_expr(expr[1],context)    

native_types = ['int','float', 'bool', 'string' ] 
def is_native_type(t):
  return t in native_types

myfile = open ("example1.phdl", "r")
data=myfile.read().replace('\n', '')

stmts = parser.parse(data,debug=0)

stmts,structs = extract(stmts,'struct')
stmts,components = extract(stmts,'component')
stmts,modules = extract(stmts,'module')
stmts,constants = extract(stmts,'constant')
stmts,functions = extract(stmts,'function')

#rewrite the name,name = type stuff
for s in structs:
   structs[s] = swapify(structs[s])

swap_part(components)
swap_part(modules)

if stmts:
  raise Exception("Unknown statements found")

if any_union([structs,components,modules,constants,functions]):
  raise Exception("constants structs module and components cannot share names")

#first order of business is to collapse any constants
context = {}
for c in constants:
  data = constants[c]
  if data[0][1] != 1:
     raise Exception("Vector constants not supported")
  if not is_native_type(data[0][0]):
     raise Exception("Only native type constants are supported")

  v = resolve_expr(data[1],{})
  context[c] = v
 
print context
#print str(functions)
#print str(structs) + str(modules) + str(components) + str(constants) + str(functions)




