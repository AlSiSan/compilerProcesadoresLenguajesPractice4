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
	'''
	def __init__(self, flu):
		self.flu = flu

		# Pila
		self.stack = []

		# Conjunto N de no terminales
		self.N = ImmutableSet(["<Programa>", "<decl_var>", "<decl_v>", "<lista_id>", "<resto_listaid>", "<Tipo>", "<Tipo_std>", "<decl_subprg>", "<instrucciones>", "<lista_inst>", "<instruccion>", "<Inst_simple>", "<resto_instsimple>", "<variable>", "<resto_var>", "<inst_e/s>", "<expresion>>", "<expr_simple>", "<resto_exsimple>", "<termino>", "<resto_term>", "<factor>", "<signo>"])

		# Caracter de fondo de pila
		self.bos = "$"
	'''

	def advance(self):
		self.component = self.lexana.Analiza()

	def analyzePrograma(self):
		if (self.component.cat == "PR" and self.component.valor == "PROGRAMA"):
			self.advance()
			self.check("Identif")
			self.check("PtoComa")
			self.analyzeDeclVar()
			self.analyzeDeclSubprg()
			self.analyzeInstrucciones()
			self.check("Punto")
		else:
			self.error()
			self.sincroniza([], [])

	def analyzeDeclVar(self):
		if (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			self.analyzeListaId()
			self.check("DosPtos")
			self.analyzeTipo()
			self.check("PtoComa")
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error()
			self.sincroniza(['PR'], ['PROC', 'FUNCION', 'INICIO'])

	def analyzeDeclV(self):
		if (self.component.cat == "Identif"):
			self.analyzeListaId()
			self.check("DosPtos")
			self.analyzeTipo()
			self.check("PtoComa")
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error()
			self.sincroniza(['PR'], ['PROC', 'FUNCION', 'INICIO'])

	def analyzeListaId(self):
		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoListaId()
		else:
			self.error()
			self.sincroniza(['DosPtos'], [])

	def analyzeRestoListaId(self):
		if (self.component.cat == "Coma"):
			self.advance()
			self.analyzeListaId()
		elif (not (self.component.cat == "DosPtos")):
			self.error()
			self.sincroniza(['DosPtos'], [])

	def analyzeTipo(self):
		if (self.component.cat == "PR" and self.component.valor == "VECTOR"):
			self.advance()
			self.check("CorAp")
			self.check("Numero")
			self.check("CorCi")
			if (self.component.cat == "PR" and self.component.valor == "DE"):
				self.advance()
				self.analyzeTipo()
			else:
				self.error()
				self.sincroniza(['PtoComa'], [])
		elif (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.analyzeTipoStd()
		else:
			self.error()
			self.sincroniza(['PtoComa'], [])

	def analyzeTipoStd(self):
		if (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.advance()
		else:
			self.error()
			self.sincroniza(['PtoComa'], [])

	def analyzeDeclSubprg(self):
		if (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION"] )):
			self.analyzeDeclSub()
			self.check("PtoComa")
			self.analyzeDeclSubprg()
		elif (not (self.component.cat == "PR" and self.component.valor == "INICIO")):
			self.error()
			self.sincroniza(['PR'], ['INICIO'])

	def analyzeDeclSub(self): # Check debería admitir PR y el conjunto de sincronizacion #############################
		if (self.component.cat == "PR" and self.component.valor == "PROC"):
			self.advance()
			self.check("Identif")
			self.check("PtoComa")
			self.analyzeInstrucciones()
		elif (self.component.cat == "PR" and self.component.valor == "FUNCION"):
			self.advance()
			self.check("Identif")
			self.check("DosPtos")
			self.analyzeTipoStd()
			self.check("PtoComa")
			self.analyzeInstrucciones()
		else:
			self.error()

	def analyzeInstrucciones(self):
		if (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			if (self.component.cat == "PR" and self.component.valor == "FIN"):
				self.advance()
			else:
				self.error()
		else:
			self.error()

	def analyzeListaInst(self):
		if (self.component.cat == "Identif" or (self.component.cat == "PR" and self.component.valor in ["INICIO", "SI", "MIENTRAS", "LEE", "ESCRIBE"])):
			self.analyzeInstruccion()
			self.check("PtoComa")
			self.analyzeListaInst()
		elif (not (self.component.cat == "PR" and self.component.valor == "FIN")):
			self.error()

	def analyzeInstruccion(self):
		if (self.component.cat == "Identif"):
			self.analyzeInstSimple()
		elif (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			if (self.component.cat == "PR" and self.component.valor == "FIN"):
				self.advance()
			else:
				self.error()
		elif (self.component.cat == "PR" and self.component.valor == "SI"):
			self.advance()
			self.analyzeExpresion()
			if (self.component.cat == "PR" and self.component.valor == "ENTONCES"):
				self.advance()
				self.analyzeInstruccion()
				if (self.component.cat == "PR" and self.component.valor == "SINO"):
					self.advance()
					self.analyzeInstruccion()
				else:
					self.error()
			else:
				self.error()
		elif (self.component.cat == "PR" and self.component.valor == "MIENTRAS"):
			self.advance()
			self.analyzeExpresion()
			if (self.component.cat == "PR" and self.component.valor == "HACER"):
				self.advance()
				self.analyzeInstruccion()
			else:
				self.error()
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
			self.check("CorCi")
			self.check("OpAsigna")
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
			self.check("CorCi")
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd", "OpMult"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "Y", "O"]))):
			self.error()

	def analyzeInstES(self):
		if (self.component.cat == "PR" and self.component.valor == "LEE"):
			self.advance()
			self.check("ParentAp")
			self.check("Identif")
			self.check("ParentCi")
		elif (self.component.cat == "PR" and self.component.valor == "ESCRIBE"):
			self.advance()
			self.check("ParentAp")
			self.analyzeExprSimple()
			self.check("ParentCi")
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
			self.check("ParentCi")
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

	def check(self, cat):
		if (self.component.cat == cat):
			self.advance()
		else:
			self.error()

	def sincroniza(self, sinc):
		while self.componente is not None and self.componente.cat not in sinc:
			self.advance()

	def error(self):
		print ("SINTAX TERROR: Line " + str(self.lexana.nlinea))
		print ("-- Component: " + str(self.component))
		self.advance()

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
