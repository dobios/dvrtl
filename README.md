# Work in Progress -- DVRTL
WIP Formalized minimal RTL Language for Deductive Verification. 

The goal of DVRTL is to be a formalized lightweight front-end for the CIRCT compiler, augmented to be used as a deductive verification language.

The language is implemented using `MyPy` with Lark as the parser generator.

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
Module m        ::= mod(x, ...,x)[req a; ens h;]{b} | mod(x, ...,x){b}
Statement s     ::= r -> v, e | x = e | x = m | assert a | assume a | m
Body b          ::= [s;]* out e;
Circuit c       ::= [s;]* 
```

## Example -- Untyped (1-bit)
Here is a simple example of how to write a 2-bit adder using untyped contRTL (untyped leads to everything being 1-bit). 
```
sum = mod (a_in, b_in, c_in) [
    req 1
    ens res eq (a_in + b_in + c_in)
]{
    axb = a_in xor b_in
    out c_in xor axb
}
carry = mod (a_in, b_in, c_in){
    axb = a_in xor b_in
    anb = a_in and b_in
    out anb or (c_in and axb)
}
add2_0 = mod (a1, a0, b1, b0) [
    req 1
    ens res eq (a0 + b0)
] {
    out sum(a0, b0, 0)
}
add2_1 = mod (a1, a0, b1, b0) [
    req 1
    ens res eq ((a0 and b0) + (a1 + b1))
]{
    c_0 = carry(a0, b0, 0)
    out sum(a1, b1, c_0) 
}
carry2 = mod (a1, a0, b1, b0) [
    req 1
    ens res eq ((a0 and b0) + (a1 and b1))
]{
    carry0 = carry(a0, b0, 0)
    out carry(a1, b1, carry0) 
}
bit0 = add2_0(0,1,0,1)
bit1 = add2_1(0,1,0,1)
overflow = carry2(0,1,0,1)

assert (bit0 eq 0) and (bit1 eq 1) and (overflow eq 0)
```

