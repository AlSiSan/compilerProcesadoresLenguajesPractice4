#!/usr/bin/env python
# -*- coding: latin-1 -*-

#########################################################################################
##
##  Clase: Flujo.
##  Funcion:  Permite leer una cadena caracter a caracter
##
##
########################################################################################
class Flujo:
  #  Contructor de la clase. Se le pasa la cadena a leer
  def __init__(self,f):
    self.pos= -1
    self.fic=f

  #Devuelve un caracter de la cadenma
  def siguiente(self):
    return self.fic.read(1)
    # if self.pos< len(self.cad)-1:
    #   self.pos+= 1
    #   return self.cad[self.pos]
    # else:
    #   return ""

  # Revierte un caracter no leido a la cadena de partida
  def devuelve(self, c):
    self.fic.seek(-1,1)
    #self.pos-= len(c)

  # Indica la posicion leida
  def posleida(self):
    return self.pos

  # Devuelve la cadena en la que estamos leyendo
  def cadena(self):
    return self.cad

import sys

 #Programa principal para probar la clase flujo.
if __name__=="__main__":
  linea= sys.stdin.readline()
  while linea and linea!= "\n":
    f= Flujo(linea)
    print "Voy a señalar los espacios:"
    c= f.siguiente()
    while c!= "":
      if c==" ":
        print f.cadena().rstrip()
        print " " * f.posleida()+"^"
        c= f.siguiente()
      c= f.siguiente()
    print "Ahora voy a probar a devolver caracteres al flujo de entrada:"
    f.devuelve(linea)
    l= ""
    for i in range(len(linea)):
      d=""
      for j in range(len(linea)-i):
        c= f.siguiente()
        d+= c
      f.devuelve(d)
      c= f.siguiente()
      l+= c
    if linea != l:
      print "Error:"
      print "  leído:", linea
      print "  reconstruido:", l
    else:
      print "BIEN"
    linea= sys.stdin.readline()
