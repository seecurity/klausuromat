# Externals
import copy

# Internals
import operations
import exceptions
from operations import BasicOperation


# A function call operation
# Result can be assigned to an identifier that can be chosen randomly
class Call(BasicOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Initial target id and code piece
        self._from = None
        self._code = None

        # Set assignment filter
        self._filters[BasicOperation.OperatorAssign] = [self._filter.has_type, self._filter.has_reference_depth]

    # Save code pieces that represent the function call
    call = property(lambda self: self._code, lambda self, value: setattr(self, '_code', value))

    # Save vars and set filter arguments depending on identifier that will be returned
    def set_from(self, from_):
        # Check if the operation is already done
        if self._done:
            raise exceptions.GeneratorOperationDisabledError()

        # Set filter arguments
        self._filter_args['type_'] = from_.type
        self._filter_args['depth'] = from_.reference_depth()

        # Save identifier and code piece
        self._from = from_

    # From identifier property
    from_ = property(lambda self: self._from, set_from)

    # Done, build resulting code and make a snapshot
    def done(self):
        # Get formatter
        formatter = self._language['format'][self.name]

        # Check if the operation is already done
        if self._done:
            raise exceptions.GeneratorOperationDisabledError()

        # Assign
        if self._assign:
            # Check if from identifier has been set
            if not self._from:
                raise exceptions.GeneratorOperationCallFromError()

            # Copy assigned identifier (before)
            self._before_assign = copy.deepcopy(self._assign)

            # Copy value or reference
            if self._from.is_pointer:
                self._assign.reference = self._from.reference
            else:
                self._assign.value = self._from.value

            # Generate code and copy assigned identifier (after)
            self._code = formatter['assign'].format(self._assign.name, self._code)
            self._assign = copy.deepcopy(self._assign)

        # Call
        else:
            # Generate code
            self._code = formatter['call'].format(self._code)

        # Make snapshot
        self.snapshot = copy.deepcopy(self._ids)

        # Done!
        self._done = True

    # Return generated code
    def code(self):
        return self._code

    # Return hint for code
    def hint(self, **_):
        # Previous value of assignment identifier
        reference = self._from.is_pointer
        lines = ['Vorher:  ' + self._before_assign.code(reference=reference),
                 'Nachher: ' + self._assign.code(reference=reference)]

        # Append to code
        return self._language['identifier']['wrapper'].format(self._language['identifier']['separator'].join(lines))

    # Return snapshot of all identifiers
    # Note: Nasty overwrite hack
    def snapshot_code(self, verify=False):
        # Check if this is verifying code
        if verify:
            # Add separator
            return self._language['verify']['id']['separator'] + '\n' + super().snapshot_code(verify=verify)

        # Nope, just a normal print
        else:
            return super().snapshot_code(verify=verify)
