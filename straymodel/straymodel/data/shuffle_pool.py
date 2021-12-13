
import torch
import warnings
import numpy as np

class ShufflePool(torch.utils.data.IterableDataset):
    def __init__(self, dataset, pool_size):
        self.dataset = dataset
        self.pool_size = pool_size

    def __iter__(self):
        iterator = iter(self.dataset)
        pool = []
        try:
            for _ in range(self.pool_size):
                pool.append(next(iterator))
        except StopIteration:
            warnings.warn(f"There are less examples than the pool size {self.pool_size}")

        while len(pool) > 0:
            index = np.random.randint(len(pool))
            try:
                item = pool[index]
                pool[index] = next(iterator)
                yield item
            except StopIteration:
                yield pool.pop(index)