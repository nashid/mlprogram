import torch
import unittest
import numpy as np

from nl2prog.language.action \
    import ExpandTreeRule, NodeType, NodeConstraint, CloseNode, \
    ApplyRule, GenerateToken, ActionOptions
from nl2prog.language.evaluator import Evaluator
from nl2prog.encoders import ActionSequenceEncoder


class TestEncoder(unittest.TestCase):
    def test_reserved_labels(self):
        encoder = ActionSequenceEncoder([], [], [], 0)
        self.assertEqual(2, len(encoder._rule_encoder.vocab))
        self.assertEqual(2, len(encoder._token_encoder.vocab))

        encoder = ActionSequenceEncoder(
            [], [], [], 0, ActionOptions(False, True))
        self.assertEqual(1, len(encoder._rule_encoder.vocab))
        self.assertEqual(2, len(encoder._token_encoder.vocab))

        encoder = ActionSequenceEncoder(
            [], [], [], 0, ActionOptions(True, False))
        self.assertEqual(2, len(encoder._rule_encoder.vocab))
        self.assertEqual(1, len(encoder._token_encoder.vocab))

    def test_encode_action(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f", "2"],
            0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(funcdef))
        evaluator.eval(GenerateToken("f"))
        evaluator.eval(GenerateToken("1"))
        evaluator.eval(GenerateToken("2"))
        evaluator.eval(GenerateToken(CloseNode()))
        action = encoder.encode_action(evaluator, ["1", "2"])

        self.assertTrue(np.array_equal(
            [
                [-1, 2, -1, -1],
                [2, -1, 2, -1],
                [2, -1, -1, 0],
                [2, -1, 3, 1],
                [2, -1, 1, -1],
                [3, -1, -1, -1]
            ],
            action.numpy()
        ))

    def test_encode_parent(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f", "2"],
            0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(funcdef))
        evaluator.eval(GenerateToken("f"))
        evaluator.eval(GenerateToken("1"))
        evaluator.eval(GenerateToken("2"))
        evaluator.eval(GenerateToken(CloseNode()))
        parent = encoder.encode_parent(evaluator)

        self.assertTrue(np.array_equal(
            [
                [-1, -1, -1, -1],
                [1, 2, 0, 0],
                [1, 2, 0, 0],
                [1, 2, 0, 0],
                [1, 2, 0, 0],
                [1, 2, 0, 1]
            ],
            parent.numpy()
        ))

    def test_encode_tree(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f", "2"],
            0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(funcdef))
        evaluator.eval(GenerateToken("f"))
        evaluator.eval(GenerateToken("1"))
        d, m = encoder.encode_tree(evaluator)

        self.assertTrue(np.array_equal(
            [[0], [1], [1]], d.numpy()
        ))
        self.assertTrue(np.array_equal(
            [[0, 1, 1], [0, 0, 0], [0, 0, 0]],
            m.numpy()
        ))

    def test_encode_empty_sequence(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f"],
            0)
        evaluator = Evaluator()
        action = encoder.encode_action(evaluator, ["1"])
        parent = encoder.encode_parent(evaluator)
        d, m = encoder.encode_tree(evaluator)

        self.assertTrue(np.array_equal(
            [
                [-1, -1, -1, -1]
            ],
            action.numpy()
        ))
        self.assertTrue(np.array_equal(
            [
                [-1, -1, -1, -1]
            ],
            parent.numpy()
        ))
        self.assertTrue(np.array_equal(np.zeros((0, 1)), d.numpy()))
        self.assertTrue(np.array_equal(np.zeros((0, 0)), m.numpy()))

    def test_encode_invalid_sequence(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f"],
            0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(funcdef))
        evaluator.eval(GenerateToken("f"))
        evaluator.eval(GenerateToken("1"))
        evaluator.eval(GenerateToken(CloseNode()))

        self.assertEqual(None, encoder.encode_action(evaluator, ["2"]))

    def test_encode_completed_sequence(self):
        none = ExpandTreeRule(NodeType("value", NodeConstraint.Node),
                              [])
        encoder = ActionSequenceEncoder([none],
                                        [NodeType(
                                            "value", NodeConstraint.Node)],
                                        ["f"],
                                        0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(none))
        action = encoder.encode_action(evaluator, ["1"])
        parent = encoder.encode_parent(evaluator)

        self.assertTrue(np.array_equal(
            [
                [-1, 2, -1, -1],
                [-1, -1, -1, -1]
            ],
            action.numpy()
        ))
        self.assertTrue(np.array_equal(
            [
                [-1, -1, -1, -1],
                [-1, -1, -1, -1]
            ],
            parent.numpy()
        ))

    def test_decode(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f"],
            0)
        evaluator = Evaluator()
        evaluator.eval(ApplyRule(funcdef))
        evaluator.eval(GenerateToken("f"))
        evaluator.eval(GenerateToken("1"))
        evaluator.eval(GenerateToken(CloseNode()))

        result = encoder.decode(encoder.encode_action(
            evaluator, ["1"])[:-1, 1:], ["1"])
        self.assertEqual(evaluator.action_sequence, result)

    def test_decode_invalid_tensor(self):
        funcdef = ExpandTreeRule(NodeType("def", NodeConstraint.Node),
                                 [("name",
                                   NodeType("value", NodeConstraint.Token)),
                                  ("body",
                                   NodeType("expr", NodeConstraint.Variadic))])
        expr = ExpandTreeRule(NodeType("expr", NodeConstraint.Node),
                              [("op", NodeType("value", NodeConstraint.Token)),
                               ("arg0",
                                NodeType("value", NodeConstraint.Token)),
                               ("arg1",
                                NodeType("value", NodeConstraint.Token))])

        encoder = ActionSequenceEncoder(
            [funcdef, expr],
            [NodeType("def", NodeConstraint.Node),
             NodeType(
                "value", NodeConstraint.Token),
             NodeType("expr", NodeConstraint.Node)],
            ["f"],
            0)
        self.assertEqual(None,
                         encoder.decode(torch.LongTensor([[-1, -1, -1]]), []))
        self.assertEqual(None,
                         encoder.decode(torch.LongTensor([[-1, -1, 1]]), []))

    def test_remove_variadic_node_types(self):
        self.assertEqual(
            [NodeType("t1", NodeConstraint.Node),
             NodeType("t2", NodeConstraint.Token)],
            ActionSequenceEncoder.remove_variadic_node_types(
                [NodeType("t1", NodeConstraint.Node),
                 NodeType("t2", NodeConstraint.Token)]))
        self.assertEqual(
            [NodeType("t1", NodeConstraint.Node),
             NodeType("t2", NodeConstraint.Token)],
            ActionSequenceEncoder.remove_variadic_node_types(
                [NodeType("t1", NodeConstraint.Variadic),
                 NodeType("t2", NodeConstraint.Token)]))
        self.assertEqual(
            [NodeType("t1", NodeConstraint.Node),
             NodeType("t2", NodeConstraint.Token)],
            ActionSequenceEncoder.remove_variadic_node_types(
                [NodeType("t1", NodeConstraint.Variadic),
                 NodeType("t2", NodeConstraint.Token),
                 NodeType("t1", NodeConstraint.Node)]))


if __name__ == "__main__":
    unittest.main()