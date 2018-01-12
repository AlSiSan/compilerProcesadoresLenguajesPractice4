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
			ids = []
			if (hasattr(self, 'component') and self.component.cat == "Identif"):
				ids = [self.component.valor]
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["VAR", "PROC", "FUNCION", "INICIO"]))
			decl_var = self.analyzeDeclVar(ids = ids)
			decl_subprg = self.analyzeDeclSubprg(ids = decl_var['ids'])
			self.analyzeInstrucciones()
			self.check(cat="Punto", sync=set([None]), endEx=True)
		else:
			self.error(msg='PROGRAMA',
				sync=set([None, "Identif"]))

	def analyzeDeclVar(self, **kwargs):
		decl_var = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			lista_id = self.analyzeListaId(ids = decl_var['ids'])
			self.check(cat="DosPtos", sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO", "ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			decl_v = self.analyzeDeclV(ids = lista_id['ids'])
			decl_var['ids'] = decl_v['ids']
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error(msg='VAR, PROC, FUNCION, INICIO',
				sync=set([None, "PR"]),
				spr=set(["PROC", "FUNCION", "INICIO"]))
		return decl_var

	def analyzeDeclV(self, **kwargs):
		decl_v = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			lista_id = self.analyzeListaId(ids = decl_v['ids'])
			self.check(cat="DosPtos", sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO", "ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			decl_v1 = self.analyzeDeclV(ids = lista_id['ids'])
			decl_v['ids'] = decl_v1['ids']
		elif (not (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION", "INICIO"] ))):
			self.error(msg='Identif, PROC, FUNCION, INICIO',
				sync=set([None, "PR"]),
				spr=set(["PROC", "FUNCION", "INICIO"]))
		return decl_v

	def analyzeListaId(self, **kwargs):
		lista_id = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			v = self.component.valor
			if(v not in lista_id['ids']):
				lista_id['ids'].append(v)
			else:
				self.errorS(id = v)
			self.advance()
			resto_listaid = self.analyzeRestoListaId(ids = lista_id['ids'])
			lista_id['ids'] = resto_listaid['ids']
		else:
			self.error(msg='Identif',
				sync=set([None, "DosPtos"]))
		return lista_id

	def analyzeRestoListaId(self, **kwargs):
		resto_listaid = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Coma"):
			self.advance()
			lista_id = self.analyzeListaId(ids = resto_listaid['ids'])
			resto_listaid['ids'] = lista_id['ids']
		elif (not (self.component.cat == "DosPtos")):
			self.error(msg='",", :',
				sync=set([None, "DosPtos"]))
		return resto_listaid

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
			self.error(msg='VECTOR, ENTERO, REAL, BOOLEANO',
				sync=set([None, "PtoComa"]))

	def analyzeTipoStd(self):
		if (self.component == None):
			return

		if (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			self.advance()
		else:
			self.error(msg='ENTERO, REAL, BOOLEANO',
				sync=set([None, "PtoComa"]))

	def analyzeDeclSubprg(self, **kwargs):
		ids = kwargs['ids']
		if (self.component == None):
			return ids

		if (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION"] )):
			ids = self.analyzeDeclSub(ids = ids)
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["INICIO", "PROC", "FUNCION"]))
			ids = self.analyzeDeclSubprg(ids = ids)
		elif (not (self.component.cat == "PR" and self.component.valor == "INICIO")):
			self.error(msg='PROC, FUNCION, INICIO',
				sync=set([None, "PR"]),
				spr=set(["INICIO"]))
		return ids

	def analyzeDeclSub(self, **kwargs):
		ids = kwargs['ids']
		if (self.component == None):
			return ids
		
		if (self.component.cat == "PR" and self.component.valor == "PROC"):
			self.advance()
			if (self.component.cat == "Identif"):
				v = self.component.valor
				if(v not in ids):
					ids.append(v)
				else:
					self.errorS(id = v)
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			self.analyzeInstrucciones()
		elif (self.component.cat == "PR" and self.component.valor == "FUNCION"):
			self.advance()
			if (self.component.cat == "Identif"):
				v = self.component.valor
				if(v not in ids):
					ids.append(v)
				else:
					self.errorS(id = v)
			self.check(cat="Identif", sync=set([None, "PtoComa", "DosPtos"]))
			self.check(cat="DosPtos", sync=set([None, "PtoComa", "PR"]), spr=set(["ENTERO", "REAL", "BOOLEANO"]))
			self.analyzeTipoStd()
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			self.analyzeInstrucciones()
		else:
			self.error(msg='PROC, FUNCION',
				sync=set([None, "PtoComa"]))
		return ids

	def analyzeInstrucciones(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			self.analyzeListaInst()
			self.check(cat="PR", valor="FIN", sync=set([None, "Punto", "PtoComa"]))
		else:
			self.error(msg='INICIO',
				sync=set([None, "Punto", "PtoComa"]))

	def analyzeListaInst(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "Identif" or (self.component.cat == "PR" and self.component.valor in ["INICIO", "SI", "MIENTRAS", "LEE", "ESCRIBE"])):
			self.analyzeInstruccion()
			self.check(cat="PtoComa", sync=set([None, "Identif", "PR"]), spr=set(["FIN", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			self.analyzeListaInst()
		elif (not (self.component.cat == "PR" and self.component.valor == "FIN")):
			self.error(msg='Identif, INICIO, SI, MIENTRAS, LEE, ESCRIBE, FIN',
				sync=set([None, "PR"]),
				spr=set(["FIN"]))

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
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["SINO"]))
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
			self.error(msg='Identif, INICIO, SI, MIENTRAS, LEE, ESCRIBE',
				sync=set([None, "PtoComa", "PR"]),
				spr=set(["SINO"]))

	def analyzeInstSimple(self):
		if (self.component == None):
			return

		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoInstSimple()
		else:
			self.error(msg='Identif',
				sync=set([None, "PtoComa", "PR"]),
				spr=set(["SINO"]))

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
			self.error(msg='[, OpAsigna, ;, SINO',
				sync=set([None, "PtoComa", "PR"]),
				spr=set(["SINO"]))

	def analyzeVariable(self):
		if (self.component == None):
			return

		if (self.component.cat == "Identif"):
			self.advance()
			self.analyzeRestoVar()
		else:
			self.error(msg='Identif',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
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
			self.error(msg='[, ;, ], ), OpRel, OpAdd, OpMult, ENTONCES, SINO, HACER, Y, O',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
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
			self.error(msg='LEE, ESCRIBE',
				sync=set([None, "PtoComa", "PR"]),
				spr=set(["SINO"]))

	def analyzeExpresion(self):
		if (self.component == None):
			return
		
		if (self.component.cat in ["Identif", "Numero", "ParentAp", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeExprSimple()
			self.analyzeExprAux()
		else:
			self.error(msg='Identif, Numero, (, OpAdd, NO, CIERTO, FALSO',
				sync=set([None, "PR", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeExprAux(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpRel"):
			self.advance()
			self.analyzeExprSimple()
		elif (not (self.component.cat in ["PtoComa", "ParentCi"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error(msg='OpRel, ;, ), ENTONCES, SINO, HACER',
				sync=set([None, "PR", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

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
			self.error(msg='Identif, Numero, (, NO, CIERTO, FALSO',
				sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeRestoExSimple(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpAdd" or (self.component.cat == "PR" and self.component.valor in ["O"])):
			self.advance()
			self.analyzeTermino()
			self.analyzeRestoExSimple()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER"]))):
			self.error(msg='OpAdd, O, ;, ], ), OpRel, ENTONCES, SINO, HACER',
				sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER", "SINO"]))

	def analyzeTermino(self):
		if (self.component == None):
			return
		
		if (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			self.analyzeFactor()
			self.analyzeRestoTerm()
		else:
			self.error(msg='Identif, Numero, (, NO, CIERTO, FALSO',
				sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["O", "ENTONCES", "HACER", "SINO"]))

	def analyzeRestoTerm(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpMult" or (self.component.cat == "PR" and self.component.valor in ["Y"])):
			self.advance()
			self.analyzeFactor()
			self.analyzeRestoTerm()
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "O"]))):
			self.error(msg='OpMult, Y, ;, ), OpRel, OpAdd, ENTONCES, SINO, HACER, O', 
				sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
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
			self.error(msg='Identif, Numero, (, NO, CIERTO or FALSO',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER", "SINO"]))

	def analyzeSigno(self):
		if (self.component == None):
			return
		
		if (self.component.cat == "OpAdd"):
			self.advance()
		else:
			self.error(msg='OpAdd',
				sync=set([None, "PR", "Identif", "ParentAp", "Numero"]),
				spr=set(["NO", "CIERTO", "FALSO"]))

	def check(self, **kwargs):
		if (self.component == None):
			return
		mes = ''
		if ('cat' in kwargs):
			if (self.component.cat == kwargs['cat']):
				mes = str(kwargs['cat'])
				if ('valor' in kwargs):
					mes = str(kwargs['valor'])
				if (self.component.cat == "PR" and 'valor' in kwargs and self.component.valor == kwargs['valor']
					or self.component.cat != "PR"):
					if('endEx' not in kwargs):
						kwargs['endEx'] = False
					self.advance(endEx=kwargs['endEx'])
					return
			if ('spr' not in kwargs):
				self.error(sync=kwargs['sync'], msg=mes)
			else:
				self.error(sync=kwargs['sync'], spr=kwargs['spr'], msg=mes)
		else:
			print ("Error en la llamada a check! Categoria no indicada!")

	def sincroniza(self, **kwargs):
		while hasattr(self, 'component') and self.component is not None and (
			self.component.cat not in kwargs['sync'] or (
				self.component.cat == 'PR' and 'PR' in kwargs['sync'] and 'spr' in kwargs and self.component.valor not in kwargs['spr']
				)):
			self.advance()
		if (not hasattr(self, 'component') or self.component is None):
			print("Fin de fichero inesperado!")
			return
		print("Sincronizado con: " + self.component.cat)
		#self.advance()

	def error(self, **kwargs):
		print ("SINTAX TERROR: Line " + str(self.lexana.nlinea))
		if 'msg' in kwargs:
			print ("EXPECTED " + kwargs['msg'])
		#print ("-- Component: " + str(self.component))
		if ('spr' not in kwargs):
			self.sincroniza(sync=kwargs['sync'])
		else:
			self.sincroniza(sync=kwargs['sync'], spr=kwargs['spr'])
	
	def errorS(self, **kwargs):
		print ("Identificador repetido " + kwargs['id'])

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
