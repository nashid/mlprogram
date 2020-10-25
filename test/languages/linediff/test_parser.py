from mlprogram.languages import Lexer
from mlprogram.languages import Token
from mlprogram.languages import TokenSequence
from mlprogram.languages import Sugar as S
from mlprogram.languages.linediff import Parser
from mlprogram.languages.linediff import Diff
from mlprogram.languages.linediff import Insert
from mlprogram.languages.linediff import Remove
from mlprogram.languages.linediff import Replace


class MockLexer(Lexer):
    def tokenize(self, value):
        if value == "":
            return None
        return TokenSequence([(-1, Token(None, v, v))
                              for v in value.split(" ")])

    def untokenize(self, value):
        if len(value.tokens) == 0:
            return None
        return " ".join([x.raw_value for _, x in value.tokens])


class TestParser(object):
    def test_parse(self):
        parser = Parser(MockLexer())
        assert parser.parse(Insert(0, "foo bar")) == \
            S.node("Insert", line_number=("int", S.leaf("int", 0)),
                   value=("str", [S.leaf("str", "foo"), S.leaf("str", "bar")]))
        assert parser.parse(Insert(0, "")) is None
        assert parser.parse(Remove(0)) == \
            S.node("Remove", line_number=("int", S.leaf("int", 0)))
        assert parser.parse(Replace(0, "foo bar")) == \
            S.node("Replace", line_number=("int", S.leaf("int", 0)),
                   value=("str", [S.leaf("str", "foo"), S.leaf("str", "bar")]))
        assert parser.parse(Replace(0, "")) is None
        assert parser.parse(Diff([Remove(0)])) == \
            S.node("Diff",
                   deltas=("Delta",
                           [S.node("Remove",
                                   line_number=("int", S.leaf("int", 0)))]))
        assert parser.parse(Diff([Replace(0, "")])) is None

    def test_unparse(self):
        parser = Parser(MockLexer())
        assert parser.unparse(parser.parse(Insert(0, "foo bar"))) == \
            Insert(0, "foo bar")
        assert parser.unparse(S.node("Insert",
                                     line_number=("int", S.leaf("int", 0)),
                                     value=("str", []))) is None
        assert parser.unparse(parser.parse(Remove(0))) == Remove(0)
        assert parser.unparse(parser.parse(Replace(0, "foo bar"))) == \
            Replace(0, "foo bar")
        assert parser.unparse(S.node("Replace",
                                     line_number=("int", S.leaf("int", 0)),
                                     value=("str", []))) is None
        assert parser.unparse(parser.parse(Diff([Remove(0)]))) == \
            Diff([Remove(0)])
        assert parser.unparse(
            S.node("Diff",
                   deltas=("Delta", [
                       S.node("Replace",
                              line_number=("int", S.leaf("int", 0)),
                              value=("str", []))]))) is None
