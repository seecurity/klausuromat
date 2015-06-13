from klausuromat.identifier import Identifier


# A generic class to filter identifiers
class IdentifierFilter:
    # Data types that are numbers
    numbers = (Identifier.DataType.INT, Identifier.DataType.CHAR, Identifier.DataType.FLOAT, Identifier.DataType.DOUBLE)
    integers = (Identifier.DataType.INT, Identifier.DataType.CHAR)

    # Constructor
    def __init__(self, settings):
        # Set settings
        self.settings = settings

    # Apply multiple filter to a list and return a filtered list
    def apply(self, filters, iterable, **kwargs):
        # Make tuple of filters if none
        try:
            iter(filters)
        except TypeError:
            filters = (filters,)

        # Apply filter(s)
        for filter_ in filters:
            iterable = list(filter(lambda a: filter_(a, **kwargs), iterable))

        # Return filtered
        return iterable

    # Check if an item matches the required filters
    def match(self, filters, item, **kwargs):
        # Make tuple of filters if none
        try:
            iter(filters)
        except TypeError:
            filters = (filters,)

        # Apply filter(s)
        for filter_ in filters:
            # Check if filter returned False
            if not filter_(item, **kwargs):
                return False

        # Nothing failed
        return True

    # Retrieve numbers
    def is_number(self, a, **_):
        return a.type in self.numbers

    # Retrieve non zero numbers
    def is_number_non_zero(self, a, **_):
        return self.is_number(a) and a.value != 0

    # Retrieve integers
    def is_integer(self, a, **_):
        return a.type in self.integers

    # Retrieve numbers that are allowed for bit shifting
    def is_shift_counter(self, a, **_):
        return self.is_integer(a) and 0 < a.value <= self.settings['MAX_SHIFT_BITS']

    # Retrieve identifiers that have a specific type
    def has_type(self, a, type_=None, **_):
        return a.type == type_

    # Retrieve identifiers that have a reference
    def has_reference(self, a, **_):
        return a.reference is not None

    # Retrieve identifiers that have a specific reference depth
    def has_reference_depth(self, a, depth=0, **_):
        return a.reference_depth() == depth

    # Retrieve identifiers that will be called by a specific type
    def is_called_by(self, a, type_=None, **_):
        return (type_ == Identifier.CallBy.VALUE and not a.called_by_reference) or \
               (type_ == Identifier.CallBy.REFERENCE and a.called_by_reference)
