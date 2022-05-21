from typing import Any, Optional, NamedTuple, TypeVar

from memalloc import MemoryAllocator, MY_OPERATIVE_MEMORY
from sys_exceptions import CustomException, custom_raise


SelfPair = TypeVar("SelfPair", bound="Pair")


class Pair(NamedTuple):
    key: Any
    value: Any

    def __eq__(self, other: SelfPair) -> bool:
        if type(self) != type(other):
            return False
        return self.key == other.key and self.value == other.value


class HashTable:
    DELETED = object()

    def __init__(self, memory: MemoryAllocator, capacity: int = 8, load_factor_threshold: float = 0.6):
        if capacity < 1:
            custom_raise(CustomException("Capacity must be a positive number"))
        if not (0 < load_factor_threshold <= 1):
            custom_raise(CustomException("Load factor must be a number between (0, 1]"))
        self._slots: list[Optional[Pair]] = capacity * [None]
        self.memory: MemoryAllocator = memory
        self._load_factor_threshold = load_factor_threshold

    def set_pair(self, key, value) -> None:
        if self.load_factor >= self._load_factor_threshold:
            self._resize_and_rehash()

        new_pair = Pair(key, value)
        self.memory.allocate(new_pair)
        for index, pair in self._probe(key):
            if pair in (None, self.DELETED) or pair.key == key:
                self._slots[index] = new_pair
                break

    def get(self, key) -> Any:
        for _, pair in self._probe(key):
            if pair is None:
                custom_raise(CustomException(f"No key {key} found"))
            if pair is self.DELETED:
                continue
            if pair.key == key:
                return pair.value
        custom_raise(CustomException(f"No key {key} found"))

    def get_or_default(self, key, default=None) -> Optional[Any]:
        for _, pair in self._probe(key):
            if pair is None:
                return default
            if pair is self.DELETED:
                continue
            if pair.key == key:
                return pair.value
        return default

    def del_pair(self, key) -> None:
        for index, pair in self._probe(key):
            if pair is None:
                custom_raise(CustomException(f"No key {key} found"))
            if pair is self.DELETED:
                continue
            if pair.key == key:
                self.memory.free(self._slots[index])
                self._slots[index] = self.DELETED
                break
        else:
            custom_raise(CustomException(f"No key {key} found"))

    @property
    def values(self):
        return [pair.value for pair in self.pairs]

    @property
    def keys(self):
        return {pair.key for pair in self.pairs}

    @property
    def pairs(self):
        return {pair for pair in self._slots if pair and pair is not self.DELETED}

    def __len__(self):
        return len(self.pairs)

    # PRIVATE

    def index(self, key) -> int:
        return hash(key) % self.size

    def raw_pair(self, key) -> Pair:
        return self._slots[self.index(key)]

    @property
    def size(self) -> int:
        return len(self._slots)

    @property
    def load_factor(self):
        occupied_or_deleted = [slot for slot in self._slots if slot]
        return len(occupied_or_deleted) / self.size

    def __contains__(self, key) -> bool:
        return self.raw_pair(key) is not None

    def __str__(self):
        pairs = []
        for key, value in self.pairs:
            pairs.append(f"{key!r}: {value!r}")
        return "{" + ", ".join(pairs) + "}"

    def __eq__(self, other):
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        return set(self.pairs) == set(other.pairs)

    def _probe(self, key):
        index = self.index(key)
        for _ in range(self.size):
            yield index, self._slots[index]
            index = (index + 1) % self.size

    def _resize_and_rehash(self):
        copy = HashTable(self.memory, self.size * 2)
        for key, value in self.pairs:
            copy.set_pair(key, value)
        for pair in self.pairs:
            self.memory.free(pair)
        self._slots = copy._slots


if __name__ == '__main__':
    m = MemoryAllocator(MY_OPERATIVE_MEMORY)
    hash_table = HashTable(m)
    for i in range(20):
        num_pairs = len(hash_table)
        num_empty = hash_table.size - num_pairs
        print(f"{num_pairs:>2}/{hash_table.size:>2}", ("X" * num_pairs) + ("." * num_empty))
        hash_table.set_pair(i, i)

    # empty hash depends on custom mem alloc
    word_dictionary = HashTable(m)
    print('empty hash', word_dictionary)
    print('memory available', m.memory_size)
    print('filling hash...')
    word_dictionary.set_pair('ananas', 'morgenshtern')
    word_dictionary.set_pair('petrushka', 'kak ukrop no ne sovsem')
    word_dictionary.set_pair('banana', 'rastet na palme')
    word_dictionary.set_pair('persik', 'vahhh kakoy')
    print('memory available', m.memory_size)
    print('filled hash', word_dictionary)
    print('deleting banana')
    word_dictionary.del_pair('banana')
    print('bananaless hash', word_dictionary)
    print('memory available', m.memory_size)
