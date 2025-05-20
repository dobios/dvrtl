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

# Arithmetic expression (used in an assertion/assumption)
class Arith(Node):
    def __init__(self, name: str) -> None:
        super().__init__(name)

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

# Binary Exclusive Or (Xor) operator 
# a | b | a xor b
# ----------------
# 1   1      0
# 1   0      1
# 0   1      1
# 0   0      0
class Xor(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("xor", lhs, rhs)

# Binary AND operator 
# a | b | a and b
# ----------------
# 1   1      1
# 1   0      0
# 0   1      0
# 0   0      0
class And(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("and", lhs, rhs)

# Binary OR operator 
# a | b | a or b
# ----------------
# 1   1      1
# 1   0      1
# 0   1      1
# 0   0      0
class Or(EBinOp):
    def __init__(self, lhs, rhs) -> None:
        super().__init__("or", lhs, rhs)


class Mux(EOp):
    def __init__(self, s: Expr, tOp: Expr, fOp: Expr) -> None:
        super().__init__("mux", [s, tOp, fOp])


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
class Zero(Value):
    def __init__(self) -> None:
        super().__init__("0")
    
    @override
    def toInt(self) -> int:
        return 0
    
# One value: represents a 1 bit  
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
class Skip(Order):
    def __init__(self) -> None:
        super().__init__("skip")
    
# Fail: result of a failed assertion 
class Fail(Value):
    def __init__(self) -> None:
        super().__init__("fail")
        
