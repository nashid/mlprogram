import unittest
import numpy as np
from mlprogram.languages.csg import show, Shape, Interpreter
from mlprogram.languages.csg \
    import Circle, Rectangle, Translation, Rotation, Union, Difference


class TestShow(unittest.TestCase):
    def test_str(self):
        c = np.zeros((3, 3), dtype=np.bool)
        self.assertEqual("   \n   \n   \n", show(c))
        c = np.eye(3, dtype=np.bool)
        self.assertEqual("#  \n # \n  #\n", show(c))


class TestShape(unittest.TestCase):
    def test_render(self):
        shape = Shape(lambda x, y: x * y == 0)
        self.assertEqual(" # \n###\n # \n", show(shape.render(3, 3)))
        self.assertEqual("  \n  \n", show(shape.render(2, 2)))

    def test_render_with_resolution(self):
        shape = Shape(lambda x, y: abs(x * y) < 0.5)
        self.assertEqual(" # \n###\n # \n", show(shape.render(3, 3, 1)))
        self.assertEqual("  ##  \n  ##  \n######\n######\n  ##  \n  ##  \n",
                         show(shape.render(3, 3, 2)))
        self.assertEqual("      \n      \n  ##  \n  ##  \n      \n      \n",
                         show(shape.render(6, 6, 1)))


class TestInterpreter(unittest.TestCase):
    def test_circle(self):
        self.assertEqual(
            "#\n",
            show(Interpreter(1, 1, 1).eval(Circle(1))))

    def test_rectangle(self):
        code = Rectangle(1, 3)
        self.assertEqual(
            " # \n # \n # \n",
            show(Interpreter(3, 3, 1).eval(code)))

    def test_translation(self):
        code = Translation(2, 1, Rectangle(1, 3))
        self.assertEqual(
            "    #\n    #\n    #\n     \n     \n",
            show(Interpreter(5, 5, 1).eval(code)))

    def test_rotation(self):
        code = Rotation(45, Rectangle(4, 1))
        self.assertEqual(
            "  #\n # \n#  \n",
            show(Interpreter(3, 3, 1).eval(code)))

    def test_union(self):
        code = Union(Rectangle(3, 1), Rectangle(1, 3))
        self.assertEqual(
            " # \n###\n # \n",
            show(Interpreter(3, 3, 1).eval(code)))

    def test_difference(self):
        code = Difference(Rectangle(1, 1), Rectangle(3, 1))
        self.assertEqual(
            "   \n# #\n   \n",
            show(Interpreter(3, 3, 1).eval(code)))


if __name__ == "__main__":
    unittest.main()
