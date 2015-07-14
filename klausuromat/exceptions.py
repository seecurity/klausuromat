# General generator error
class GeneratorError(Exception):
    def __init__(self, msg, **kwargs):
        self.msg = msg

        # Add optional arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return self.msg


# General identifier error
class GeneratorIdentifierError(GeneratorError):
    pass


# Compile error
class GeneratorCompileError(GeneratorError):
    pass


# Verify error
class GeneratorVerifyError(GeneratorError):
    pass


# Operation is not defined
class GeneratorOperationUnknownError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Unknown operation "{}"'.format(self.name)


# Generation not possible (ran out of operations)
class GeneratorGenerationNotPossibleError(GeneratorError):
    pass


# General JSON error
class GeneratorJSONError(GeneratorError):
    pass


# JSON key is not defined
class GeneratorJSONKeyError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return 'Key "{}" missing in JSON file'.format(self.key)


# Unknown data type
class GeneratorUnknownDataTypeError(Exception):
    def __init__(self, nr):
        self.nr = nr

    def __str__(self):
        return 'Unknown data type "{}"'.format(self.nr)


# Incompatible data types (tried to reference an incompatible identifier)
class GeneratorIncompatibleDataTypesError(Exception):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

    def __str__(self):
        return 'Incompatible data types: "{}" and "{}" are not the same data type'.format(self.src, self.dst)


# Operation not possible (ran out of identifiers)
class GeneratorOperationNotPossibleError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Operation "{}" not possible (ran out of identifiers)'.format(self.name)


class GeneratorOperationSnapshotError(Exception):
    def __str__(self):
        return 'Operation has no snapshot'


# Operation is enabled (not done)
class GeneratorOperationEnabledError(Exception):
    def __str__(self):
        return 'Operation is still enabled. Call method "done" before trying to retrieve code.'


# Operation is disabled (already done)
class GeneratorOperationDisabledError(Exception):
    def __str__(self):
        return 'Operation is already disabled. Changes to operands are not allowed anymore.'


# Operation Call is missing the identifier that represents the function return
class GeneratorOperationCallFromError(Exception):
    def __str__(self):
        return 'Operation (function call) will be assigned but no return value has been set'


# Generator has been disabled
class GeneratorDisabledError(Exception):
    def __str__(self):
        return 'Generator is disabled'


# Generator is inactive
class GeneratorInactiveError(Exception):
    def __str__(self):
        return 'Generator is inactive'


# General conditional error
class GeneratorConditionalError(GeneratorError):
    pass


# Conditional condition is unknown
class GeneratorConditionalUnknownConditionError(Exception):
    def __init__(self, instance):
        self.instance = instance

    def __str__(self):
        return 'Could not retrieve value of condition: {}'.format(self.instance)


# Random generator setting exception (explains)
class RandomGeneratorSettingError(GeneratorError):
    pass
