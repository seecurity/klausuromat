# Define usable operations
__all__ = ['BasicGenerator', 'CodeGenerator', 'RandomCodeGenerator',
           'GeneratorChild', 'FunctionGenerator', 'ConditionalGenerator']

# Import all submodules as classes
from generator.basic import BasicGenerator
from generator.code import CodeGenerator
from generator.random import RandomCodeGenerator

from generator.child import GeneratorChild
from generator.function import FunctionGenerator
from generator.if_else import ConditionalGenerator