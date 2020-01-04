import ast as python_ast
import transpyle
from enum import Enum
from typing import Union
from nl2prog.language.ast import AST
from .python_ast_to_ast import to_ast
from .ast_to_python_ast import to_python_ast


class ParseMode(Enum):
    Single = 1
    Eval = 2
    Exec = 3


def parse(code: str, mode: ParseMode = ParseMode.Single) -> Union[AST, None]:
    try:
        past = python_ast.parse(code)
        if mode == ParseMode.Exec:
            return to_ast(past)
        else:
            return to_ast(past.body[0])
    except:  # noqa
        return None


def unparse(ast: AST) -> Union[str, None]:
    unparser = transpyle.python.unparser.NativePythonUnparser()

    try:
        return unparser.unparse(to_python_ast(ast))
    except:  # noqa
        return None
