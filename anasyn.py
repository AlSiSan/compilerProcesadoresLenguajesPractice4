#!/usr/bin/env python

import componentes
import errores
import flujo
import string
import sys

from sys import argv
from analex import Analex
from sets import ImmutableSet

class SynAna:
	def advance(self):
		self.component = self.lexana.Analiza()

	def analyzePrograma(self):
		if (self.component.cat == "PR" and self.component.valor == "PROGRAMA"):
			self.advance()
			self.check(cat="Identif", sync=set())
			self.check(cat="PtoComa", sync=set())
			self.analyzeDeclVar()
			self.analyzeDeclSubprg()
			self.analyzeInstrucciones()
			self.check(cat="Punto", sync=set())
		else:
			self.error()

	def analyzeDeclVar(self):
		if (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			self.analyzeListaId()
			self.check(cat="DosPtos", sync=set())
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set())
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error()

	def analyzeDeclV(self):
		if (self.component.cat == "Identif"):
			self.analyzeListaId()
			self.check(cat="DosPtos", sync=set())
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set())
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error()

	def analyzeListaId(self):
		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoListaId()
		else:
			self.error()
			self.sincroniza()

	def analyzeRestoListaId(self):
		if (self.component.cat == "Coma"):
			self.advance()
			self.analyzeListaId()
		elif (not (self.component.cat == "DosPtos")):
			self.error()

	def analyzeTipo(self):
		if (self.component.cat == "PR" and self.component.valor == "VECTOR"):
			self.advance()
			self.check(cat="CorAp", sync=set())
			self.check(cat="Numero", sync=set())
			self.check(cat="CorCi", sync=set())
			self.check(cat="PR", valor="DE", sync=set(['PtoComa'], []))
			self.analyzeTipo()
		elif (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.analyzeTipoStd()
		else:
			self.error()

	def analyzeTipoStd(self):
		if (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.advance()
		else:
			self.error()

	def analyzeDeclSubprg(self):
		if (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION"] )):
			self.analyzeDeclSub()
			self.check(cat="PtoComa", sync=set())
			self.analyzeDeclSubprg()
		elif (not (self.component.cat == "PR" and self.component.valor == "INICIO")):
			self.error()

	def analyzeDeclSub(self): # Check deberia admitir PR y el conjunto de sincronizacion #############################
		if (self.component.cat == "PR" and self.component.valor == "PROC"):
			self.advance()
			self.check(cat="Identif", sync=set())
			self.check(cat="PtoComa", sync=set())
			self.analyzeInstrucciones()
		elif (self.component.cat == "PR" and self.component.valor == "FUNCION"):
			self.advance()
			self.check(cat="Identif", sync=set())
			self.check(cat="DosPtos", sync=set())
			self.analyzeTipoStd()
			self.check(cat="PtoComa", sync=set())
			self.analyzeInstrucciones()
		else:
			self.error()

	def analyzeInstrucciones(self):
		if (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			self.check(cat="PR", valor="FIN", sync=set())
		else:
			self.error()

	def analyzeListaInst(self):
		if (self.component.cat == "Identif" or (self.component.cat == "PR" and self.component.valor in ["INICIO", "SI", "MIENTRAS", "LEE", "ESCRIBE"])):
			self.analyzeInstruccion()
			self.check(cat="PtoComa", sync=set())
			self.analyzeListaInst()
		elif (not (self.component.cat == "PR" and self.component.valor == "FIN")):
			self.error()

	def analyzeInstruccion(self):
		if (self.component.cat == "Identif"):
			self.analyzeInstSimple()
		elif (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			self.check(cat="PR", valor="FIN", sync=set())
		elif (self.component.cat == "PR" and self.component.valor == "SI"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="PR", valor="ENTONCES", sync=set())
			self.analyzeInstruccion()
			self.check(cat="PR", valor="SINO", sync=set())
			self.analyzeInstruccion()
		elif (self.component.cat == "PR" and self.component.valor == "MIENTRAS"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="PR", valor="HACER", sync=set())
			self.analyzeInstruccion()
		elif (self.component.cat == "PR" and self.component.valor in ["LEE", "ESCRIBE"]):
			self.analyzeInstES()
		else:
			self.error()

	def analyzeInstSimple(self):
		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoInstSimple()
		else:
			self.error()

	def analyzeRestoInstSimple(self):
		if (self.component.cat == "CorAp"):
			self.advance()
			self.analyzeExprSimple()
			self.check(cat="CorCi", sync=set())
			self.check(cat="OpAsigna", sync=set())
			self.analyzeExpresion()
		elif (self.component.cat == "OpAsigna"):
			self.advance()
			self.analyzeExpresion()
		elif (not (self.component.cat == "PtoComa" or (self.component.cat == "PR" and self.component.valor == "SINO"))):
			self.error()

	def analyzeVariable(self):
		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoVar()
		else:
			self.error()

	def analyzeRestoVar(self):
		if (self.component.cat == "CorAp"):
			self.advance()
			self.analyzeExprSimple()
			self.check(cat="CorCi", sync=set())
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd", "OpMult"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "Y", "O"]))):
			self.error()

	def analyzeInstES(self):
		if (self.component.cat == "PR" and self.component.valor == "LEE"):
			self.advance()
			self.check(cat="ParentAp", sync=set())
			self.check(cat="Identif", sync=set())
			self.check(cat="ParentCi", sync=set())
		elif (self.component.cat == "PR" and self.component.valor == "ESCRIBE"):
			self.advance()
			self.check(cat="ParentAp", sync=set())
			self.analyzeExprSimple()
			self.check(cat="ParentCi", sync=set())
		else:
			self.error()

	def analyzeExpresion(self):
		if (self.component.cat in ["Identif", "Numero", "ParentAp", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeExprSimple()
			self.analyzeExprAux()
		else:
			self.error()

	def analyzeExprAux(self):
		if (self.component.cat == "OpRel"):
			self.advance()
			self.analyzeExprSimple()
		elif (not (self.component.cat in ["PtoComa", "ParentCi"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error()

	def analyzeExprSimple(self):
		if (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		elif(self.component.cat == "OpAdd"):
			self.analyzeSigno()
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		else:
			self.error()

	def analyzeRestoExSimple(self):
		if (self.component.cat == "OpAdd" or (self.component.cat == "PR" and self.component.valor in ["O"])):
			self.advance()
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error()

	def analyzeTermino(self):
		if (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeFactor()
			self.analyzeRestoTerm()
		else:
			self.error()

	def analyzeRestoTerm(self):
		if (self.component.cat == "OpMult" or (self.component.cat == "PR" and self.component.valor in ["Y"])):
			self.advance()
			self.analyzeFactor()
			self.analyzeRestoTerm()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "O"]))):
			self.error()

	def analyzeFactor(self):
		if (self.component.cat == "Identif"):
			self.analyzeVariable()
		elif (self.component.cat == "Numero"):
			self.advance()
		elif (self.component.cat == "ParentAp"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="ParentCi", sync=set())
		elif (self.component.cat == "PR" and self.component.valor == "NO"):
			self.advance()
			self.analyzeFactor()
		elif (self.component.cat == "PR" and self.component.valor in ["CIERTO", "FALSO"]):
			self.advance()
		else:
			self.error()

	def analyzeSigno(self):
		if (self.component.cat == "OpAdd"):
			self.advance()
		else:
			self.error()

	def check(self, **kwargs):
		if (self.component.cat == kwargs['cat']):
			if 'valor' in kwargs:
				if (self.component.valor != kwargs['valor']):
					self.error(kwargs['sync'])
			self.advance()
		else:
			self.error(kwargs['sync'])

	def sincroniza(self, *args):
		#while self.componente is not None and self.componente.cat not in args[0]:
		#	self.advance()
		self.advance()

	def error(self, *args): 
		print ("SINTAX TERROR: Line " + str(self.lexana.nlinea))
		print ("-- Component: " + str(self.component))
		self.sincroniza(args)

	def __init__(self, lexana):
		self.lexana = lexana
		self.advance()


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
	synana=SynAna(analex)
	try:
		synana.analyzePrograma()
	except errores.Error, err:
		sys.stderr.write("%s\n" % err)
		analex.muestraError(sys.stderr)
