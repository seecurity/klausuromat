import copy

from klausuromat import generator, exceptions, identifier, operations


# Conditional statement generator
class ConditionalGenerator(generator.GeneratorChild):
    # Initialize
    def __init__(self, ids, settings, language, filter_, parent):
        # Let parent class do all the initializing stuff
        super().__init__(settings, language, filter_, parent)

        # Store real and sandbox identifiers
        self._ids_actual = ids
        self._ids_copy = copy.deepcopy(ids)

        # Save initial values
        self._conditions = []
        self._condition_true = None
        self._else = False

    # Add if clause to generator
    # Accepts an operation instance or an identifier instance as condition
    def add_if(self, condition):
        # Check if an "else" has been added already (no "if" possible)
        if self._else:
            raise exceptions.GeneratorConditionalError('Can not add if clause, else clause already set')

        # Add condition
        self._add_condition(condition)

    # Add else clause to generator
    def add_else(self):
        # Check if no "if" has been set yet (no "else" possible)
        if not self._conditions:
            raise exceptions.GeneratorConditionalError('Can not add else clause, no if clause set yet')

        # Check if an "else" has been added already (another "else" not possible)
        elif self._else:
            raise exceptions.GeneratorConditionalError('Can not add else clause, else clause already set')

        # Add condition and store that we have added an else clause
        self._add_condition()
        self._else = True

    # Done, nothing will be added anymore
    def done(self):
        # Set identifiers and operations to the condition that was true
        if self._condition_true:
            _, self._ids, self._operations = self._condition_true

        # Or if there is no condition true, just set ids and an empty list of operations
        else:
            self._ids = self._ids_actual
            self._operations = []

        # Disable self and reactivate parent generator
        self.active = False

    # Add a condition
    def _add_condition(self, condition=None):
        # Reset operations if conditions are not empty
        if self._conditions:
            self._operations = []

        # If clause
        if condition is not None:
            # Get value
            value = self._get_condition_value(condition)

        # Else clause
        else:
            value = False if self._condition_true else True

        # Set identifiers to a copy or the real identifiers depending on whether the condition is true or not
        self._ids = self._ids_actual if not self._condition_true and value else copy.deepcopy(self._ids_copy)

        # Make tuple of gathered information
        conditional = (condition, self._ids, self._operations)

        # Update conditionTrue attribute if this condition is true and none was true before
        if not self._condition_true and value:
            self._condition_true = conditional

        # Append conditional to conditions
        self._conditions.append(conditional)

    # Get condition value (of operation or identifier)
    def _get_condition_value(self, condition):
        # Condition is an identifier
        if isinstance(condition, identifier.Identifier):
            return condition.value

        # Condition is an operation
        elif isinstance(condition, operations.BasicOperation):
            return condition.result

        # Condition is something else we don't accept
        else:
            raise exceptions.GeneratorConditionalUnknownConditionError(condition)

    # Get condition code (of operation or identifier)
    def _get_condition_code(self, condition):
        # Condition is none
        if condition is None:
            return None

        # Condition is an identifier
        elif isinstance(condition, identifier.Identifier):
            return condition.dereference

        # Condition is an operation
        elif isinstance(condition, operations.BasicOperation):
            return condition.code()

        # Condition is something else we don't accept
        else:
            raise exceptions.GeneratorConditionalUnknownConditionError(condition)

    # Return code pieces (with verifying code if requested)
    def code_pieces(self, options):
        # Save code options so we don't have to pass it to every function
        self._options = options

        # Default and start values
        code = self._code_pieces_default()

        # Build comment
        if self._options.get('comments'):
            code['main'].append(self._indent() + self._language['comment'].format('Conditional'))

        # Start verify block
        if self._options.get('verify'):
            code['main'].append(self._code_pieces_verify_start())

        # Loop through conditions
        for i, condition in enumerate(self._conditions):
            # Unpack condition
            *_, operations_ = condition

            # Build condition
            code['main'].append(self._code_pieces_condition(condition, i))

            # Block start
            self._options['block'] += 1

            # Add operations
            self._code_pieces_operations(code, operations_, key='main', block=False)

            # Block end
            self._options['block'] -= 1

        # Build end block
        code['main'].append(self._indent() + self._language['conditional']['bottom'])

        # End verify block
        if self._options.get('verify'):
            code['main'].append(self._code_pieces_verify_end())

        # Return dictionary
        return code

    # Return code pieces that represent a condition
    def _code_pieces_condition(self, condition, i):
        operation, *_ = condition

        # Get formatting key for this condition
        if operation is None:
            key = 'else'
        elif i == 0:
            key = 'if'
        else:
            key = 'elif'

        # Return formatted condition
        return self._indent() + self._language['conditional']['top'][key].format(self._get_condition_code(operation))
