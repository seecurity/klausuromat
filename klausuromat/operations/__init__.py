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
from .basic import BasicOperation
from .binary import BinaryOperation
from .init import Initialize
from .result import Result
from .call import Call

from .eq_ import Equal
from .ne_ import NotEqual
from .lt_ import LessThan
from .le_ import LessThanOrEqual
from .gt_ import GreaterThan
from .ge_ import GreaterThanOrEqual

from .add_ import Addition
from .and_ import BitwiseAnd
from .div_ import Division
from .lshift_ import LeftShift
from .mod_ import Modulo
from .mul_ import Multiplication
from .or_ import BitwiseOr
from .rshift_ import RightShift
from .sub_ import Subtraction
from .xor_ import BitwiseXor