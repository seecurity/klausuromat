import logging
import io
import json
import random
import copy

from klausuromat import exceptions, operations, ifilter, identifier
from .child import GeneratorChild
from .function import FunctionGenerator
from .if_else import ConditionalGenerator


# Basic code generator that can build (verifying) code but is not able to compile it
class BasicGenerator:
    # Possible operations
    all_operations = operations.all_

    # Initialize
    def __init__(self, settings, language):
        # Open settings file (JSON) and convert to dict
        with io.open(settings[0], mode='r', encoding=settings[1]) as fd:
            self._settings = json.load(fd)

        # Open language file (JSON) and convert to dict
        with io.open(language[0], mode='r', encoding=language[1]) as fd:
            self._language = json.load(fd)

        # Build list of types
        self._type_list = [type_['name'] for type_ in self._language['type']]

        # Start logging
        log = '/'.join((self._settings['LOG_DIRECTORY'], self._settings['LOG_FILENAME']))
        logging.basicConfig(filename=log, level=logging.DEBUG)
        logging.info('Created instance of "{}"'.format(self.__class__.__name__))

        # Instantiate class filter
        self._filter = ifilter.IdentifierFilter(self._settings)

        # Save initial values
        self._options = {}
        self._requirements = []
        self._namespace = set()
        self._active = self
        self._ids = []
        self._operations = []

    # Make iterable
    def __iter__(self):
        return iter(self._operations)

    # Set active generator or disable (False)
    def set_active(self, value):
        # Raise exception if the generator has been disabled already
        if not self._active:
            raise exceptions.GeneratorDisabledError()

        self._active = value

    # Active property
    active = property(lambda self: self._active, set_active)

    # Add an Identifier to this generator
    def add_identifier(self, type_, name=None, value=None, reference=None, call_by=None):
        # Build instance of identifier and append it
        id_ = self._identifier(type_, name=name, value=value, reference=reference, call_by=call_by)
        self._ids.append(id_)

        # Return identifier instance
        return id_

    # Initialize identifiers
    def initialize(self):
        # Use initialize operation
        self.add_operation(self.get_operation(operations.Initialize))

    # Add function generator and return instance
    def add_function(self, name=None, ids=None):
        # Sample ids from specified range if they are not set
        if ids is None:
            ids = self._sample_identifiers(self._settings['FUNCTION_IDENTIFIER_RANGE'], ids)

        # Create function generator and return
        return self._add_child(FunctionGenerator, ids=ids, name=name)

    # Add conditional generator and return instance
    def add_conditional(self):
        # Create conditional generator and return
        return self._add_child(ConditionalGenerator)

    # Do a random operation
    # Note: No configuration possible on an operation, therefore there is no return
    #       Use getOperation() and addOperation() instead
    def operate(self, op_list=None):
        # Check if this generator is active
        self._check_active_state()

        # Check operator list
        if op_list is None:
            # Build list of operations
            op_list = BasicGenerator.all_operations[:]
        elif type(op_list) is str:
            # Cast to list
            op_list = [op_list]
        elif type(op_list) is not list:
            # Raise if not a list
            raise TypeError('Expected str or list, received type {}'.format(type(op_list)))
        else:
            # Copy list
            op_list = op_list[:]

        # Log operation list
        logging.info('Possible operations: {}'.format(op_list))

        # Choose an operation randomly and pop it from the list
        random.shuffle(op_list)
        call = op_list.pop()

        # Check if operator exists
        try:
            call = vars(operations)[call]
        except KeyError as exc:
            raise exceptions.GeneratorOperationUnknownError(call) from exc

        # Apply operation on the current set of identifiers
        try:
            operation = self.get_operation(call)
            operation.random()
        except exceptions.GeneratorOperationNotPossibleError as exc:
            # No operation left
            if not op_list:
                logging.error('No operation could use the current set of identifiers')
                logging.info('Identifiers: {}'.format(self._ids))
                raise exceptions.GeneratorGenerationNotPossibleError(
                    'No operation could use the current set of identifiers') from exc
            # Try to use another operation
            else:
                logging.info('Operation failed: {}'.format(call))
                logging.info('Identifiers: {}'.format(self._ids))
                return self.operate(op_list)

        # Let operation know we're done and append operation
        self.add_operation(operation)

    # Create instance of an operation
    def get_operation(self, operator):
        # Choose randomly from list if operator is not a string
        if not isinstance(operator, str):
            try:
                operator = random.choice(operator)
            except TypeError:
                pass

        # Get operator from string
        if isinstance(operator, str):
            try:
                operator = vars(operations)[operator]
            except KeyError as exc:
                raise exceptions.GeneratorOperationUnknownError(operator) from exc

        # Check if format string exists in JSON file
        # Note: This is a bit bugged at the moment, as the requirements have to be added to the main generator
        #       And it's dirty...
        try:
            requirements = self._language['format'][operator.__name__]['requires']
        except KeyError as exc:
            raise exceptions.GeneratorJSONKeyError(operator.__name__) from exc

        # Apply operation on the current set of identifiers
        instance = operator(self._ids, self._settings, self._language, self._filter)
        self._requirements.extend(requirements)  # Dirty!

        # Return created instance
        return instance

    # Append operation instance to generator
    def add_operation(self, operation):
        # Append operation
        self._operations.append(operation)

    # Compare identifiers with internal stored identifiers
    def compare_identifiers(self, all_ids):
        # Retrieve operations that have a result or are a generator
        operations_ = [operation for operation in self._operations
                       if hasattr(operation, 'result') or isinstance(operation, GeneratorChild)]

        # Compare amount of operations
        if len(operations_) != len(all_ids):
            logging.error(
                'One or more operation is missing in real results. '
                'Predicted: {}; Real: {}'.format(len(operations_), len(all_ids)))
            return False

        # Loop through operations
        for index, ids in enumerate(zip(operations_, all_ids)):
            # Unpack
            operation, real = ids

            # Operation is another generator
            if isinstance(operation, GeneratorChild):
                if not operation.compare_identifiers(real):
                    return False

            # Normal operation
            else:
                # Loop through identifiers
                for id_ in operation.snapshot:
                    # Check if identifier exists in real results
                    if id_.name not in real:
                        logging.error('Operation[{}] "{}", Identifier "{}" is missing in real results'.format(
                            index, operation.__class__.__name__, id_.name))
                        return False

                    # Check if values are equal
                    if id_.value != real[id_.name]:
                        logging.error('Operation[{}] "{}", Identifier "{}": {} != {}'.format(
                            index, operation.__class__.__name__, id_.name, id_.value, real[id_.name]))
                        logging.info('Identifiers of the operation above: {}'.format(operation.snapshot))
                        return False

        # No error: Code seems to be fine
        return True

    # Return raw code
    def code(self, **options):
        # Get code pieces
        code = self.code_pieces(options)

        # Join and wrap code pieces
        code = {key: ('\n'.join(set(value)) if key == 'requirements' else '\n'.join(value))
                for key, value in code.items()}

        # Add line breaks (after)
        keys = ['requirements', 'prototypes']
        code.update({key: value + '\n\n' for key, value in code.items() if key in keys and value})

        # Add line breaks (before)
        keys = ['functions']
        code.update({key: '\n\n' + value for key, value in code.items() if key in keys and value})

        # Return wrapped content
        return self._language['wrapper'].format(code)

    # Create instance of an identifier
    def _identifier(self, type_, **kwargs):
        return identifier.Identifier(self._settings, self._language, self._type_list, self._namespace, type_, **kwargs)

    # Add a child generator and return it's instance
    def _add_child(self, call, ids=None, **kwargs):
        # Set ids if none
        if ids is None:
            ids = self._ids

        # Create instance, append to operations and set active state
        gen = call(ids, self._settings, self._language, self._filter, self, **kwargs)
        self._operations.append(gen)
        self.active = gen

        return gen

    # Raise depending on active state
    def _check_active_state(self):
        # Generator is disabled
        if not self.active:
            raise exceptions.GeneratorDisabledError()

        # Generator is inactive
        elif self.active != self:
            raise exceptions.GeneratorInactiveError()

    # Sample from identifiers by a specified range
    def _sample_identifiers(self, range_, ids):
        # Use all identifiers as source if ids is not set
        if ids is None:
            ids = self._ids

        # Sample from identifiers
        start, stop = range_
        try:
            n = random.randrange(start, stop if len(ids) > stop else len(ids))
        except ValueError:
            n = len(ids)
        return random.sample(ids, len(ids) if n > len(ids) else n)

    # Return code pieces (with verifying code if requested)
    def code_pieces(self, options):
        # Save code options so we don't have to pass it to every function
        self._options = options

        # Store amount of indentations
        if 'block' not in self._options:
            self._options['block'] = 1

        # Default and start values
        code = self._code_pieces_default()

        # Add operations
        self._code_pieces_operations(code, self._operations)

        # Add resulting identifiers
        if self._options.get('result'):
            self._code_pieces_result(code)

        # Return dictionary
        return code

    # Return code pieces defaults for code generation
    def _code_pieces_default(self):
        # Code piece dictionary
        code = {key: [] for key in ['requirements', 'prototypes', 'main', 'functions']}

        # Requirements (e.g. includes)
        code['requirements'] = self._requirements

        return code

    # Return code pieces that returns the final values of all identifiers
    def _code_pieces_result(self, code, key='main'):
        # Retrieve result by using a result operation
        indent = self._indent()
        code[key].append(indent + self.get_operation(operations.Result).snapshot_code().replace('\n', '\n' + indent))

    # Append code pieces of all operations inside to a specified key
    def _code_pieces_operations(self, code, operations_, key='main', block=True):
        # Start verify block
        if block and self._options.get('verify'):
            code[key].append(self._code_pieces_verify_start())

        # Loop through operations
        for i, operation in enumerate(operations_):
            # Add separator (if not a function)
            # Note: This is quite nasty... but necessary to avoid JSON corruption
            if i > 0 and self._options.get('verify') and not isinstance(operation, FunctionGenerator):
                code[key].append(self._code_pieces_verify_separator())

            # Generator (child)
            if isinstance(operation, GeneratorChild):
                # Append code of child generator
                self._code_pieces_child(code, operation)

            # Normal operation
            else:
                # Append code of operation
                self._code_pieces_operation(code[key], operation)

        # End verify block
        if block and self._options.get('verify'):
            code[key].append(self._code_pieces_verify_end())

    # Append code pieces of a normal operation
    def _code_pieces_operation(self, code, operation):
        # Get indent
        indent = self._indent()

        # Add operation name (if requested and operation is a normal operation [not special like call, result, ...])
        if self._options.get('comments') and operation.name in BasicGenerator.all_operations:
            code.append(indent + self._language['comment'].format(operation.name))

        # Show result (as hint)
        if self._options.get('identifiers') and operation.assign:
            # Append to code (with bit representation when necessary)
            code.append(operation.hint(bits=(operation.name in operations.bitop)))

        # Add generated code
        code.append(indent + operation.code().replace('\n', '\n' + indent) +
                    ('\n' if not self._options.get('verify') else ''))

        # Add verifying code pieces
        if self._options.get('verify'):
            code.append(indent + operation.snapshot_code(verify=True).replace('\n', '\n' + indent) + '\n')

    # Append code pieces that have been generated by a child
    def _code_pieces_child(self, code, operation):
        # Get code of child
        child = operation.code_pieces(copy.copy(self._options))

        # Extend code lists
        for key, value in child.items():
            code.setdefault(key, []).extend(value)

    # Return code pieces that start a verifying block
    def _code_pieces_verify_start(self):
        return self._indent() + self._language['verify']['id']['start']

    # Return code pieces that separate verifying blocks
    def _code_pieces_verify_separator(self):
        return self._indent() + self._language['verify']['id']['separator']

    # Return code pieces that end a verifying block
    def _code_pieces_verify_end(self):
        return self._indent() + self._language['verify']['id']['end']

    # Maximum identifier depth used in generator
    def _max_identifier_depth(self):
        max_ = {}
        # Loop through identifiers and find the one that has the maximum amount of references
        for id_ in self._ids:
            depth = id_.reference_depth()

            # Value is greater than the current value stored
            if depth > max_.get(id_.type, -1):
                max_[id_.type] = depth

        return max_

    # Return indent (block count) * indent string
    def _indent(self):
        return self._options['block'] * self._language['indent']
