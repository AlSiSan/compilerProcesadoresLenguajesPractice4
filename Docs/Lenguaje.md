# compilerProcesadoresLenguajesPractice4

PROGRAMA id


--decl variables (opt)



--decl funciones (opt)



--programa principal


INICIO


instr0;


.


.


.


instrN;


FIN



---------------------------------------------------


Programa:


PROGRAMA <id> (<Variables>)* (<Funcion>|<Proc>)* <Bloque>
	
	

Tipo: ENTERO, REAL, BOOLEANO, <Vector>
	
	
Vector: VECTOR [<ENTERO>] DE <Tipo>
	
	
Variables:


	var
	
	
	<id>, ..., <id>: <Tipo>;
	
	
	<id>, ..., <id>: <Tipo>;
	
	
Bloque:


INICIO


	instr0
	
	
	.
	
	
	.
	
	
	.
	
	
	instrN
	
	
FIN



Funcion:


	FUNCION <id>: <Tipo>; <Bloque>
	
	
	

Comentario: {[^{]*}


Los espacios solo se usan para separar componentes léxicos. Tabulaciones y saltos son para legibilidad, nada más.


letra: [a-zA-Z]


digito: [0-9]


id: <letra>(<letra>|<digito>)*
	
	
id puede tener longitud máxima.


digitos: <digito>+
	
	
fraccion_opt: .<digitos>|λ
	
	
num: <digitos><fraccion_opt>
	
	

ifelse: SI <Condicion> ENTONCES <Bloque>( SINO <Bloque>)?
	
	

palclave = {PROGRAMA, VAR, VECTOR, ENTERO, REAL, BOOLEANO, PROC, FUNCION, INICIO, FIN, SI, ENTONCES, SINO, MIENTRAS, HACER, LEE, ESCRIBE, Y, O, NO, CIERTO}



oprelac = {=, <>, <, <=, >=, >}


opsuma = {+, -}


opmult = {*, /}


opasign = {:=}



L = palclave + oprelac + opsuma + opmult + opasign + [a-zA-Z0-9:;,\[\]\(\)]
 
