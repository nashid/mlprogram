import numpy as np
from torchnlp.encoders import LabelEncoder

from mlprogram import Environment
from mlprogram.languages import Token
from mlprogram.utils.transform.text import (
    EncodeCharacterQuery,
    EncodeWordQuery,
    ExtractReference,
)


class TestExtractReference(object):
    def test_happy_path(self):
        def tokenize(value: str):
            return [Token(None, value + "dnn", value)]

        transform = ExtractReference(tokenize)
        result = transform(Environment(inputs={"text_query": ""}))
        assert [Token(None, "dnn", "")] == result.states["reference"]


class TestEncodeWordQuery(object):
    def test_happy_path(self):
        transform = EncodeWordQuery(LabelEncoder(["dnn"]))
        result = transform(Environment(
            states={"reference": [Token(None, "dnn", "")]}
        ))
        assert [1] == result.states["word_nl_query"].numpy().tolist()


class TestEncodeCharacterQuery(object):
    def test_simple_case(self):
        cencoder = LabelEncoder(["a", "b", "t", "e"], 0)
        transform = EncodeCharacterQuery(cencoder, 3)
        result = transform(Environment(
            states={"reference": [
                Token(None, "ab", "ab"),
                Token(None, "test", "test")
            ]}
        ))
        char_query = result.states["char_nl_query"]
        assert np.array_equal([[1, 2, -1], [3, 4, 0]],
                              char_query.numpy())
