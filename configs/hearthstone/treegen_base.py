imports = ["../treegen/base.py"]
params = {
    "word_threshold": 3,
    "token_threshold": 0,
    "max_word_length": 128,
    "max_arity": 128,
    "max_tree_depth": 128,
    "char_embedding_size": 256,
    "rule_embedding_size": 256,
    "hidden_size": 256,
    "decoder_hidden_size": 1024,
    "tree_conv_kernel_size": 3,
    "n_head": 1,
    "n_block": 6,
    "dropout": 0.15,
    "batch_size": 1,
    "n_epoch": 25,
    "eval_interval": 10,
    "snapshot_interval": 1,
    "beam_size": 15,
    "max_step_size": 250,
    "metric_top_n": [1],
    "metric_threshold": 1.0,
    "metric": "bleu@1",
    "n_evaluate_process": 2,
}
parser = mlprogram.languages.python.Parser(
    split_value=mlprogram.datasets.hearthstone.SplitValue(),
)
extract_reference = mlprogram.datasets.hearthstone.TokenizeQuery()
is_subtype = mlprogram.languages.python.IsSubtype()
dataset = mlprogram.datasets.hearthstone.download()
metrics = {
    "accuracy": mlprogram.metrics.Accuracy(),
    "bleu": mlprogram.languages.python.metrics.Bleu(),
}