import numpy as np
import logging

from torch.utils import data
from torch.utils.data import IterableDataset
from typing import Optional, Any, Tuple, Dict, List

from mlprogram.utils import Reference as R
from mlprogram.languages.csg import AST, Reference
from mlprogram.languages.csg import Circle, Rectangle
from mlprogram.languages.csg import Translation, Rotation
from mlprogram.languages.csg import Union, Difference


logger = logging.getLogger(__name__)


class Dataset(IterableDataset):
    def __init__(
            self, canvas_size: int,
            depth: int, length_stride: int,
            degree_stride: int,
            reference: bool = False,
            seed: Optional[int] = None):
        self.canvas_size = canvas_size
        self.depth = depth
        s = self.canvas_size // 2
        self.reference = reference
        self.size_candidates = \
            list(range(1, s + 1))[::length_stride]
        self.length_candidates = list(range(-s, s + 1))[::length_stride]
        self.degree_candidates = list(range(-180, 180))[::degree_stride]
        self.leaf_candidates = ["Circle", "Rectangle"]
        self.node_candidates = ["Translation", "Rotation",
                                "Union", "Difference"]
        self.seed = seed if seed is not None else 0

    def sample_ast(self, rng: np.random.RandomState, depth: int) -> AST:
        if depth == 1:
            t = rng.choice(self.leaf_candidates)
            if t == "Circle":
                return Circle(rng.choice(self.size_candidates))
            elif t == "Rectangle":
                return Rectangle(rng.choice(self.size_candidates),
                                 rng.choice(self.size_candidates))
            else:
                raise Exception(f"Invalid type: {t}")
        else:
            t = rng.choice(self.node_candidates)
            if t == "Translation":
                return Translation(rng.choice(self.length_candidates),
                                   rng.choice(self.length_candidates),
                                   self.sample_ast(rng, depth - 1))
            elif t == "Rotation":
                return Rotation(rng.choice(self.degree_candidates),
                                self.sample_ast(rng, depth - 1))
            elif t == "Union":
                if rng.choice([True, False]):
                    return Union(self.sample_ast(rng, depth - 1),
                                 self.sample_ast(rng, rng.randint(1, depth)))
                else:
                    return Union(self.sample_ast(rng, rng.randint(1, depth)),
                                 self.sample_ast(rng, depth - 1))
            elif t == "Difference":
                if rng.choice([True, False]):
                    return Difference(self.sample_ast(rng, depth - 1),
                                      self.sample_ast(rng,
                                                      rng.randint(1, depth)))
                else:
                    return Difference(self.sample_ast(rng,
                                                      rng.randint(1, depth)),
                                      self.sample_ast(rng, depth - 1))
            else:
                raise Exception(f"Invalid type: {t}")

    def to_reference(self, code: AST, n_ref: int = 0) \
            -> Tuple[List[Tuple[R, AST]], int]:
        if isinstance(code, Circle):
            return [(R(str(n_ref)), code)], n_ref
        elif isinstance(code, Rectangle):
            return [(R(str(n_ref)), code)], n_ref
        elif isinstance(code, Translation):
            retval, n_ref = self.to_reference(code.child, n_ref)
            retval.append((
                R(str(n_ref + 1)),
                Translation(code.x, code.y,
                            Reference(R(str(n_ref))))
            ))
            return retval, n_ref + 1
        elif isinstance(code, Rotation):
            retval, n_ref = self.to_reference(code.child, n_ref)
            retval.append((
                R(str(n_ref + 1)),
                Rotation(code.theta_degree,
                         Reference(R(str(n_ref))))
            ))
            return retval, n_ref + 1
        elif isinstance(code, Union):
            retval0, n_ref0 = self.to_reference(code.a, n_ref)
            retval1, n_ref1 = self.to_reference(code.b, n_ref0 + 1)
            retval0.extend(retval1)
            retval0.append((
                R(str(n_ref1 + 1)),
                Union(Reference(R(str(n_ref0))),
                      Reference(R(str(n_ref1))))
            ))
            return retval0, n_ref1 + 1
        elif isinstance(code, Difference):
            retval0, n_ref0 = self.to_reference(code.a, n_ref)
            retval1, n_ref1 = self.to_reference(code.b, n_ref0 + 1)
            retval0.extend(retval1)
            retval0.append((
                R(str(n_ref1 + 1)),
                Difference(Reference(R(str(n_ref0))),
                           Reference(R(str(n_ref1))))
            ))
            return retval0, n_ref1 + 1
        logger.warning(f"Invalid node type {code.type_name()}")
        return [], -1

    def __iter__(self):
        worker_info = data.get_worker_info()
        if worker_info is None:
            seed = self.seed
        else:
            seed = self.seed + worker_info.id
        rng = np.random.RandomState(seed)

        class InternalIterator:
            def __init__(self, parent: Dataset):
                self.parent = parent
                self.depth_prob = [1 << d for d in range(self.parent.depth)]
                self.depth_prob = \
                    [p / sum(self.depth_prob) for p in self.depth_prob]

            def __next__(self) -> Any:
                depth = rng.multinomial(1, self.depth_prob).nonzero()[0] + 1
                ast = self.parent.sample_ast(rng, depth)
                if self.parent.reference:
                    refs, output = self.parent.to_reference(ast)
                    retval: Dict[str, Any] = {
                        "ground_truth": [refs]
                    }
                else:
                    retval = {
                        "ground_truth": [ast]
                    }
                return retval

        return InternalIterator(self)
