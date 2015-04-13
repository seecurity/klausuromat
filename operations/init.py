# Externals
import copy

# Internals
from operations import BasicOperation


# Initialization & definition of predefined identifiers
class Initialize(BasicOperation):
    # Constructor
    def __init__(self, *args):
        # Do all the initializing stuff
        super().__init__(*args)

        # Generate initializing code, make snapshot and disable self
        self._build_code()
        self.snapshot = copy.deepcopy(self._ids)
        #self._code = None
        self._done = True

    # Return generated code
    def code(self):
        return self._code

    # Generate the code we will print later
    def _build_code(self):
        # Get formatter
        formatter = self._language['format'][self.name]['code']

        # Loop through identifiers
        id_list = []
        for id_ in self._ids:
            # No value
            if (not id_.is_pointer and id_.value is None) or (id_.is_pointer and id_.reference is None):
                code = formatter['2'].format(id_.type_str, id_.name)

            # Not a pointer and value specified
            elif not id_.is_pointer:
                code = formatter['3'].format(id_.type_str, id_.name, id_.value)

            # Identifier is a pointer and has a reference
            else:
                code = formatter['3'].format(id_.type_str, id_.name, id_.reference.address)

            # Append to id list
            id_list.append(code)

        # Join all the code pieces
        self._code = '\n'.join(id_list)
