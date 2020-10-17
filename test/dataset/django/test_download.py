import tempfile
import os
from mlprogram import Environment
from mlprogram.datasets.django import download


class TestDownload(object):
    def test_download(self):
        values = ["line0\nline1\nline2\n", "x = 10\nif True:\nelse:\n"]

        def get(path):
            return values.pop(0)
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "path.pt")
            dataset = download(cache_path=cache_path, get=get, num_train=1,
                               num_test=1)
        train_dataset = dataset["train"]
        test_dataset = dataset["test"]
        valid_dataset = dataset["valid"]

        assert 1 == len(train_dataset)
        assert train_dataset[0] == Environment(
            inputs={"input": "line0"},
            supervisions={"ground_truth": "x = 10"}
        )

        assert 1 == len(test_dataset)
        assert test_dataset[0] == Environment(
            inputs={"input": "line1"},
            supervisions={"ground_truth": "if True:"}
        )

        assert 1 == len(valid_dataset)
        assert valid_dataset[0] == Environment(
            inputs={"input": "line2"},
            supervisions={"ground_truth": "else:"}
        )

    def test_cache(self):
        values = ["line0\nline1\nline2\n", "x = 10\nif True:\nelse:\n"]

        def get(path):
            return values.pop(0)

        def get2(path):
            raise NotImplementedError
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_path = os.path.join(tmpdir, "path.pt")
            dataset0 = download(cache_path=cache_path, get=get, num_train=1,
                                num_test=1)
            dataset1 = download(cache_path=cache_path, get=get2, num_train=2,
                                num_test=0)
        assert list(dataset0["train"]) + list(dataset0["test"]) == \
            list(dataset1["train"])
        assert list(dataset0["valid"]) == list(dataset1["valid"])
