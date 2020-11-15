from mlprogram import Environment
from mlprogram.languages import BatchedState, Kinds, Lexer, Token
from mlprogram.languages.linediff import (
    AddTestCases,
    Diff,
    Expander,
    Interpreter,
    IsSubtype,
    Parser,
    Remove,
    Replace,
    ToEpisode,
    UpdateInput,
    get_samples,
)


class MockLexer(Lexer):
    def tokenize(self, code):
        return [Token(None, code, code)]


class TestIsSubType(object):
    def test_happy_path(self):
        assert IsSubtype()("Delta", "Delta")
        assert IsSubtype()("Insert", "Delta")
        assert IsSubtype()("Delta", "Delta")
        assert IsSubtype()("str", "value")
        assert not IsSubtype()(Kinds.LineNumber(), "value")


class TestGetSamples(object):
    def test_happy_path(self):
        samples = get_samples(Parser(MockLexer()))
        assert len(samples.rules) == 5
        assert len(samples.tokens) == 0


class TestToEpisode(object):
    def test_happy_path(self):
        to_episode = ToEpisode(Interpreter(), Expander())
        episode = to_episode(Environment(
            inputs={"test_cases": [("xxx\nyyy", None)]},
            supervisions={"ground_truth": Diff([Replace(0, "zzz"), Remove(1)])}
        ))
        assert len(episode) == 2
        assert episode[0].inputs["test_cases"] == [("xxx\nyyy", "zzz\nyyy")]
        assert episode[1].inputs["test_cases"] == [("zzz\nyyy", "zzz")]


class TestAddTestCases(object):
    def test_happy_path(self):
        f = AddTestCases()
        entry = f(Environment(
            inputs={"code": "xxx\nyyy"},
        ))
        assert entry.inputs["test_cases"] == [("xxx\nyyy", None)]


class TestUpdateInput(object):
    def test_happy_path(self):
        f = UpdateInput()
        entry = f(Environment(
            inputs={"test_cases": [("xxx\nyyy", None)]},
        ))
        assert entry.inputs["code"] == "xxx\nyyy"
        assert entry.inputs["text_query"] == "xxx\nyyy"
        state = BatchedState({}, {Diff([]): ["foo"]}, [Diff([])])
        entry = f(Environment(
            states={"interpreter_state": state},
        ))
        assert entry.inputs["code"] == "foo"
        assert entry.inputs["text_query"] == "foo"
