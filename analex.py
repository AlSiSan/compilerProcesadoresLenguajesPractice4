#!/usr/bin/env python

import componentes
import errores
import flujo
import string
import sys

from sys import argv
from sets import ImmutableSet

class Analex:
#############################################################################
##  Conjunto de palabras reservadas para comprobar si un identificador es PR
#############################################################################
	PR = ImmutableSet(["PROGRAMA", "VAR", "VECTOR","DE", "ENTERO", "REAL", "BOOLEANO", "PROC", "FUNCION", "INICIO", "FIN", "SI", "ENTONCES", "SINO", "MIENTRAS", "HACER", "LEE", "ESCRIBE", "Y", "O", "NO", "CIERTO","FALSO"])

	############################################################################
	#
	#  Funcion: __init__
	#  Tarea:  Constructor de la clase
	#  Prametros:  flujo:  flujo de caracteres de entrada
	#  Devuelve: --
	#
	############################################################################
	def __init__(self, flu):
		#Debe completarse con  los campos de la clase que se consideren necesarios
		self.flu = flu
		self.nlinea=1 #contador de lineas para identificar errores

	############################################################################
	#
	#  Funcion: Analiza
	#  Tarea:  Identifica los diferentes componentes lexicos
	#  Parametros:  --
	#  Devuelve: Devuelve un componente lexico
	#
	############################################################################
	def Analiza(self):
		ch = self.flu.siguiente()
		if ch==" ":
			while (ch == ' '):
				ch = self.flu.siguiente()
				#self.flu.devuelve()
			return self.Analiza()
			# quitar todos los caracteres blancos 
			#buscar el siguiente componente lexico que sera devuelto )
		elif ch== "+" or ch == '-':
			return componentes.OpAdd(ch)
			# debe crearse un objeto de la clasee OpAdd que sera devuelto
		elif ch== "*" or ch == '/':
			return componentes.OpMult(ch)
		elif ch == '[':
			return componentes.CorAp()
		elif ch == ']': #asi con todos los simbolos y operadores del lenguaje
			return componentes.CorCi()
		elif ch == '(':
			return componentes.ParentAp()
		elif ch == ')':
			return componentes.ParentCi()
		elif ch == ';':
			return componentes.PtoComa()
		elif ch == ',': #asi con todos los simbolos y operadores del lenguaje
			return componentes.Coma()
		elif ch == '.': #asi con todos los simbolos y operadores del lenguaje
			return componentes.Punto()
		elif ch == "{":
			while (ch != '}'):
				if ch == '\n':
 					self.nlinea += 1
				elif len(ch) == 0:
					print ("ERROR: Comentario no cerrado")
					return None
				ch = self.flu.siguiente()
			self.flu.devuelve()
			return self.Analiza()
		elif ch == "}":
			print "ERROR: Comentario no abierto" # tenemos un comentario no abierto
			return self.Analiza()
		elif ch==":":
			ch = self.flu.siguiente()
			if ch == '=':
				return componentes.OpAsigna()
			self.flu.devuelve()
			return componentes.DosPtos()
		elif ch == '=':
			return componentes.OpRel(ch)
		elif ch in ['<', '>']:
			fch = ch
			ch = self.flu.siguiente()
			if ch == '=' or (fch == '<' and ch == '>'):
				return componentes.OpRel(fch + ch)
			self.flu.devuelve()
			return componentes.OpRel(fch)
    
		#Completar los operadores y categorias lexicas que faltan
		elif ch.isalpha():
			iden = ch
			ch = self.flu.siguiente()
			while ch.isalpha() or ch.isdigit():
				iden += ch
				ch = self.flu.siguiente()
			self.flu.devuelve()
			if iden in self.PR and len(iden) != 0:
				return componentes.PR(iden, self.nlinea)
			return componentes.Identif(iden, self.nlinea)
			#leer entrada hasta que no sea un caracter valido de un identificador
			#devolver el ultimo caracter a la entrada
			# Comprobar si es un identificador o PR y devolver el objeto correspondiente
		elif ch.isdigit():
			num = ch
			isInt = True
			ch = self.flu.siguiente()
			while ch.isdigit():
				num += ch
				ch = self.flu.siguiente()
			if ch == '.':
				num += ch
				isInt = False
				ch = self.flu.siguiente()
				while ch.isdigit():
					num += ch
					ch = self.flu.siguiente()
			self.flu.devuelve()
			return componentes.Numero(isInt, num)
		elif ch == '\r':
			return self.Analiza()
			#Leer todos los elementos que forman el numero 
			# devolver el ultimo caracter que ya no pertenece al numero a la entrada
			# Devolver un objeto de la categoria correspondiente 
		elif ch== '\n':
			self.nlinea += 1
			return self.Analiza()
			#incrementa el numero de linea ya que acabamos de saltar a otra
			# devolver el siguiente componente encontrado
		return None

############################################################################
#
#  Funcion: __main__
#  Tarea:  Programa principal de prueba del analizador lexico
#  Prametros:  --
#  Devuelve: --
#
############################################################################
if __name__=="__main__":
	script, filename=argv
	txt=open(filename)
	print "Este es tu fichero %r" % filename
	i=0
	fl = flujo.Flujo(txt)
	analex=Analex(fl)
	try:
		c=analex.Analiza()
		while c :
			print c
			c=analex.Analiza()
		i=i+1
	except errores.Error, err:
		sys.stderr.write("%s\n" % err)
#analex.muestraError(sys.stderr)