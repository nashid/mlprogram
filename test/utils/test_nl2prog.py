import unittest
from mlprogram.metrics import Accuracy
from mlprogram.utils.nl2prog import evaluate, Result
from mlprogram.utils.data import ListDataset
from mlprogram.decoders import Result as DecoderResult


class TestEvaluate(unittest.TestCase):
    def test_simple_case(self):
        def encode(query):
            if query == "query0":
                return {"output": ["c0", "c1", "c2"]}
            elif query == "query1":
                return {"output": ["c2", "c3", "c0"]}
            else:
                return {"output": ["c2", "c3", "c5"]}

        def synthesize(state):
            for i, s in enumerate(state["output"]):
                yield DecoderResult(s, -i)

        accuracy = Accuracy(str, str)
        dataset = \
            ListDataset([{
                "query": ["query0", "query1", "query2"],
                "ground_truth": ["c0", "c1", "c4"]
            }])
        results = evaluate(dataset, encode, synthesize,
                           metrics={"accuracy": accuracy})

        self.assertEqual(
            results.metrics,
            {1: {"accuracy": 1.0 / 3}, 3: {"accuracy": 2.0 / 3}})
        self.assertEqual(3, len(results.results))
        self.assertEqual(
            Result("query0", ["c0", "c1", "c4"], ["c0", "c1", "c2"],
                   {1: {"accuracy": 1.0}, 3: {"accuracy": 1.0}}),
            results.results[0])
        self.assertEqual(
            Result("query1", ["c0", "c1", "c4"], ["c2", "c3", "c0"],
                   {1: {"accuracy": 0.0}, 3: {"accuracy": 1.0}}),
            results.results[1])
        self.assertEqual(
            Result("query2", ["c0", "c1", "c4"], ["c2", "c3", "c5"],
                   {1: {"accuracy": 0.0}, 3: {"accuracy": 0.0}}),
            results.results[2])


if __name__ == "__main__":
    unittest.main()
