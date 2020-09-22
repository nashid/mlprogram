import torch
from typing \
    import TypeVar, Generic, Generator, Optional, List, Callable, Any, Tuple
from mlprogram.samplers import SamplerState, Sampler, DuplicatedSamplerState
from mlprogram.utils.data import Collate
from mlprogram.utils import logging

logger = logging.Logger(__name__)

Input = TypeVar("Input")
Output = TypeVar("Output")
State = TypeVar("State")


class SamplerWithValueNetwork(Sampler[Input, Output, State],
                              Generic[Input, Output, State]):
    def __init__(self,
                 sampler: Sampler[Input, Output, State],
                 transform: Callable[[State], Any],
                 collate: Collate,
                 value_network: torch.nn.Module,
                 batch_size: int = 1):
        self.sampler = sampler
        self.transform = transform
        self.collate = collate
        self.value_network = value_network
        self.batch_size = batch_size

    @logger.function_block("initialize")
    def initialize(self, input: Input) -> State:
        return self.sampler.initialize(input)

    def create_output(self, input, state: State) \
            -> Optional[Tuple[Output, bool]]:
        return self.sampler.create_output(input, state)

    def batch_k_samples(self, states: List[SamplerState[State]],
                        ks: List[int]) \
            -> Generator[DuplicatedSamplerState[State],
                         None, None]:
        with logger.block("batch_k_samples"):
            self.value_network.eval()
            outputs = []
            value_network_inputs = []
            for state in self.sampler.batch_k_samples(states, ks):
                input = self.transform(state.state.state)
                outputs.append(state)
                value_network_inputs.append(input)
                if len(outputs) == self.batch_size:
                    with torch.no_grad(), logger.block("calculate_value"):
                        value = self.value_network(
                            self.collate(value_network_inputs))
                    for value, output in zip(value, outputs):
                        yield DuplicatedSamplerState(
                            SamplerState(value.item(), output.state.state),
                            output.num)
                    outputs = []
                    value_network_inputs = []
            if len(outputs) != 0:
                with torch.no_grad(), logger.block("calculate_value"):
                    value = self.value_network(
                        self.collate(value_network_inputs))
                for value, output in zip(value, outputs):
                    yield DuplicatedSamplerState(
                        SamplerState(value.item(), output.state.state),
                        output.num)