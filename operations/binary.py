# Externals
import random
import copy

# Internals
import exceptions
import enumerator
import identifier
from operations import BasicOperation


# Basic Operation that can be extended to represent an operation
class BinaryOperation(BasicOperation):
    OperatorSide = enumerator.Enum(ASSIGN=0, LEFT=1, RIGHT=2)

    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Initialize sides
        self._left = None
        self._right = None

    # Fill everything with random values and disable
    def random(self, assign=True):
        self.left = None
        self.right = None

        # Assign if requested
        if assign:
            self.assign = None

        # Done!
        self.done()

    # Set left operand
    def set_left(self, operand=None):
        self._set_operand(BinaryOperation.OperatorSide.LEFT, operand)

    # Left operand property
    left = property(lambda self: self._left, set_left)

    # Set right operand
    def set_right(self, operand=None):
        self._set_operand(BinaryOperation.OperatorSide.RIGHT, operand)

    # Right operand property
    right = property(lambda self: self._right, set_right)

    # Done, calculate result and make a snapshot
    def done(self):
        # Check if the operation is already done
        if self._done:
            raise exceptions.GeneratorOperationDisabledError()

        # Overwrite oeprands with copies of themself
        self._left = copy.deepcopy(self._left)
        self._right = copy.deepcopy(self._right)

        # Calculate result
        self.result = self.calculate(self._operand_value(self._left), self._operand_value(self._right))

        # Assign (if needed)
        if self._assign:
            # Copy assigned identifier (before), set value and copy assigned identifier (after)
            self._before_assign = copy.deepcopy(self._assign)
            self._assign.value = self.result
            self._assign = copy.deepcopy(self._assign)

        # Make snapshot and overwrite operands with copies of themself
        self.snapshot = copy.deepcopy(self._ids)

        # Done!
        self._done = True

    # Return code of this operation
    def code(self):
        # Check if the operation is still active
        if not self._done:
            raise exceptions.GeneratorOperationEnabledError()

        # Build operation code
        code = self._language['format'][self.name]['code'].format(self._operand_code(self._left),
                                                                  self._operand_code(self._right))

        # Add assignment to code (if assigned)
        if self._assign:
            code = self._language['operation']['assignment'].format(self._operand_code(self._assign), code)

        # Return code
        return code

    # Return hint for code
    def hint(self, bits=False):
        # Get operation code with values
        code = self._language['format'][self.name]['code'].format(self._operand_value(self._left),
                                                                  self._operand_value(self._right))

        # Previous value of assignment identifier and result including calculation
        lines = ['Vorher:  ' + self._before_assign.code(),
                 'Nachher: ' + self._assign.code(calculation=code)]

        # Bit representation (if necessary)
        if bits:
            # Get operation code with bits
            code = self._language['format'][self.name]['code'].format(self._operand_bits(self._left),
                                                                      self._operand_bits(self._right))

            # Append to lines
            lines.append(' ' * 9 + self._assign.code(calculation=code, bits=True))

        # Append to code
        return self._language['identifier']['wrapper'].format(self._language['identifier']['separator'].join(lines))

    # Set operand
    def _set_operand(self, side, operand):
        # Check if the operation is already done
        if self._done:
            raise exceptions.GeneratorOperationDisabledError()

        # Random identifier/value if no identifier/value specified
        if operand is None:
            # Set default and roll the dice
            filtered = None
            dice = random.random()

            # Use an identifier
            if dice < self._settings['OPERATION_IDENTIFIER_CHANCE']:
                # Filter identifier
                filtered = list(self._filter.apply(self._filters[side], self._ids, **self._filter_args)) \
                    if side in self._filters else self._ids

            # Check if list is empty and fallback numbers have been supplied
            if not filtered and side in self._fallback:
                filtered = self._fallback[side]

            # Choose from filtered list
            operand = self._choice(filtered)

        # Operand specified
        else:
            # Identifier: Check if our filters match the specified identifier
            #noinspection PyProtectedMember
            if isinstance(operand, identifier.Identifier) \
                    and side in self._filters \
                    and not ifilter.match(self._filters[side], operand):
                raise exceptions.GeneratorOperationNotPossibleError(
                    'Operand does not match filter(s):{}'.format(operand))

            # Operation: Check if this operation has already been assigned
            elif isinstance(operand, BasicOperation) and operand._assign:
                raise exceptions.GeneratorOperationNotPossibleError(
                    'Operand is an operation that has been assigned already')

        # Set operand
        key = '_left' if side == BinaryOperation.OperatorSide.LEFT else '_right'
        setattr(self, key, operand)
