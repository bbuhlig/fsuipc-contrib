--[[
rotfsev: FSUIPC event-based fast/slow event generator for rotary switches
Version 20210620-0-e723f2a

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

This module monitors a set of rotary switches for fast vs. slow
toggling based on a user provided threshold between successive
button events. If the rotary is moved fast enough that consecutive
button events are received within a threshold, a fast virtual button
is sent and successive button events are ignored. Otherwise a slow
virtual button is sent for each button event if consecutive events
are not received within the threshold. If your device is "glitchy"
and regularly generates spurious fast events even when turning
the rotary slowly, you can tell the module to treat a configurable
number of fast events received within a time period as slow events.

Each virtual button can be assigned in the .ini to send FS control
commands and keypresses, such as variable rates for trim adjustments
on an elevator trim wheel, ref p.25 of the Advanced User's Guide.

This module provides a generally similar concept to the Rotaries.lua
approach but takes advantage of buttons that are directly detected by
FSUIPC and is primarily event-based rather than poll-based. Thus it
should be more efficient/performant.

Define the desired buttons according to the array passed to the
init() function at the bottom of the file.
]]

_BtnDefs={}
_SlowBtnSet=-1
_FastCount=0
function _gen_slow_btn()
  event.cancel('_gen_slow_btn')
  if (_SlowBtnSet >= 0) then
     ipc.btnToggle(_SlowBtnSet)
     _SlowBtnSet=-1
     _FastCount=0
  end
end

function _btnevent(j,b,ud)
  local time_ms=ipc.elapsedtime()
  local btninfo=_BtnDefs[j][b]
  if btninfo._fastDeadline <= time_ms then
     if _SlowBtnSet == btninfo.SlowVirtualButton then
        if (_FastCount >= btninfo.FastThreshFilter_cnt) then
           event.cancel('_gen_slow_btn')
           _SlowBtnSet=-1
           _FastCount=0
           ipc.btnToggle(btninfo.FastVirtualButton)
           btninfo._fastDeadline = time_ms + btninfo.FastThresh_ms
        else
           ipc.btnToggle(_SlowBtnSet)
           _FastCount = _FastCount + 1
           event.timer(btninfo.FastThresh_ms,'_gen_slow_btn')
        end
     else
        event.timer(btninfo.FastThresh_ms,'_gen_slow_btn')
        _SlowBtnSet=btninfo.SlowVirtualButton
     end
  end
end

function _convert_joy_letter_to_num(ltr)
  -- TODO implement
  return 2
end

function init(defs)
  local def
  for _,def in ipairs(defs) do
    local joynum = _convert_joy_letter_to_num(def.Joystick)
    if _BtnDefs[joynum] == nil then
       _BtnDefs[joynum] = {}
    end
    _BtnDefs[joynum][def.Button]={
       SlowVirtualButton=def.Slow,
       FastVirtualButton=def.Fast,
       FastThresh_ms=def.FastThresh_ms,
       FastThreshFilter_cnt=def.FastThreshFilter_cnt,
       _fastDeadline=0
    }
    event.button(def.Joystick,def.Button,
                 (def.PressEvent and 1 or 0)+(def.ReleaseEvent and 2 or 0),
                 '_btnevent')
  end
end

function VirtualButton(joy,btn)
  if joy < 64 or joy > 72 then
    error("Bad joy code, must be 64-72, was " + joy)
  elseif btn < 0 or btn > 31 then
    error("Bad btn code, must be 0-31, was " + btn)
  end
  return (joy-64)*32+btn
end


init({
  -- 1st actual rotary button to manage
  {Joystick='B',Button=12, -- inc direction of the inc/dec
   -- trigger event upon button press?
   PressEvent=true,
   -- trigger event upon button release?
   ReleaseEvent=false,
   -- virtual button to generate when turning slowly
   Slow=VirtualButton(70,2),
   -- virtual button to generate when turning fast
   Fast=VirtualButton(70,3),
   -- generate fast vBtn when a new event happens within this threshold of the
   -- last event...
   FastThresh_ms=100,
   -- ... except require this many consecutive fast events before generating
   -- fast vButton (and keep sending slow vButtons each event until that happens.)
   FastThreshFilter_cnt=0},

  -- 2nd actual rotary button to manage
  {Joystick='B',Button=13, -- dec direction of the inc/dec
   PressEvent=true,
   ReleaseEvent=false,
   Slow=VirtualButton(70,1),
   Fast=VirtualButton(70,0),
   FastThresh_ms=100,
   FastThreshFilter_cnt=0},

  -- 3rd actual rotary button to manage
  {Joystick='B',Button=21, -- fwd (trim down) on the trim wheel
   PressEvent=true,
   ReleaseEvent=false,
   Slow=VirtualButton(68,1),
   Fast=VirtualButton(68,0),
   FastThresh_ms=100,
   FastThreshFilter_cnt=0},

  -- 4th actual rotary button to manage
  {Joystick='B',Button=22, -- rev (trim up) on the trim wheel
   PressEvent=true,
   ReleaseEvent=false,
   Slow=VirtualButton(68,2),
   Fast=VirtualButton(68,3),
   FastThresh_ms=100,
   FastThreshFilter_cnt=0}
})
