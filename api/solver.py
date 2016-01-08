from sympy.core.symbol import Symbol
from sympy.solvers.solvers import solve as solve_system
from sympy.core.relational import Equality as Eq
from sympy.simplify.simplify import simplify
from sympy import true, false, pretty


__all__ = ["solve", "Dependency"]


def solve(statements):
    # Find all the symbols mentioned in the statements.
    symbols = set()
    for statement in statements:
        symbols = symbols.union(statement.atoms(Symbol))

    known_symbols = set()
    results = {}

    # Initial pass over the statements to see which ones are
    # "simple knowns": lhs is a symbol and rhs is non-symbolic.
    equations = set()
    for statement in statements:
        known_symbol = as_known(statement)
        if known_symbol is not None:
            if known_symbol.lhs in results:
                raise Exception(
                    'Conflicting values of ' + str(known_symbol.lhs)
                )
            results[known_symbol.lhs] = simplify(known_symbol.rhs)
            known_symbols.add(known_symbol.lhs)
            continue
        equations.add(statement)

    # Substitute all of the "simple knowns" into the equations
    # to take care of the simple cases.
    if len(known_symbols) > 0:
        for equation in equations:
            for symbol, value in results.iteritems():
                equation = equation.subs(symbol, value)

            remaining_symbols = equation.atoms(Symbol)
            if len(remaining_symbols) == 0:
                continue
            else:
                known_symbol = as_known(equation)
                if known_symbol is not None:
                    results[known_symbol.lhs] = simplify(known_symbol.rhs)
                    known_symbols.add(known_symbol.lhs)

    # Re-substitute all of the original equations with what we now know.
    # In the process, we might eliminate all of the symbols from
    # some of the equations. If any of them reduce to False then there
    # is an inconsistency in the statements which the user must fix.
    if len(known_symbols) > 0:
        reduced_equations = set()
        for equation in equations:
            subst_equation = equation
            for symbol, value in results.iteritems():
                subst_equation = subst_equation.subs(symbol, value)

            if subst_equation == false:
                raise Exception('Inconsistency evaluating ' + pretty(equation))
            elif subst_equation != true:
                reduced_equations.add(subst_equation)
        equations = reduced_equations

    unresolved = set()

    if len(symbols - known_symbols) > 0:
        try:
            solutions = solve_system(equations, set=True)
        except NotImplementedError:
            raise Exception('No solution found')

        if type(solutions) is tuple:
            if len(solutions[1]) == 0:
                raise Exception('No solution found')

            for i, lhs in enumerate(solutions[0]):
                sol_equs = (Eq(lhs, solution[i]) for solution in solutions[1])
                for sol_equ in sol_equs:
                    known_symbol = as_known(sol_equ)
                    if known_symbol is not None:
                        results[known_symbol.lhs] = known_symbol.rhs
                        known_symbols.add(known_symbol.lhs)
                    else:
                        unresolved.add(sol_equ)
        else:
            if type(solutions) is list:
                for solution in solutions:
                    sol_equs = (
                        Eq(lhs, rhs) for lhs, rhs in solution.iteritems()
                    )
                    for sol_equ in sol_equs:
                        known_symbol = as_known(sol_equ)
                        if known_symbol is not None:
                            results[known_symbol.lhs] = known_symbol.rhs
                            known_symbols.add(known_symbol.lhs)
                        else:
                            unresolved.add(sol_equ)
            else:
                raise Exception('No finite solution found')

    # Any unresolved equations become dependency declarations.
    unknowns = {}
    for equation in unresolved:
        equ_symbols = equation.atoms(Symbol)
        for symbol in equ_symbols:
            if symbol in known_symbols:
                continue

            if symbol not in unknowns:
                unknowns[symbol] = set()

            unknowns[symbol].add(Dependency(symbol, equation))

    # In case there's anything we haven't taken care of yet, put
    # an empty dependency set in the unknowns.
    for symbol in symbols:
        if symbol not in results and symbol not in unknowns:
            unknowns[symbol] = set()

    return results, unknowns


def as_known(statement):
    symbols = statement.atoms(Symbol)
    if len(symbols) == 1:
        symbol = tuple(symbols)[0]
        solutions = solve_system(statement, symbol)
        if len(solutions) == 1:
            return Eq(symbol, solutions[0])

    return None


class Dependency:
    def __init__(self, symbol, equation):
        self.symbol = symbol
        self.orig_equation = equation

    @property
    def required_symbols(self):
        required = self.orig_equation.atoms(Symbol)
        required.remove(self.symbol)
        return required

    @property
    def lhs(self):
        return self.symbol

    @property
    def rhs(self):
        return solve_system(self.orig_equation, self.symbol)

    @property
    def equations(self):
        lhs = self.lhs
        return [Eq(lhs, rhs) for rhs in self.rhs]

    def __hash__(self):
        return hash((self.symbol, self.orig_equation))

    def __eq__(a, b):
        if type(b) != Dependency:
            return False

        return (a.symbol, b.orig_equation) == (b.symbol, b.orig_equation)

    def __repr__(self):
        return "<Dependency %r>" % tuple(self.required_symbols)
