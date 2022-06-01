from memalloc import MemoryAllocator
from sys_exceptions import CustomException, custom_raise

SYSTEM_MEMORY = 1024


class Collection:
    def __init__(self, memory: MemoryAllocator):
        self.elements = []
        self.memory: MemoryAllocator = memory

    def __str__(self):
        return str(self.elements)

    def _out_of_elements_alert(self):
        if not self.elements:
            custom_raise(CustomException(1, 'Collection out of elements'))


class Stack(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self.elements.pop()
        self.memory.free(element)
        return element


class Deck(Collection):
    def push_first(self, element):
        self.memory.allocate(element)
        self.elements.insert(0, element)

    def pop_first(self):
        self._out_of_elements_alert()

        element = self.elements.pop(0)
        self.memory.free(element)
        return element

    def push_last(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop_last(self):
        self._out_of_elements_alert()

        element = self.elements.pop()
        self.memory.free(element)
        return element


class Queue(Collection):
    def push(self, element):
        self.memory.allocate(element)
        self.elements.append(element)

    def pop(self):
        self._out_of_elements_alert()

        element = self.elements.pop(0)
        self.memory.free(element)
        return element
