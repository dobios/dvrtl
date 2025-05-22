# DVRTL
Formalized minimal RTL Language for Deductive Verification. 

DVRTL is a lightweight front-end for the CIRCT compiler, augmented to be used as a deductive verification language.

## Syntax 
The syntax was defined to closely mimic the abstraction level of the CIRCT core IR, while also being slightly more human-friendly to write than an MLIR program. 

The formal definition of the full syntax is as follows:
```
Registers r     Variables x
Value v         ::= 0 | 1
Order o         ::= skip | fail
Expression e    ::=	e xor e | e and e | e or e | mux e e e |
                        v | r | x | m (e,...,e) | x (e,...,e)
Arithmetic a    ::= a impl a | a + a | a - a | a eq a |
                        a xor a | a and a | a or a | e
Contract h      ::= res | a
Module m        ::= mod(x, ...,x)[req a; ens h]{b} | mod(x, ...,x){b}
Statement s     ::= r -> v, e | x = e | x = m | assert a | assume a | m
Body b          ::= [s]* ; out e
Circuit c       ::= [s]* 
```


