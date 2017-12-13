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
	def advance(self, endEx = False):
		self.component = self.lexana.Analiza()
		if (not endEx and not self.endErr and self.component is None):
			self.endErr = True
			print("Fin de fichero inesperado!")

	def analyzePrograma(self):
		if (self.component == None):
			return
		if (self.component.cat == "PR" and self.component.valor == "PROGRAMA"):
			self.advance()
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["VAR", "PROC", "FUNCION", "INICIO"]))
			self.analyzeDeclVar()
			self.analyzeDeclSubprg()
			self.analyzeInstrucciones()
			self.check(cat="Punto", sync=set([None]), endEx=True)
		else:
			self.error(sync=set([None, "Identif"]))

	def analyzeDeclVar(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			self.analyzeListaId()
			self.check(cat="DosPtos", sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO", "ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error(sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO"]))

	def analyzeDeclV(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "Identif"):
			self.analyzeListaId()
			self.check(cat="DosPtos", sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO", "ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			self.analyzeDeclV()
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error(sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO"]))

	def analyzeListaId(self):
		
		if (self.component == None):
			return

		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoListaId()
		else:
			self.error(sync=set([None, "DosPtos"]))

	def analyzeRestoListaId(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "Coma"):
			self.advance()
			self.analyzeListaId()
		elif (not (self.component.cat == "DosPtos")):
			self.error(sync=set([None, "DosPtos"]))

	def analyzeTipo(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "PR" and self.component.valor == "VECTOR"):
			self.advance()
			self.check(cat="CorAp", sync=set([None, "PtoComa", "Numero"]))
			self.check(cat="Numero", sync=set([None, "PtoComa", "CorCi"]))
			self.check(cat="CorCi", sync=set([None, "PtoComa", "PR"]), spr=set(["DE"]))
			self.check(cat="PR", valor="DE", sync=set([None, "PtoComa", "PR"]), spr=set(["ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			self.analyzeTipo()
		elif (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.analyzeTipoStd()
		else:
			self.error(sync=set([None, "PtoComa"]))

	def analyzeTipoStd(self):
		
		if (self.component == None):
			return

		if (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.advance()
		else:
			self.error(sync=set([None, "PtoComa"]))

	def analyzeDeclSubprg(self):
		
		if (self.component == None):
			return
		

		if (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION"] )):
			self.analyzeDeclSub()
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["INICIO", "PROC", "FUNCION"]))
			self.analyzeDeclSubprg()
		elif (not (self.component.cat == "PR" and self.component.valor == "INICIO")):
			self.error(sync=set([None, "PR"]), spr=set(["INICIO"]))

	def analyzeDeclSub(self): # Check deberia admitir PR y el conjunto de sincronizacion #############################
		
		if (self.component == None):
			return
		
		if (self.component.cat == "PR" and self.component.valor == "PROC"):
			self.advance()
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			self.analyzeInstrucciones()
		elif (self.component.cat == "PR" and self.component.valor == "FUNCION"):
			self.advance()
			self.check(cat="Identif", sync=set([None, "PtoComa", "DosPtos"]))
			self.check(cat="DosPtos", sync=set([None, "PtoComa", "PR"]), spr=set(["ENTERO", "REAL", "BOOLEANO"]))
			self.analyzeTipoStd()
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			self.analyzeInstrucciones()
		else:
			self.error(sync=set([None, "PtoComa"]))

	def analyzeInstrucciones(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			self.check(cat="PR", valor="FIN", sync=set([None, "Punto", "PtoComa"]))
		else:
			self.error(sync=set([None, "Punto", "PtoComa"]))

	def analyzeListaInst(self):
		

		if (self.component == None):
			return
		
		if (self.component.cat == "Identif" or (self.component.cat == "PR" and self.component.valor in ["INICIO", "SI", "MIENTRAS", "LEE", "ESCRIBE"])):
			self.analyzeInstruccion()
			self.check(cat="PtoComa", sync=set([None, "Identif", "PR"]), spr=set(["FIN", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			self.analyzeListaInst()
		elif (not (self.component.cat == "PR" and self.component.valor == "FIN")):
			self.error(sync=set([None, "PR"]), spr=set(["FIN"]))

	def analyzeInstruccion(self):
		

		if (self.component == None):
			return
		
		if (self.component.cat == "Identif"):
			self.analyzeInstSimple()
		elif (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			self.check(cat="PR", valor="FIN", sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))
		elif (self.component.cat == "PR" and self.component.valor == "SI"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="PR", valor="ENTONCES", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			self.analyzeInstruccion()
			self.check(cat="PR", valor="SINO", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			self.analyzeInstruccion()
		elif (self.component.cat == "PR" and self.component.valor == "MIENTRAS"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="PR", valor="HACER", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			self.analyzeInstruccion()
		elif (self.component.cat == "PR" and self.component.valor in ["LEE", "ESCRIBE"]):
			self.analyzeInstES()
		else:
			self.error(sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))

	def analyzeInstSimple(self):
		
		if (self.component == None):
			return
		

		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoInstSimple()
		else:
			self.error(sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))

	def analyzeRestoInstSimple(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "CorAp"):
			self.advance()
			self.analyzeExprSimple()
			self.check(cat="CorCi", sync=set([None, "PtoComa", "PR", "OpAsigna"]), spr=set(["SINO"]))
			self.check(cat="OpAsigna", sync=set([None, "PtoComa", "PR", "Identif", "Numero", "ParentAp", "OpAdd"]), spr=set(["SINO", "NO", "CIERTO", "FALSO"]))
			self.analyzeExpresion()
		elif (self.component.cat == "OpAsigna"):
			self.advance()
			self.analyzeExpresion()
		elif (not (self.component.cat == "PtoComa" or (self.component.cat == "PR" and self.component.valor == "SINO"))):
			self.error(sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))

	def analyzeVariable(self):
		
		if (self.component == None):
			return
		

		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoVar()
		else:
			self.error(sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))

	def analyzeRestoVar(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat == "CorAp"):
			self.advance()
			self.analyzeExprSimple()
			self.check(cat="CorCi", sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd", "OpMult"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "Y", "O"]))):
			self.error(sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))

	def analyzeInstES(self):
		
		if (self.component == None):
			return
		

		if (self.component.cat == "PR" and self.component.valor == "LEE"):
			self.advance()
			self.check(cat="ParentAp", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO"]))
			self.check(cat="Identif", sync=set([None, "ParentCi", "PtoComa", "PR"]), spr=set(["SINO"]))
			self.check(cat="ParentCi", sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))
		elif (self.component.cat == "PR" and self.component.valor == "ESCRIBE"):
			self.advance()
			self.check(cat="ParentAp", sync=set([None, "Identif", "Numero", "OpAdd", "ParentAp", "PtoComa", "PR"]), spr=set(["SINO", "NO", "CIERTO", "FALSO"]))
			self.analyzeExprSimple()
			self.check(cat="ParentCi", sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))
		else:
			self.error(sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))

	def analyzeExpresion(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat in ["Identif", "Numero", "ParentAp", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeExprSimple()
			self.analyzeExprAux()
		else:
			self.error(sync=set([None, "PR", "ParentCi", "PtoComa"]), spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeExprAux(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpRel"):
			self.advance()
			self.analyzeExprSimple()
		elif (not (self.component.cat in ["PtoComa", "ParentCi"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error(sync=set([None, "PR", "ParentCi", "PtoComa"]), spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeExprSimple(self):
		
		if (self.component == None):
			return
		
		if (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		elif(self.component.cat == "OpAdd"):
			self.analyzeSigno()
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		else:
			self.error(sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeRestoExSimple(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpAdd" or (self.component.cat == "PR" and self.component.valor in ["O"])):
			self.advance()
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error(sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeTermino(self):
		if (self.component == None):
			return
		
		if (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeFactor()
			self.analyzeRestoTerm()
		else:
			self.error(sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["O", "ENTONCES", "HACER", "SINO"]))

	def analyzeRestoTerm(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpMult" or (self.component.cat == "PR" and self.component.valor in ["Y"])):
			self.advance()
			self.analyzeFactor()
			self.analyzeRestoTerm()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "O"]))):
			self.error(sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["O", "ENTONCES", "HACER", "SINO"]))

	def analyzeFactor(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "Identif"):
			self.analyzeVariable()
		elif (self.component.cat == "Numero"):
			self.advance()
		elif (self.component.cat == "ParentAp"):
			self.advance()
			self.analyzeExpresion()
			self.check(cat="ParentCi", sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))
		elif (self.component.cat == "PR" and self.component.valor == "NO"):
			self.advance()
			self.analyzeFactor()
		elif (self.component.cat == "PR" and self.component.valor in ["CIERTO", "FALSO"]):
			self.advance()
		else:
			self.error(sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))

	def analyzeSigno(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpAdd"):
			self.advance()
		else:
			self.error(sync=set([None, "PR", "Identif", "ParentAp", "Numero"]),
				spr=set(["NO", "CIERTO", "FALSO"]))

	def check(self, **kwargs):
		if (self.component == None):
			return
		if ('cat' in kwargs):
			if (self.component.cat == kwargs['cat']):
				if (self.component.cat == "PR" and 'valor' in kwargs and self.component.valor == kwargs['valor']
					or self.component.cat != "PR"):
					if('endEx' not in kwargs):
						kwargs['endEx'] = False
					self.advance(endEx=kwargs['endEx'])
					return
			if ('spr' not in kwargs):
				self.error(sync=kwargs['sync'])
			else:
				self.error(sync=kwargs['sync'], spr=kwargs['spr'])
		else:
			print ("Error en la llamada a check! Categoria no indicada!")

	def sincroniza(self, **kwargs):
		while hasattr(self, 'component') and (
			self.component.cat not in kwargs['sync'] or (
				self.component.cat == 'PR' and 'PR' in kwargs['sync'] and 'spr' in kwargs and self.component.valor not in kwargs['spr']
				)):
			self.advance()
			print("Sincronizado con: " + self.component.cat)
		if (not hasattr(self, 'component')):
			print("Fin de fichero inesperado!")
		#self.advance()

	def error(self, **kwargs): 
		print ("SINTAX TERROR: Line " + str(self.lexana.nlinea))
		print ("-- Component: " + str(self.component))
		if ('spr' not in kwargs):
			self.sincroniza(sync=kwargs['sync'])
		else:
			self.sincroniza(sync=kwargs['sync'], spr=kwargs['spr'])

	def __init__(self, lexana):
		self.lexana = lexana
		self.endErr = False
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
