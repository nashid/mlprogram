import torch
import torch.nn as nn
from typing import Tuple
from nl2prog.nn.utils import rnn
from nl2prog.nn.treegen\
    import NLReader, ASTReader, Decoder, Predictor, Embedding
from nl2prog.encoders import Encoder


class TrainModel(nn.Module):
    def __init__(self, encoder: Encoder,
                 max_query_len: int, max_token_len: int, max_children_num: int,
                 num_heads: int,
                 num_nl_reader_blocks: int, num_ast_reader_blocks: int,
                 num_decoder_blocks: int, hidden_size: int,
                 feature_size: int, dropout: float):
        super(TrainModel, self).__init__()
        self.rule_num = \
            encoder.action_sequence_encoder._rule_encoder.vocab_size
        self.token_num = \
            encoder.action_sequence_encoder._token_encoder.vocab_size
        rule_num = self.rule_num + self.token_num

        self.query_embedding = Embedding(encoder.annotation_encoder.vocab_size,
                                         255, max_token_len, hidden_size,
                                         hidden_size, hidden_size)
        # node_type encoder and token encoder have unkown labels
        type_num = \
            encoder.action_sequence_encoder._node_type_encoder.vocab_size + \
            encoder.action_sequence_encoder._token_encoder.vocab_size + \
            max_query_len - 2
        self.rule_embedding = Embedding(
            rule_num, type_num,
            max_children_num + 1, hidden_size, hidden_size, hidden_size, 0)

        self.nl_reader = NLReader(hidden_size, hidden_size, num_heads, dropout,
                                  num_nl_reader_blocks)
        self.ast_reader = ASTReader(hidden_size, hidden_size, 3, num_heads,
                                    dropout, num_ast_reader_blocks)
        self.decoder = Decoder(feature_size, hidden_size, hidden_size,
                               num_heads, dropout, num_decoder_blocks)
        self.predictor = Predictor(hidden_size, hidden_size, rule_num,
                                   hidden_size)

    def forward(self,
                token_query: rnn.PaddedSequenceWithMask,
                char_query: rnn.PaddedSequenceWithMask,
                previous_action: rnn.PaddedSequenceWithMask,
                rule_previous_action: rnn.PaddedSequenceWithMask,
                depth: rnn.PaddedSequenceWithMask,
                adjacency_matrix: torch.Tensor
                ) -> Tuple[torch.FloatTensor, torch.FloatTensor,
                           torch.FloatTensor]:
        """
        Parameters
        ----------
        token_query: rnn.PaddedSequenceWithMask
            The minibatch of sequences.
            The shape of each sequence is (sequence_length).
        char_query: rnn.PaddedSequenceWithMask
            The minibatch of sequences.
            The shape of each sequence is (sequence_length, max_token_len).
            The padding value should be 0 (null charactor).
        previous_aciton: rnn.PaddedSequenceWithMask
            The previous action sequence.
            The encoded tensor with the shape of
            (len(action_sequence) + 1, 3). Each action will be encoded by
            the tuple of (ID of the applied rule, ID of the inserted token,
            the index of the word copied from the query).
            The padding value should be 0.
        rule_previous_action: rnn.PaddedSequenceWithMask
            The rule of previous action sequence.
            The shape of each sequence is
            (action_length, max_children_num + 1).
        depth: torch.Tensor
            The depth of actions. The shape is (L, B) where L is the sequence
            length, B is the batch size.
        adjacency_matrix: torch.Tensor
            The adjacency matrix. The shape is (B, L, L) where B is the batch
            size, L is the sequence length.

        Returns
        -------
        rule_pred: rnn.PackedSequenceWithMask
            The log probabilities of apply-rule
        token_pred: rnn.PaddedSequenceWithMask
            The log probabilities of gen-token
        copy_pred: rnn.PaddedSequenceWithMask
            The log probabilities of copy-token
        """

        # Embed inputs
        e_token_query, e_char_query = \
            self.query_embedding(token_query.data, char_query.data)
        e_action, e_action_type = \
            self.rule_embedding(previous_action.data,
                                rule_previous_action.data)

        query_features = self.nl_reader(
            rnn.PaddedSequenceWithMask(e_token_query, token_query.mask),
            e_char_query)
        ast_features = self.ast_reader(
            rnn.PaddedSequenceWithMask(e_action, previous_action.mask),
            depth, e_action_type, adjacency_matrix)

        features = self.decoder(
            rnn.PaddedSequenceWithMask(e_action, previous_action.mask),
            query_features, ast_features)
        _rule_prob, copy_prob = self.predictor(features, query_features)
        rule_prob, token_prob = torch.split(_rule_prob.data,
                                            [self.rule_num, self.token_num],
                                            dim=2)
        return rnn.PaddedSequenceWithMask(rule_prob, _rule_prob.mask), \
            rnn.PaddedSequenceWithMask(token_prob, _rule_prob.mask), \
            copy_prob