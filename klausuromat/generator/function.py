import random

from klausuromat import exceptions, operations
from .child import GeneratorChild


# Function generator
class FunctionGenerator(GeneratorChild):
    # Function names
    names = [
        'kirk', 'spock', 'mccoy', 'scott', 'sulu', 'uhura', 'chekov', 'chapel',
        'picard', 'riker', 'data', 'la_forge', 'worf', 'crusher', 'pulaski', 'troi', 'yar', 'guinan',
        'sisko', 'nerys', 'odo', 'bashir', 'dax', 'o_brien', 'quark',
        'garak', 'martok', 'gowron', 'rom', 'nog', 'leeta', 'dukat', 'weyoun',
        'janeway', 'chakotay', 'tuvok', 'torres', 'paris', 'kim', 'the_doctor', 'neelix', 'kes',
        'archer', 't_pol', 'tucker', 'reed', 'sato', 'mayweather', 'phlox',
        'Q'
    ]

    # Initialize
    def __init__(self, ids, *args, name=None):
        # Let parent class do all the initializing stuff
        super().__init__(*args)

        # Set namespace to an empty set
        self._namespace = set()

        # Default return identifier
        self._return = None

        # Virtually pass identifiers to function
        self._ids = [id_.pass_to_function(self._namespace) for id_ in ids]

        # Choose random name if none specified
        if name is None:
            index = random.randrange(0, len(FunctionGenerator.names))
            self.name = FunctionGenerator.names.pop(index)

    # Set identifier that will be returned
    def set_return(self, value):
        # Check if identifier is in list
        if value not in self._ids:
            raise exceptions.GeneratorIdentifierError('Identifier is not in the current namespace')

        self._return = value

    # Return property
    return_ = property(lambda self: self._return, set_return)

    # Choose random identifier that will be returned
    def return_random(self):
        # Choose randomly of a type that is present in main function
        self._return = random.choice(self._filter_return_identifiers())

    # String representation of return type
    type_str = property(lambda self: self._return.type_str
                        if self._return is not None
                        else self._language['function']['noneType'])

    # Call function (disables this generator)
    def call(self):
        # Disable self and reactivate parent generator
        self.active = False

        # Add call operation to parent
        operation = self.parent.get_operation(operations.Call)
        # Set call code piece
        operation.call = self._code_pieces_call()
        # Let operation know we're done
        operation.done()
        # Add operation to parent
        self.parent.add_operation(operation)

    # Assign function (disables this generator)
    def assign(self, ids=None):
        # Disable self and reactivate parent generator
        self.active = False

        # Choose return identifier if not present
        if self.return_ is None:
            self.return_random()

        # Get assign operation from parent
        operation = self.parent.get_operation(operations.Call)
        # Set call code piece
        operation.call = self._code_pieces_call()
        # Set identifier that will be returned
        operation.from_ = self.return_
        # Assign a random (or specified) identifier to the function return
        operation.assign = ids
        # Let operation know we're done
        operation.done()
        # Add operation to parent
        self.parent.add_operation(operation)

    # Get all identifiers of this generator that are not greater than a maximum depth specified by the parent generator
    def _filter_return_identifiers(self):
        #noinspection PyProtectedMember
        max_ = self.parent._max_identifier_depth()
        return [id_ for id_ in self._ids
                if id_.reference_depth() <= max_.get(id_.type, self._settings['POINTER_DEPTH_MAX'])]

    # Return code pieces (with verifying code if requested)
    def code_pieces(self, options):
        # Save code options so we don't have to pass it to every function
        self._options = options

        # Default and start values
        code = self._code_pieces_default()

        # Build prototype & function head
        code['prototypes'].append(self._code_pieces_prototype())
        code['functions'].append(self._code_pieces_function())

        # Build function call
        if self._options.get('comments'):
            code['main'].append(self._indent() + self._language['comment'].format('Function ' + self.name))

        # Reset block
        self._options['block'] = 1

        # Add operations
        self._code_pieces_operations(code, self._operations, key='functions')

        # Add resulting identifiers
        if self._options.get('result'):
            self._code_pieces_result(code, key='functions')

        # Add return
        # Note: Nothing can be added to this function afterwards!
        if self.return_:
            code['functions'].append(self._code_pieces_return())

        # Build function bottom
        code['functions'].append(self._language['function']['bottom'])

        # Return dictionary
        return code

    # Return formatted arguments
    def _code_pieces_arguments(self, format_, argument_format):
        # Build and format argument list
        formatter, separator = argument_format
        arguments = separator.join([formatter.format(id_) for id_ in self._ids])

        # Wrap arguments
        return format_.format(self, arguments)

    # Return code pieces that represent a function prototype
    def _code_pieces_prototype(self):
        return self._code_pieces_arguments(self._language['function']['prototype'],
                                           self._language['function']['argument'])

    # Return code pieces that represent the head of a function
    def _code_pieces_function(self):
        return self._code_pieces_arguments(self._language['function']['top'],
                                           self._language['function']['argument'])

    # Return code pieces that represent a function call
    def _code_pieces_call(self):
        return self._code_pieces_arguments(self._language['function']['call']['format'],
                                           self._language['function']['call']['argument'])

    # Return code pieces that represent the return value
    def _code_pieces_return(self):
        return self._indent() + self._language['function']['return'].format(self.return_)
