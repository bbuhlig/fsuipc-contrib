"""
utils.py -- General module utlities
Version 20210616-0-98035cd

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
import re
import inspect
import string
import traceback
from . import _globals

def _init_section():
   _gen_trace_dict()

   _globals.Section_idx = 0
   _globals.Trace_file_idx=0
   _globals.Trace_file_dict=dict()

def section(header,fixed_tokens=None):
   _init_section()
   print()
   print(f'[{header}]')
   if fixed_tokens:
      if isinstance(fixed_tokens,dict):
         for key,value in fixed_tokens.items():
            print(f'{key}={value} ;{gen_trace_str()}')
      else:
         print(fixed_tokens)

def end_section():
   _init_section()

def val(x):
   if hasattr(x,'value'):
      return x.value
   elif hasattr(x,'_value_'):
      return x._value_
   else:
      return x

def filter_ini(fn,*argv):
   with open(fn,'r') as ini_ifh:
      copythru = True
      for line in ini_ifh.read().splitlines():
         section_match = re.match("^\[(?P<section>[^\.]+).*?\]",line)
         if section_match:
            copythru = all(section_match.group('section') != arg for arg in argv)
         if copythru:
            print(line)


_N2alpha = dict(zip(range(1, 27), string.ascii_lowercase))



# Based on https://stackoverflow.com/a/58204926
_N2alphadict = dict(zip(range(1, 27), string.ascii_lowercase))
def _n2alphacode(v):
   n = v // 26
   r = (1+v) % 26
   return f'{n2alphacode(n-1) if n > 0 else ""}{_N2alphadict[r] if r > 0 else "z"}'

def gen_trace_str():
   infelems=list()
   last_file=None
   for frame, b in traceback.walk_stack(inspect.currentframe().f_back.f_back):
      cur_file=frame.f_globals["__file__"]
      cur_file_code = _globals.Trace_file_dict.get(cur_file,None)
      if not cur_file_code:
         cur_file_code = _n2alphacode(_globals.Trace_file_idx)

         _globals.Trace_file_dict[cur_file] = cur_file_code
         _globals.Trace_file_idx += 1
         
      infelems.append(f'{cur_file_code}{frame.f_lineno}')

   trace_str =';'.join(infelems)
   if len(trace_str) > 64:
      trace_str=f'~{trace_str[-64:]}'

   return trace_str

def _gen_trace_dict():
   for filename, code in sorted(_globals.Trace_file_dict.items(),
                                key=lambda x: x[1]):
      dictstr1 = f'{code}>'
      dictstr2 = filename
      if len(dictstr1) + len(dictstr2) > 64:
         short_dictstr2_len = 63-len(dictstr1)
         dictstr2 = f'~{filename[-short_dictstr2_len:]}'

      _globals.Section_idx += 1 
      print(f'{_globals.Section_idx}=;{dictstr1}{dictstr2}')
 
