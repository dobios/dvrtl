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
    identifier\tA
    zero
    expr_xor
      identifier\tC
      scoped_expr
        expr_xor
          identifier\ta
          identifier\tb
  reg
    identifier\tB
    one
    identifier\tB
  reg
    identifier\tC
    zero
    expr_or
      scoped_expr
        expr_and
          identifier\tA
          identifier\tB
      scoped_expr
        expr_and
          identifier\tC
          scoped_expr
            expr_xor
              identifier\tA
              identifier\tB
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree mini passed")

    # checks that an assertrtl design can be parsed
    def test_parse_tree_assert(self):
        parser: Parser = parse("tests/dv/assert.dv", isfilename=True)
        expected_tree: str = """start
  reg
    identifier\tA
    zero
    expr_xor
      identifier\tC
      scoped_expr
        expr_xor
          identifier\ta
          identifier\tb
  reg
    identifier\tAp
    zero
    identifier\tA
  reg
    identifier\tB
    one
    identifier\tB
  reg
    identifier\tC
    zero
    expr_or
      scoped_expr
        expr_and
          identifier\tA
          identifier\tB
      scoped_expr
        expr_and
          identifier\tC
          scoped_expr
            expr_xor
              identifier\tA
              identifier\tB
  stmt_assert
    arith_xor
      identifier\tA
      identifier\tAp
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree assert passed")

    # checks that a modrtl design can be parsed
    def test_parse_tree_mod(self):
        parser: Parser = parse("tests/dv/mod.dv", isfilename=True)
        expected_tree: str = """start
  bind
    identifier\tsum
    module
      list_of_variables
        identifier\ta_in
        identifier\tb_in
        identifier\tc_in
      body
        bind
          identifier\taxb
          expr_xor
            identifier\ta_in
            identifier\tb_in
        out
          expr_xor
            identifier\tc_in
            identifier\taxb
  bind
    identifier\tcarry
    module
      list_of_variables
        identifier\ta_in
        identifier\tb_in
        identifier\tc_in
      body
        bind
          identifier\taxb_
          expr_xor
            identifier\ta_in
            identifier\tb_in
        bind
          identifier\tanb
          expr_and
            identifier\ta_in
            identifier\tb_in
        out
          expr_or
            identifier\tanb
            scoped_expr
              expr_and
                identifier\tc_in
                identifier\taxb_
  bind
    identifier\tadd2_0
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      out
        call
          identifier\tsum
          list_of_expr
            identifier\ta0
            identifier\tb0
            zero
  bind
    identifier\tadd2_1
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      body
        bind
          identifier\tc_0
          call
            identifier\tcarry
            list_of_expr
              identifier\ta0
              identifier\tb0
              zero
        out
          call
            identifier\tsum
            list_of_expr
              identifier\ta1
              identifier\tb1
              identifier\tc_0
  bind
    identifier\tcarry2
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      body
        bind
          identifier\tcarry0
          call
            identifier\tcarry
            list_of_expr
              identifier\ta0
              identifier\tb0
              zero
        out
          call
            identifier\tcarry
            list_of_expr
              identifier\ta1
              identifier\tb1
              identifier\tcarry0
  bind
    identifier\tbit0
    call
      identifier\tadd2_0
      list_of_expr
        zero
        one
        zero
        one
  bind
    identifier\tbit1
    call
      identifier\tadd2_1
      list_of_expr
        zero
        one
        zero
        one
  bind
    identifier\toverflow
    call
      identifier\tcarry2
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
            identifier\tbit0
            zero
        scoped_arith
          eq
            identifier\tbit1
            one
      scoped_arith
        eq
          identifier\toverflow
          zero
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree mod passed")

    # checks that an untyped design can be parsed
    def test_parse_tree_untyped(self):
        parser: Parser = parse("tests/dv/untyped.dv", isfilename=True)
        expected_tree: str = """start
  bind
    identifier\tsum
    module
      list_of_variables
        identifier\ta_in
        identifier\tb_in
        identifier\tc_in
      contract
        one
        eq
          identifier\tres
          scoped_arith
            add
              add
                identifier\ta_in
                identifier\tb_in
              identifier\tc_in
      body
        bind
          identifier\taxb
          expr_xor
            identifier\ta_in
            identifier\tb_in
        out
          expr_xor
            identifier\tc_in
            identifier\taxb
  bind
    identifier\tcarry
    module
      list_of_variables
        identifier\ta_in
        identifier\tb_in
        identifier\tc_in
      body
        bind
          identifier\taxb_
          expr_xor
            identifier\ta_in
            identifier\tb_in
        bind
          identifier\tanb
          expr_and
            identifier\ta_in
            identifier\tb_in
        out
          expr_or
            identifier\tanb
            scoped_expr
              expr_and
                identifier\tc_in
                identifier\taxb_
  bind
    identifier\tadd2_0
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      contract
        one
        eq
          identifier\tres
          scoped_arith
            add
              identifier\ta0
              identifier\tb0
      out
        call
          identifier\tsum
          list_of_expr
            identifier\ta0
            identifier\tb0
            zero
  bind
    identifier\tadd2_1
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      contract
        one
        eq
          identifier\tres
          scoped_arith
            add
              scoped_expr
                expr_and
                  identifier\ta0
                  identifier\tb0
              scoped_arith
                add
                  identifier\ta1
                  identifier\tb1
      body
        bind
          identifier\tc_0
          call
            identifier\tcarry
            list_of_expr
              identifier\ta0
              identifier\tb0
              zero
        out
          call
            identifier\tsum
            list_of_expr
              identifier\ta1
              identifier\tb1
              identifier\tc_0
  bind
    identifier\tcarry2
    module
      list_of_variables
        identifier\ta1
        identifier\ta0
        identifier\tb1
        identifier\tb0
      contract
        one
        eq
          identifier\tres
          scoped_arith
            add
              scoped_expr
                expr_and
                  identifier\ta0
                  identifier\tb0
              scoped_expr
                expr_and
                  identifier\ta1
                  identifier\tb1
      body
        bind
          identifier\tcarry0
          call
            identifier\tcarry
            list_of_expr
              identifier\ta0
              identifier\tb0
              zero
        out
          call
            identifier\tcarry
            list_of_expr
              identifier\ta1
              identifier\tb1
              identifier\tcarry0
  bind
    identifier\tbit0
    call
      identifier\tadd2_0
      list_of_expr
        zero
        one
        zero
        one
  bind
    identifier\tbit1
    call
      identifier\tadd2_1
      list_of_expr
        zero
        one
        zero
        one
  bind
    identifier\toverflow
    call
      identifier\tcarry2
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
            identifier\tbit0
            zero
        scoped_arith
          eq
            identifier\tbit1
            one
      scoped_arith
        eq
          identifier\toverflow
          zero
"""
        self.maxDiff = None
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree untyped passed")

    # Checks that a minirtl design can be parsed and converted to an AST
    def test_ast_mini(self):
      parser: Parser = parse("tests/dv/mini.dv", isfilename=True)
      
      print(parser.ast.toString())
      expected_ast = parser.ast

      self.assertEqual(parser.ast, expected_ast)

      print("test ast mini passed")

if __name__ == '__main__':
    unittest.main()