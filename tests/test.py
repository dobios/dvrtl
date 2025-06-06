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

class BTORTestParser(unittest.TestCase):
    """Check whether BTOR interface is working properly"""
     
    # Checks that a minirtl design can be parsed
    def test_parse_tree_mini(self):
        parser: Parser = parse("tests/dv/mini.dv", isfilename=True)

        expected_tree: str = """start
  register
    A
    bit
    xor
      C
      scoped_expr
        xor
          a
          b
  register
    B
    bit
    B
  register
    C
    bit
    or
      scoped_expr
        and
          A
          B
      scoped_expr
        and
          C
          scoped_expr
            xor
              A
              B
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree mini passed")

    # checks that an assertrtl design can be parsed
    def test_parse_tree_assert(self):
        parser: Parser = parse("tests/dv/assert.dv", isfilename=True)
        expected_tree: str = """start
  register
    A
    bit
    xor
      C
      scoped_expr
        xor
          a
          b
  register
    Ap
    bit
    A
  register
    B
    bit
    B
  register
    C
    bit
    or
      scoped_expr
        and
          A
          B
      scoped_expr
        and
          C
          scoped_expr
            xor
              A
              B
  assert
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
          xor
            a_in
            b_in
        xor
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
          axb
          xor
            a_in
            b_in
        bind
          anb
          and
            a_in
            b_in
        or
          anb
          scoped_expr
            and
              c_in
              axb
  bind
    add2_0
    module
      list_of_variables
        a1
        a0
        b1
        b0
      call
        sum
        list_of_expr
          a0
          b0
          bit
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
              bit
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
              bit
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
        bit
        bit
        bit
        bit
  bind
    bit1
    call
      add2_1
      list_of_expr
        bit
        bit
        bit
        bit
  bind
    overflow
    call
      carry2
      list_of_expr
        bit
        bit
        bit
        bit
  assert
    arith_and
      arith_and
        scoped_arith
          sub
            bit0
            bit
        scoped_arith
          sub
            bit1
            bit
      scoped_arith
        sub
          overflow
          bit
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
        bit
        sub
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
          xor
            a_in
            b_in
        xor
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
          axb
          xor
            a_in
            b_in
        bind
          anb
          and
            a_in
            b_in
        or
          anb
          scoped_expr
            and
              c_in
              axb
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
              bit
              sub
                res
                scoped_arith
                  add
                    a0
                    b0
            call
              sum
              list_of_expr
                a0
                b0
                bit
        bind
          add2_1
          module
            list_of_variables
              a1
              a0
              b1
              b0
            contract
              bit
              sub
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
                    bit
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
            bit
            sub
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
                  bit
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
          bit
          bit
          bit
          bit
  bind
    bit1
    call
      add2_1
      list_of_expr
        bit
        bit
        bit
        bit
  bind
    overflow
    call
      carry2
      list_of_expr
        bit
        bit
        bit
        bit
  assert
    arith_and
      arith_and
        scoped_arith
          sub
            bit0
            bit
        scoped_arith
          sub
            bit1
            bit
      scoped_arith
        sub
          overflow
          bit
"""
        self.assertEqual(parser.tree.pretty(), expected_tree)

        print("test parse tree untyped passed")

if __name__ == '__main__':
    unittest.main()