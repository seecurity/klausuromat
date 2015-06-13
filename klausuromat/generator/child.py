# Externals
import logging
import copy

# Internals
import generator


# Generator that can build (verifying) code but is not able to compile it
# This is an interface for child classes that can be added to a BasicGenerator
class GeneratorChild(generator.BasicGenerator):
    # Initialize
    #noinspection PyProtectedMember,PyMissingConstructor
    def __init__(self, settings, language, filter_, parent):
        # Save parent generator instance
        self.parent = parent

        # Save some stuff
        self._settings = settings
        self._language = language
        self._filter = filter_

        # Save initial values
        self._options = {}
        self._requirements = []
        self._active = self
        self._namespace = copy.copy(parent._namespace)
        self._ids = []
        self._operations = []

        # Log class
        logging.info('Created instance of "{}"'.format(self.__class__.__name__))

    # Set active generator or disable (False)
    def set_active(self, value):
        # Call super method
        super().set_active(value)

        # Set parent generator attribute to parent if this generator is disabled
        if not value:
            self.parent.active = self.parent

    # Active property
    active = property(lambda self: self._active, set_active)
