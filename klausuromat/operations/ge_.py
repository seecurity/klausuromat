# Internals
from .binary import BinaryOperation


# Greater than (or equal): [c = ]a >= b
class GreaterThanOrEqual(BinaryOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Set filters
        self._filters = {
            BinaryOperation.OperatorSide.ASSIGN: self._filter.is_number,
            BinaryOperation.OperatorSide.LEFT: self._filter.is_integer,
            BinaryOperation.OperatorSide.RIGHT: self._filter.is_integer
        }

        # Set fallback numbers
        self._fallback = {
            BinaryOperation.OperatorSide.LEFT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE'])),
            BinaryOperation.OperatorSide.RIGHT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE']))
        }

    # Calculate
    def calculate(self, left, right):
        return left >= right
