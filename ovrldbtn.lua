--[[
ovrldbtn - event-based manager of an overloaded button for FSUIPC
Version 20210616-0-27a8a7f

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

This module implements the "overloading" of a joystick button to control
multiple actions by mapping various patterns of clicking that button to those
different actions. The basic supported pattern is a train of consecutive button
clicks, and a variant is the train of clicks except with the final click
continuing to be held down. Different actions are signaled by changing the
length of consecutive clicks or click-and-holds. For example, the actions on
the overloaded button as noted below left, could trigger the corresponding
actions below right.

- single click and release : reset view
- single click and hold    : transmit voice while held
- double click and release : toggle view zoom
- double click and hold    : enable 2nd use of other buttons while held
- triple click and release : toggle internal/external view
- triple click and hold    : enable 3rd use of other buttons while held

Each click and release sequence toggles a different virtual button, to which
you can assign in the INI file like any physical button. Similarly each click
and hold sequence will press a virtual button during the hold and will
release the virtual button once the overloaded joystick button is released.
Upon detecting a particular sequence, the module will play a short audio
WAV file as feedback to you about what it detected.

The module implements a similar concept as TripleUse.lua but can handle an
arbitrarily long click sequence, manages virtual buttons instead of directly
using lua calls to trigger the associated actions, is event-based for better
efficiency compared to polling, and manages the sound feedback.

Presently the module supports managing a single overloaded button. To manage
multiple buttons, you could make copies of this script under different names
so that an additional lua thread is launched for each additional button.

See the below CONFIGURATION section for parameters to configure as well as
more detailed documentation. A first time user might have a hard time
understanding some of the details, because tradeoffs in some of the settings
are subtle. Thus I recommend starting out with the defaults in the more complex
parameters until you have had a chance to experiment, after which point some of
the subtle points should become clearer.

One piece of mandatory "configuration" you will need to deal with is the
installation of the audio WAV files, so that part is discussed now.


AUDIO FEEDBACK

The framework gives audible feedback on the detected click and clkNhold actions
by playing WAV files.

As an example, in my setup I generated generate morse code WAV files from
https://www.meridianoutpost.com/resources/etools/calculators/calculator-morse-code.php
per the below table, so that the dit's and dah's correspond to the
sequence of clicks and holds. 

Letter    Morse Code   Representing
 ===      =====        ======================
  E       .            single click
  T       -            single click-and-hold
  I       ..           double click
  A       .-           double click-and-hold
  S       ...          triple click
  U       ..-          triple click-and-hold
  H       ....         4x click
  V       ...-         4x click-and-hold
  5       .....        5x click
  4       ....-        5x click-and-hold

In my setup, I generated the fastest morse code that the WAV generator would
provide, and used a different pitch for clicks versus the click-and-holds.

The generated WAV files need to be installed in the FSUIPC directory, and need
to be named according to a convention that makes it easy for the module to
pick the right file based on what it detected. For all the click-and-release
sequences (e.g. single click, double click, triple click, ...), that
convention is:

 - [Joystick Code]_[Button Code]c[Number of clicks].wav

For the click-and-holds (e.g. single click-and-hold, double click-and hold...)
the convention is:

 - [Joystick Code]_[Button Code]h[Number of clicks].wav

For example, a double-click on joystick "A" button "0" will play "A_0c2.wav".
A 5x click-and-hold on joystick "2" button "13" would play "2_13h5.wav".

As you'll learn more about in the CONFIGURATION section, 'n_clicks_max' defines
the maximum sequence of click-and-releases and click-and-holds that will be
detected by the module, so you need only generate these files for
[Number of clicks] ranging from 1 to 'n_clicks_max'.

Then, one final sound: the WAV file "ovrldbtn.wav" is played on startup of the
framework, as an indicator the framework is ready and as a test of the sound
system. For my 'ovrldbtn.wav', I used the aforementioned website to generate a
morse code WAV file that plays the word "ready".

--]]

-- CONFIGURATION

-- Joycode number/joyletter string for the joystick w/ the button to overload
joy = 'A'

-- Button id for the button to overload
btn = 0

--[[
n_click_threshold_ms:
Maximum time (in milliseconds) between the release of a button click and the
press of another click, for the later click to be considered an n_click.
For example, upon releasing the button, click it again within this time to
consider the action an n_click=2, then release it and click it again within
another period of this duration to consider it an n_click=3 -... and so on
until n_clicks_max is reached. The action associated with an n_click series
will only be triggered after this amount of time passes after the release of
the last click. The larger the value, the more leisurely your finger twitches
from release-to-next-press can be to have them still registered as an n_click.
But this time also represents a delay that you must wait for after the release
of the last click before the associated action is generated, or that you start
clicking again to trigger a new n_click sequence. Note this value doesn't
affect the period between pressing a button and releasing it; for that
consideration see button_hold_threshold_ms. n_click_threshold_ms only affects
how quickly the button must be pressed after being released, to be treated as a
continuation of the active n_click series.
--]]
n_click_threshold_ms = 300

--[[
n_clicks_max: if the button is successively clicked more than this number of
times within n_click_threshold_ms of prior button releases, the number of extra
clicks are ignored and the generated action will reflect only n_clicks=
n_clicks_max. However the n_clicks=n_clicks_max action will not be generated
until n_click_threshold_ms after the release of the last physical click.
For example if this were set to 2, a click,click,click-series would generate
the same action as if you had done a click,click, though will wait to do so
until after the release of the 3rd click. Larger numbers allow you to bind more
actions to the overloaded button which might be useful mainly when
n_click_threshold_ms is larger, to allow your brain the time to reliably count
how many clicks in a row you've pressed. Smaller numbers can let you more
easily generate the n_clicks=n_clicks_max action because you won't need to as
precisely count a series of rapid finger twitches, so long as you can be sure
you clicked at least n_clicks_max number of times.
--]]
n_clicks_max = 3

--[[
vbtn_base_clicks:
The framework will toggle a virtual button "N" when the button is N-clicked,
whose ID is vbtn_base_clicks + N - 1. Use the provided function VirtualButton
to calculate vbtn_base_clicks for the N=1 virtual button, and additional
buttons will be managed up through n_clicks_max. For example if n_clicks_max=4
and vbtn_base_clicks=VirtualButton(64,8), then button 64,8 will be toggled on
every single-click, 64,9 will be toggled on every double-click, 64,10 will be
toggled on every triple-click, and 64,11 will be toggled every 4-click ...
through vbtn_base_clicks + n_clicks_max.
--]]
function VirtualButton(joy,btn)
   if (joy >= 64) and (btn >= 0) and (btn < 16) then
      return ((joy-64)*16)+btn
   end
end

vbtn_base_clicks = VirtualButton(65,1)

--[[
btn_hold_threshold_ms: If after a button click, a button release is not
detected prior to this amount of time (in milliseconds), the button will be
considered held and the clickNhold action for the current value of n_clicks
will be generated. Contrasted with n_click_threshold_ms which constrains how
long you can wait between a button release and the next button press before an
n_click action is generated, this parameter constrains how long you can wait
between a button press and its release before a clickNhold action is generated.
Longer values let your finger move more slowly to release the button when
clicking through an n_click series, but will lengthen how long you have to keep
the button held to generate a clickNhold action. If you only care about n_click
actions and not about any clickNHold actions, then you could set this value to
something impossibly large. Of course actually holding the button down for any
amount of time in an n_click series will lengthen how long it takes before the
n_click action is triggered.
--]]
btn_hold_threshold_ms = 200

--[[
vbtn_base_clkNhold:
The framework will set a virtual button "N" if and only if the button is being
N-click-and held, where N is vbtn_base_clkNhold + N - 1. Use the defined
function VirtualButton(joy,btn) to calculate vbtn_base_clicks for the N=1
virtual button, and additional buttons will be managed up through n_clicks_max.
Only one vButton within the range will be set at a given time, and it will be 
cleared when the held button is released. For example if n_clicks_max=4 and
vbtn_base_clicks=VirtualButton(66,1), then button 66,1 will be set on every
single-click-and-hold, 66,2 will be set on every double-click-and-hold, 66,3
will be set on every triple-click-and-hold, 66,4 will be set every
4x-click-and-hold...  through vbtn_base_clkNhold + n_clicks_max.
--]]
vbtn_base_clkNhold = VirtualButton(66,1)

--
-- IMPLEMENTATION
--
_sound_pfx_base=joy .. "_" .. btn
_sound_pfx_click=_sound_pfx_base .. "c"
_sound_pfx_clkNhold=_sound_pfx_base .. "h"

-- state variables
_last_btn_dn_time_ms = 0
_n_clicks = 0
_pending_button_rel_events = 0
_n_clkNhold = 0

function _process_button_release(button_currently_released)
   event.cancel("_ev_button_held")

   if (_n_clkNhold > 0) then
      ipc.btnRelease(vbtn_base_clkNhold+_n_clkNhold-1)
      _n_clkNhold = 0
   else
      if (button_currently_released) then
         event.timer(n_click_threshold_ms, '_ev_click')
      end
   end
end

function _button_pressed(j, b, du)
   local cur_btn_dn_time_ms=ipc.elapsedtime()

   event.cancel("_ev_click")

   if (_pending_button_rel_events > 0) then
      _process_button_release(false)
   end

   _pending_button_rel_events = _pending_button_rel_events + 1

   if (cur_btn_dn_time_ms - _last_btn_dn_time_ms > n_click_threshold_ms) then
      _n_clicks = 1
   else
      if (_n_clicks < n_clicks_max) then
         _n_clicks = _n_clicks + 1
      end
   end

   _last_btn_dn_time_ms = cur_btn_dn_time_ms

   event.timer(btn_hold_threshold_ms,"_ev_button_held")
end

function _ev_button_held(elapsed_time_ms)
   sound.play(_sound_pfx_clkNhold .. _n_clicks)

   event.cancel("_ev_button_held")
   ipc.btnPress(vbtn_base_clkNhold+_n_clicks-1)
   _n_clkNhold = _n_clicks
end

function _ev_click(elapsed_time_ms)
   sound.play(_sound_pfx_click .. _n_clicks)
   event.cancel("_ev_click")

   ipc.btnToggle(vbtn_base_clicks+_n_clicks-1)
end


function _button_released(j, b, du)
   if (_pending_button_rel_events == 1) then
      _process_button_release(true)
   end
   _pending_button_rel_events = _pending_button_rel_events - 1
end

event.button(joy, btn, 1, "_button_pressed")
event.button(joy, btn, 2, "_button_released")

sound.play("ovrldbtn") -- Alert readiness

