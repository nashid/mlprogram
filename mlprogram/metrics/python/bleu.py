from typing import Dict, Any, List
from mlprogram.metrics import Metric
import re
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction


class Bleu(Metric[str]):
    def __call__(self, input: Dict[str, Any], value: str) -> float:
        gts = input["ground_truth"]
        sm = SmoothingFunction()

        def tokenize(code: str) -> List[str]:
            code = re.sub(r'([^A-Za-z0-9_])', r' \1 ', code)
            code = re.sub(r'([a-z])([A-Z])', r'\1 \2', code)
            code = re.sub(r'\s+', ' ', code)
            code = re.sub(r'["\']', '`', code)
            tokens = [t for t in code.split(' ') if t]
            return tokens

        ref = [tokenize(ref) for ref in gts]
        cand = tokenize(value)
        return sentence_bleu(ref,
                             cand,
                             weights=[0.25] * min(4, len(ref)),
                             smoothing_function=sm.method3)
