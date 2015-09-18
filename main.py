#!/usr/bin/python

from yacc import parser;
from netlist import expand;
from copy import deepcopy;
from collections import OrderedDict

def extract(stmts,v):
  ret = {}
  for s in filter(lambda t: t[0] == v, stmts) :
    if s[1] in ret.keys():
      raise Exception("duplicate " + v + " definition")
    ret[s[1]] = s[2]
  return (filter(lambda t: t[0] != v, stmts),ret)

def swapify(s):
   members = OrderedDict()
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

native_types = ['int','float', 'bool', 'string', 'wire', 'power' ] 
def is_native_type(t):
  return t in native_types

#make sure there isn't anything stupid like multiple ports with same name
def check_fields(ary):
  for a in ary:
    t = ary[a]
    newdata = {}
    for b in t:
      if b[0] in newdata:
         raise Exception("duplicate component/module fields")
      newdata[b[0]] = b[1]
    ary[a] = newdata

def get_module_name(module):
  for n,m in modules.items():
    if m == module:
      return n
  for n,m in components.items():
    if m == module:
      return n

def evaluate_module(module,pname,port_args,gen_args,hierarchy):
  module = deepcopy(module)

  hierarchy = deepcopy(hierarchy)
  hierarchy.append(get_module_name(module))
  iname = deepcopy(hierarchy)
  instances.append(iname)
  generic_context = {}

  #TODO: support a number of different arg mapping techniques
  if 'generic' in module:
    if len(gen_args) and len(gen_args) != len(module['generic']):
      raise Exception("Generic argument list error")
    for idx, g in enumerate(module['generic']):
      if g[1][1] != 1:
        raise Exception("Vector generics not supported")
      if not is_native_type(g[1][0]):
        raise Exception("Non native type generics not support")
      if g[0] in generic_context:
        raise Exception("Duplicate generic parameter")
      generic_context[g[0]] = resolve_expr(g[2],constant_context)
      if idx < len(gen_args):
        generic_context[g[0]] = gen_args[idx]

  var_context = dict(constant_context,**generic_context)
  
  sig_context = {}
  if 'port' in module:
    if len(port_args) != len(module['port']):
      raise Exception("Port width mismatch")
    for p,m in zip(port_args,module['port']):
      sig_context[m] = module['port'][m][1]

  if 'body' in module:
    var_decls = filter(lambda t: len(t) == 2, module['body'])
    module['body'] = filter(lambda t: len(t) != 2, module['body'])
    var_decls = swapify(var_decls)
    if any_union([generic_context, var_decls, sig_context]):
      raise Exception("variable already declared")
    sig_context = dict(sig_context,**var_decls)

  for s in sig_context:
      signals.append((iname,s,sig_context[s]))


  if 'port' in module:
    for p,m in zip(port_args,module['port']):
      #print "fooo: " + str(module['port'][m])
      assign((pname,p),(iname,(m,)),var_context)

  if not 'body' in module:
    return 

  #Resolve vector widths
  for s in sig_context:
    sig_context[s] = (sig_context[s][0], resolve_expr(sig_context[s][1],var_context))

  m_instances = {}
  for c in filter(lambda t: t[0] == 'component', module['body']):
    if not c[2][0] in components:
      raise Exception("Component not found") 

    hierarchy.append(c[1])
    instance_common(components[c[2][0]],var_context,sig_context,c[2][1],hierarchy,iname)
    hierarchy.pop()

    m_instances[c[1]] = c[2] 
  module['body'] = filter(lambda t: t[0] != 'component', module['body'])

  for c in filter(lambda t: t[0] == 'module', module['body']):
    if not c[2][0] in modules:
      raise Exception("Module not found") 

    hierarchy.append(c[1])
    instance_common(modules[c[2][0]],var_context,sig_context,c[2][1],hierarchy,iname)
    hierarchy.pop()
	
    m_instances[c[1]] = c[2] 
  module['body'] = filter(lambda t: t[0] != 'module', module['body'])

  generates = {}
  for c in filter(lambda t: t[0] == 'generate', module['body']):
    hierarchy.append(c[1])
    evaluate_generate(c[2],deepcopy(var_context),sig_context,hierarchy,iname)
    hierarchy.pop()
  module['body'] = filter(lambda t: t[0] != 'generate', module['body'])

  for c in filter(lambda t: t[0] == '=', module['body']):
    assign((iname,c[1]),(iname,c[2]),var_context)
  module['body'] = filter(lambda t: t[0] != '=', module['body'])

  if module['body']:
    raise Exception("unknown body elements")
  hierarchy.pop()

def exists(instance,ref,context):
  found = None
  #print instance
  #print ref
  #print context
  for s in signals:
    #print "######"
    #print s
    #print instance
    #print ref
    if len(ref) > 1:
      tup = (instance,ref[0],ref[1])
      #print tup
      if tup == s:
        print "found tup"
        return True
    if s[0] == instance and (s[1] == ref[0][0] or s[1] == ref[0]):
      found = {s[1]:s[2]}
      #print "found"
      break;
  if not found:
    return False

  for e in ref:
    if not type(e) is tuple:
      e = (e,0)
    #print found
    #print e
    if not e[0] in found:
       print "not found: " + str(e[0])+ ", " + str(found)
       return False
    v = resolve_expr(e[1],context)
    if v >= found[e[0]][1]:
       print "too big " + str(v) + ", " + str(found[e[0]][1])
       return False
    if not is_native_type(found[e[0]][0]):
	       found = structs[found[e[0]][0]]
	
  return True

def assign(loc1, loc2, context):
  if not exists(loc1[0],loc1[1],context) or not exists(loc2[0],loc2[1],context):
    raise Exception("Variable reference does not exist") 

  loc1 = resolve(loc1,context)
  loc2 = resolve(loc2,context)

  assignments.append((loc1,loc2))

def resolve(loc,context):
  ary = []
  for l in loc[1]:
    if type(l) is tuple:
      ary.append((l[0],resolve_expr(l[1],context)))
    else:
      ary.append(l)
  return (loc[0],ary)

def evaluate_generate(stmts,var_context,sig_context,hierarchy,iname):
  for s in stmts:
    if s[0] == 'for':
      if s[1] in var_context or s[1] in sig_context:
        raise Exception("variable already declared")
      for i in range(resolve_expr(s[2],var_context),resolve_expr(s[3],var_context)):
        hierarchy.append(i)
        var_context[s[1]] = i
        evaluate_generate(s[4],deepcopy(var_context),sig_context,hierarchy,iname)
        hierarchy.pop()
    elif s[0] == 'component':
      hierarchy.append(s[1])
      instance_common(components[s[2][0]],var_context,sig_context,s[2][1],hierarchy,iname)
      hierarchy.pop()
    elif s[0] == 'module':
      hierarchy.append(s[1])
      instance_common(modules[s[2][0]],var_context,sig_context,s[2][1],hierarchy,iname)
      hierarchy.pop()
    elif s[0] == '=':
      assign((iname,s[1]),(iname,s[2]),var_context)
    else:
      raise Exception("unknown generate")

def instance_common(component,var_context,sig_context,parms,hierarchy,iname):
  port_args = []
  generic_args = []

  for p in filter(lambda t : t[0] == 'port', parms):
    port_args = p[1]#,map(sig_context.__getitem__,p[1]))
  for g in filter(lambda t : t[0] == 'generic', parms):
    generic_args = g[1]
  generic_args = map(lambda t : resolve_expr(t,var_context),generic_args)   
 
 
  evaluate_module(component,iname,port_args,generic_args,hierarchy)


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

check_fields(components)
check_fields(modules)

#modules cannot have pin footprint or symbol
for m in modules:
  m = modules[m]
  if 'pin' in m or 'footprint' in m or 'symbol' in m:
    raise Exception("Fields not allowed for module")
  if not 'body' in m:
    raise Exception("Modules must have a body")

if stmts:
  raise Exception("Unknown statements found")

if any_union([structs,components,modules,constants,functions]):
  raise Exception("constants structs module and components cannot share names")

#first order of business is to collapse any constants
constant_context = {}
for c in constants:
  data = constants[c]
  if data[0][1] != 1:
     raise Exception("Vector constants not supported")
  if not is_native_type(data[0][0]):
     raise Exception("Only native type constants are supported")

  v = resolve_expr(data[1],{})
  constant_context[c] = v

#structs must now have their vector length resolvable
for s in structs:
  for e in structs[s]:
    structs[s][e] = (structs[s][e][0],resolve_expr(structs[s][e][1],constant_context))

#there must be a module named top
if not 'top' in modules:
  raise Exception("No top module found")

top_module = modules['top']

#top module cannot have ports
if 'port' in top_module:
  raise Exception("Cannot have port on top module")

instances = []
signals = []
assignments = []
evaluate_module(top_module, [], {}, {}, [])

#print "Modules:"
#for i in filter(lambda k : k[0] in modules, instances):
#  print i

#print "Components:"
#for i in filter(lambda k : k[0] in components, instances):
#  print i

#print "Signals:"
#for i in signals:
#  print i

#print "Assignments:"
#for i in assignments:
#  print i

expand(signals,assignments,structs)



