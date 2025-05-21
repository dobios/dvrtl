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
Syntax definition of the contRTL language.
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
"""
from typing_extensions import override
from typing import Optional, TypeAlias
from functools import reduce

# Abstract node in the AST
class Node:
    # Nodes by default only contain a name
    # @param{name: str} : human-readable name of the node
    #   this is equivalent to how it can be viewed in the source. 
    def __init__(self, name: str) -> None:
        self.name: str = name 

    # Returns a human-readable version of the node
    def serialize(self) -> str:
        return self.name

# Statement in our circuit, these are the core nodes of a design.
class Stmt(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

# Symbol refering to either a register or a name binding in our context
class Symbol(Node):
    # Defined by a symbol name and a linked expression
    # @param{sym: str}: The name given to the symbol
    # @param{stmt: Stmt}: The statement that declared this symbol
    def __init__(self, sym: str, stmt: Stmt) -> None:
        super().__init__(sym)
        self.expr: Stmt = stmt

# Arithmetic expression (used in an assertion/assumption)
class Arith(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

# Synthesizable expression, these are also valid arithmetic expressions
class Expr(Arith):
    def __init__(self, name: str) -> None:
        super().__init__(name)

# Top-level Root Node of our AST
class Circuit:
    # Circuits are defined by a list of statements
    # @param{body: list[Stmt]} : The body of our circuit
    #   defined as a list of statements
    def __init__(self, body : list[Stmt]) -> None:
        self.body: list[Stmt] = body

    # Returns a full serialization of our circuit
    def serialize(self) -> str:
        return reduce( \
            lambda acc, s: acc + s.serialize() + "\n", \
            self.body, \
            "" \
        )
    

################################################
## Values v ::= 0 | 1
################################################

# Value: Leaf node of our AST
class Value(Expr):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    # Returns an integer representation of our value
    def toInt(self) -> int:
        return int(self.name)

# Zero value: represents a 0 bit
# Denotational Semantics:
#   [[0]] = 0
class Zero(Value):
    def __init__(self) -> None:
        super().__init__("0")
    
    @override
    def toInt(self) -> int:
        return 0
    
# One value: represents a 1 bit  
# Denotational Semantics:
#   [[1]] = 1
class One(Value):
    def __init__(self) -> None:
        super().__init__("1")
    
    @override
    def toInt(self) -> int:
        return 1
    

################################################
## Orders o ::= skip | fail
################################################

# Order: Actionable result of an assertion evaluation
class Order(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

# Skip: result of a successful assertion/assumptio
# Denotational Semantics:
#   [[skip]] = _
class Skip(Order):
    def __init__(self) -> None:
        super().__init__("skip")
    
# Fail: result of a failed assertion 
# Denotational Semantics (in KAT):
#   [[fail]] = 0?
class Fail(Value):
    def __init__(self) -> None:
        super().__init__("fail")


################################################
## Arithmetic a ::=
#   a impl a | a + a | a - a | a eq a | 
#       a xor a | a and a | a or a | e
################################################

# Arithmetic variadic operator
class AOp(Arith):
    # Defined by a name and an arbitrary number of operands
    # @param{ops: list[Arith]} : a list of operand arithmetic expressions
    def __init__(self, name: str, ops: list[Arith]) -> None:
        super().__init__(name)
        self.ops: list[Arith] = ops

    @override
    def serialize(self) -> str:
        operands_s: str = reduce( \
            lambda acc, s: f"{acc} {s.serialize()}",  \
            self.ops, "" \
        )
        return f"{self.name} {operands_s}"

# Arithmetic binary operator
class ABinOp(AOp):
    # Defined by two operands
    # @param{lhs: Arith} : Left-hand-side operand
    # @param{rhs: Arith} : Right-hand-side operand
    # Operands are additionally stored in a list for ease of use
    def __init__(self, name: str, lhs: Arith, rhs: Arith) -> None:
        super().__init__(name, [lhs, rhs])
        self.lhs: Arith = lhs
        self.rhs: Arith = rhs

    @override
    def serialize(self) -> str:
        return f"{self.lhs.serialize()} {self.name} {self.rhs.serialize()}"

# Logical Implication
# Denotational Semantics:
#   [[a0 impl a1]] = ¬[[a0]] ∨ [[a1]]
class Impl(ABinOp):
    # Defined by two arithmetic operands
    # @param {ant: Arith}: Antecedent of the implication
    # @param {cons: Arithm}: Consequent of the implication
    def __init__(self, ant: Arith, cons: Arith) -> None:
        super().__init__("impl", ant, cons)

# Arithmetic Unsigned Addition
# Denotational Semantics:
#   [[a0 + a1]] = [[a0]] + [[a1]]
class Add(ABinOp):
    def __init__(self, name, lhs, rhs):
        super().__init__(name, lhs, rhs)

# Arithmetic Unsigned Subtraction
# Denotational Semantics:
#   [[a0 - a1]] = [[a0]] - [[a1]]
class Sub(ABinOp):
    def __init__(self, name, lhs, rhs):
        super().__init__(name, lhs, rhs)

# Bitwise Equality
# Denotational Semantics:
#   [[ e1 eq e2 ]] = ¬([[e1]] ⊕ [[e2]])
#
# Truth Table:
# v0 | v1 | v0 eq v1
# ----------------
# 1   1      1
# 1   0      0
# 0   1      0
# 0   0      1
class Eq(ABinOp):
    def __init__(self, name, lhs, rhs):
        super().__init__(name, lhs, rhs)

# Binary Logical Exclusive Or (Xor) operator 
# Denotational semantics: 
#   [[ a1 xor 1 ]]  = ¬ [[a1]]
#   [[ a1 xor a2 ]] = [[a1]] ⊕ [[a2]]
#
# Truth Table:
# v0 | v1 | v0 xor v1
# ----------------
# 1   1      0
# 1   0      1
# 0   1      1
# 0   0      0
class Xor(ABinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("xor", lhs, rhs)

# Binary Logical AND operator 
# Denotational semantics: 
#   [[ a1 and a2 ]] = [[a1]] ∧ [[a2]]
#
# Truth Table:
# v0 | v1 | v0 and v1
# ----------------
# 1   1      1
# 1   0      0
# 0   1      0
# 0   0      0
class And(ABinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("and", lhs, rhs)

# Binary Logical OR operator 
# Denotational semantics: 
#   [[ a1 or a2 ]] = [[a1]] ∨ [[a2]]
#
# Truth Table:
# v0 | v1 | v0 or v1
# ----------------
# 1   1      1
# 1   0      1
# 0   1      1
# 0   0      0
class Or(ABinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("or", lhs, rhs)


################################################
## Expression e ::=	
#   e xor e | e and e | e or e | mux e e e |                  
#       v | r | x | m (e,...,e) | x (e,...,e)
################################################

# Synthesizable variadic operator
class EOp(Expr):
    # Defined by a name and an arbitrary number of operands
    # @param{ops: list[Expr]} : a list of operand expressions
    def __init__(self, name: str, ops: list[Expr]) -> None:
        super().__init__(name)
        self.ops: list[Expr] = ops

    @override
    def serialize(self) -> str:
        operands_s: str = reduce( \
            lambda acc, s: f"{acc} {s.serialize()}",  \
            self.ops, "" \
        )
        return f"{self.name} {operands_s}"

# Synthesizable binary operator
class EBinOp(EOp):
    # Defined by two operands
    # @param{lhs: Expr} : Left-hand-side operand
    # @param{rhs: Expr} : Right-hand-side operand
    # Operands are additionally stored in a list for ease of use
    def __init__(self, name: str, lhs: Expr, rhs: Expr) -> None:
        super().__init__(name, [lhs, rhs])
        self.lhs: Expr = lhs
        self.rhs: Expr = rhs

    @override
    def serialize(self) -> str:
        return f"{self.lhs.serialize()} {self.name} {self.rhs.serialize()}"

# Binary Synthesizable Exclusive Or (Xor) operator 
# Denotational semantics: 
#   [[ e1 xor 1 ]]  = ¬ [[e1]]
#   [[ e1 xor e2 ]] = [[e1]] ⊕ [[e2]]
#
# Truth Table:
# v0 | v1 | v0 xor v1
# ----------------
# 1   1      0
# 1   0      1
# 0   1      1
# 0   0      0
class EXor(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("xor", lhs, rhs)

# Binary Synthesizable AND operator 
# Denotational semantics: 
#   [[ e1 and e2 ]] = [[e1]] ∧ [[e2]]
#
# Truth Table:
# v0 | v1 | v0 and v1
# ----------------
# 1   1      1
# 1   0      0
# 0   1      0
# 0   0      0
class EAnd(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("and", lhs, rhs)

# Binary Synthesizable OR operator 
# Denotational semantics: 
#   [[ e1 or e2 ]] = [[e1]] ∨ [[e2]]
#
# Truth Table:
# v0 | v1 | v0 or v1
# ----------------
# 1   1      1
# 1   0      1
# 0   1      1
# 0   0      0
class EOr(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("or", lhs, rhs)


# Multiplexer (conditional selector)
# Denotational semantics: 
#   [[ mux e1 e2 e3 ]] = ([[e1]] ∧ [[e2]]) ∨ (¬ [[e1]] ∧ [[e3]])
class Mux(EOp):
    # Defined by 3 operands
    # @param{s: Expr}   : (e1) Selector signal, decides which operand is selected 
    # @param{tOp: Expr} : (e2) Selected operand if [|s|] = 1 
    # @param{fOp: Expr} : (e3) Selected operand if [|s|] = 0 
    def __init__(self, s: Expr, tOp: Expr, fOp: Expr) -> None:
        super().__init__("mux", [s, tOp, fOp])
        self.s: Expr = s
        self.tOp: Expr = tOp
        self.fOp: Expr = fOp


################################################
# Modules and Contracts
################################################

# Abstract Contract node
class Contract(Node):
    # Defined by a keyword and a condition
    # @param{cond: Arithm}: The condition that will be checked
    #   as either a pre- or a post-condition
    def __init__(self, name: str, cond: Arith) -> None:
        super().__init__(name)
        self.cond: Arith = cond

    @override
    def serialize(self) -> str:
        return f"{self.name} {self.cond.serialize()}"

# Postcondition arithmetic expression
# Only valid in a module definition
# Can contain a Res reference
class PostCond(Contract):
    def __init__(self, cond: Arith) -> None:
        super().__init__("ens", cond)
    
# Precondition arithmetic expression
# Only valid in a module definition
# Can contain a Res reference
class PreCond(Contract):
    def __init__(self, cond: Arith):
        super().__init__("req", cond)

# Special result reference
# Only valid inside of a postcondition
# References the output of the current module
class Res(Arith):
    def __init__(self) -> None:
        super().__init__("res")

# Free variable definition (only valid at the top-level)
# This is mostly used for elaboration and not exposed to the user
class In(Stmt):
    # Defined by a single name that will be used 
    # to reference the free variable
    def __init__(self, name: str) -> None:
        super().__init__(name)
        
    @override
    def serialize(self) -> str:
        return f"in {self.name}"

# Ouput expression of a module
class Out(Node):
    # Defined by a single expression
    # @param{e: Expr}: output expression of the module
    def __init__(self, e: Expr) -> None:
        super().__init__("out")
        self.e: Expr = e

    @override
    def serialize(self) -> str:
        return f"{self.name} {self.e.serialize()}"

# Module definition
class Module(Stmt):
    # Defined by a list of input names, an optional contract, and a body
    # @param{args: list[In]}: list of input names
    # @param[Optional]{contract}: Pre-condition and Post-condition specifying this module
    # @param{body}: the body of the module, defined by:
    #   {stmts: list[Stmt]}: A list of statements defining names used in the output expression
    #   [Optional]{out: Out}: Output expression of the module
    #      --> Only omitted in the case where the module is at the top-level
    def __init__( \
            self, \
            args: list[In], \
            contract: Optional[tuple[PreCond, PostCond]], \
            body: tuple[list[Stmt], Optional[Out]] \
    ) -> None:
        super().__init__("mod")
        self.args: list[In] = args
        self.contract: Optional[tuple[PreCond, PostCond]] = contract
        self.body: tuple[list[Stmt], Optional[Out]] = body
        (self.stmts, self.out) = self.body    

# Arguments can typically be any named thing or unnamed expression
Arg: TypeAlias = Symbol | Expr | In
Callable: TypeAlias = Module | Symbol

# Instance of a module or a name of a module
class Inst(Expr):
    # Defined by a callable element (either a symbol or a module),
    #   a module that is being instanciated (same as c or dealiased name),
    #   and a list of arguments that must be similar to the arguments of the module
    # @param{c: Callable}: Module or name of a module being instantiated
    # @param{m: Module}: Module being instantiated (dealiased version of c)
    # @param{args: list[Arg]}: List of arguments, must be similar to module arguments
    def __init__(self, c: Callable, m: Module, args: list[Arg]) -> None:
        super().__init__("inst")
        # Check if the called symbol is callable
        if isinstance(c, Symbol):
            assert isinstance(c.expr, Module), f"Non-Callable instance of Symbol {c.name}"

        # Set fields if instance is valid
        self.c: Callable = c
        self.m: Module = c.expr \
            if isinstance(c, Symbol) and isinstance(c.expr, Module) \
            else m
        self.args: list[Arg] = args

        # Check that the given arguments are similar to the ones accepted by the module
        assert len(self.m.args) == len(self.args), \
            f"There are {len(self.m.args)} module arguments, but only {len(self.args)} were given!"


################################################
## Statement s  ::=
#   r -> v, e | x = e | x = m | 
#       assert a | assume a | 
#       mod(x, ...,x)[req a; ens h]{b} | 
#       mod(x, ...,x){b}
################################################

# Abstract Node for any statement that defines a new name
class Def(Stmt):
    def __init__(self, name: str) -> None:
        super().__init__(name)

    # Converts the current statement into a symbol that can be stored in the context
    def toSymbol(self) -> Symbol:
        return Symbol(self.name, self)

# Name binding for either an expression or a module
# e.g. x = a and b
#      not = mod(x){x xor 1}
class Bind(Def):
    # Defined by a name and either an expression or a module
    # @param{name: str}: the name that can be used to reference the given argument
    # @param{e: Expr | Module}: Argument to be bound to the given name
    def __init__(self, name: str, e: Expr | Module) -> None:
        super().__init__(name)
        self.e: Expr | Module = e

    @override
    def serialize(self) -> str:
        return f"{self.name} = {self.e.serialize()}"
    

# Register Definition
#   Notation: 
#       Substitution of r by v in e := e[v/r] 
#       Denotation at cycle k := [[e]]k
# Denotational Semantics:
#   [[r → v, e]]0 = [[v]]
#   [[r → v, e]]1 = [[ e[v/r] ]]
#   [[r → v, e]]k = [[ e[ [[r → v, e]]k−1 /r ] ]]
#   [[r0 → v0, e0; ...; ri → vi, ei]]0 = [[v0]] ; ...; [[vi]]
#   [[r0 → v0, e0; ...; ri → vi, ei]]1 = [[ e0[v0/r0]...[vi/ri] ]]; ...; [[ ei[v0/r0]...[vi/ri] ]]
#   [[r0 → v0, e0; ...; ri → vi, ei]]k = 
#       [[ e0[ [[r0 → v0, e0]]k−1 /r0 ]...[ [[ri → vi, ei]]k−1 /ri ] ]];
#       ...;
#       [[ ei[ [[r0 → v0, e0]]k−1 /r0 ]...[ [[ri → vi, ei]]k−1 /ri ] ]];
class Reg(Def):
    # Defined by a name, an initial value and a next expression
    # @param{sym: str}: name that the register can be referred to by
    # @param{init: Value}: initial value of the register
    # @param{next: Expr}: Expression defining how the register's value
    #   progresses across each cycle.
    def __init__(self, name: str, init: Value, next: Expr) -> None:
        super().__init__(name)
        self.init: Value = init
        self.next: Expr = next

    @override
    def serialize(self) -> str:
        return f"{self.name} -> {self.init.serialize()}, {self.next.serialize()}"
    

# Abstract Node for a verification statement
class Verif(Stmt):
    # Defined by a keyword and a condition
    # @param{cond: Arith}: Arithmetic expression used as the condition to be checked
    def __init__(self, name: str, cond: Arith) -> None:
        super().__init__(name)
        self.cond: Arith = cond

    @override
    def serialize(self) -> str:
        return f"{self.name} {self.cond.serialize()}"

# Assertion that checks if a given condition evaluates to 1
class Assert(Verif):
    def __init__(self, cond: Arith) -> None:
        super().__init__("assert", cond)

# Assumption that adds a given predicate to a knowledge context
# These predicates will be considered to hold for all assertions
class Assume(Verif):
    def __init__(self, cond: Arith) -> None:
        super().__init__("assume", cond)
        

