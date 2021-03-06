"""
buttons.py -- Button helpers
Version 20210620-0-f6d579c

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
from .utils import val, gen_trace_str
from . import _globals
from .offsets import OffsetCondition
from . import controls


class ButtonAction(Enum):
   REPEAT  = 'R'
   RELEASE = 'U'
   PRESS   = 'P'
   HOLD    = 'H'
   PRESS_AND_RELEASE = ''

class ButtonCondition:
   class Test(Enum):
      PRESSED  = {False:'-',  True:'+' }
      FLAG_SET = {False:'F-', True:'F+'}

   def __init__(self, joycode, btncode, condition_test, condition_state):
      self._joycode = joycode
      self._btncode = btncode
      self._condition_test = condition_test
      self._condition_state = condition_state

   def __str__(self):
      return ''.join(map(str,[
                      '(',
                      self._condition_test.value[bool(self._condition_state)],
                      self._joycode, ',', self._btncode, ')']))

class ButtonEnum(Enum):
   @property
   def joycode(self):
      return f'{val(self.JoystickCode)},{val(self)}'

   @property
   def CondPressed(self):
      return ButtonCondition(self.JoystickCode,val(self),
                             ButtonCondition.Test.PRESSED,True)

   @property
   def CondNotPressed(self):
      return ButtonCondition(self.JoystickCode,val(self),
                             ButtonCondition.Test.PRESSED,False)

   @property
   def CondFlagSet(self):
      return ButtonCondition(self.JoystickCode,val(self),
                             ButtonCondition.Test.FLAG_SET,True)

   @property
   def CondFlagClear(self):
      return ButtonCondition(self.JoystickCode,val(self),
                             ButtonCondition.Test.FLAG_SET,False)

   # Use this property to get the button's encoding for the params
   # for Toggle_button_flag, Set_button_flag and Clear_button_flag
   # APIs exposed by FSUIPC (ref Advanced Users Guide p.26)
   @property
   def ButtonFlagAPIParamCode(self):
      if not isinstance(self.JoystickCode,int):
         raise ValueError(f'button JoystickCode is {self.JoystickCode}, but ButtonFlagAPIParamCode only supports JoyNumbers. You probably need to use Lua for this.')

      return 256*self.JoystickCode+val(self)

   def _virt_btn_ctrl(self):
      if self.JoystickCode < 64 or self.JoystickCode > 72:
         raise RuntimeError(f"Bad JoystickCode {self.JoystickCode}, must be 64-72")

      btncode=val(self)
      if btncode < 0 or self.JoystickCode > 31:
         raise RuntimeError(f"Bad button code {btncode}, must be 0-31")

      return OffsetCtrl(offset=0x3340+((self.JoystickCode-64) *4),
                        size=OffsetSize.Int32, llimit=0, ulimit=31)

   # Use this property to get the offset control for pressing the virtual button
   @property
   def VirtPress(self):
      return self._virt_btn_ctrl.op(OffsetCtrl.Operation.Setbits,1 << val(self))

   # Use this property to get the offset control for releasing the virtual button
   @property
   def VirtRelease(self):
      return self._virt_btn_ctrl.op(OffsetCtrl.Operation.Clearbits,1 << val(self))

   # Use this property to get the offset control for toggling the virtual button
   @property
   def VirtToggle(self):
      return self._virt_btn_ctrl.op(OffsetCtrl.Operation.Togglebits,1 << val(self))


def btnmap(button,control,conds=[],action=ButtonAction.PRESS):

   if action == ButtonAction.PRESS_AND_RELEASE:
      act = [ButtonAction.PRESS,ButtonAction.RELEASE]
   else:
      act = [action]

   param = 0

   while not hasattr(control,'ctrlcode') and not isinstance(control,tuple):
      control = val(control)

   if hasattr(control,'ctrlparam'):
      param = control.ctrlparam
   elif isinstance(control,tuple):
      control, param = control

   for action in act:
      s = val(action)

      if not isinstance(conds,list):
         conds=[conds]

      offset_conditions=list()
      button_conditions=list()
      for cond in conds:
         if isinstance(cond, OffsetCondition):
            offset_conditions.append(cond)
         elif hasattr(cond, 'CondPressed'): # ButtonEnum duck-typing
            button_conditions.append(cond.CondPressed) # Default ButtonEnum's to their CondPressed
         else: # ButtonCondition, or string ... either way append it raw
            button_conditions.append(cond)


      if len(button_conditions) > 0:
         s = f"C{s}{''.join(map(lambda x : str(val(x)),button_conditions))}"

      if len(offset_conditions) > 0:
         s = f"{' '.join(map(str,offset_conditions))} {s}"

      if hasattr(control,'ctrlcode'):
         ctrlcode=control.ctrlcode
      else:
         ctrlcode=control


      s = s + f'{val(button.joycode)},{ctrlcode},{val(param)}'

      _globals.Section_idx += 1

      print(f'{_globals.Section_idx}={s} ;{gen_trace_str()}')

