from klausuromat import operations


# Equal: [c = ]a == b
class Equal(operations.BinaryOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Set filters
        self._filters = {
            operations.BinaryOperation.OperatorSide.ASSIGN: self._filter.is_number,
            operations.BinaryOperation.OperatorSide.LEFT: self._filter.is_integer,
            operations.BinaryOperation.OperatorSide.RIGHT: self._filter.is_integer
        }

        # Set fallback numbers
        self._fallback = {
            operations.BinaryOperation.OperatorSide.LEFT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE'])),
            operations.BinaryOperation.OperatorSide.RIGHT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE']))
        }

    # Calculate
    def calculate(self, left, right):
        return left == right
