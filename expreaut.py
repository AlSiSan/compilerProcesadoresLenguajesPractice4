class InvalidTransition(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class InvalidState(ValueError):
	pass

class InvalidAFDSymbol(ValueError):
	pass

class AFD:
	def __init__ (self, states, alphabet, initst, trans, fstates):
		self.states = states
		self.alphabet = alphabet
		self.initst = initst
		self.trans = trans
		self.fstates = fstates
		
		for tran in trans:
			if tran[0] not in states:
				raise InvalidTransition("State " + tran[0] + " is not in states")
			if tran[1] not in alphabet:
				raise InvalidTransition("Symbol " + tran[1] + " is not in the alphabet")
			if tran[2] not in states:
				raise InvalidTransition("State " + tran[2] + " is not in states")
		if initst not in states:
			raise InvalidState("Initial state must be in the states set")
		for fstate in fstates:
			if fstate not in states:
				raise InvalidState("Final states must be in the states set")
	
	def applyTrans(self, state, chara):
		if chara not in self.alphabet:
			raise InvalidAFDSymbol("Symbol " + chara + " is not in the alphabet")
		dest = [d for (i, s, d) in self.trans if i == state and chara == s]
		# i -> Estado inicial, s -> Simbolo, d -> Estado destino
		if dest == []:
			return None
		else:
			return dest[0]
	
	def auxParse (self, cstate, string):
		if string != "" and cstate is not None:
			return self.auxParse(self.applyTrans(cstate, string[0]), string[1:])
		else:
			return cstate
		
	def parseStr (self, string):
		final = self.auxParse(self.initst, string)
		return final in self.fstates
		
