"""
Top-level syntax definition of the contRTL language.
The formal definition of the full syntax is as follows:

Registers r     Variables x
Value v         ::= 0 | 1
Order o         ::= skip | fail
Expression e    ::=	e xor e | e and e | e or e | mux e e e |
                        v | r | x | m (e,...,e) | x (e,...,e)
Arithmetic a    ::= a impl a | a + a | a - a | a eq a |
                        a xor a | a and a | a or a | e
Contract h      ::= res | a
Module m        ::= mod(x, ...,x)[req a; ens a]{b} | mod(x, ...,x){b}
Statement s     ::= r -> v, e | x = e | x = m | assert a | assume a | m
Body b          ::= [s]* ; out e
Circuit c       ::= [s]* 
"""
from typing_extensions import override
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
## Arithmetic a ::=
#   a impl a | a + a | a - a | a eq a | 
#       a xor a | a and a | a or a | e
################################################

# Arithmetic expression (used in an assertion/assumption)
class Arith(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

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

# Arithmetic Equality
# Denotational Semantics:
#   [[ e1 eq e2 ]] = ¬([[e1]] ⊕ [[e2]])
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

# Synthesizable expression, these are also valid arithmetic expressions
class Expr(Arith):
    def __init__(self, name: str) -> None:
        super().__init__(name)

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

# Symbol refering to either a register or a name binding in our context
class Symbol(Expr):
    # Defined by a symbol name and a linked expression
    # @param{sym: str}: The name given to the symbol
    # @param{stmt: Stmt}: The statement that declared this symbol
    def __init__(self, sym: str, stmt: Stmt) -> None:
        super().__init__(sym)
        self.expr: Stmt = stmt


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
        
