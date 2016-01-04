
from scanner import new_scanner, TokenType
from StringIO import StringIO

from sympy.core.numbers import Float
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
        return self.p_factor()
        # TODO: implement the rest of this
        lhs = self.p_sign()

    def p_sign(self):
        sign = None
        if self.scanner.next[0] == TokenType.PUNCT:
            if self.scanner.next[1] in ('-', '+'):
                sign = self.scanner.read()

        operand = self.p_factor()

        if sign is not None:
            # TODO: Wrap the operand in a sign node
            pass
        else:
            return operand

    def p_factor(self):
        peek = self.scanner.next

        if peek[0] == TokenType.NUMBER:
            self.scanner.read()
            return Float(peek[1])
        elif peek[0] == TokenType.SYMBOL:
            self.scanner.read()
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
        else:
            raise Exception('Term cannot begin with ' + repr(peek))


def parse_expr(s):
    f = StringIO(s)
    scanner = new_scanner(f)
    parser = Parser(scanner)
    return parser.parse_expression()
