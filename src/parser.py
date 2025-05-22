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
import multiprocessing

# Parser for the contRTL language.
class Parser:
    # Maintains 3 fields during parsing
    # @field{context: list[Symbol]}: A context containing
    #   all of the name bindings in the program.
    #   Given that our language is declarative, we allow for
    #   def-after-use, meaning that all names in the program are valid
    #   in all locations.
    # @field{circuit: Circuit}: The circuit resulting from the parse.
    # @field{done: Bool}: A flag signaling the state of the parsing process
    def __init__(self) -> None:
        self.context: list[Symbol] = []
        self.circuit: Circuit = Circuit([], [])
        self.done: bool = False

    # Clears the parser, allowing it to parse again
    def clear(self) -> None:
        self.context = []
        self.circuit = Circuit([], [])
        self.done = False

    # Parse a single statement in the circuit
    def parse(self, line: str) -> None:
        pass
    
    # Parses a given circuit implementation in parallel
    def parsePar(self, c: str) -> None:
        # Only parse once
        assert not self.done, "Parse is already completed!"
        
        # Create a thread pool
        pool = multiprocessing.Pool()

        # Parse all lines in parallel
        pool.map( \
            self.parse, \
            c.strip('\n').split(';') \
        )

    # Parse a given circuit implementation sequentially
    def parseSeq(self, c: str) -> None: 
        # Only parse once
        assert not self.done, "Parse is already completed!"

        # Parse all lines sequentially
        map(self.parse, c.strip('\n').split(';'))

    # Fully serializes a given circuit
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


