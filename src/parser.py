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
Parser definition of the contRTL language.
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

The AST is implemented in syntax.py.
"""

from syntax import *

class Parser:
    def __init__(self) -> None:
        self.context: list[Symbol] = []
        self.circuit: Circuit = Circuit([])

    def parse(self, line: str) -> None:
        pass

    def parseAll(self, c: str) -> None:
        pass

    def serialize(self) -> str:
        return self.circuit.serialize()
    
    #######################################
    # visitors
    #######################################

    def parseReg(self, r: str) -> Reg:
        return Reg("", Value(""), Expr(""))

    def parseExpr(self, e: str) -> Expr:
        return Expr("")

    def parseStmt(self, s: str) -> Stmt:
        return Stmt("")


