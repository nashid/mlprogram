import unittest
import ast as python_ast

import nl2code.language.ast as ast

from nl2code.language.python._ast_to_python_ast import to_builtin_type
from nl2code.language.python import to_ast, to_python_ast


class TestToBuiltinType(unittest.TestCase):
    def test_int(self):
        self.assertEqual(10, to_builtin_type("10", "int"))

    def test_bool(self):
        self.assertEqual(True, to_builtin_type("True", "bool"))

    def test_bytes(self):
        self.assertEqual(bytes([10, 10]),
                         to_builtin_type(bytes([10, 10]).decode(), "bytes"))

    def test_None(self):
        self.assertEqual(None, to_builtin_type("None", "NoneType"))


class TestToPythonAST(unittest.TestCase):
    def test_node(self):
        node = python_ast.Expr()
        name = python_ast.Name()
        setattr(name, "id", None)
        setattr(name, "ctx", None)
        setattr(node, "value", name)
        node2 = to_python_ast(to_ast(node))
        self.assertEqual(python_ast.dump(node), python_ast.dump(node2))

    def test_builtin_type(self):
        self.assertEqual(10, to_python_ast(ast.Leaf("int", "10")))
        self.assertEqual(True, to_python_ast(ast.Leaf("bool", "True")))

    def test_variadic_args(self):
        node = python_ast.List()
        n = python_ast.Num()
        s = python_ast.Str()
        setattr(n, "n", 10)
        setattr(s, "s", "foo")
        setattr(node, "elts", [n, s])
        setattr(node, "ctx", None)
        self.assertEqual(
            python_ast.dump(node),
            python_ast.dump(to_python_ast(to_ast(node))))

    def test_optional_arg(self):
        node = python_ast.Yield()
        setattr(node, "value", None)
        self.assertEqual(python_ast.dump(node),
                         python_ast.dump(to_python_ast(to_ast(node))))

    def test_empty_list(self):
        node = python_ast.List()
        setattr(node, "ctx", None)
        setattr(node, "elts", [])
        self.assertEqual(
            python_ast.dump(node),
            python_ast.dump(to_python_ast(to_ast(node))))


if __name__ == "__main__":
    unittest.main()