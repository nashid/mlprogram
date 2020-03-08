import torch
import numpy as np
from typing import Callable, List, Any, Optional, Tuple, Union
from torchnlp.encoders import LabelEncoder

from nl2prog.language.evaluator import Evaluator
from nl2prog.encoders import ActionSequenceEncoder
from nl2prog.utils import Query


class TransformQuery:
    def __init__(self, tokenize_query: Callable[[str], Query],
                 word_encoder: LabelEncoder, char_encoder: LabelEncoder,
                 max_word_length):
        self.tokenize_query = tokenize_query
        self.word_encoder = word_encoder
        self.char_encoder = char_encoder
        self.max_word_length = max_word_length

    def __call__(self, query: Union[str, List[str]]) -> Tuple[List[str], Any]:
        if isinstance(query, str):
            query = self.tokenize_query(query)
        else:
            q = Query([], [])
            for word in query:
                q2 = self.tokenize_query(word)
                q.query_for_dnn.extend(q2.query_for_dnn)
                q.query_for_synth.extend(q2.query_for_synth)
            query = q

        word_query = self.word_encoder.batch_encode(query.query_for_dnn)
        char_query = \
            torch.ones(len(query.query_for_dnn), self.max_word_length).long() \
            * -1
        for i, word in enumerate(query.query_for_dnn):
            chars = self.char_encoder.batch_encode(word)
            length = min(self.max_word_length, len(chars))
            char_query[i, :length] = \
                self.char_encoder.batch_encode(word)[:length]
        return query.query_for_synth, (word_query, char_query)


class TransformEvaluator:
    def __init__(self,
                 action_sequence_encoder: ActionSequenceEncoder,
                 max_arity: int, train: bool = True):
        self.action_sequence_encoder = action_sequence_encoder
        self.max_arity = max_arity
        self.train = train

    def __call__(self, evaluator: Evaluator, query_for_synth: List[str]) \
            -> Optional[Tuple[Tuple[torch.Tensor, torch.Tensor, torch.Tensor,
                                    torch.Tensor], torch.Tensor]]:
        a = self.action_sequence_encoder.encode_action(evaluator,
                                                       query_for_synth)
        rule_prev_action = \
            self.action_sequence_encoder.encode_each_action(
                evaluator, query_for_synth, self.max_arity)
        depth, matrix = self.action_sequence_encoder.encode_tree(evaluator)
        if a is None:
            return None
        if self.train:
            if np.any(a[-1, :].numpy() != -1):
                return None
            prev_action = a[:-2, 1:]
            rule_prev_action = rule_prev_action[:-1]
            depth = depth[:-1]
            matrix = matrix[:-1, :-1]
        else:
            prev_action = a[:-1, 1:]
            rule_prev_action = \
                self.action_sequence_encoder.encode_each_action(
                    evaluator, query_for_synth, self.max_arity)

        return (prev_action, rule_prev_action, depth, matrix), prev_action
