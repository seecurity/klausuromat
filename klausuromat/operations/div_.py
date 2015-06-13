from klausuromat import operations


# Division: [c = ]a / b
class Division(operations.BinaryOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Set filters
        self._filters = {
            operations.BinaryOperation.OperatorSide.ASSIGN: self._filter.is_number,
            operations.BinaryOperation.OperatorSide.LEFT: self._filter.is_number,
            operations.BinaryOperation.OperatorSide.RIGHT: self._filter.is_number_non_zero
        }

        # Set fallback numbers
        self._fallback = {
            operations.BinaryOperation.OperatorSide.LEFT: list(range(*self._settings['IDENTIFIER_VALUE_RANGE'])),
            operations.BinaryOperation.OperatorSide.RIGHT: [x for x in range(*self._settings['IDENTIFIER_VALUE_RANGE']) if x != 0]
        }

    # Calculate
    def calculate(self, left, right):
        return left / right
