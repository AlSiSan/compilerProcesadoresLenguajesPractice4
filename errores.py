#!/usr/bin/env python
# -*- coding: latin-1 -*-

class Error(Exception):
  def __init__(self, mensaje):
    self.mensaje= mensaje

  def __str__(self):
    return self.mensaje

class ErrorLexico(Error):
  def __init__(self, mensaje):
    self.mensaje= "Error lexico: %s" % mensaje

class ErrorSintactico(Error):
  def __init__(self, mensaje):
    self.mensaje= "Error sintáctico: %s" % mensaje

class ErrorSemantico(Error):
  def __init__(self, mensaje):
    self.mensaje= "Error semántico: %s" % mensaje

class ErrorEjecucion(Error):
  def __init__(self, mensaje):
    self.mensaje= "Error de ejecución: %s" % mensaje
