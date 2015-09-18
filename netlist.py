#!/usr/bin/python

def fixderef(k):
  l = []
  for i in k:
#    if type(i) is tuple:
      l.append(i)
#    else:
#      l.append((i,0))
  return l
 
def fixit(k):
  return (k[0],fixderef(k[1]))

def expand(signals,assignments,structs):	
  assignments = map(lambda k: (fixit(k[0]),fixit(k[1])), assignments)

  for a in assignments:
    print a
