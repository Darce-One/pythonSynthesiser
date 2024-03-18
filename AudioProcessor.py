from typing import List
from Generators import SinGen

class AudioProcessor():
    def __init__(self, sample_rate: int, block_size: int) -> None:
        self.left_channel: List[float] = []
        self.right_channel: List[float] = []
        self.sample_rate: int = sample_rate
        self.block_size: int = block_size



    def prepare_to_play(self) -> None:
        self.sin_gen = SinGen(440, 0.1, self.sample_rate)

    def process_block(self) -> None:
        for i in range(self.block_size):
            sample = self.sin_gen.process()
            self.left_channel.append(sample)
            self.right_channel.append(sample)

    def get_right_channel(self) -> List[float]:
        return self.right_channel

    def get_left_channel(self) -> List[float]:
        return self.left_channel
