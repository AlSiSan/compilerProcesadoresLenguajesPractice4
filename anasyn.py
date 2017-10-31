#!/usr/bin/env python

import componentes
import errores
import flujo
import string
import sys

from sys import argv
from analex import Analex
from sets import ImmutableSet

class SynLex:
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

	def analyzeDeclVar(self):
		if (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			self.analyzeListaId()
			self.check("DosPtos")
			self.analyzeTipo()
			self.check("PtoComa")
			self.analyzeDeclV()

	def analyzeDeclV(self):
		self.analyzeListaId()
		self.check("DosPtos")
		self.analyzeTipo()
		self.check("PtoComa")
		self.analyzeDeclV()

	def analyzeListaId(self):
		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoListaId()
		else:
			self.error()

	def analyzeRestoListaId(self):
		if (self.component.cat == "Coma"):
			self.analyzeListaId()

	def analyzeTipo(self):
		if (self.component.cat == "PR" and self.component.valor == "VECTOR"):
			self.advance()
			self.check("CorAp")
			if (self.component.cat == "Numero" and self.component.isInt):
				self.advance()
				self.check("CorCi")
				if (self.component.cat == "PR" and self.component.valor == "DE"):
					self.advance()
					self.analyzeTipo()
				else:
					self.error()
			else:
				self.error()
		else:
			self.analyzeTipoStd()

	def analyzeTipoStd(self):
		if (self.component.cat == "PR" and self.component.valor == "ENTERO"):
			self.advance()
		elif (self.component.cat == "PR" and self.component.valor == "REAL"):
			self.advance()
		elif (self.component.cat == "PR" and self.component.valor == "BOOLEANO"):
			self.advance()
		else:
			self.error()

	def analyzeDeclSubprg################adakfbkagbfagbfkbafkbajkfbskjakjdbsjkadbksjabdsjkabd

	def check(self, cat):
		if (self.component == cat):
			self.advance()
		else:
			self.error()

	def error(self):
		pass

	def __init__(self, lexana):
		self.lexana = lexana
		self.advance()
		self.analyzePrograma()
		self.check("eof") ############

	def predAna(self):
		self.stack.append(self.bos) # Se introduce el simbolo de fondo de pila
		self.stack.append("<Programa>") # Se introduce el primer N

		analex = Analex(self.flu) # Inicializar analizador lexico
		try:
			a = analex.Analiza()
			while (stack[-1] != self.bos):
				X = self.stack.pop()
				if (self.N.contains(X))
		except errores.Error, err:
			sys.stderr.write("%s\n" % err)
			analex.muestraError(sys.stderr)
