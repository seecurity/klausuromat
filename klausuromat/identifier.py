# Externals
import random
import string

# Internals
import exceptions
import enumerator


# Identifier representation
class Identifier:
    # Supported data types
    DataType = enumerator.Enum(INT=0, CHAR=1, FLOAT=2, DOUBLE=3)
    # Supported calls
    CallBy = enumerator.Enum(VALUE=0, REFERENCE=1)
    # Identifier names
    names = string.ascii_lowercase

    # Storage
    def __init__(self, settings, language, type_list, namespace, type_,
                 name=None, value=None, reference=None, call_by=None, from_=None):
        # Check if value and reference have been set at the same time
        if value is not None and reference is not None:
            raise exceptions.GeneratorIdentifierError(
                'It is not possible to set a reference (e.g. a pointer to another identifier)'
                'and a value at the same time')

        # Set stuff
        self._name = None
        self._value = None
        self._reference = None
        self._call_by = None

        # Set necessary settings
        self._settings = settings
        self._language = language
        self.type_list = type_list
        self._namespace = namespace

        # Set start attributes
        self.type = type_
        self.from_ = from_
        self.name = name
        self.reference = reference
        self.call_by = call_by

        # Generate random value if no reference has been specified and value is None
        if value is None and reference is None:
            multiplicator = self._settings['IDENTIFIER_FLOAT_MULTIPLICATOR'] \
                if self.type == Identifier.DataType.FLOAT or self.type == Identifier.DataType.DOUBLE \
                else 1
            self.value = multiplicator * random.randrange(*self._settings['IDENTIFIER_VALUE_RANGE'])

        # Set value
        if value is not None:
            self.value = value

    # Representation
    def __repr__(self):
        data = self.type_str, self.name, \
            '{} = {}'.format(self.reference.address, self.value) if self.is_pointer else self.value
        return str(data)

    # Code reprsentation
    def code(self, reference=False, calculation=None, bits=False):
        # Build formatter depending on whether there is a calculation string or not
        formatter = '{{}} = {} = {{}}'.format(calculation) if calculation else '{} = {}'

        # Return reference of reference (as address)
        if reference:
            return formatter.format(self.name, self.reference.address)

        # Return value of origin
        else:
            return formatter.format(self.dereference, bin(int(self.origin.value)) if bits else self.origin.value)

    # Returns another instance of this identifier depending on how it's virtually passed to a function
    # (by value or by reference)
    def pass_to_function(self, namespace, name=None):
        settings = (self._settings, self._language, self.type_list, namespace, self.type, name)

        # Call by value
        if self.call_by == Identifier.CallBy.VALUE:
            # Copy value (if not pointer) or reference (if pointer)
            value = reference = None
            if self.is_pointer:
                reference = self.reference
            else:
                value = self.value

            new_id = Identifier(*settings, value=value, reference=reference, from_=self.name)

        # Call by reference
        else:
            new_id = Identifier(*settings, reference=self, from_=self.address)

        # Return new instance
        return new_id

    # Set name (or choose randomly)
    def set_name(self, value):
        # Delete previous name
        if self._name is not None:
            self.namespace.remove(self._name)

        # List of available names
        available = [name for name in Identifier.names if name not in self.namespace]

        # Choose randomly if none
        if value is None:
            value = random.choice(available)

        # Check if identifier is not in namespace
        if value not in self.namespace:
            self.namespace.add(value)
            self._name = value

        # Identifier is already listed in this namespace
        else:
            raise exceptions.GeneratorIdentifierError("Duplicate identifier names detected")

    # Name property
    name = property(lambda self: self._name, set_name)

    # Set namespace (add own identifier name)
    def set_namespace(self, value):
        # Delete current name as the namespace has changed
        self._name = None

        # Save new namespace
        self._namespace = value

    # Namespace property
    namespace = property(lambda self: self._namespace, set_namespace)

    # Check if reference is an identifier and has the same type
    def set_reference(self, reference):
        # No reference -> not a pointer
        if reference is None:
            self._reference = None

        # Reference has the same type
        elif reference.type == self.type:
            self._reference = reference

        # Reference types are incompatible
        else:
            raise exceptions.GeneratorIncompatibleDataTypesError(self.type_str, reference.type_str)

    # Reference property
    reference = property(lambda self: self._reference, set_reference)

    # Set identifier and convert value according to type
    def set_value(self, value):
        # Pointer
        if self.reference is not None:
            self.reference.value = value

        # Integer / Char
        if self.type == Identifier.DataType.INT or self.type == Identifier.DataType.CHAR:
            self._value = int(value)

        # Float / Double
        elif self.type == Identifier.DataType.FLOAT or self.type == Identifier.DataType.DOUBLE:
            self._value = float(value)

        # Unknown type
        else:
            raise exceptions.GeneratorUnknownDataTypeError(self.type)

    # Value property
    value = property(lambda self: self.reference.value if self.is_pointer else self._value, set_value)

    # Set call by value/reference if passed to a function
    def set_call_by(self, value):
        # Choose randomly if none
        if value is None:
            value = random.choice([self.CallBy.VALUE, self.CallBy.REFERENCE])

        # Set value
        self._call_by = value

    # Call by property
    call_by = property(lambda self: self._call_by, set_call_by)

    # Pointer depth (number of references until value)
    def reference_depth(self, count=0):
        # No reference
        if self.reference is None:
            return count

        # Call counter of reference
        return self.reference.reference_depth(count + 1)

    # Instance of identifier after dereferencing
    origin = property(lambda self: self.reference.origin if self.is_pointer else self)

    # Check if identifier is a pointer
    is_pointer = property(lambda self: self.reference is not None)

    # The amount of '*' until the value has been reached
    dereference_asterisks = property(lambda self: self._language['dereference'] * self.reference_depth())

    # Assign value representation (dereference if pointer)
    dereference = property(lambda self: self.dereference_asterisks + self.name)

    # Address identifier representation
    address = property(lambda self: self._language['addressing'] + self.name)

    # String representation of type
    type_str = property(lambda self: self.type_list[self.type] + self.dereference_asterisks)

    # Check if this identifier will be called by reference, e.g. is called by reference or has a reference
    called_by_reference = property(lambda self: self.call_by == Identifier.CallBy.REFERENCE or self.reference is not None)
