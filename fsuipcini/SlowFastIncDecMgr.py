"""
SlowFastIncDecMgr.py -- Manager of Slow/Fast actions on a Rotary Encoder
Version 20210616-0-4d7af4d

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
from .buttons import btnmap, ButtonAction


class SlowFastIncDecMgr():
   def __init__(self, slow_decr_btn, slow_incr_btn,
                      fast_decr_btn, fast_incr_btn):
      self._slow_decr_btn = slow_decr_btn
      self._slow_incr_btn = slow_incr_btn
      self._fast_decr_btn = fast_decr_btn
      self._fast_incr_btn = fast_incr_btn

   def btnmap(self,ctrl_dec,ctrl_inc,conds=None,fast_ctrl_dec=None,fast_ctrl_inc=None,fast_ctrl_events=1):
      btnmap(self._slow_decr_btn,ctrl_dec,action=ButtonAction.PRESS_AND_RELEASE,conds=conds)
      btnmap(self._slow_incr_btn,ctrl_inc,action=ButtonAction.PRESS_AND_RELEASE,conds=conds)

      for _ in range(fast_ctrl_events):
         btnmap(self._fast_decr_btn,fast_ctrl_dec or ctrl_dec,action=ButtonAction.PRESS_AND_RELEASE,conds=conds)

      for _ in range(fast_ctrl_events):
         btnmap(self._fast_incr_btn,fast_ctrl_inc or ctrl_inc,action=ButtonAction.PRESS_AND_RELEASE,conds=conds)

   def btnmapgroup(self,ctrl_dec,ctrl_inc,group_conds=[],fast_ctrl_dec=None,fast_ctrl_inc=None,fast_ctrl_events=1,all_conds=[]):

      if not isinstance(group_conds,list):
         group_conds = [ group_conds ]

      self.btnmap(ctrl_dec,ctrl_inc,
                  conds=all_conds+group_conds,
                  fast_ctrl_dec=fast_ctrl_dec,
                  fast_ctrl_inc=fast_ctrl_inc,
                  fast_ctrl_events=fast_ctrl_events)

