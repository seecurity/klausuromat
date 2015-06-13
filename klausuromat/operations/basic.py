# Externals
import random
import copy

# Internals
import exceptions
import identifier


# Basic Operation that can be extended to represent an operation
class BasicOperation:
    OperatorAssign = 0

    # Constructor
    def __init__(self, ids, settings, language, filter_):
        # Save identifiers
        self._ids = ids

        # Save some stuff
        self._settings = settings
        self._language = language
        self._filter = filter_

        # Filter, filter arguments and fallback (numbers) dict
        self._filters = {}
        self._filter_args = {}
        self._fallback = {}

        # Save initial values
        self._done = False
        self._before_assign = None
        self._assign = None
        self.snapshot = None
        self.result = None

    # Name property
    name = property(lambda self: self.__class__.__name__)

    # Identifiers property
    ids = property(lambda self: self._ids, lambda self, value: setattr(self, '_ids', value))

    # Assign operation to an identifier
    def set_assign(self, value=None):
        # Check if the operation is already done
        if self._done:
            raise exceptions.GeneratorOperationDisabledError()

        # Get assign key
        key = BasicOperation.OperatorAssign

        # Random identifier if none specified
        if value is None:
            filtered = list(self._filter.apply(self._filters[key], self._ids, **self._filter_args)) \
                if key in self._filters else self._ids
            value = self._choice(filtered)

        # Set attribute
        self._assign = value

    # Assign property
    assign = property(lambda self: self._assign, set_assign)

    # Return snapshot of all identifiers
    def snapshot_code(self, verify=False):
        # Check if the operation is still active
        if not self._done:
            raise exceptions.GeneratorOperationEnabledError()

        # Check if no snapshot has been made
        if not self.snapshot:
            raise exceptions.GeneratorOperationSnapshotError()

        # Get formatters
        l = self._language['verify']['id'] if verify else self._language['result']

        # Identifier lists
        formatters = []
        values = []

        # Loop through identifiers
        #noinspection PyTypeChecker
        for id_ in self.snapshot:
            # Unpack vars
            formatter, value = self._language['type'][id_.type]['item']['verify' if verify else 'result']

            # Append identifier to list
            formatters.append(formatter.format(id_))
            values.append(value.format(id_))

        # Format and return code
        code = l['print']['wrapper'].format(l['print']['separator'].join(formatters),
                                            l['print']['separator'].join(values))
        return l['prepend'] + code + l['append'] if verify else l['before'] + code

    # Get value of an operand which could be an identifier, an operation or a simple value
    def _operand_value(self, operand):
        # Operand is an identifier
        if isinstance(operand, identifier.Identifier):
            return operand.value

        # Operand is another operation
        elif isinstance(operand, BasicOperation):
            return operand.result

        # Operand is a simple value
        else:
            return operand

    # Get code of an operand which could be an identifier, an operation or a simple value
    def _operand_code(self, operand):
        # Operand is an identifier
        if isinstance(operand, identifier.Identifier):
            return operand.dereference

        # Operand is another operation
        elif isinstance(operand, BasicOperation):
            return self._language['operation']['parantheses'].format(operand.code())

        # Operand is a simple value
        else:
            return operand

    # Get bit representation of an operand which could be an identifier, an operation or a simple value
    def _operand_bits(self, operand):
        return bin(self._operand_value(operand))

    # Choose one identifier randomly
    def _choice(self, ids):
        try:
            return random.choice(ids)
        except IndexError as exc:
            raise exceptions.GeneratorOperationNotPossibleError(self.__class__) from exc

    # Choose <amount> identifiers randomly
    def _sample(self, ids, amount):
        try:
            return random.sample(ids, amount)
        except ValueError as exc:
            raise exceptions.GeneratorOperationNotPossibleError(self.__class__) from exc
