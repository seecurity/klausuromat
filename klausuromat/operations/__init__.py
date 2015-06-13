# Usable operations
__all__ = ['BasicOperation', 'BinaryOperation', 'Initialize', 'Result', 'Call',
           'Equal', 'NotEqual', 'LessThan', 'LessThanOrEqual', 'GreaterThan', 'GreaterThanOrEqual'
           'Addition', 'BitwiseAnd', 'Division', 'LeftShift', 'Modulo', 'Multiplication', 'BitwiseOr', 'RightShift',
           'Subtraction', 'BitwiseXor']

# Operations that can be choosen randomly from
all_ = ['Addition', 'BitwiseAnd', 'Division', 'LeftShift', 'Modulo', 'Multiplication', 'BitwiseOr', 'RightShift',
        'Subtraction', 'BitwiseXor']

# Basic arithmetic operations
arithmetic = ['Addition', 'Division', 'Multiplication', 'Subtraction']

# Bitwise operators
bitwise = ['BitwiseAnd', 'BitwiseOr', 'BitwiseXor']

# Bit shifts
shift = ['LeftShift', 'RightShift']

# Bit operations
bitop = shift + bitwise

# Special operations
special = ['Modulo']

# Import all submodules as classes
from operations.basic import BasicOperation
from operations.binary import BinaryOperation
from operations.init import Initialize
from operations.result import Result
from operations.call import Call

from operations.eq_ import Equal
from operations.ne_ import NotEqual
from operations.lt_ import LessThan
from operations.le_ import LessThanOrEqual
from operations.gt_ import GreaterThan
from operations.ge_ import GreaterThanOrEqual

from operations.add_ import Addition
from operations.and_ import BitwiseAnd
from operations.div_ import Division
from operations.lshift_ import LeftShift
from operations.mod_ import Modulo
from operations.mul_ import Multiplication
from operations.or_ import BitwiseOr
from operations.rshift_ import RightShift
from operations.sub_ import Subtraction
from operations.xor_ import BitwiseXor