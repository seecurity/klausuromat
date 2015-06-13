import math

from .binary import BinaryOperation


# Modulo: [c = ]a % b
class Modulo(BinaryOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Set filters
        self._filters = {
            BinaryOperation.OperatorSide.ASSIGN: self._filter.is_number,
            BinaryOperation.OperatorSide.LEFT: self._filter.is_integer,
            BinaryOperation.OperatorSide.RIGHT: (self._filter.is_integer, self._filter.is_number_non_zero)
        }

        # Set fallback numbers
        self._fallback = {
            BinaryOperation.OperatorSide.LEFT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE'])),
            BinaryOperation.OperatorSide.RIGHT: [x for x in range(*self._settings['IDENTIFIER_VALUE_RANGE']) if x != 0]
        }

    # Calculate
    def calculate(self, left, right):
        return math.fmod(left, right)
