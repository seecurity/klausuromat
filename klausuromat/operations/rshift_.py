from .binary import BinaryOperation


# Right shift by using 3 identifiers: c = a >> b
class RightShift(BinaryOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Set filters
        self._filters = {
            BinaryOperation.OperatorSide.ASSIGN: self._filter.is_number,
            BinaryOperation.OperatorSide.LEFT: self._filter.is_integer,
            BinaryOperation.OperatorSide.RIGHT: self._filter.is_shift_counter
        }

        # Set fallback numbers
        self._fallback = {
            BinaryOperation.OperatorSide.LEFT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE'])),
            BinaryOperation.OperatorSide.RIGHT: list(range(0, self._settings['MAX_SHIFT_BITS'] + 1))
        }

    # Calculate
    def calculate(self, left, right):
        return left >> right

    # Get bit representation of an operand which could be an identifier, an operation or a simple value
    def _operand_bits(self, operand):
        return bin(self._operand_value(operand)) if operand == self._left else self._operand_value(operand)
