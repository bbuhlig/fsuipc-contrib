"""
controls.py -- Controls helper
Version 20210616-0-102b38e

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
from enum import Enum
from .utils import val
import re

class Control:
   def GetFullName(self,enumval):
      return self.__class__._FullNameData.get(enumval.name,None)

   @property
   def ctrlcode(self):
      return f'{self.__class__._CtrlIdPrefix}{val(self)}'



def CreateControls(enumtypename,fn,
                   ctrl_id_pfx='',
                   name_filt_fn=None,
                   calling_module=None,
                   raw_name_regex="[\w\.]+"):
   enum_data=dict()
   full_name_data=dict()
   with open(fn,'r') as ctrls_ifh:
      for line in ctrls_ifh.read().splitlines():
         ctrl_match = re.match(f"^(?P<ctrl_num>\d{{4,}})\s+(?P<raw_name>{raw_name_regex})",line)
         if ctrl_match:
             raw_name = ctrl_match.group('raw_name')
             ctrl_name = name_filt_fn(raw_name) if name_filt_fn else raw_name
             enum_data[ctrl_name] = ctrl_match.group('ctrl_num')
             full_name_data[ctrl_name] = raw_name
   if calling_module:
      enumclass = Enum(value=enumtypename,names=enum_data,type=Control,module=calling_module)
   else:
      enumclass = Enum(value=enumtypename,names=enum_data,type=Control)
   enumclass._FullNameData = full_name_data
   enumclass._CtrlIdPrefix = ctrl_id_pfx
   return enumclass


