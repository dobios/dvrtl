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

from functools import reduce
import unittest

from src.parser import *

def parsewrapper (filepath) -> list[str]:
    dvstr: list[str] = []
    with open(filepath, "r") as f:
        dvstr = f.readlines()
    return dvstr

def reduce_p_str(p_str: list[str]) -> str:
    return reduce(lambda acc, s: acc + s + "\n", p_str, "")

class DVRTLTestParser(unittest.TestCase):
    """Check whether DVRTL interface is working properly"""
     
    # Checks that a minirtl design can be parsed
    def test_parse_tree_mini(self):
        parser: Parser = parse("tests/dv/mini.dv", isfilename=True)

        expected_tree: str = """start
  reg
    A
    zero
    expr_xor
      C
      scoped_expr
        expr_xor
          a
          b
  reg
    B
    one
    B
  reg
    C
    zero
    expr_or
      scoped_expr
        expr_and
          A
          B
      scoped_expr
        expr_and
          C
          scoped_expr
            expr_xor
              A
              B
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree mini passed")

    # checks that an assertrtl design can be parsed
    def test_parse_tree_assert(self):
        parser: Parser = parse("tests/dv/assert.dv", isfilename=True)
        expected_tree: str = """start
  reg
    A
    zero
    expr_xor
      C
      scoped_expr
        expr_xor
          a
          b
  reg
    Ap
    zero
    A
  reg
    B
    one
    B
  reg
    C
    zero
    expr_or
      scoped_expr
        expr_and
          A
          B
      scoped_expr
        expr_and
          C
          scoped_expr
            expr_xor
              A
              B
  stmt_assert
    arith_xor
      A
      Ap
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree assert passed")

    # checks that a modrtl design can be parsed
    def test_parse_tree_mod(self):
        parser: Parser = parse("tests/dv/mod.dv", isfilename=True)
        expected_tree: str = """start
  bind
    sum
    module
      list_of_variables
        a_in
        b_in
        c_in
      body
        bind
          axb
          expr_xor
            a_in
            b_in
        out
          expr_xor
            c_in
            axb
  bind
    carry
    module
      list_of_variables
        a_in
        b_in
        c_in
      body
        bind
          axb_
          expr_xor
            a_in
            b_in
        bind
          anb
          expr_and
            a_in
            b_in
        out
          expr_or
            anb
            scoped_expr
              expr_and
                c_in
                axb_
  bind
    add2_0
    module
      list_of_variables
        a1
        a0
        b1
        b0
      out
        call
          sum
          list_of_expr
            a0
            b0
            zero
  bind
    add2_1
    module
      list_of_variables
        a1
        a0
        b1
        b0
      body
        bind
          c_0
          call
            carry
            list_of_expr
              a0
              b0
              zero
        out
          call
            sum
            list_of_expr
              a1
              b1
              c_0
  bind
    carry2
    module
      list_of_variables
        a1
        a0
        b1
        b0
      body
        bind
          carry0
          call
            carry
            list_of_expr
              a0
              b0
              zero
        out
          call
            carry
            list_of_expr
              a1
              b1
              carry0
  bind
    bit0
    call
      add2_0
      list_of_expr
        zero
        one
        zero
        one
  bind
    bit1
    call
      add2_1
      list_of_expr
        zero
        one
        zero
        one
  bind
    overflow
    call
      carry2
      list_of_expr
        zero
        one
        zero
        one
  stmt_assert
    arith_and
      arith_and
        scoped_arith
          eq
            bit0
            zero
        scoped_arith
          eq
            bit1
            one
      scoped_arith
        eq
          overflow
          zero
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree mod passed")

    # checks that an untyped design can be parsed
    def test_parse_tree_untyped(self):
        parser: Parser = parse("tests/dv/untyped.dv", isfilename=True)
        expected_tree: str = """start
  bind
    sum
    module
      list_of_variables
        a_in
        b_in
        c_in
      contract
        one
        eq
          res
          scoped_arith
            add
              add
                a_in
                b_in
              c_in
      body
        bind
          axb
          expr_xor
            a_in
            b_in
        out
          expr_xor
            c_in
            axb
  bind
    carry
    module
      list_of_variables
        a_in
        b_in
        c_in
      body
        bind
          axb_
          expr_xor
            a_in
            b_in
        bind
          anb
          expr_and
            a_in
            b_in
        out
          expr_or
            anb
            scoped_expr
              expr_and
                c_in
                axb_
  stmt_seq
    stmt_seq
      stmt_seq
        bind
          add2_0
          module
            list_of_variables
              a1
              a0
              b1
              b0
            contract
              one
              eq
                res
                scoped_arith
                  add
                    a0
                    b0
            out
              call
                sum
                list_of_expr
                  a0
                  b0
                  zero
        bind
          add2_1
          module
            list_of_variables
              a1
              a0
              b1
              b0
            contract
              one
              eq
                res
                scoped_arith
                  add
                    scoped_arith
                      arith_and
                        a0
                        b0
                    scoped_arith
                      add
                        a1
                        b1
            body
              bind
                c_0
                call
                  carry
                  list_of_expr
                    a0
                    b0
                    zero
              out
                call
                  sum
                  list_of_expr
                    a1
                    b1
                    c_0
      bind
        carry2
        module
          list_of_variables
            a1
            a0
            b1
            b0
          contract
            one
            eq
              res
              scoped_arith
                add
                  scoped_arith
                    arith_and
                      a0
                      b0
                  scoped_arith
                    arith_and
                      a1
                      b1
          body
            bind
              carry0
              call
                carry
                list_of_expr
                  a0
                  b0
                  zero
            out
              call
                carry
                list_of_expr
                  a1
                  b1
                  carry0
    bind
      bit0
      call
        add2_0
        list_of_expr
          zero
          one
          zero
          one
  bind
    bit1
    call
      add2_1
      list_of_expr
        zero
        one
        zero
        one
  bind
    overflow
    call
      carry2
      list_of_expr
        zero
        one
        zero
        one
  stmt_assert
    arith_and
      arith_and
        scoped_arith
          eq
            bit0
            zero
        scoped_arith
          eq
            bit1
            one
      scoped_arith
        eq
          overflow
          zero
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree untyped passed")

    # Checks that a minirtl design can be parsed and converted to an AST
    def test_ast_mini(self):
      parser: Parser = parse("tests/dv/mini.dv", isfilename=True)
      
      print(parser.ast)
      expected_ast = parser.ast

      self.assertEqual(parser.ast, expected_ast)

      print("test ast mini passed")

if __name__ == '__main__':
    unittest.main()