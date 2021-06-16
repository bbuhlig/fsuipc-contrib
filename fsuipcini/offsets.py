"""
offsets.py -- Offsets helper
Version 20210616-0-0a8f870

The MIT License (MIT)
Copyright © 2021 Blake Buhlig

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
“Software”), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom
the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


Description:

WARNING: This is a prototype work-in-progress; expect problems.

TODO

"""
from .controls import Control
from .utils import val
from enum import Enum

class OffsetSize(Enum):
   def __init__(self,ctrlcode,condcode):
      self.ctrlcode=ctrlcode
      self.condcode=condcode

   Float32 = (0,None)
   Byte    = (1,'B')
   Int8    = (1,'B')
   Word    = (2,'W')
   Int16   = (2,'W')
   DWord   = (3,'D')
   Int32   = (3,'D')
   Float64 = (4,None)


class OffsetCondition:
   class Test(Enum):
      EQUAL = '='
      NOT_EQUAL = '!'
      LESS_THAN = '<'
      GREATER_THAN = '>'

   def __init__(self,size,offset,condvalue,mask=None,test=Test.EQUAL):

      self._size_condcode = size.condcode
      self._offset = offset
      self._condvalue = condvalue
      self._mask = mask
      self._test = test

   def __str__(self):
      offset = self._offset
      mask_out = f'&x{self._mask:%X}' if self._mask is not None else ''
      test = self._test.value
      condvalue = self._condvalue

      retval = f'{self._size_condcode}{offset:04X}{mask_out}{test}{condvalue}'
      return retval


class OffsetCtrl(Control):
   _CtrlIdPrefix = 'C'

   _BITSHIFT_OPERATION = 26
   class Operation(Enum):
      Set               =  0
      Setbits           =  1
      Clrbits           =  2
      Togglebits        =  3
      IncrementUnsigned =  4
      DecrementUnsigned =  8
      IncrementSigned   = 12
      DecrementSigned   = 16
      IncrementCyclic   = 20
      DecrementCyclic   = 24
      FloatSet          = 28
      FloatInc          = 30

   @property
   def operation_is_decrement(self):
      return (val(self._operation) & val(self.__class__.Operation.DecrementUnsigned) != 0)

   _BITSHIFT_SIZE = 24

   @property
   def value(self):
      c = self._operation.value << self.__class__._BITSHIFT_OPERATION
      c = c | self._size_ctrlcode << self.__class__._BITSHIFT_SIZE
      c = c | self.offset

      return f'x{c:08X}'

   def __init__(self,offset,size,llimit=0,ulimit=0):
      self.offset = val(offset)
      self._size_ctrlcode = size.ctrlcode
      self._llimit = val(llimit)
      self._ulimit = val(ulimit)

   def op(self,operation,operand):
      self._operation = operation
      limit = val(self._llimit if self.operation_is_decrement else self._ulimit)
      param = ((limit << 16) | operand) & 0xFFFFFFFF

      return (self, f'x{param:08X}')



class OffsetValEnum(Enum):
   def __init__(self,value):

      if hasattr(self.__class__,'llimit'):

         if self.__class__.llimit > value:
            self.__class__.llimit = value

         if self.__class__.ulimit < value:
            self.__class__.ulimit = value

         self.__class__.Ctrl = OffsetCtrl(offset = self.__class__.Offset.value,
                                          size   = self.__class__.Size.value,
                                          llimit = self.__class__.llimit,
                                          ulimit = self.__class__.ulimit)

      elif hasattr(self.__class__,'Offset') and hasattr(self.__class__,'Size'):
         self.__class__.llimit = value
         self.__class__.ulimit = value

   @property
   def equal_condition(self):

      return OffsetCondition(size = self.__class__.Size.value,
                             offset = self.__class__.Offset.value,
                             condvalue = val(self))

