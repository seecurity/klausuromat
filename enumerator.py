# Basic enumerator
class Enum:
    # Initialize
    def __init__(self, **enums):
        # Set enumerations
        for key, value in enums.items():
            setattr(self, key, value)

        # Store values
        self.__values = enums.values()

        # Set length
        self.__len = len(enums)

    # Get length
    def __len__(self):
        return self.__len

    # Check if item is in values
    def __contains__(self, item):
        return item in self.__values
