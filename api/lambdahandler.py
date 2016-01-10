import json
import re

from parser import parse_expr
from solver import solve
from sympy import latex, Eq


def lambda_handler(event, context):
    statement_sources = event['statements']

    statements = [
        Eq(parse_expr(s[0]), parse_expr(s[1])) for s in statement_sources
    ]

    knowns, unknowns = solve(statements)

    ret = {
        "known": {},
        "unknown": {},
    }

    for symbol, value in knowns.iteritems():
        if type(value) is not tuple:
            value = (value,)

        ret["known"][latex(symbol)] = {
            "results": [
                {
                    "float": latex(possibility.evalf()),
                    "rational": latex(possibility),
                }
                for possibility in value
            ],
        }

    for symbol, resolutions in unknowns.iteritems():
        ret["unknown"][latex(symbol)] = {
            "resolutions": [
                {
                    "dependencies": [
                        latex(dep_symbol)
                        for dep_symbol in resolution.required_symbols
                    ],
                    "solutions": [
                        latex(solution)
                        for solution in (
                            resolution.rhs if type(resolution.rhs) is list
                            else [resolution.rhs,]
                        )
                    ],
                } for resolution in resolutions
            ],
        }

    return ret
