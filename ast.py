#!/usr/bin/env python

class AST:
	def __init__(self, id, instrucciones):
		self.id = id
		self.instrucciones = instrucciones

class NodoAsignacion:
	def __init__(self, iz, dcha):
		self.iz = iz
		self.dcha = dcha

class NodoSi:
	def __init__(self, cond, sentenciassi, sentenciasno):
		self.cond = cond
		self.sentenciassi = sentenciassi
		self.sentenciasno = sentenciasno

class NodoMientras:
	def __init__(self, cond, sentencias):
		self.cond = cond
		self.sentencias = sentencias

class NodoEscritura:
	def __init__(self, expr):
		self.expr = expr

class NodoSCompuesta:
	def __init__(self, sentencias):
		self.sentencias = sentencias

class NodoCompara:
	def __init__(self, op, tipo, iz, dcha):
		self.op = op
		self.tipo = tipo
		self.iz = iz
		self.dcha = dcha

class NodoAritmetica:
	def __init__(self, op, tipo, iz, dcha):
		self.op = op
		self.tipo = tipo
		self.iz = iz
		self.dcha = dcha

class NodoLogica:
	def __init__(self, op, tipo, iz, dcha):
		self.op = op
		self.tipo = tipo
		self.iz = iz
		self.dcha = dcha

class NodoNegacion:
	def __init__(self, tipo, dcha):
		self.tipo = tipo
		self.dcha = dcha

class NodoNumero:
	def __init__(self, valor, tipo):
		if tipo == 0:
			self.valor = int(valor)
		else:
			self.valor = float(valor)
		self.tipo = tipo	# 0 para entero, 1 para real

class NodoLogico:
	def __init__(self, valor, tipo):
		choices = {'CIERTO': 1, 'FALSO': 0}
		self.valor = choices[valor]	# 0 para FALSO, cualquier otra cosa para CIERTO

class NodoLlamadaFuncion:
	def __init__(self, funcion, tipo):
		self.funcion = funcion
		self.tipo = tipo

class NodoLlamadaProc:
	def __init__(self, proc):
		self.proc = proc

class NodoAccesoVariable:
	def __init__(self, variable, tipo):
		self.variable = variable
		self.tipo = tipo

class NodoAccesoVector:
	def __init__(self, tipo, vector, expresion):
		self.tipo = tipo
		self.vector = vector
		self.expresion = expresion
