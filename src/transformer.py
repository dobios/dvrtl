#########################################################################
# Formalized Minimal RTL Language for Deductive Verification.
# Copyright (C) 2025  Amelia Dobis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#########################################################################

"""
Transformer definition of the dvrtl language.
The formal definition of the full syntax is as follows:

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

The AST is implemented in syntax.py and dvrtl.lark
"""

from lark import Transformer
from .syntax import *

## Transforms a parse tree into a DVRTL AST
## Straightforward transformation, little comments needed
class DVRTLTransformer(Transformer):
    ## Base elements
    def identifier(self, id):
        return Symbol(id[1:-1], None)
    
    def list_of_variables(self, id, l_id):
        return list(id).append(list(l_id))
    
    def list_of_expr(self, e, l_e):
        return list(e).append(list(l_e))
    
    def zero(self):
        return Zero()
    
    def one(self):
        return One()
    
    ## Expressions (synthesizable language)
    def expr_xor(self, e0, e1):
        return EXor(e0, e1)
    
    def expr_and(self, e0, e1):
        return EAnd(e0, e1)
    
    def expr_or(self, e0, e1):
        return EOr(e0, e1)
    
    def mux(self, s, e0, e1):
        return Mux(s, e0, e1)
    
    def scoped_expr(self, e):
        return e
    
    def call(self, id, l_e):
        return Inst(id, l_e)
    
    ## Arithmetic expressions (assertion language)
    def impl(self, a0, a1):
        return Impl(a0, a1)
    
    def arith_xor(self, a0, a1):
        return Xor(a0, a1)
    
    def arith_and(self, a0, a1):
        return And(a0, a1) 
    
    def arith_or(self, a0, a1):
        return Or(a0, a1)
    
    def add(self, a0, a1):
        return Add(a0, a1)
    
    def sub(self, a0, a1):
        return Sub(a0, a1)
    
    def eq(self, a0, a1):
        return Eq(a0, a1)

    # syntactic sugar, directly desugars to xor(a, 1)
    def arith_not(self, a):
        return Not(a)
    
    def scoped_arith(self, a):
        return a
    
    ## Module definition
    def res(self):
        return Res()
    
    def precond(self, a):
        return PreCond(a)
    
    def postcond(self, a):
        return PostCond(a)
    
    def contract(self, pre, post):
        return Contract(pre, post)
    
    def out(self, e):
        return Out(e)
    
    def body(self, l_s, out):
        return Body(l_s, out)
    
    def module(self, l_v, c, b):
        return Module(l_v, c, b)
    
    ## Statements
    def reg(self, id, init, next):
        return Reg(id, init, next)
    
    def bind(self, id, e):
        return Bind(id, e)
    
    def stmt_assert(self, a):
        return Assert(a)
    
    def stmt_assume(self, a):
        return Assume(a)
    
    def ano_module(self, m):
        return m
    
    def stmt_seq(self, s0, s1):
        return list(s0, s1)
    
    def start(self, l_s):
        return Circuit(l_s, list())
        