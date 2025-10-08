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

The AST is implemented in syntax.py and parse tree in dvrtl.lark/parser.py
"""

from lark import Transformer, Token
from .syntax import *

## Transforms a parse tree into a DVRTL AST
## Straightforward transformation, little comments needed
class DVRTLTransformer(Transformer):
    @override
    def __init__(self, visit_tokens = True):
        super().__init__(visit_tokens)
        self.context: list[Symbol] = []

    ## All methods here are lark tranformer visitors of the form node(self, children: list[node])

    ## Base elements
    def identifier(self, c):
        (id,) = c 
        
        # Typecheck for the child extraction
        assert isinstance(id, Token)

        # Retrieve the actual name
        name = id.value

        # Check context for content
        ref: list[Symbol] = [s for s in self.context if s == Symbol(name, None)]
        return ref[0] if len(ref) > 0 else Symbol(name, None)
    
    def list_of_variables(self, c):
        # Unpack children
        (id, l_id) = (c[0], c[1:])
        return [id].append(l_id)
    
    def list_of_expr(self, c):
        # unpack children
        (e, l_e) = (c[0], c[1:])
        return [e].append(l_e)
    
    def zero(self, c):
        return Zero()
    
    def one(self, c):
        return One()
    
    ## Expressions (synthesizable language)
    def expr_xor(self, c):
        # unpack children
        (e0, e1,) = c
        return EXor(e0, e1)
    
    def expr_and(self, c):
        # unpack children
        (e0, e1,) = c
        return EAnd(e0, e1)
    
    def expr_or(self, c):
        # unpack children
        (e0, e1,) = c
        return EOr(e0, e1)
    
    def mux(self, c):
        # unpack children
        (s, e0, e1,) = c
        return Mux(s, e0, e1)
    
    def scoped_expr(self, c):
        (e,) = c
        return e
    
    def call(self, c):
        (id, l_e) = (c[0], c[1:]) 
        
        # Check that we have extracted the right children
        assert isinstance(id, Symbol)

        name = id.name
        
        # fetch module referenced by symbol
        mods: Module = [ \
            s.expr for s in self.context \
            if s.name == name and isinstance(s.expr, Module) \
        ]

        # Workaround for printing either typed objects because mypy is stupid
        def sym_to_str(sym: Symbol) -> str:
            if sym.expr is None:
                return (sym.name, "")
            return (sym.name, sym.expr.serialize())
        
        # debug print
        print(f"CONTEXT: {list(map(sym_to_str, self.context))}")
        
        assert len(mods) != 0, f"No module with name {name} was found!"
        return Inst(mods[0], l_e)
    
    ## Arithmetic expressions (assertion language)
    def impl(self, c):
        (a0, a1,) = c
        return Impl(a0, a1)
    
    def arith_xor(self, c):
        (a0, a1,) = c
        return Xor(a0, a1)
    
    def arith_and(self, c):
        (a0, a1,) = c
        return And(a0, a1) 
    
    def arith_or(self, c):
        (a0, a1,) = c
        return Or(a0, a1)
    
    def add(self, c):
        (a0, a1,) = c
        return Add(a0, a1)
    
    def sub(self, c):
        (a0, a1,) = c
        return Sub(a0, a1)
    
    def eq(self, c):
        (a0, a1,) = c
        return Eq(a0, a1)

    # syntactic sugar, directly desugars to xor(a, 1)
    def arith_not(self, c):
        (a,) = c
        return Not(a)
    
    def scoped_arith(self, c):
        (a,) = c
        return a
    
    ## Module definition
    def res(self, c):
        return Res()
    
    def precond(self, c):
        (a,) = c
        return PreCond(a)
    
    def postcond(self, c):
        (a,) = c
        return PostCond(a)
    
    def contract(self, c):
        (pre, post,) = c
        return Contract(pre, post)
    
    def out(self, c):
        (e,) = c
        return Out(e)
    
    def body(self, c):
        (l_s, out) = (c[0:-2], c[-1])
        out_res = None # avoid aliasing
        # Out is optional
        if not isinstance(out, Out):
            l_s.append(out)
        else:
            out_res = out
        return Body(l_s, out_res)
    
    def module(self, c):
        (l_v, cntr, b) = (c[0:-2], c[-2], c[-1])
        cntr_res = None # avoid aliasing
        # Contract is optional, this should handle that
        if not isinstance(cntr, Contract):
            l_v.append(cntr)
        else:
            cntr_res = cntr
        return Module(l_v, cntr_res, b)
    
    ## Statements
    ## Symbol creating statements must also update the context
    def reg(self, c):
        (id, init, next,) = c

        # Check that we have extracted the right children
        assert isinstance(id, Symbol)

        # Create the register statement
        reg = Reg(id.name, init, next)

        # Make sure that the symbol doesn't already exist
        assert not (id in self.context), \
            f"Symbol {id.name} was defined multiple times!! Symbols must only have one definition"
        
        # Update the context with the new symbol
        sym: Symbol = Symbol(id.name, reg)
        self.context.append(sym)
        return reg
    
    def bind(self, c):
        (id, e,) = c

        # Check that we have extracted the right children
        assert isinstance(id, Symbol)

        # Define the bind statement
        bind: Bind = Bind(id.name, e)

        assert not (id in self.context), \
            f"Symbol {id.name} was defined multiple times!! Symbols must only have one definition"

        # Update the context
        sym: Symbol = Symbol(id.name, bind)
        self.context.append(sym)
        return bind
    
    def stmt_assert(self, c):
        (a,) = c
        return Assert(a)
    
    def stmt_assume(self, c):
        (a,) = c
        return Assume(a)
    
    def ano_module(self, c):
        (m,) = c
        return m
    
    def stmt_seq(self, c):
        (s0, s1,) = c
        return [s0].append(s1)
    
    def start(self, l_s):
        return Circuit(l_s, self.context)
        

