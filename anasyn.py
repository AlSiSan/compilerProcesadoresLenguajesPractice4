#!/usr/bin/env python

import componentes
import errores
import flujo
import string
import sys
import ast

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
		tree = None
		if (self.component == None):
			self.errored = True
		elif (self.component.cat == "PR" and self.component.valor == "PROGRAMA"):
			self.advance()
			ids = []
			v = None
			if (hasattr(self, 'component') and hasattr(self.component, 'cat') and self.component.cat == "Identif"):
				ids = [self.component.valor]
				v = self.component.valor
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["VAR", "PROC", "FUNCION", "INICIO"]))
			decl_var = self.analyzeDeclVar(ids = ids)
			decl_subprg = self.analyzeDeclSubprg(ids = decl_var['ids'], tipo_id = decl_var['tipo_id'])
			instrucciones = self.analyzeInstrucciones(ids = decl_subprg['ids'], tipo_id = decl_subprg['tipo_id'])
			self.check(cat="Punto", sync=set([None]), endEx=True)
			tree = ast.AST(v, instrucciones['nodos'])
		else:
			self.error(msg='PROGRAMA',
				sync=set([None]))
		return (tree, not self.errored)

	def analyzeDeclVar(self, **kwargs):
		decl_var = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "VAR"):
			self.advance()
			lista_id = self.analyzeListaId(ids = decl_var['ids'])
			self.check(cat="DosPtos", sync=set([None, "PR"]), spr=set(["PROC", "FUNCION", "INICIO", "ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			tipo = self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			decl_v = self.analyzeDeclV(ids = lista_id['ids'])
			decl_var['tipo_id'] = {}
			if 'tipo_id' in decl_v:
				decl_var['tipo_id'] = decl_v['tipo_id']
			if 'mids' in lista_id:
				for id in lista_id['mids']:
					decl_var['tipo_id'][id] = tipo['tipo']
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
			tipo = self.analyzeTipo()
			self.check(cat="PtoComa", sync=set([None, "PR", "Identif"]), spr=set(["PROC", "FUNCION", "INICIO"]))
			decl_v1 = self.analyzeDeclV(ids = lista_id['ids'])
			decl_v['tipo_id'] = {}
			if 'tipo_id' in decl_v1:
				decl_v['tipo_id'] = decl_v1['tipo_id']
			if 'mids' in lista_id:
				for id in lista_id['mids']:
					decl_v['tipo_id'] = tipo['tipo']
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
			lista_id['mids'] = []
			if 'mids' in resto_listaid:
				lista_id['mids'] = resto_listaid['mids']
			lista_id['mids'].append(v)
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
			resto_listaid['mids'] = lista_id['mids']
			resto_listaid['ids'] = lista_id['ids']
		elif (not (self.component.cat == "DosPtos")):
			self.error(msg='",", :',
				sync=set([None, "DosPtos"]))
		return resto_listaid

	def analyzeTipo(self, **kwargs):
		tipo = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "VECTOR"):
			self.advance()
			self.check(cat="CorAp", sync=set([None, "PtoComa", "Numero"]))
			self.check(cat="Numero", sync=set([None, "PtoComa", "CorCi"]))
			self.check(cat="CorCi", sync=set([None, "PtoComa", "PR"]), spr=set(["DE"]))
			self.check(cat="PR", valor="DE", sync=set([None, "PtoComa", "PR"]), spr=set(["ENTERO", "REAL", "BOOLEANO", "VECTOR"]))
			tipo1 = self.analyzeTipo()
			tipo['tipo'] = (4, tipo1['tipo'])
		elif (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			tipo_std = self.analyzeTipoStd()
			tipo['tipo'] = tipo_std['tipo']
		else:
			self.error(msg='VECTOR, ENTERO, REAL, BOOLEANO',
				sync=set([None, "PtoComa"]))
		return tipo

	def analyzeTipoStd(self, **kwargs):
		tipo_std = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and (self.component.valor in ["ENTERO", "REAL", "BOOLEANO"] )):
			if self.component.valor == "ENTERO":
				tipo_std['tipo'] = (0,)
			elif self.component.valor == "REAL":
				tipo_std['tipo'] = (1,)
			else:
				tipo_std['tipo'] = (2,)
			self.advance()
		else:
			self.error(msg='ENTERO, REAL, BOOLEANO',
				sync=set([None, "PtoComa"]))
		return tipo_std

	def analyzeDeclSubprg(self, **kwargs):
		decl_subprg = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and (self.component.valor in ["PROC", "FUNCION"] )):
			decl_sub = self.analyzeDeclSub(ids = decl_subprg['ids'], tipo_id = decl_subprg['tipo_id'])
			self.check(cat="PtoComa", sync=set([None, "PR"]), spr=set(["INICIO", "PROC", "FUNCION"]))
			decl_subprg1 = self.analyzeDeclSubprg(ids = decl_sub['ids'])
			if 'tipo_id' in decl_subprg1:
				decl_subprg['tipo_id'] = decl_subprg1['tipo_id']
			decl_subprg['tipo_id'][decl_sub['id']] = decl_sub['tipo']
			decl_subprg['ids'] = decl_subprg1['ids']
		elif (not (self.component.cat == "PR" and self.component.valor == "INICIO")):
			self.error(msg='PROC, FUNCION, INICIO',
				sync=set([None, "PR"]),
				spr=set(["INICIO"]))
		return decl_subprg

	def analyzeDeclSub(self, **kwargs):
		decl_sub = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "PROC"):
			self.advance()
			if (self.component.cat == "Identif"):
				v = self.component.valor
				if(v not in decl_sub['ids']):
					decl_sub['ids'].append(v)
				else:
					self.errorS(id = v)
			self.check(cat="Identif", sync=set([None, "PtoComa"]))
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			decl_sub['id'] = v
			decl_sub['tipo'] = (5, )
			decl_sub['tipo_id'][v] = (5, )
			self.analyzeInstrucciones(ids = decl_sub['ids'], tipo_id = decl_sub['tipo_id'])
		elif (self.component.cat == "PR" and self.component.valor == "FUNCION"):
			self.advance()
			if (self.component.cat == "Identif"):
				v = self.component.valor
				if(v not in decl_sub['ids']):
					decl_sub['ids'].append(v)
				else:
					self.errorS(id = v)
			self.check(cat="Identif", sync=set([None, "PtoComa", "DosPtos"]))
			self.check(cat="DosPtos", sync=set([None, "PtoComa", "PR"]), spr=set(["ENTERO", "REAL", "BOOLEANO"]))
			tipo_std = self.analyzeTipoStd()
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["INICIO"]))
			decl_sub['id'] = v
			decl_sub['tipo'] = (6, tipo_std['tipo'])
			decl_sub['tipo_id'][v] = (6, tipo_std['tipo'])
			self.analyzeInstrucciones(ids = decl_sub['ids'], tipo_id = decl_sub['tipo_id'])
		else:
			self.error(msg='PROC, FUNCION',
				sync=set([None, "PtoComa"]))
		return decl_sub

	def analyzeInstrucciones(self, **kwargs):
		instrucciones = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			lista_inst = self.analyzeListaInst(ids = instrucciones['ids'], tipo_id = instrucciones['tipo_id'])
			self.check(cat="PR", valor="FIN", sync=set([None, "Punto", "PtoComa"]))
			instrucciones['nodos'] = lista_inst['nodos']
		else:
			self.error(msg='INICIO',
				sync=set([None, "Punto", "PtoComa"]))
		return instrucciones

	def analyzeListaInst(self, **kwargs):
		lista_inst = kwargs
		lista_inst['nodos'] = []
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif" or (self.component.cat == "PR" and self.component.valor in ["INICIO", "SI", "MIENTRAS", "LEE", "ESCRIBE"])):
			instruccion = self.analyzeInstruccion(ids = lista_inst['ids'], tipo_id = lista_inst['tipo_id'])
			self.check(cat="PtoComa", sync=set([None, "Identif", "PR"]), spr=set(["FIN", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			lista_inst1 = self.analyzeListaInst(ids = lista_inst['ids'], tipo_id = lista_inst['tipo_id'])
			if instruccion['bloque'] == 0:
				lista_inst['nodos'] = [instruccion['nodo']]
			else:
				lista_inst['nodos'] = instruccion['nodo']
			lista_inst['nodos'] = lista_inst['nodos'] + lista_inst1['nodos']
		elif (not (self.component.cat == "PR" and self.component.valor == "FIN")):
			self.error(msg='Identif, INICIO, SI, MIENTRAS, LEE, ESCRIBE, FIN',
				sync=set([None, "PR"]),
				spr=set(["FIN"]))
		return lista_inst

	def analyzeInstruccion(self, **kwargs):
		instruccion = kwargs
		instruccion['bloque'] = 0
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			inst_simple = self.analyzeInstSimple(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			instruccion['nodo'] = inst_simple['nodo']
		elif (self.component.cat == "PR" and self.component.valor == "INICIO"):
			self.advance()
			lista_inst = self.analyzeListaInst(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			self.check(cat="PR", valor="FIN", sync=set([None, "PtoComa"]))
			instruccion['bloque'] = 1
			instruccion['nodo'] = lista_inst['nodos']
		elif (self.component.cat == "PR" and self.component.valor == "SI"):
			self.advance()
			expresion = self.analyzeExpresion(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			self.check(cat="PR", valor="ENTONCES", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			instruccion1 = self.analyzeInstruccion(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			self.check(cat="PtoComa", sync=set([None, "PtoComa", "PR"]), spr=set(["SINO"]))
			self.check(cat="PR", valor="SINO", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["SINO", "INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			instruccion2 = self.analyzeInstruccion(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			instruccion['nodo'] = ast.NodoSi(expresion['nodo'], instruccion1['nodo'], instruccion2['nodo'])
		elif (self.component.cat == "PR" and self.component.valor == "MIENTRAS"):
			self.advance()
			expresion = self.analyzeExpresion(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			self.check(cat="PR", valor="HACER", sync=set([None, "Identif", "PtoComa", "PR"]), spr=set(["INICIO", "LEE", "ESCRIBE", "SI", "MIENTRAS"]))
			instruccion1 = self.analyzeInstruccion(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			instruccion['nodo'] = ast.NodoMientras(expresion['nodo'], instruccion1['nodo'])
		elif (self.component.cat == "PR" and self.component.valor in ["LEE", "ESCRIBE"]):
			inst_es = self.analyzeInstES(ids = instruccion['ids'], tipo_id = instruccion['tipo_id'])
			instruccion['nodo'] = inst_es['nodo']
		else:
			self.error(msg='Identif, INICIO, SI, MIENTRAS, LEE, ESCRIBE',
				sync=set([None, "PtoComa"]))
		return instruccion

	def analyzeInstSimple(self, **kwargs):
		inst_simple = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			v = self.component.valor
			if (v not in inst_simple['ids']):
				self.errorBefore(id = v)
			self.advance()
			resto_instsimple = self.analyzeRestoInstSimple(ids = inst_simple['ids'],
															tipo = inst_simple['tipo_id'][v],
															tipo_id = inst_simple['tipo_id'],
															id = v)
			if resto_instsimple['vector'] == 0:
				inst_simple['nodo'] = ast.NodoAsignacion(ast.NodoAccesoVariable(v, inst_simple['tipo_id'][v][0]), resto_instsimple['expr'])
			else:
				inst_simple['nodo'] = ast.NodoAsignacion(ast.NodoAccesoVector(inst_simple['tipo_id'][v][1][0], v, resto_instsimple['exprvec']), resto_instsimple['expr'])
		else:
			self.error(msg='Identif',
				sync=set([None, "PtoComa"]))
		return inst_simple

	def analyzeRestoInstSimple(self, **kwargs):
		resto_instsimple = kwargs
		resto_instsimple['vector'] = 0
		if (self.component == None):
			pass
		elif (self.component.cat == "CorAp"):
			resto_instsimple['vector'] = 1
			if resto_instsimple['tipo'][0] != 4:
				self.errorNotVector(id = resto_instsimple['id'])
			self.advance()
			expr_simple = self.analyzeExprSimple(ids = resto_instsimple['ids'], tipo_id = resto_instsimple['tipo_id'])
			resto_instsimple['exprvec'] = expr_simple['nodo']
			if expr_simple['tipo'][0] != 0:
				self.errorAVector()
			self.check(cat="CorCi", sync=set([None, "PtoComa", "OpAsigna"]))
			self.check(cat="OpAsigna", sync=set([None, "PtoComa", "PR", "Identif", "Numero", "ParentAp", "OpAdd"]), spr=set(["NO", "CIERTO", "FALSO"]))
			expresion = self.analyzeExpresion(ids = resto_instsimple['ids'], tipo_id = resto_instsimple['tipo_id'])
			if (expresion['tipo'] != resto_instsimple['tipo'][1] and not (resto_instsimple['tipo'][1][0] == 1 and expresion['tipo'][0] == 0)):
				self.errorCast(tipo1 = expresion['tipo'][0], tipo2 = resto_instsimple['tipo'][1][0])
			resto_instsimple['expr'] = expresion['nodo']
		elif (self.component.cat == "OpAsigna"):
			self.advance()
			expresion = self.analyzeExpresion(ids = resto_instsimple['ids'], tipo_id = resto_instsimple['tipo_id'])
			if (expresion['tipo'] != resto_instsimple['tipo'] and not (resto_instsimple['tipo'][0] == 1 and expresion['tipo'][0] == 0)):
				self.errorCast(tipo1 = expresion['tipo'][0], tipo2 = resto_instsimple['tipo'][0])
			resto_instsimple['expr'] = expresion['nodo']
		elif (not (self.component.cat == "PtoComa" or (self.component.cat == "PR" and self.component.valor == "SINO"))):
			self.error(msg='[, OpAsigna, ;',
				sync=set([None, "PtoComa"]))
		return resto_instsimple

	def analyzeVariable(self, **kwargs):
		variable = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			variable['id'] = self.component.valor
			if (variable['id'] not in variable['ids']):
				self.errorBefore(id = variable['id'])
			self.advance()
			resto_var = self.analyzeRestoVar(ids = variable['ids'], tipo_id = variable['tipo_id'])
			if resto_var['vector'] == 0:
				variable['tipo'] = variable['tipo_id'][variable['id']]
				variable['nodo'] = ast.NodoAccesoVariable(variable['id'], variable['tipo'][0])
			elif variable['tipo_id'][variable['id']][0] == 4:
				variable['tipo'] = variable['tipo_id'][variable['id']][1]
				variable['nodo'] = ast.NodoAccesoVector(variable['tipo'][0], variable['id'], resto_var['nodo'])
			else:
				self.errorNotVector(id = variable['id'])
			variable['vector'] = resto_var['vector']
		else:
			self.error(msg='Identif',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER"]))
		return variable

	def analyzeRestoVar(self, **kwargs):
		resto_var = kwargs
		resto_var['vector'] = 0
		if (self.component == None):
			pass
		elif (self.component.cat == "CorAp"):
			resto_var['vector'] = 1
			self.advance()
			expr_simple = self.analyzeExprSimple(ids = resto_var['ids'], tipo_id = resto_var['tipo_id'])
			self.check(cat="CorCi", sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER"]))
			resto_var['nodo'] = expr_simple['nodo']
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd", "OpMult"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "SINO", "HACER", "Y", "O"]))):
			self.error(msg='[, ;, ], ), OpRel, OpAdd, OpMult, ENTONCES, HACER, Y, O',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER"]))
		return resto_var

	def analyzeInstES(self, **kwargs):
		inst_es = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "PR" and self.component.valor == "LEE"):
			self.advance()
			self.check(cat="ParentAp", sync=set([None, "Identif", "PtoComa"]))
			v = None
			if (hasattr(self, 'component') and hasattr(self.component, 'cat') and self.component.cat == "Identif"):
				v = self.component.valor
				if (v not in variable['ids']):
					self.errorBefore(id = self.component.valor)
			self.check(cat="Identif", sync=set([None, "ParentCi", "PtoComa"]))
			self.check(cat="ParentCi", sync=set([None, "PtoComa"]))
			inst_es['nodo'] = ast.NodoAccesoVariable(v, inst_es['tipo_id'][v][0])
		elif (self.component.cat == "PR" and self.component.valor == "ESCRIBE"):
			self.advance()
			self.check(cat="ParentAp", sync=set([None, "Identif", "Numero", "OpAdd", "ParentAp", "PtoComa", "PR"]), spr=set(["NO", "CIERTO", "FALSO"]))
			expr_simple = self.analyzeExprSimple(ids = inst_es['ids'], tipo_id = inst_es['tipo_id'])
			self.check(cat="ParentCi", sync=set([None, "PtoComa"]))
			inst_es['nodo'] = ast.NodoEscritura(expr_simple['nodo'])
		else:
			self.error(msg='LEE, ESCRIBE',
				sync=set([None, "PtoComa"]))
		return inst_es

	def analyzeExpresion(self, **kwargs):
		expresion = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat in ["Identif", "Numero", "ParentAp", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			expr_simple = self.analyzeExprSimple(ids = expresion['ids'], tipo_id = expresion['tipo_id'])
			expr_aux = self.analyzeExprAux(ids = expresion['ids'], tipo_id = expresion['tipo_id'], tipo = expr_simple['tipo'])
			expresion['tipo'] = expr_aux['tipo']
			if 'op' not in expr_aux:
				expresion['nodo'] = expr_simple['nodo']
			else:
				expresion['nodo'] = ast.NodoCompara(expr_aux['op'], expresion['tipo'][0], expr_simple['nodo'], expr_aux['dcha'])
		else:
			self.error(msg='Identif, Numero, (, OpAdd, NO, CIERTO, FALSO',
				sync=set([None, "PR", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER"]))
		return expresion

	def analyzeExprAux(self, **kwargs):
		expr_aux = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "OpRel"):
			expr_aux['op'] = self.component.op
			self.advance()
			expr_simple = self.analyzeExprSimple(ids = expr_aux['ids'], tipo_id = expr_aux['tipo_id'])
			if (expr_aux['tipo'][0] <= 1 and expr_simple['tipo'][0] <= 1):
				expr_aux['tipo'] = (2, )
			else:
				self.errorComp(tipo1 = expr_aux['tipo'][0], tipo2 = expr_simple['tipo'][0])
			expr_aux['dcha'] = expr_simple['nodo']
		elif (not (self.component.cat in ["PtoComa", "ParentCi"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "HACER"]))):
			self.error(msg='OpRel, ;, ), ENTONCES, HACER',
				sync=set([None, "PR", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER"]))
		return expr_aux

	def analyzeExprSimple(self, **kwargs):
		expr_simple = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			termino = self.analyzeTermino(ids = expr_simple['ids'], tipo_id = expr_simple['tipo_id'])
			resto_exsimple = self.analyzeRestoExSimple(ids = expr_simple['ids'], tipo_id = expr_simple['tipo_id'])
			if ('tipo' in resto_exsimple):
				if (termino['tipo'][0] <= 1 and resto_exsimple['tipo'][0] <= 1):
					expr_simple['tipo'] = (max(termino['tipo'][0], resto_exsimple['tipo'][0]), )
					expr_simple['nodo'] = ast.NodoAritmetica(resto_exsimple['op'], expr_simple['tipo'], termino['nodo'], resto_exsimple['nodo'])
				elif (termino['tipo'] == resto_exsimple['tipo'] and termino['tipo'][0] == 2):
					expr_simple['tipo'] = termino['tipo']
					expr_simple['nodo'] = ast.NodoLogica(resto_exsimple['op'], expr_simple['tipo'][0], termino['nodo'], resto_exsimple['nodo'])
				else:
					self.errorCompat(tipo1 = termino['tipo'][0], tipo2 = resto_exsimple['tipo'][0])
			else:
				if (termino['tipo'][0] <= 2):
					expr_simple['tipo'] = termino['tipo']
					expr_simple['nodo'] = termino['nodo']
				else:
					self.errorCompat(tipo1 = termino['tipo'][0], tipo2 = -1)
		elif(self.component.cat == "OpAdd"):
			self.analyzeSigno()
			termino = self.analyzeTermino(ids = expr_simple['ids'], tipo_id = expr_simple['tipo_id'])
			resto_exsimple = self.analyzeRestoExSimple(ids = expr_simple['ids'], tipo_id = expr_simple['tipo_id'])
			if ('tipo' in resto_exsimple):
				if (termino['tipo'][0] <= 1 and resto_exsimple['tipo'][0] <= 1):
					expr_simple['tipo'] = (max(termino['tipo'][0], resto_exsimple['tipo'][0]), )
					expr_simple['nodo'] = ast.NodoAritmetica(resto_exsimple['op'], expr_simple['tipo'][0], termino['nodo'], resto_exsimple['dcha'])
				elif (termino['tipo'] != resto_exsimple['tipo']):
					self.errorCompat(tipo1 = termino['tipo'][0], tipo2 = resto_exsimple['tipo'][0])
				else:
					self.errorUnsigned(tipo = termino['tipo'][0])
			else:
				if (termino['tipo'][0] <= 1):
					expr_simple['tipo'] = termino['tipo']
					expr_simple['nodo'] = termino['nodo']
				else:
					self.errorUnsigned(tipo = termino['tipo'][0])
		else:
			self.error(msg='Identif, Numero, (, NO, CIERTO, FALSO',
				sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER"]))
		return expr_simple

	def analyzeRestoExSimple(self, **kwargs):
		resto_exsimple = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "OpAdd" or (self.component.cat == "PR" and self.component.valor in ["O"])):
			cat = self.component.cat
			if cat == "OpAdd":
				resto_exsimple['op'] = self.component.op
			else:
				resto_exsimple['op'] = 'O'
			self.advance()
			termino = self.analyzeTermino(ids = resto_exsimple['ids'], tipo_id = resto_exsimple['tipo_id'])
			resto_exsimple1 = self.analyzeRestoExSimple(ids = resto_exsimple['ids'], tipo_id = resto_exsimple['tipo_id'])
			if 'tipo' in resto_exsimple1:
				if (termino['tipo'][0] <= 1 and resto_exsimple1['tipo'][0] <= 1 and cat == "OpAdd"):
					resto_exsimple['tipo'] = (max(termino['tipo'][0], resto_exsimple1['tipo'][0]), )
					resto_exsimple['dcha'] = ast.NodoAritmetica(resto_exsimple1['op'], resto_exsimple['tipo'][0], termino['nodo'], resto_exsimple1['dcha'])
				elif (termino['tipo'] == resto_exsimple1['tipo'] and termino['tipo'][0] == 2 and cat == "PR"):
					resto_exsimple['tipo'] = (2, )
					resto_exsimple['dcha'] = ast.NodoLogica(resto_exsimple1['op'], resto_exsimple['tipo'][0], termino['nodo'], resto_exsimple1['nodo'])
				else:
					self.errorCompat(tipo1 = termino['tipo'][0], tipo2 = resto_exsimple1['tipo'][0])
			else:
				if (termino['tipo'][0] <= 1 and cat == "OpAdd"):
					resto_exsimple['tipo'] = termino['tipo']
					resto_exsimple['dcha'] = termino['nodo']
				elif (termino['tipo'][0] == 2 and cat == "PR"):
					resto_exsimple['tipo'] = (2, )
					resto_exsimple['dcha'] = termino['nodo']
				else:
					self.errorCompat(tipo1 = termino['tipo'][0], tipo2 = -1)
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "HACER"]))):
			self.error(msg='OpAdd, O, ;, ], ), OpRel, ENTONCES, HACER',
				sync=set([None, "PR", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["ENTONCES", "HACER"]))
		return resto_exsimple

	def analyzeTermino(self, **kwargs):
		termino = kwargs
		termino['nodo'] = None
		if (self.component == None):
			pass
		elif (self.component.cat in ["Identif", "Numero", "ParentAp"] or (self.component.cat == "PR" and self.component.valor in ["NO", "CIERTO", "FALSO"])):
			factor = self.analyzeFactor(ids = termino['ids'], tipo_id = termino['tipo_id'])
			resto_term = self.analyzeRestoTerm(ids = termino['ids'], tipo_id = termino['tipo_id'])
			if 'tipo' in resto_term:
				if (factor['tipo'][0] <= 1 and resto_term['tipo'][0] <= 1):
					termino['tipo'] = (max(factor['tipo'][0], resto_term['tipo'][0]), )
					termino['nodo'] = ast.NodoAritmetica(resto_term['op'], termino['tipo'][0], termino['nodo'], resto_term['dcha'])
				elif (factor['tipo'] == resto_term['tipo'] and factor['tipo'][0] == 2):
					termino['tipo'] = (2, )
					termino['nodo'] = ast.NodoLogica(resto_term['op'], termino['tipo'][0], termino['nodo'], resto_term['dcha'])
				else:
					self.errorCompat(tipo1 = factor['tipo'][0], tipo2 = resto_term['tipo'][0])
			else:
				if (factor['tipo'][0] <= 2):
					termino['tipo'] = factor['tipo']
					termino['nodo'] = factor['nodo']
				else:
					self.errorCompat(tipo1 = factor['tipo'][0], tipo2 = -1)

		else:
			self.error(msg='Identif, Numero, (, NO, CIERTO, FALSO',
				sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["O", "ENTONCES", "HACER"]))
		return termino

	def analyzeRestoTerm(self, **kwargs):
		resto_term = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "OpMult" or (self.component.cat == "PR" and self.component.valor in ["Y"])):
			cat = self.component.cat
			if cat == "OpMult":
				resto_term['op'] = self.component.op
			else:
				resto_term['op'] = "Y"
			self.advance()
			factor = self.analyzeFactor(ids = resto_term['ids'], tipo_id = resto_term['tipo_id'])
			resto_term1 = self.analyzeRestoTerm(ids = resto_term['ids'], tipo_id = resto_term['tipo_id'])
			if 'tipo' in resto_term1:
				if (factor['tipo'][0] <= 1 and resto_term1['tipo'][0] <= 1 and cat == "OpMult"):
					resto_term['tipo'] = (max(factor['tipo'][0], resto_term1['tipo'][0]), )
					resto_term['dcha'] = ast.NodoAritmetica(resto_term1['op'], resto_term['tipo'][0], factor['nodo'], resto_term1['dcha'])
				elif (factor['tipo'] == resto_term['tipo'] and factor['tipo'][0] == 2 and cat == "PR"):
					resto_term['tipo'] = (2, )
					resto_term['dcha'] = ast.NodoLogica(resto_term1['op'], resto_term['tipo'][0], factor['nodo'], resto_term1['dcha'])
				else:
					self.errorCompat(tipo1 = factor['tipo'][0], tipo2 = resto_term1['tipo'][0])
			else:
				if (factor['tipo'][0] <= 1 and cat == "OpMult"):
					resto_term['tipo'] = factor['tipo']
					resto_term['dcha'] = factor['nodo']
				elif (factor['tipo'][0] == 2 and cat == "PR"):
					resto_term['tipo'] = (2, )
					resto_term['dcha'] = factor['nodo']
				else:
					self.errorCompat(tipo1 = factor['tipo'][0], tipo2 = -1)
		elif (not (self.component.cat in ["PtoComa", "CorCi", "ParentCi", "OpRel", "OpAdd"] or (self.component.cat == "PR" and self.component.valor in ["ENTONCES", "HACER", "O"]))):
			self.error(msg='OpMult, Y, ;, ), OpRel, OpAdd, ENTONCES, HACER, O', 
				sync=set([None, "PR", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["O", "ENTONCES", "HACER"]))
		return resto_term

	def analyzeFactor(self, **kwargs):
		factor = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "Identif"):
			variable = self.analyzeVariable(ids = factor['ids'], tipo_id = factor['tipo_id'])
			factor['tipo'] = variable['tipo']
			if variable['vector'] == 0:
				factor['nodo'] = ast.NodoAccesoVariable(variable['id'], variable['tipo'][0])
			else:
				factor['nodo'] = ast.NodoAccesoVector(variable['tipo'][1][0], variable['id'], variable['expresion'])
		elif (self.component.cat == "Numero"):
			if (self.component.isInt):
				factor['tipo'] = (0, )
			else:
				factor['tipo'] = (1, )
			factor['nodo'] = ast.NodoNumero(self.component.num, factor['tipo'][0])
			self.advance()
		elif (self.component.cat == "ParentAp"):
			self.advance()
			expresion = self.analyzeExpresion(ids = factor['ids'], tipo_id = factor['tipo_id'])
			self.check(cat="ParentCi", sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER"]))
			factor['tipo'] = expresion['tipo']
			factor['nodo'] = expresion['nodo']
		elif (self.component.cat == "PR" and self.component.valor == "NO"):
			self.advance()
			factor1 = self.analyzeFactor(ids = factor['ids'], tipo_id = factor['tipo_id'])
			factor['tipo'] = (2, )
			if (factor1['tipo'][0] != 2):
				self.errorCast(tipo1 = factor1['tipo'][0], tipo2 = 2)
			factor['nodo'] = ast.NodoNegacion(factor['tipo'][0], factor1['nodo'])
		elif (self.component.cat == "PR" and self.component.valor in ["CIERTO", "FALSO"]):
			factor['nodo'] = ast.NodoLogico(self.component.valor)
			self.advance()
		else:
			self.error(msg='Identif, Numero, (, NO, CIERTO or FALSO',
				sync=set([None, "PR", "OpMult", "OpAdd", "OpRel", "CorCi", "ParentCi", "PtoComa"]),
				spr=set(["Y", "O", "ENTONCES", "HACER"]))
		return factor

	def analyzeSigno(self, **kwargs):
		signo = kwargs
		if (self.component == None):
			pass
		elif (self.component.cat == "OpAdd"):
			self.advance()
		else:
			self.error(msg='OpAdd',
				sync=set([None, "PR", "Identif", "ParentAp", "Numero"]),
				spr=set(["NO", "CIERTO", "FALSO"]))
		return signo

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
		self.errored = True
		print ("SINTAX TERROR: Line " + str(self.lexana.nlinea))
		if 'msg' in kwargs:
			print ("EXPECTED " + kwargs['msg'])
		#print ("-- Component: " + str(self.component))
		if ('spr' not in kwargs):
			self.sincroniza(sync=kwargs['sync'])
		else:
			self.sincroniza(sync=kwargs['sync'], spr=kwargs['spr'])
	
	def errorS(self, **kwargs):
		self.errored = True
		print ("Identificador repetido " + kwargs['id'])
	
	def errorBefore(self, **kwargs):
		self.errored = True
		print ("El identificador " + kwargs['id'] + " no ha sido declarado!")
	
	def errorCast(self, **kwargs):
		self.errored = True
		choices = {0: 'ENTERO', 1: 'REAL', 2: 'BOOLEANO', 4: 'VECTOR', 5: 'PROC', 6: 'FUNCION', -1: 'ERROR'}
		print ("No se puede pasar de " + choices[kwargs['tipo1']] + " a " + choices[kwargs['tipo2']])
	
	def errorNotVector(self, **kwargs):
		self.errored = True
		print (kwargs['id'] + " no es un VECTOR")
	
	def errorAVector(self, **kwargs):
		self.errored = True
		print ("Se debe usar un ENTERO en los accesos a vector")
	
	def errorComp(self, **kwargs):
		self.errored = True
		choices = {0: 'ENTERO', 1: 'REAL', 2: 'BOOLEANO', 4: 'VECTOR', 5: 'PROC', 6: 'FUNCION', -1: 'ERROR'}
		print (choices[kwargs['tipo1']] + " y " + choices[kwargs['tipo2']] + " no son comparables")
	
	def errorCompat(self, **kwargs):
		self.errored = True
		choices = {0: 'ENTERO', 1: 'REAL', 2: 'BOOLEANO', 4: 'VECTOR', 5: 'PROC', 6: 'FUNCION', -1: 'ERROR'}
		print (choices[kwargs['tipo1']] + " y " + choices[kwargs['tipo2']] + " no son compatibles")
	
	def errorUnsigned(self, **kwargs):
		self.errored = True
		choices = {0: 'ENTERO', 1: 'REAL', 2: 'BOOLEANO', 4: 'VECTOR', 5: 'PROC', 6: 'FUNCION', -1: 'ERROR'}
		print (choices[kwargs['tipo']] + " no puede tener signo")

	def __init__(self, lexana):
		self.lexana = lexana
		self.endErr = False
		self.errored = False
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
		ast, result = synana.analyzePrograma()
		if (result):
			print ("NOICE!")
			print ast
		else:
			print ("THE PROGRAM HAS ERRORS!")
	except errores.Error, err:
		sys.stderr.write("%s\n" % err)
		analex.muestraError(sys.stderr)
