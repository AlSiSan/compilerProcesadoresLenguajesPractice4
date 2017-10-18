#!/usr/bin/env python

import string
import sys
######################################################################################
##
##  Define varias clases que definen cada uno de los diferentes componentes lexicos
##
##
##
######################################################################################

# Clase generica que define un componente lexico 
class Componente:
  def __init__(self):
    self.cat= str(self.__class__.__name__)

 #este metodo mostrara por pantalla un componente lexico
  def __str__(self):
    s=[]
    for k,v in self.__dict__.items():
      if k!= "cat": s.append("%s: %s" % (k,v))
    if s:
      return "%s (%s)" % (self.cat,", ".join(s))
    else:
      return self.cat
#definicion de las clases que representan cada uno de los componentes lexicos
#Algunas tendran camps adicionales para almacenar informacion importante (valor de un numero, etc)

#clases para los simbolos de puntuacion y operadores

class OpAsigna (Componente): 
 pass

class LlaveAp(Componente):
 pass

class LlaveCi (Componente):
 pass

class ParentAp(Componente):
 pass

class ParentCi(Componente):
 pass

class CorAp(Componente):
 pass

class CorCi(Componente):
 pass

class Punto(Componente):
 pass

class Coma(Componente):
 pass

class PtoComa(Componente):
 pass

class DosPtos(Componente):
 pass

# Clase que define la categoria OpAdd 
class OpAdd(Componente):
  def __init__(self, op):
    Componente.__init__(self)
    self.op= op

# Clase que define la categoria OpMult
class OpMult(Componente):
  def __init__(self, op):
    Componente.__init__(self)
    self.op= op

#clase para representar los numeros.
#Puede dividirse en 2 para representar los enteros y los reales de forma independiente
#Si se opta por una sola categoria debe alamcenarse el tipo de los datos ademas del valor
class Numero (Componente):
  def __init__(self, isInt, num):
    Componente.__init__(self)
    self.isInt = isInt
    self.num = num
  
#clase para representar los identificadores.
class Identif (Componente):
  def __init__(self,v,nl):
    Componente.__init__(self)
    self.valor= v
    self.linea=nl

#Clase que reprresenta las palabras reservadas.
#Sera una clase independiente de los identificadores para facilitar el analisis sintactico
class PR(Componente):
  def __init__(self, v,nl):
   Componente.__init__(self)
   self.valor = v
   self.linea=nl

# Clase que define la categoria OpRel
#Debe alnmacenarse que operador es concretamente

class OpRel (Componente):
  def __init__(self, op):
    Componente.__init__(self)
    self.op= op


