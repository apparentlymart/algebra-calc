
from plex import *
import re

__all__ = ["new_scanner"]

letter = Range("AZaz")
space = Any(" ")
digit = Range("09")

greek_letters = set([
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "omicron",
    "pi",
    "rho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "chi",
    "psi",
    "omega",
    "digamma",
])
greek_letters.update(
    [letter_name[0].upper() + letter_name[1:] for letter_name in greek_letters]
)
math_letter = letter
for letter_name in greek_letters:
    math_letter = math_letter | (Str("\\") + Str(letter_name) + Opt(space))

command_punct_names = set([
    "div",    # MathQuill doesn't actually generate this but user can type it
    "times",
    "cdot",   # MathQuill uses this for explicit multiplication
    "infty",  # infinity symbol
    "inf",    # synonym for infty
])
command_punct = (
    (Str("\\left") + Opt(space) + Any("(")) |
    (Str("\\right") + Opt(space) + Any(")"))
)
for command_punct_name in command_punct_names:
    if command_punct is None:
        command_punct = (
            Str("\\") + Str(command_punct_name) + Opt(space)
        )
    else:
        command_punct = (
            command_punct | (Str("\\") + Str(command_punct_name) + Opt(space))
        )

command_pat = Str("\\") + (Rep1(letter) | AnyChar) + Opt(space)
sym_subscript_pat = (
    Str('{') + Rep1(math_letter | digit) + Str('}') |
    (math_letter | digit)
)


class TokenType(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "TokenType.%s" % self.name


TokenType.COMMAND = TokenType('COMMAND')
TokenType.NUMBER = TokenType('NUMBER')
TokenType.SYMBOL = TokenType('SYMBOL')
TokenType.OBLOCK = TokenType('OBLOCK')
TokenType.CBLOCK = TokenType('CBLOCK')
TokenType.PUNCT = TokenType('PUNCT')


lexicon = Lexicon([
    (math_letter + Opt(Str("_") + sym_subscript_pat), TokenType.SYMBOL),
    (command_punct, TokenType.PUNCT),
    (command_pat, TokenType.COMMAND),
    (Rep1(digit) + Opt(Str(".") + Rep1(digit)), TokenType.NUMBER),
    (Str("{"), TokenType.OBLOCK),
    (Str("}"), TokenType.CBLOCK),
    (Rep1(space), IGNORE),
    (AnyChar, TokenType.PUNCT),
])


class PeekScanner(object):

    normalize_punct = {
        r'\left(': "(",
        r'\right)': ")",
        r'\inf': r'\infty',
        r'\cdot': r'\times',
    }

    sym_sub_re = re.compile(r'^(.)\_\{([a-zA-Z0-9]|\\[a-z]+ ?)\}$')

    def __init__(self, scanner):
        self._scanner = scanner
        self._peeked = None

    @property
    def next(self):
        if self._peeked is None:
            self._peeked = self._normalize(self._scanner.read())
        return self._peeked

    def read(self):
        token = self.next
        self._peeked = None
        return token

    def _normalize(self, token):
        # For easier matching in the parser, we normalize a few different
        # forms the scanner allows into a predictable shape.

        if token[0] == TokenType.PUNCT:
            token = list(token)
            token[1] = token[1].replace(' ', '')
            if token[1] in self.normalize_punct:
                token[1] = self.normalize_punct[token[1]]
        elif token[0] == TokenType.SYMBOL:
            token = list(token)

            def sym_sub(matchobj):
                return '%s_%s' % (
                    matchobj.group(1), matchobj.group(2).replace(' ', '')
                )

            token[1] = self.sym_sub_re.sub(sym_sub, token[1]).rstrip()
        elif token[0] == TokenType.COMMAND:
            token = list(token)
            token[1] = token[1].rstrip()

        return tuple(token)


def new_scanner(stream):
    return PeekScanner(Scanner(lexicon, stream))
