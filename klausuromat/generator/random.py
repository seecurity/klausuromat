import random
import string

from klausuromat import identifier, generator, exceptions, enumerator, operations, ifilter


# Random code generator that has the ability to verify it's own code
class RandomCodeGenerator(generator.CodeGenerator):
    # All possible identifier
    types = [identifier.Identifier.DataType.INT, identifier.Identifier.DataType.FLOAT]

    # Predefined operator levels
    operator_levels = (
        # 1. Level: +, -, *, /
        operations.arithmetic,

        # 2. Level (implies above): i++, ++i, i--, --i, +=, -=, *=, /=
        # Missing: all
        operations.arithmetic,

        # 3. Level (implies above): &, |, ^, %
        # Missing: &=, |=, ^=, %=
        operations.arithmetic + operations.bitwise,

        # 4. Level (implies above): <<, >>
        # Missing: <<=, >>=
        operations.all_
    )

    # Predefined conditional levels
    # TODO: implement this!
    conditional_levels = (
        # 1. Level: ???
        # TODO: ^
        ['Equal', 'NotEqual', 'LessThan', 'LessThanOrEqual', 'GreaterThan', 'GreaterThanOrEqual']
    )

    # Pointer level
    PointerLevel = enumerator.Enum(NONE=0, SINGLE_REFERENCES=1, MULTIPLE_REFERENCES=2)

    # Function level
    FunctionLevel = enumerator.Enum(NONE=0, BY_VALUE=1, BY_REFERENCE=2)

    # Identifier slot
    IdentifierSlot = enumerator.Enum(FREE=0, DATA_TYPE=1, POINTER=2)

    # Generator slot
    GeneratorSlot = enumerator.Enum(FREE=0, OPERATION=1, FUNCTION=2, CONDITIONAL=3)

    # Initialize
    def __init__(self, settings=('settings.json', 'utf-8'), language=('languages/c.json', 'utf-8')):
        # Let parent class do all the initializing stuff
        super().__init__(settings, language)

        # List of possible identifier names
        self.names = list(string.ascii_lowercase)

        # Save initial vars
        self._id_range = random.randrange(*self._settings['IDENTIFIER_AMOUNT_RANGE'])
        self._id_range_max = self._settings['IDENTIFIER_AMOUNT_RANGE'][1] - 1
        self._op_range = random.randrange(*self._settings['OPERATION_AMOUNT_RANGE'])
        self._op_range_max = self._settings['OPERATION_AMOUNT_RANGE'][1] - 1
        self._operators = []
        self._filter = ifilter.IdentifierFilter(self._settings)

        # Generator information
        self._generators = {
            RandomCodeGenerator.GeneratorSlot.FUNCTION: (
                generator.FunctionGenerator,
                lambda: self._function_level != RandomCodeGenerator.FunctionLevel.NONE,
                self._settings['FUNCTION_CHANCE'],
                self._settings['FUNCTION_AMOUNT_MAX']
            ),
            RandomCodeGenerator.GeneratorSlot.CONDITIONAL: (
                generator.ConditionalGenerator,
                lambda: self._conditionals,
                self._settings['CONDITIONAL_AMOUNT_MAX'],
                self._settings['CONDITIONAL_CHANCE']
            )
        }

        # Levels
        self._operator_level = None
        self._pointer_level = RandomCodeGenerator.PointerLevel.NONE
        self._function_level = RandomCodeGenerator.FunctionLevel.NONE

        # Booleans
        self._void = True
        self._float = False
        self._conditionals = False

    # Operators
    def set_operators(self, operators):
        # Check if all operators exist in operation list
        if not all(operator in RandomCodeGenerator.all_operations for operator in operators):
            raise exceptions.RandomGeneratorSettingError('Unknown operator in list')

        # Save operators (copy)
        self._operators = list(operators)

    # Operator property
    operators = property(lambda self: self._operators, set_operators)

    # Operator level
    def set_operator_level(self, level):
        # Convert level to integer
        level = self._get_level(level, 'Operator')

        # Check if level exists in level range
        if not RandomCodeGenerator.operator_levels[level]:
            raise exceptions.RandomGeneratorSettingError(
                'Operator level is expected to be {} <= level < {}'.format(0, len(RandomCodeGenerator.operator_levels)))

        # Save level and operators of level
        self._operator_level = level
        self._operators = RandomCodeGenerator.operator_levels[level][:]

    # Operator level property
    operator_level = property(lambda self: self._operator_level, set_operator_level)

    # Pointer level
    def set_pointer_level(self, level):
        # Convert level to integer
        level = self._get_level(level, 'Pointer')

        # Check if level exists in level range
        if level not in RandomCodeGenerator.PointerLevel:
            raise exceptions.RandomGeneratorSettingError(
                'Pointer level is expected to be {} <= level < {}'.format(0, len(RandomCodeGenerator.PointerLevel)))

        # Apply level
        self._pointer_level = level

    # Pointer level property
    pointer_level = property(lambda self: self._pointer_level, set_pointer_level)

    # Pointer level
    def set_function_level(self, level):
        # Convert level to integer
        level = self._get_level(level, 'Function')

        # Check if level exists in level range
        if level not in RandomCodeGenerator.FunctionLevel:
            raise exceptions.RandomGeneratorSettingError(
                'Function level is expected to be {} <= level < {}'.format(0, len(RandomCodeGenerator.FunctionLevel)))

        # Apply level
        self._function_level = level

    # Pointer level property
    function_level = property(lambda self: self._function_level, set_function_level)

    # Void function property
    void = property(lambda self: self._void, lambda self, value: setattr(self, '_void', bool(value)))

    # Floating point property
    float_ = property(lambda self: self._float, lambda self, value: setattr(self, '_float', bool(value)))

    # Conditional statements property
    conditionals = property(lambda self: self._conditionals,
                            lambda self, value: setattr(self, '_conditionals', bool(value)))

    # Add function generator and return instance
    #noinspection PyMethodOverriding
    def add_function(self):
        # Filter identifiers for call by value
        if self._function_level == RandomCodeGenerator.FunctionLevel.BY_VALUE:
            # Get identifiers that have no reference and sample from them
            ids = list(self._filter.apply(self._filter.has_reference_depth, self._ids, depth=0))
            ids = self._sample_identifiers(self._settings['FUNCTION_IDENTIFIER_RANGE'], ids)

        # Filter identifiers for call by reference
        else:
            # Copy identifier list
            ids = self._ids[:]

            # Check if there are no identifiers that will be called by reference
            if self._ids_called_by_reference() == 0:
                # Remove from list of identifiers and set it to call by reference
                id_ = random.choice(ids)
                ids.remove(id_)
                id_.call_by = identifier.Identifier.CallBy.REFERENCE
            else:
                # Remove from list of identifiers that will be called by reference
                by_reference_ids = self._filter.apply(self._filter.is_called_by, ids, type_=identifier.Identifier.CallBy.REFERENCE)
                id_ = random.choice(list(by_reference_ids))
                ids.remove(id_)

            # Make new range from settings, get identifiers and add our first identifier to it
            start, stop = self._settings['FUNCTION_IDENTIFIER_RANGE']
            range_ = (start - 1, stop - 1)
            ids = [id_] + self._sample_identifiers(range_, ids)

            # Now shuffle them around so no one notices
            random.shuffle(ids)

        # Call parent method
        function = super().add_function(ids=ids)

        # Return
        return function

    # Build and return generated code
    def code(self):
        # Generate and add identifiers
        self._generate_identifiers()

        # Initialize self
        self.initialize()

        # Generate operations
        self._generate_operations()

        # Verify results
        self.verify()

        # Get code from parent class
        return super().code(comments=True, identifiers=True, result=True)

    # Convert level to digit
    def _get_level(self, level, type_):
        try:
            return int(level)
        except (ValueError, TypeError):
            raise exceptions.RandomGeneratorSettingError('{} level is expected to be a digit'.format(type_))

    # Get all identifiers that match our criteria
    def _filter_ids(self, type_=None, depth=None):
        ids = self._ids

        # Filter by type
        if type_ is not None:
            ids = self._filter.apply(self._filter.has_type, ids, type_=type_)

        # Filter by reference depth
        if depth is not None:
            ids = self._filter.apply(self._filter.has_reference_depth, ids, depth=depth)

        # Return ids as list
        return list(ids)

    # Count identifiers that have a specific type
    def _ids_have_type(self, type_):
        return sum(1 for id_ in self._ids if id_.type == type_)

    # Count identifiers that have a specific reference depth
    def _ids_have_reference_depth(self, depth):
        return sum(1 for id_ in self._ids if id_.reference_depth() == depth)

    # Count identifiers that will be called by reference
    def _ids_called_by_reference(self):
        return sum(1 for id_ in self._ids if id_.called_by_reference)

    # Generate identifiers while following the "one or more" rule
    def _generate_identifiers(self):
        # Set to call by value if function level is "by value"
        call_by = identifier.Identifier.CallBy.VALUE if self._function_level == RandomCodeGenerator.FunctionLevel.BY_VALUE else None

        # Copy names and types
        types = RandomCodeGenerator.types[:]

        # Check if float is enabled
        if not self._float:
            types.remove(identifier.Identifier.DataType.FLOAT)

        # Tuple of possible pointer depths
        if self._pointer_level == RandomCodeGenerator.PointerLevel.NONE:
            depths = False
        elif self._pointer_level == RandomCodeGenerator.PointerLevel.SINGLE_REFERENCES:
            depths = (0,)  # the comma is needed here to tell Python that we want a tuple
        else:
            depths = tuple(range(0, self._settings['POINTER_DEPTH_MAX']))

        # Put identifier data types in slots
        slots = [(RandomCodeGenerator.IdentifierSlot.DATA_TYPE, type_) for type_ in types]
        # Put identifier pointer in slots
        if depths:
            slots.extend([(RandomCodeGenerator.IdentifierSlot.POINTER, depth) for depth in range(0, len(depths))])

        # Compare length of slots with identifier range
        if len(slots) > self._id_range_max:
            # Maximum range is too small
            raise exceptions.GeneratorGenerationNotPossibleError(
                'Identifier range is too small for the selected options.')
        elif self._id_range < len(slots) <= self._id_range_max:
            # Current range has to be extended but is <= maximum range
            self._id_range = len(slots)

        # Merge free slots with allocated slots
        slots = [(RandomCodeGenerator.IdentifierSlot.FREE, None)] * (self._id_range - len(slots)) + slots

        # Add identifiers to slots
        self._fill_id_slots(slots, types, depths, call_by)

    # Fill slots by adding identifiers to this generator
    def _fill_id_slots(self, slots, types, depths, call_by):
        # Loop through slots
        for slot_type, slot_value in slots:
            # Reset vars
            type_ = id_ = ids = None

            # Name
            index = random.randrange(0, len(self.names))
            name = self.names.pop(index)

            # Data type slot: Check if we need one identifier of this type
            if slot_type == RandomCodeGenerator.IdentifierSlot.DATA_TYPE and self._ids_have_type(slot_value) == 0:
                type_ = slot_value

            # Pointer slot: Check if we need a pointer here
            elif slot_type == RandomCodeGenerator.IdentifierSlot.POINTER and \
                    self._ids_have_reference_depth(slot_value + 1) == 0:
                ids = self._filter_ids(depth=slot_value)
                # Raise exception if ids is an empty list
                if not ids:
                    raise exceptions.GeneratorIdentifierError('No identifier left to reference to')

            # Free slot: We can do what we want!
            else:
                # Pointers allowed: Roll the dice
                if self._ids and depths and random.random() < self._settings['POINTER_CHANCE']:
                    # Add a pointer
                    ids = self._filter_ids(type_=random.choice(types), depth=random.choice(depths))
                else:
                    # Add a normal identifier
                    type_ = random.choice(types)

            # Identifiers existing
            if ids:
                # Choose an identifier and use it's type
                id_ = random.choice(ids)
                type_ = id_.type

            # No identifier existing and type has not been set yet
            elif type_ is None:
                # Choose a type randomly
                type_ = random.choice(types)

            # Turn off call by reference for pointers if pointer level is set to single references only
            # TODO dirty hack! doesn't matter as this system has been rewritten in branch array
            if id_ is not None and self._pointer_level == RandomCodeGenerator.PointerLevel.SINGLE_REFERENCES:
                call_by = identifier.Identifier.CallBy.VALUE

            # Add identifier to generator
            self.add_identifier(type_, name, reference=id_, call_by=call_by)

    # Generate operations while following the "one or more" rule for any type of generator
    def _generate_operations(self):
        # Put one operation into slots
        slots = [RandomCodeGenerator.GeneratorSlot.OPERATION]

        # Put child generators that are required into slots
        # Function generator
        if self._function_level != RandomCodeGenerator.FunctionLevel.NONE:
            slots.append(RandomCodeGenerator.GeneratorSlot.FUNCTION)

        # Conditional generator
        if self._conditionals:
            slots.append(RandomCodeGenerator.GeneratorSlot.CONDITIONAL)

        # Compare length of slots with operation range
        if len(slots) > self._op_range_max:
            # Maximum range is too small
            raise exceptions.GeneratorGenerationNotPossibleError(
                'Operation range is too small for the selected options.')
        elif self._op_range < len(slots) <= self._op_range_max:
            # Current range has to be extended but is <= maximum range
            self._op_range = len(slots)

        # Merge free slots with allocated slots
        slots = [RandomCodeGenerator.GeneratorSlot.FREE] * (self._op_range - len(slots)) + slots

        # Add operations to slots
        self._fill_op_slots(slots)

    # Fill slots by adding operations/generators to this generator
    def _fill_op_slots(self, slots):
        # Create operations
        i = 0
        while i < len(slots):
            # Check if slot requires to add a generator
            gen = self._generator_required(slots[i])

            # Function slot
            if gen == generator.FunctionGenerator:
                # Add function
                func = self.add_function()

                # Do a random amount of operations (but at least one)
                i += self._do_operations(i, func, slots, self._settings['FUNCTION_OPERATION_AMOUNT_MAX'])

                # Check if we want to return something and assign it to an identifier or just call the function
                if not self.void and \
                        ((self._count_functions_returning() == 0) or
                        (random.random() < self._settings['FUNCTION_RETURN_CHANCE'])):
                    func.assign()
                else:
                    func.call()

            # Conditional slot
            elif gen == generator.ConditionalGenerator:
                # Add conditional statement
                conditional = self.add_conditional()

                # Add if clause (and possibly an else if clause)
                for _ in range(0, 1 if random.random() < self._settings['CONDITIONAL_ELSE_IF_CHANCE'] else 2):
                    # TODO: delete the following line or implement it as an conditional level
                    #operation = self.get_operation(self._operators)
                    # TODO: use conditional levels
                    operation = self.get_operation(RandomCodeGenerator.conditional_levels)
                    operation.random(assign=False)
                    conditional.add_if(operation)

                    # Do a random amount of operations (but at least one)
                    i += self._do_operations(i, conditional, slots, self._settings['CONDITIONAL_OPERATION_AMOUNT_MAX'])

                # Add else clause
                if random.random() < self._settings['CONDITIONAL_ELSE_CHANCE']:
                    conditional.add_else()

                    # Do a random amount of operations (but at least one)
                    i += self._do_operations(i, conditional, slots, self._settings['CONDITIONAL_OPERATION_AMOUNT_MAX'])

                # Done!
                conditional.done()

            # Operation slot
            else:
                # Do an arithmetic operation on the main generator
                self.operate(self._operators)

            # Increase counter
            i += 1

    # Return class or False depending on whether a generator is required or not
    def _generator_required(self, slot):
        # Slot is free
        if slot == RandomCodeGenerator.GeneratorSlot.FREE:
            # Roll the dice
            dice = random.random()

            # Loop through generator types
            for gen, enabled, chance, max_ in self._generators.values():
                # Generator is enabled and does not exceed the maximum amount of this generator type
                # Check if the generator is lucky
                if enabled() and self._count_generators(gen) < max_ and dice < chance:
                    return gen

        # Slot is representing a class (e.g. a generator)
        elif slot != RandomCodeGenerator.GeneratorSlot.OPERATION:
            # Get information about this generator type
            gen, *_ = self._generators[slot]

            # Check if a generator exists (only one is required)
            if self._count_generators(gen) == 0:
                return gen

        # Nothing else triggered: Operation slot
        return False

    # Do a random amount of operations (but at least one), depending on free slots
    def _do_operations(self, i, gen, slots, max_):
        # Calculate max and range
        max_ = min(self._count_free_slots(slots[i + 1:]), max_)
        range_ = range(0, 1 if max_ <= 1 else random.randint(1, max_))

        # Do random operations
        for _ in range_:
            gen.operate(self._operators)

        # Return amount of operations made (if there have been free slots)
        return min(len(range_), max_)

    # Count free slots
    def _count_free_slots(self, slots):
        return sum(1 for slot in slots if slot == RandomCodeGenerator.GeneratorSlot.FREE)

    # Count generators that are a specific instance
    def _count_generators(self, instance):
        return sum(1 for op in self._operations if isinstance(op, instance))

    # Count function generators that have a return value
    def _count_functions_returning(self):
        return sum(1 for op in self._operations if isinstance(op, generator.FunctionGenerator) and op.return_)
