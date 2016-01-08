from __future__ import division

import functools
from scanner import new_scanner, TokenType
from StringIO import StringIO

from sympy import sqrt, sin, cos, tan, pi, oo
from sympy.core.numbers import Float, Rational, I, E, pi
from sympy.core.symbol import Symbol

__all__ = ["parse_expr"]


class Parser(object):

    def __init__(self, scanner):
        self.scanner = scanner

    def parse_expression(self):
        expr = self.p_expression()
        if self.scanner.next[0] != None:
            raise Exception('Extra tokens after end of expression')
        return expr

    def p_expression(self):
        return self.p_sum()

    def p_sum(self):
        lhs = self.p_product()
        op = self.scanner.next
        if op[0] == TokenType.PUNCT and op[1] in ('+', '-'):
            self.scanner.read()
            # Call this function recursively so that we can
            # chain together sums like x + y + z + ...
            rhs = self.p_sum()
            if op[1] == '-':
                return lhs - rhs
            else:
                return lhs + rhs

        return lhs

    def p_product(self):
        lhs = self.p_exponent()
        op = self.scanner.next
        # Multiplication is implied by having no punctuation
        # at all, but we also support an explicit \times.
        if op[0] is None:
            # If we're at the end of the string then we can't multiply!
            return lhs

        if op[0] == TokenType.CBLOCK:
            return lhs

        if op[0] == TokenType.PUNCT:
            if op[1] in ('+', '-', ')', ']'):
                return lhs

            if op[1] in (r'\times', '\div'):
                # Eat the operator
                self.scanner.read()

        rhs = self.p_product()
        if op[1] == '\div':
            return lhs / rhs
        else:
            return lhs * rhs

    def p_exponent(self):
        lhs = self.p_sign()
        op = self.scanner.next
        if op[0] == TokenType.PUNCT and op[1] == ('^'):
            self.scanner.read()
            rhs = self.p_exponent()
            return lhs ** rhs

        return lhs

    def p_sign(self):
        sign = None
        if self.scanner.next[0] == TokenType.PUNCT:
            if self.scanner.next[1] in ('-', '+'):
                sign = self.scanner.read()
                operand = self.p_sign()
                if sign[1] == '-':
                    return -operand
                else:
                    return operand

        return self.p_factor()

    def p_factor(self):
        peek = self.scanner.next

        if peek[0] == TokenType.NUMBER:
            self.scanner.read()
            return Rational(peek[1])
        elif peek[0] == TokenType.SYMBOL:
            self.scanner.read()
            if peek[1] == 'i':
                return I
            elif peek[1] == 'e':
                return E
            elif peek[1] == '\pi':
                return pi
            else:
                return Symbol(peek[1])
        elif peek[0] == TokenType.PUNCT:
            if peek[1] == '(':
                self.scanner.read()
                expr = self.p_expression()
                close = self.scanner.read()
                if close[0] != TokenType.PUNCT or close[1] != ')':
                    raise Exception('Mismatched parentheses')
                return expr
            else:
                raise Exception('Unexpected ' + peek[1])
        elif peek[0] == TokenType.COMMAND:
            if peek[1] == r'\sqrt':
                self.scanner.read()
                if self.scanner.next[1] == '[':
                    self.scanner.read()
                    power_expr = self.p_expression()
                    if self.scanner.next[1] != ']':
                        raise Exception(
                            'Expected [ but got ' + self.scanner.next[1]
                        )
                    self.scanner.read()
                    inner = self.p_block_expr()
                    return inner ** Rational(1, power_expr)
                else:
                    inner = self.p_block_expr()
                    return sqrt(inner)
            elif peek[1] == r'\frac':
                self.scanner.read()
                num_expr = self.p_block_expr()
                den_expr = self.p_block_expr()
                return num_expr / den_expr
            elif peek[1] == r'\cos':
                self.scanner.read()
                operand_expr = self.p_expression()
                return cos(operand_expr)
            elif peek[1] == r'\sin':
                self.scanner.read()
                operand_expr = self.p_expression()
                return sin(operand_expr)
            elif peek[1] == r'\tan':
                self.scanner.read()
                operand_expr = self.p_expression()
                return tan(operand_expr)
            else:
                raise Exception('Unknown command ' + peek[1])
        else:
            raise Exception('Term cannot begin with ' + repr(peek))

    def p_block_expr(self):
        open_brace = self.scanner.read()
        if open_brace[0] != TokenType.OBLOCK:
            raise Exception('Expected { but got ' + open_brace[1])

        expr = self.p_expression()

        close_brace = self.scanner.read()
        if close_brace[0] != TokenType.CBLOCK:
            raise Exception('Expected } but got ' + close_brace[1])

        return expr


def parse_expr(s):
    f = StringIO(s)
    scanner = new_scanner(f)
    parser = Parser(scanner)
    return parser.parse_expression()
