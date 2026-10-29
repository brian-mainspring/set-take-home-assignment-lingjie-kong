import random


class SensorGenerator:
    """
    Simulates an environmental input signal via a bounded random walk.

    Each call to next() nudges the value by a random amount within step_range
    and clamps the result to [min_value, max_value]. Passing a controlled
    SensorGenerator in tests gives peripheral controllers deterministic inputs,
    making it straightforward to verify their actuation logic in isolation.
    """

    def __init__(self, initial_value, min_value, max_value, step_range):
        self._value = initial_value
        self._min = min_value
        self._max = max_value
        self._step_range = step_range

    def next(self):
        self._value += random.uniform(-self._step_range, self._step_range)
        self._value = max(self._min, min(self._max, self._value))
        return self._value

    @property
    def value(self):
        return self._value
