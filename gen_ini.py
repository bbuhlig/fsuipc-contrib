#!/usr/bin/python3
"""
gen_ini.py -- FSUIPC7.ini generator for a Honeycomb Alpha/Bravo based FS rig
Version 20210628-0-073677f

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

This python3.7+ script leverages the fsuipcini modules I am writing to help
auto-generate FSUIPC7 button assignments appropriate for my VR flightsim
rig mainly consisting of Honeycomb Alpha & Bravo hardware.
As of the writing of this description, it is nowhere near complete for my
ultimate purpose, and I'm publishing it mainly as an example of how the
fsuipcini modules can be used to generate complex button assignments.

The motivation for the fsuipcini modules came from what I realized
was going to end up being a complicated set of button mappings I was
working toward, to reach my goal of having comprehensive control over
a wide variety of aircraft using the Alpha and Bravo but in a manner
that is usable while in a VR headset. Very generally, my button mapping
philosophy is to leverage the Alpha's trigger button, the Alpha's
magneto rotary selector, and the Bravo's autopilot/bug rotary selector
in various combinations as "shift" buttons to allow a potential overloading
of (theoretically) 50 or more functions per each of Alpha/Bravo's stateless
push buttons (i.e. not the rockers and toggles). Probably because of my
lack of familiarity with the INI file, I kept getting lost in interpreting
the INI directly as I kept iterating on the most meaningful mappings
for my use, and found myself wanting a more human readable version of it.
Eventually I settled on writing a python based framework to get me there.

"""


import argparse
from enum import Enum
import re
from fsuipcini.controls import CreateControls, CreateFSUIPCControls
from fsuipcini.utils import filter_ini, section, end_section
from fsuipcini.buttons import btnmap, ButtonAction
from fsuipcini.keys import KeyControl, VK, VKM
from fsuipcini.offsets import OffsetControl, OffsetSize, OffsetValEnum
import fsuipcini.SlowFastIncDecMgr
import fsuipcini.devices.honeycomb.alpha
import fsuipcini.devices.honeycomb.bravo

parser = argparse.ArgumentParser(
                            description="Generate FSUIPC ini file sections")
parser.add_argument("updateinifile", nargs='?',
                    help="(optional) read the INI at the given path, "+
                         "then update it with sections generated by this script "+
                         "filtered out. Always outputs windows line endings. " +
                         "Does NOT make a backup copy, so do that before running this "
                         "if you care." )
args=parser.parse_args()

# The "Controls List for MSFS Build 999.txt" file is provided by the
# the FSUIPC7 installer. Controls are listed twice in that file --
# first sorted by control ID then sorted by control name -- but whatever
# the last encountered mapping is between name and ID will be used, so
# the fact they are duplicated should not be issue.
# For demo convenience, try finding that file in a couple possible locations if
# not in the current directory
SimCtrl = CreateControls("SimCtrl",
                         [f'{x}Controls List for MSFS Build 999.txt' for x in \
                           ["", "c:/FSUIPC7/", "/mnt/c/FSUIPC7"]],
                         calling_module=__name__)

# See fsuipc_controls.txt for more information about how this enum type is
# dynamically generated.
FsuipcCtrl = CreateFSUIPCControls("FsuipcCtrl", calling_module=__name__)

# The script cip_to_evt.py converts a Mobiflight CIP file to a set of
# custom event files, and the script gen_custom_ctrls_info.py takes both
# the CIP and the custom event files to generate custom_ctrls_info.tsv.txt,
# which is then parsed here to make named MobiFlight control enums available.
# The name_filt_fn strips the leading "MobiFlight." text and everything
# after the alphanumberic-and-underscore description prior to conversion
# into a dynamically created set of control enums prefixed with "MBFCtrl".

# Fallback to custom_ctrls_info.tsv.DEMO.txt if custom_ctrls_info.tsv.txt
# doesn't exist. This allows this script to work "out-of-the-box" if
# cloned from git and immediately run without modifications, but as this
# gen_ini.py file is just a demo of what you can write with the fsuipcini
# library, running it that way should not be expected to generate a working
# config for the reasons documented in custom_ctrls_info.tsv.DEMO.txt.

MBFCtrl = CreateControls("MBFCtrl",
                         ["custom_ctrls_info.tsv.txt",
                          "custom_ctrls_info.tsv.DEMO.txt"],
                         name_filt_fn=lambda n:
                            re.sub(pattern=r'MobiFlight\.',repl='', count=1,
                                   flags=re.IGNORECASE,
                                   string=re.sub(pattern=r' .*', repl='',
                                                 string=n,count=1)),
                         calling_module=__name__)

# Define aliases for controls implemented by keystrokes. An important use for
# this section is as reference while configuring FS2020 with appropriate key
# bindings

class KeyCtrl(KeyControl,Enum):
   VR_COCKPIT_ZOOM=(VK.SPACE,VKM.SHIFT)
   TOGGLE_ACTIVE_PAUSE=VK.PAUSE
   TOGGLE_FULL_PAUSE_ESC=(VK.PAUSE,VKM.SHIFT)
   RESET_COCKPIT_VIEW=(VK.SPACE,VKM.CTRL)
   VR_CAMERA_RESET=VK.SPACE
   VR_MODE_TOGGLE=(VK.OEM_5,VKM.CTRL)
   VR_TOOLBAR_TOGGLE=VK.OEM_5
   TOGGLE_FLASHLIGHT=(VK.L,VKM.ALT)
   TRANSLATE_COCKPIT_VIEW_FORWARD=(VK.UP,VKM.CTRL)
   TRANSLATE_COCKPIT_VIEW_BACKWARD=(VK.DOWN,VKM.CTRL)
   TRANSLATE_COCKPIT_VIEW_LEFT=VK.LEFT
   TRANSLATE_COCKPIT_VIEW_RIGHT=VK.RIGHT
   INCREASE_COCKPIT_VIEW_HEIGHT=VK.UP
   DECREASE_COCKPIT_VIEW_HEIGHT=VK.DOWN

   def __init__(self,arg0,*argv):
      if isinstance(arg0,KeyControl):
         kc = arg0
      elif isinstance(arg0,VK):
         kc = KeyControl(arg0,*argv)
      elif isinstance(arg0,tuple):
         t0, tothers = arg0
         kc = KeyControl(t0,*tothers)
      else:
         raise RuntimeError("Unknown ctor arg type")

      self._value_ = kc

# Instantiate instances of buttons for the Alpha and Bravo
Alpha = fsuipcini.devices.CreateButtons('Alpha',joycode='A',
                    mappings=fsuipcini.devices.honeycomb.alpha.ButtonMappings)

Bravo = fsuipcini.devices.CreateButtons('Bravo',joycode='B',
                    mappings=fsuipcini.devices.honeycomb.bravo.ButtonMappings)


# I define a given "PanelMode" a particular combination of positions of
# the Alpha magneto rotary selector combined with the Bravo autopilot/bug
# rotary selector. Since there are 5 positions for each of these rotary
# selectors, this allows a theoretical maximum 25 unique PanelModes,
# with each push button theoretically behaving differently in each PanelMode.
# Of course, the state of the Alpha trigger or simulator state (offsets)
# could further multiply the options.

class PanelMode():
   # When FDSel is not pressed, the POV hat shall be assigned to
   # manipulating views; when FDSel is pressed, the POV hat shall be
   # assignable to a other uses, e.g. joysticks associated with
   # Functional Display systems. If not possible to co-locate all POV
   # hat uses other than view manipulation on the FDSel button, you
   # probably need to create mappings for whatever subset of the particular
   # ROTARYSEL combinations to "Press" a virtual button, then make the
   # NotPressed state of that virtual button the condition on which the POV
   # hat can be assigned to view manipulation
   FDSel       = Alpha.ROTARYSEL_5

   # autopilot and OBI controls
   AP_OBI      = [Alpha.ROTARYSEL_4, Bravo.ROTARYSEL_1]
   # Heading indicator/bug and altimeter adjustment
   HDG_ALT     = [Alpha.ROTARYSEL_4, Bravo.ROTARYSEL_2]
   # Transponder and ADF radios
   XPNDR_ADF   = [Alpha.ROTARYSEL_4, Bravo.ROTARYSEL_3]
   # COM radios
   COM         = [Alpha.ROTARYSEL_4, Bravo.ROTARYSEL_4]
   # NAV radios
   NAV         = [Alpha.ROTARYSEL_4, Bravo.ROTARYSEL_5]
   # Multi-function display (e.g. G1000 MFD)
   MFD         = [FDSel, Bravo.ROTARYSEL_1]
   # Primary Flight display (e.g. G1000 PFD)
   PFD         = [FDSel, Bravo.ROTARYSEL_2]

# The G1000 displays each have 14 different rotary encoder switches that need
# mapping . Supposing 1 Alpha position per display, the bravo rotary would
# select 5 of them, times 3 for AlphaTrigHeld.FALSE/CLICK1/CLICK2

# Physically they are:
# NAV Whole, NAV Fract; VOL
# COM Whole, COM Fract; VOL
# CRS, BARO
# FMS Outer, FMS Inner
# HDG
# MAP Zoom
# ALT Upper, ALT Lower

# There are also 12 softkeys, 6 FMS buttons, 2 radio swaps,
# and 12 AP buttons (MFD only)

# Map HDG and BARO on the PFD, exclusively.

# NAV and COM could only be on the PFD


#PFD mappings
# NAV Whole, NAV Fract; VOL :   AlphaTrigHeld.FALSE/CLICK1/CLICKs
# COM Whole, COM Fract; VOL :   AlphaTrigHeld.FALSE/CLICK1/CLICKs
# HDG/ BARO :   AlphaTrigHeld.FALSE/CLICK1
# MAP Zoom
# FMS Outer, FMS Inner : AlphaTrigHeld.FALSE/CLICK1

#MFD mappings
# CRS, BARO? :   AlphaTrigHeld.FALSE/CLICK1
# MAP Zoom
# ALT Upper, ALT Lower : AlphaTrigHeld.FALSE/CLICK1 (MFD only)
# FMS Outer, FMS Inner : AlphaTrigHeld.FALSE/CLICK1


# The Alpha trigger button (Alpha.LY_TRIG) is managed by the ovrldbtn.lua
# plugin. Through it clicks, double-clicks, triple-clicks etc. can be mapped
# to particular controls...
alphaTrigClicks = dict(
   CLICK1 = 1,
   CLICK2 = 2,
   CLICK3 = 3,
   CLICK4 = 4
)
AlphaTrig = fsuipcini.devices.CreateButtons('AlphaTrig',joycode=65,
                                            mappings=alphaTrigClicks)

# ...and keeping the trigger held after single,double,triple... clicking
# can represent unique shift modifiers for other buttons
AlphaTrigHeld = fsuipcini.devices.CreateButtons('AlphaTrigHeld',joycode=66,
                                                mappings=alphaTrigClicks)
AlphaTrigHeld.FALSE = "(-A,0)"

# The rotfsev.lua plugin manages fast vs. slow manipulation of the Bravo's
# rotary encoder (Bravo.ROTENC_INCR, Bravo.ROTENC_DECR). The result is 4
# possible types of actions that can be overloaded to various controls
# depending on the selected PanelMode and other shift modfiers.
BravoRotEnc = fsuipcini.devices.CreateButtons('BravoRotEnc',joycode=70,
                                              mappings=dict(
   DEC_FAST = 0,
   DEC_SLOW = 1,
   INC_SLOW = 2,
   INC_FAST = 3
))

BravoRotEnc.mgr = fsuipcini.SlowFastIncDecMgr.SlowFastIncDecMgr(
    slow_decr_btn=BravoRotEnc.DEC_SLOW, slow_incr_btn=BravoRotEnc.INC_SLOW,
    fast_decr_btn=BravoRotEnc.DEC_FAST, fast_incr_btn=BravoRotEnc.INC_FAST)

# The rotfsev.lua plugin also manages fast vs. slow manipulation of the
# Bravo's trim wheel (Bravo.TRIMWHEEL_DOWN, Bravo.TRIMWHEEL_UP). We can
# add in the holding of the Alpha trigger as an additional shift to
# further increase the manipulation speed of the elevator control.
BravoTrimWheel = fsuipcini.devices.CreateButtons('BravoTrimWheel',joycode=68,
                                                 mappings=dict(
   DOWN_FAST = 0,
   DOWN_SLOW = 1,
   UP_SLOW   = 2,
   UP_FAST   = 3
))

ElvTrimCtrl=OffsetControl(offset = 0x0BC0,
                          size   = OffsetSize.Int16,
                          llimit = -16383,
                          ulimit =  16383)

ElvTrimCtrl.IncrSlow = SimCtrl.ELEV_TRIM_UP
ElvTrimCtrl.DecrSlow = SimCtrl.ELEV_TRIM_DN

[
   [ ElvTrimCtrl.IncrFast, ElvTrimCtrl.IncrFaster, ElvTrimCtrl.IncrFastest ],
   [ ElvTrimCtrl.DecrFast, ElvTrimCtrl.DecrFaster, ElvTrimCtrl.DecrFastest ]
] = map( lambda mult_func : map(mult_func, [1, 2, 8]),
         map(lambda oper : lambda mult : ElvTrimCtrl.op(oper, mult * 128),
             [ OffsetControl.Operation.IncrementSigned,
               OffsetControl.Operation.DecrementSigned ])
       )

class ParkingBrakeIsNotSet(OffsetValEnum):
   Offset = 0x0BC8
   Size = OffsetSize.Int16

   TRUE = 0

class StructuralDeiceSwitchIsOff(OffsetValEnum):
   Offset = 0x337D
   Size = OffsetSize.Int8

   TRUE = 0

class PropellerDeiceSwitchIsOff(OffsetValEnum):
   Offset = 0x2440
   Size = OffsetSize.Int32

   TRUE = 0

# If passed as an arg, regenerate the current FSUIPC7.ini file filtering out any
# Buttons sections
if args.updateinifile:
   filter_ini(args.updateinifile,'Buttons')



# Now generate a new Buttons section
section("Buttons",{
   "PollInterval":25,
   "ButtonRepeat":"20,10",
   "IgnoreThese":"B.12, B.13, B.21, B.22"
})

# Here are some basic button mappings. Each btnmap() call generates a single
# entry in the buttons section, with a comment that points at the python file
# and line info where the btnmap() call was made. To save chars against the 64
# char comment limit, filenames are mapped into letter codes as they are
# encountered, i.e. "a" for the first such file encountered in the section,
# "b" for the second, ... "z" for the 26th, "aa" for the 27th, etc... The
# mapping of letter codes to file names are output in comments at the bottom
# of the section.  If the btnmap() call was made in a python function that was
# called by another function Q, which was in turn called by another R, etc...,
# then the entire stack of functions is listed separated by semicolons with the
# first in the list identifying the function that called btnmap, the next
# identifying Q, the next R, etc...  For example, the following output...
#
#   514=CU(+A,133)(+B,17)(+66,1)70,3,C65883,0 ;b53;b60;a598
#   515=HB,8,C65966,0 ;a602
#   516=;a>./gen_ini.py
#   517=;b>/home/bbuhlig/fsuipccfg/fsuipcini/SlowFastIncDecMgr.py
#
# shows that INI entry 514 was generated by line 53 of the SlowFastIncDecMgr.py
# module, as the result of a function call made at line 60 of that same file,
# which in turn was invoked because of a function call at line 598 of
# ./gen_ini.py.  INI entry 515 was generated by a call to btnmap() at line 602
# of ./gen_ini.py, and no function calls were involved.  Entry 515 is the
# last btnmap() call for the section because entries 516 and 517 are the
# end-of-section comments that identify what letter codes map to what
# filenames.
#
# Notably version information for each file is not logged in the comments
# so don't get confused by file/line info possibly reflecting file version
# diffs between what they are now vs. when the comments were generated.
#



btnmap(Alpha.MASTER_ALT_ON,SimCtrl.ALTERNATOR_ON)
btnmap(Alpha.MASTER_ALT_OFF,SimCtrl.ALTERNATOR_OFF)
btnmap(Alpha.MASTER_BAT_ON,SimCtrl.MASTER_BATTERY_ON)
btnmap(Alpha.MASTER_BAT_OFF,SimCtrl.MASTER_BATTERY_OFF)
btnmap(Alpha.AVIONICS_BUS1_ON,SimCtrl.AVIONICS_MASTER_1_ON)
btnmap(Alpha.AVIONICS_BUS1_OFF,SimCtrl.AVIONICS_MASTER_1_OFF)
btnmap(Alpha.AVIONICS_BUS2_ON,SimCtrl.AVIONICS_MASTER_2_ON)
btnmap(Alpha.AVIONICS_BUS2_OFF,SimCtrl.AVIONICS_MASTER_2_OFF)
btnmap(Alpha.BCN_ON,SimCtrl.BEACON_LIGHTS_SET)
btnmap(Alpha.BCN_OFF,SimCtrl.TOGGLE_BEACON_LIGHTS)
btnmap(Alpha.LAND_ON,SimCtrl.LANDING_LIGHTS_ON)
btnmap(Alpha.LAND_OFF,SimCtrl.LANDING_LIGHTS_OFF)
btnmap(Alpha.TAXI_ON,SimCtrl.TAXI_LIGHTS_SET)
btnmap(Alpha.TAXI_OFF,SimCtrl.TOGGLE_TAXI_LIGHTS)
btnmap(Alpha.NAV_ON,SimCtrl.NAV_LIGHTS_SET)
btnmap(Alpha.NAV_OFF,SimCtrl.TOGGLE_NAV_LIGHTS)
btnmap(Alpha.STROBE_ON,SimCtrl.STROBES_ON)
btnmap(Alpha.STROBE_OFF,SimCtrl.STROBES_OFF)

btnmap(Alpha.RY_RED,SimCtrl.AUTOPILOT_DISENGAGE_TOGGLE,
       conds=AlphaTrigHeld.FALSE)
btnmap(Alpha.RY_RED,SimCtrl.PARKING_BRAKES,
       conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.LY_QBL_U,SimCtrl.INC_COWL_FLAPS)
btnmap(Alpha.LY_QTL_D,SimCtrl.DEC_COWL_FLAPS)
btnmap(Alpha.RY_QBL_R,SimCtrl.RUDDER_TRIM_LEFT)
btnmap(Alpha.RY_QBR_L,SimCtrl.RUDDER_TRIM_RIGHT)

btnmap(Bravo.ROCKER_1_OFF,SimCtrl.TOGGLE_PROPELLER_DEICE,
       conds=PropellerDeiceSwitchIsOff.TRUE.CondNotEqual)
btnmap(Bravo.ROCKER_1_ON,SimCtrl.TOGGLE_PROPELLER_DEICE,
       conds=PropellerDeiceSwitchIsOff.TRUE.CondEqual)
btnmap(Bravo.ROCKER_2_ON,SimCtrl.WINDSHIELD_DEICE_ON)
btnmap(Bravo.ROCKER_2_OFF,SimCtrl.WINDSHIELD_DEICE_OFF)
btnmap(Bravo.ROCKER_3_ON,SimCtrl.PITOT_HEAT_ON)
btnmap(Bravo.ROCKER_3_OFF,SimCtrl.PITOT_HEAT_OFF)
btnmap(Bravo.ROCKER_4_ON,SimCtrl.ANTI_ICE_ON)
btnmap(Bravo.ROCKER_4_OFF,SimCtrl.ANTI_ICE_OFF)
btnmap(Bravo.ROCKER_5_ON,SimCtrl.PANEL_LIGHTS_ON)
btnmap(Bravo.ROCKER_5_ON,SimCtrl.CABIN_LIGHTS_ON)
btnmap(Bravo.ROCKER_5_OFF,SimCtrl.PANEL_LIGHTS_OFF)
btnmap(Bravo.ROCKER_5_OFF,SimCtrl.CABIN_LIGHTS_OFF)
btnmap(Bravo.ROCKER_6_ON,SimCtrl.PAUSE_ON)
btnmap(Bravo.ROCKER_6_OFF,SimCtrl.PAUSE_OFF)

btnmap(Bravo.FLAPS_DOWN,SimCtrl.FLAPS_INCR)
btnmap(Bravo.FLAPS_UP,SimCtrl.FLAPS_DECR)
btnmap(Bravo.GEAR_UP,SimCtrl.GEAR_UP)
btnmap(Bravo.GEAR_DOWN,SimCtrl.GEAR_DOWN)
for toga in [Bravo.THROTLVR1_AND_2_TOGA,Bravo.THROTLVR3_TOGA,
             Bravo.THROTLVR4_TOGA]:
   btnmap(toga,SimCtrl.AUTO_THROTTLE_TO_GA),


# Map the magneto controls to the magneto switches only when
# the alpha trigger is being held (click-click&hold to select the 2nd
# engine's magneto)
btnmap(Alpha.MAG_OFF,(SimCtrl.MAGNETO1_SET,0),conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_R,(SimCtrl.MAGNETO1_SET,1),conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_L,(SimCtrl.MAGNETO1_SET,2),conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_BOTH,(SimCtrl.MAGNETO1_SET,3),conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_START,(SimCtrl.SET_STARTER1_HELD,1),
                        conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_START,(SimCtrl.SET_STARTER1_HELD,0),
                        action=ButtonAction.RELEASE,conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.MAG_OFF,(SimCtrl.MAGNETO2_SET,0),conds=AlphaTrigHeld.CLICK2)
btnmap(Alpha.MAG_R,(SimCtrl.MAGNETO2_SET,1),conds=AlphaTrigHeld.CLICK2)
btnmap(Alpha.MAG_L,(SimCtrl.MAGNETO2_SET,2),conds=AlphaTrigHeld.CLICK2)
btnmap(Alpha.MAG_BOTH,(SimCtrl.MAGNETO2_SET,3),conds=AlphaTrigHeld.CLICK2)
btnmap(Alpha.MAG_START,(SimCtrl.SET_STARTER2_HELD,1),
                        conds=AlphaTrigHeld.CLICK2)
btnmap(Alpha.MAG_START,(SimCtrl.SET_STARTER2_HELD,0),
                        action=ButtonAction.RELEASE,conds=AlphaTrigHeld.CLICK2)


# TODO map a voice transmit button for some kind of VATSIM or PilotEdge client
#btnmap(Alpha.LY_WHITE,VOICE_TRANSMIT,action=ButtonAction.HOLD)

#
# General simulator controls
#

btnmap(Alpha.LY_QBR_U,SimCtrl.SIM_RATE_DECR,conds=AlphaTrigHeld.CLICK1)
btnmap(Alpha.LY_QTR_D,SimCtrl.SIM_RATE_INCR,conds=AlphaTrigHeld.CLICK1)




# Map the Bravo trim wheel to the Elevator Trim control
btnmap(BravoTrimWheel.DOWN_SLOW,ElvTrimCtrl.DecrSlow,
       conds=AlphaTrigHeld.FALSE, action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.DOWN_FAST,ElvTrimCtrl.DecrFast,
       conds=AlphaTrigHeld.FALSE, action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.DOWN_SLOW,ElvTrimCtrl.DecrFaster,
       conds=AlphaTrigHeld.CLICK1,action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.DOWN_FAST,ElvTrimCtrl.DecrFastest,
       conds=AlphaTrigHeld.CLICK1,action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.UP_SLOW,  ElvTrimCtrl.IncrSlow,
       conds=AlphaTrigHeld.FALSE, action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.UP_FAST,  ElvTrimCtrl.IncrFast,
       conds=AlphaTrigHeld.FALSE, action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.UP_SLOW,  ElvTrimCtrl.IncrFaster,
       conds=AlphaTrigHeld.CLICK1,action=ButtonAction.PRESS_AND_RELEASE)
btnmap(BravoTrimWheel.UP_FAST,  ElvTrimCtrl.IncrFastest,
       conds=AlphaTrigHeld.CLICK1,action=ButtonAction.PRESS_AND_RELEASE)

#
# Map VR Controls to Alpha trigger clicks.
#

# VR Cockpit Zoom
btnmap(AlphaTrig.CLICK1,
       (FsuipcCtrl.Key_Press_Hold, KeyCtrl.VR_COCKPIT_ZOOM.FsuipcCtrlCode),
       conds=AlphaTrig.CLICK1.CondFlagClear)
btnmap(AlphaTrig.CLICK1,
       (FsuipcCtrl.Key_Release, KeyCtrl.VR_COCKPIT_ZOOM.FsuipcCtrlCode),
       conds=AlphaTrig.CLICK1.CondFlagSet)

# Use a similar principle with stateless actions on stateful buttons, i.e.
# rockertgl.lua replacement. Simple lua code would use Lua event.offset to get
# changes on state, and assign that state to some virtual button. In button
# mappings, toggle rocker button action to the state-changing toggle control,
# conditionally on the virtual button state

btnmap(AlphaTrig.CLICK2,KeyCtrl.VR_MODE_TOGGLE)

# TODO The VR Toolbar is most likely interacted with via the trackball so
#  put VR_TOOLBAR_TOGGLE on one of the trackball buttons.

# VR_CAMERA_RESET and related RESET_COCKPIT_VIEW are implemented
# as AlphaTrigHeld.CLICK2 modified down/up POV actions below.

#
# POV hat:
#
#  In cockpit view, translate TRANSLATE_COCKPIT_VIEW; use AlphaTrigHeld.CLICK1
#    to pick FWD/BACK on the hat. AlphaTrigHeld.CLICK2 and down on the HAT
#    resets the cockpit view; ..and up does a VR Camera Reset
#  In drone or external views, move around using the essentially the same
#    bindings as cockpit view, with perhaps some extensions.  But try
#    to bind only a particular set of keys that does the right thing in
#    all modes, because there doesn't appear to be a way to detect the
#    current view mode via SimConnect. If that becomes necessary, some sort
#    of state tracking would need to be done through maybe a rocker toggle, or
#    an internally managed offset like how the WHOLE/FRACT stuff is done
#  In a PFD/MFD mode, move the PFD/MFD joystick

pov_mappings = [
  ([Alpha.LY_HAT_U,Alpha.LY_HAT_UR,Alpha.LY_HAT_UL] , [ # Up
     (KeyCtrl.INCREASE_COCKPIT_VIEW_HEIGHT,
        [AlphaTrigHeld.FALSE,PanelMode.FDSel.CondNotPressed]),
     (KeyCtrl.TRANSLATE_COCKPIT_VIEW_FORWARD,
        [AlphaTrigHeld.CLICK1,PanelMode.FDSel.CondNotPressed]),
     (KeyCtrl.VR_CAMERA_RESET,
        [AlphaTrigHeld.CLICK2,PanelMode.FDSel.CondNotPressed],
        ButtonAction.PRESS),
     (MBFCtrl.AS1000_MFD_JOYSTICK_UP, PanelMode.MFD),
     (MBFCtrl.AS1000_PFD_JOYSTICK_UP, PanelMode.PFD),
# appears inop    (MBFCtrl.Generic_Lwr_JOYSTICK_UP, PanelMode.MFD),
   ]),
  ([Alpha.LY_HAT_R,Alpha.LY_HAT_UR,Alpha.LY_HAT_DR] , [ # Right
     (KeyCtrl.TRANSLATE_COCKPIT_VIEW_RIGHT, [PanelMode.FDSel.CondNotPressed]),
     (MBFCtrl.AS1000_MFD_JOYSTICK_RIGHT, PanelMode.MFD),
     (MBFCtrl.AS1000_PFD_JOYSTICK_RIGHT, PanelMode.PFD),
# appears inop    (MBFCtrl.Generic_Lwr_JOYSTICK_RIGHT, PanelMode.MFD),
   ]),
  ([Alpha.LY_HAT_D,Alpha.LY_HAT_DR,Alpha.LY_HAT_DL] , [ # Down
     (KeyCtrl.DECREASE_COCKPIT_VIEW_HEIGHT,
        [AlphaTrigHeld.FALSE,PanelMode.FDSel.CondNotPressed]),
     (KeyCtrl.TRANSLATE_COCKPIT_VIEW_BACKWARD,
        [AlphaTrigHeld.CLICK1,PanelMode.FDSel.CondNotPressed]),
     (KeyCtrl.RESET_COCKPIT_VIEW,
        [AlphaTrigHeld.CLICK2,PanelMode.FDSel.CondNotPressed],
        ButtonAction.PRESS),
     (MBFCtrl.AS1000_MFD_JOYSTICK_DOWN, PanelMode.MFD),
     (MBFCtrl.AS1000_PFD_JOYSTICK_DOWN, PanelMode.PFD),
# appears inop     (MBFCtrl.Generic_Lwr_JOYSTICK_DOWN, PanelMode.MFD),
   ]),
  ([Alpha.LY_HAT_L,Alpha.LY_HAT_UL,Alpha.LY_HAT_DL] , [ # Left
     (KeyCtrl.TRANSLATE_COCKPIT_VIEW_LEFT, [PanelMode.FDSel.CondNotPressed]),
     (MBFCtrl.AS1000_MFD_JOYSTICK_LEFT, PanelMode.MFD),
     (MBFCtrl.AS1000_PFD_JOYSTICK_LEFT, PanelMode.PFD),
# appears inop     (MBFCtrl.Generic_Lwr_JOYSTICK_LEFT, PanelMode.MFD),
   ])
]

for buttons, ctrl_act_cond_mappings in pov_mappings:
  for button in buttons:
    for ctrl_act_cond_mapping in ctrl_act_cond_mappings:

       action=ButtonAction.REPEAT
       if len(ctrl_act_cond_mapping) == 3:
          control,conds,action = ctrl_act_cond_mapping
       else:
          control,conds = ctrl_act_cond_mapping

       if not isinstance(conds,list):
          conds=list(conds)

       btnmap(button,control,conds=conds,action=action)


# Work through PanelMode assignments

# The button flag state for Bravo.ROTENC_SEL_1L is meant to change what's
# controlled by the Bravo.ROTENC in the following panel modes; for consistency
# of operation it's necessary to reset the Bravo.ROTENC button flag state when
# entering these modes.

physical_panel_mode_selector_button = Bravo.ROTENC_SEL_1L

# Unfortunately it is difficult to do this when using a joyletter based
# physical button because FsuipcCtrl.Clear_button_flag cannot take a joyletter
# based param. We could work around this by mapping presses of this physical
# button to press a virtual button, whose button flag state is then used to
# change what's controlled by the Bravo.ROTENC.  # Or another approach is to deal
# with this in a Lua plugin, which can map joyletters to joynumbers in various
# ways, then trap event.button for the related eventsand then send the
# appropriate Clear_button_flag command. I happen to have other Lua based needs
# to manage this so it's easiest for now to do it there, though the need
# for that other lua code is fading.  So eventually I might do it the first
# way.
panel_mode_selector_button = physical_panel_mode_selector_button


for pm in [ PanelMode.AP_OBI,
            PanelMode.COM,
            PanelMode.NAV,
            PanelMode.HDG_ALT
          ]:
   for pm_sel in pm:
      cndlist = [ pms.CondPressed for pms in pm if pms != pm_sel ]

      if isinstance(panel_mode_selector_button.JoystickCode,int):

         btnmap(pm,
                (FsuipcCtrl.Clear_button_flag,
                 panel_mode_selector_button.ButtonFlagAPIParamCode),
                conds=cnds)
      else:
         # Assume Lua takes care of it
         pass

# PanelMode.XPNDR_ADF is very similar to the above, but needs a couple offsets
# used as button conditions reset to 0 rather than a button flag, when the
# appropriate panel mode switches are selected

for paramlist in [
                   [SimCtrl.VOR1_OBI_DEC,
                    SimCtrl.VOR1_OBI_INC,
                    [panel_mode_selector_button.CondFlagClear],
                    FsuipcCtrl.Vor1_Obi_Dec_Fast,
                    FsuipcCtrl.Vor1_Obi_Inc_Fast],

                   [SimCtrl.VOR2_OBI_DEC,
                    SimCtrl.VOR2_OBI_INC,
                    [panel_mode_selector_button.CondFlagSet],
                    FsuipcCtrl.Vor2_Obi_Dec_Fast,
                    FsuipcCtrl.Vor2_Obi_Inc_Fast]
                ]:

    BravoRotEnc.mgr.btnmapgroup(*paramlist, all_conds=PanelMode.AP_OBI)

btnmap(Bravo.HDG,SimCtrl.AP_HDG_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.NAV,SimCtrl.AP_NAV1_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.APR,SimCtrl.AP_APR_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.REV,SimCtrl.AP_BC_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.ALT,SimCtrl.AP_ALT_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.CRS,SimCtrl.AP_PANEL_VS_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.IAS,SimCtrl.AP_AIRSPEED_HOLD,conds=PanelMode.AP_OBI)
btnmap(Bravo.AP, SimCtrl.AUTOPILOT_DISENGAGE_TOGGLE,conds=PanelMode.AP_OBI)


# NAV and COM PanelMode
nav_conds=[Alpha.ROTARYSEL_1,Bravo.ROTARYSEL_5]
com_conds=[Alpha.ROTARYSEL_1,Bravo.ROTARYSEL_4]
# NAV1/COM1 is selectable via not holding the Alpha trigger
# NAV2/COM2 is selectible via Alpha trigger single click-n-hold
radio_sel=[None,[AlphaTrigHeld.FALSE],[AlphaTrigHeld.CLICK1]]
# Whole/Fractional frequency select toggles the button to the
# left of the Rotary encoder
fract_sel={False:[panel_mode_selector_button.CondFlagClear],
           True:[panel_mode_selector_button.CondFlagSet]}

# Swapping primary and standby frequencies by pressing the
# button 2 to the left of the Rotary encoder
btnmap(Bravo.ROTENC_SEL_2L,SimCtrl.NAV1_RADIO_SWAP,
       conds=PanelMode.NAV+radio_sel[1])
btnmap(Bravo.ROTENC_SEL_2L,SimCtrl.NAV2_RADIO_SWAP,
       conds=PanelMode.NAV+radio_sel[2])
btnmap(Bravo.ROTENC_SEL_2L,SimCtrl.COM1_RADIO_SWAP,
       conds=PanelMode.COM+radio_sel[1])
btnmap(Bravo.ROTENC_SEL_2L,SimCtrl.COM2_RADIO_SWAP,
       conds=PanelMode.COM+radio_sel[2])

# Rotary encoder will dial frequency up and down, in single
# increments when moved fast and in clusters of 4 increments
# when moved fast.
for paramlist in [
                   [SimCtrl.NAV1_RADIO_WHOLE_DEC,
                    SimCtrl.NAV1_RADIO_WHOLE_INC,
                    PanelMode.NAV+radio_sel[1]+fract_sel[False]],
                   [SimCtrl.NAV1_RADIO_FRACT_DEC,
                    SimCtrl.NAV1_RADIO_FRACT_INC,
                    PanelMode.NAV+radio_sel[1]+fract_sel[True]],
                   [SimCtrl.NAV2_RADIO_WHOLE_DEC,
                    SimCtrl.NAV2_RADIO_WHOLE_INC,
                    PanelMode.NAV+radio_sel[2]+fract_sel[False]],
                   [SimCtrl.NAV2_RADIO_FRACT_DEC,
                    SimCtrl.NAV2_RADIO_FRACT_INC,
                    PanelMode.NAV+radio_sel[2]+fract_sel[True]],
                   [SimCtrl.COM_RADIO_WHOLE_DEC,
                    SimCtrl.COM_RADIO_WHOLE_INC,
                    PanelMode.COM+radio_sel[1]+fract_sel[False]],
                   [SimCtrl.COM_RADIO_FRACT_DEC,
                    SimCtrl.COM_RADIO_FRACT_INC,
                    PanelMode.COM+radio_sel[1]+fract_sel[True]],
                   [SimCtrl.COM2_RADIO_WHOLE_DEC,
                    SimCtrl.COM2_RADIO_WHOLE_INC,
                    PanelMode.COM+radio_sel[2]+fract_sel[False]],
                   [SimCtrl.COM2_RADIO_FRACT_DEC,
                    SimCtrl.COM2_RADIO_FRACT_INC,
                    PanelMode.COM+radio_sel[2]+fract_sel[True]]
   ]:
    BravoRotEnc.mgr.btnmapgroup(*paramlist, fast_ctrl_events=4)


# In PanelMode.XPNDR_ADF...

# ... when the Alpha trigger is not held down, the transponder
# is selected.
xpndr_conds=PanelMode.XPNDR_ADF+[AlphaTrigHeld.FALSE]

# For the transponder, the rotary encoder will inc/dec a given selected
# digit. The next digit is selected by clicking the button to the left
# of the rotary encoder, and the prior digit is slected by clicking the
# button 2 to its left.

class XpndrSel(OffsetValEnum):
   Offset     = 0x66C0
   Size       = OffsetSize.Byte

   XPNDR_1000 = 0
   XPNDR_100  = 1
   XPNDR_10   = 2
   XPNDR_1    = 3

btnmap(Bravo.ROTENC_SEL_1L,
       XpndrSel.Ctrl.op(OffsetControl.Operation.IncrementCyclic,1),
       conds=xpndr_conds)
btnmap(Bravo.ROTENC_SEL_2L,
       XpndrSel.Ctrl.op(OffsetControl.Operation.DecrementCyclic,1),
       conds=xpndr_conds)

# Likewise for the ADF, except the Alpha trigger must be click-n-held
class ADFSel(OffsetValEnum):
   Offset     = 0x66C1
   Size       = OffsetSize.Byte

   ADF_100    = 0
   ADF_10     = 1
   ADF_1      = 2

adf_conds=PanelMode.XPNDR_ADF+[AlphaTrigHeld.CLICK1]

btnmap(Bravo.ROTENC_SEL_1L,
       ADFSel.Ctrl.op(OffsetControl.Operation.IncrementCyclic,1), conds=adf_conds)
btnmap(Bravo.ROTENC_SEL_2L,
       ADFSel.Ctrl.op(OffsetControl.Operation.DecrementCyclic,1), conds=adf_conds)
btnmap(Bravo.ROTENC_SEL_3L,SimCtrl.ADF1_RADIO_SWAP, conds=adf_conds)

# Once a digit is selected, rotating the inc/dec slowly will change
# the selected digit by 1, and rotating fast will change by 4.
for paramlist in [
                   [SimCtrl.XPNDR_1000_DEC,
                    SimCtrl.XPNDR_1000_INC,
                    [XpndrSel.XPNDR_1000.CondEqual]+xpndr_conds],
                   [SimCtrl.XPNDR_100_DEC,
                    SimCtrl.XPNDR_100_INC,
                    [XpndrSel.XPNDR_100.CondEqual]+xpndr_conds],
                   [SimCtrl.XPNDR_10_DEC,
                    SimCtrl.XPNDR_10_INC,
                    [XpndrSel.XPNDR_10.CondEqual]+xpndr_conds],
                   [SimCtrl.XPNDR_1_DEC,
                    SimCtrl.XPNDR_1_INC,
                    [XpndrSel.XPNDR_1.CondEqual]+xpndr_conds],
                   [SimCtrl.ADF_100_DEC,
                    SimCtrl.ADF_100_INC,
                    [ADFSel.ADF_100.CondEqual]+adf_conds],
                   [SimCtrl.ADF_10_DEC,
                    SimCtrl.ADF_10_INC,
                    [ADFSel.ADF_10.CondEqual]+adf_conds],
                   [SimCtrl.ADF_1_DEC,
                    SimCtrl.ADF_1_INC,
                    [ADFSel.ADF_1.CondEqual]+adf_conds]
   ]:

    BravoRotEnc.mgr.btnmapgroup(*paramlist, fast_ctrl_events=4)



headingbug_conds=[AlphaTrigHeld.FALSE, panel_mode_selector_button.CondFlagClear]
gyrodrift_conds =[AlphaTrigHeld.FALSE, panel_mode_selector_button.CondFlagSet]
altdrift_conds  =[AlphaTrigHeld.CLICK1]

for paramlist in [
                   [SimCtrl.HEADING_BUG_DEC,
                    SimCtrl.HEADING_BUG_INC,
                    headingbug_conds,
                    FsuipcCtrl.Heading_Bug_Dec_Fast,
                    FsuipcCtrl.Heading_Bug_Inc_Fast
                   ],
                   [SimCtrl.GYRO_DRIFT_DEC,
                    SimCtrl.GYRO_DRIFT_INC,
                    gyrodrift_conds,
                    None,None,4],
                   [SimCtrl.KOHLSMAN_DEC,
                    SimCtrl.KOHLSMAN_INC,
                    altdrift_conds,
                    None,None,4]
   ]:
    BravoRotEnc.mgr.btnmapgroup(*paramlist, all_conds=PanelMode.HDG_ALT)



btnmap(Bravo.THROTLVR2_REVERSER,SimCtrl.THROTTLE1_DECR,
       action=ButtonAction.HOLD)
btnmap(Bravo.THROTLVR3_REVERSER,SimCtrl.THROTTLE2_DECR,
       action=ButtonAction.HOLD)
btnmap(Bravo.THROTLVR4_REVERSER,SimCtrl.THROTTLE3_DECR,
       action=ButtonAction.HOLD)
btnmap(Bravo.THROTLVR5_REVERSER,SimCtrl.THROTTLE4_DECR,
       action=ButtonAction.HOLD)


# Throttle detents must follow profile specific throttle assignments
btnmap(Bravo.THROTLVR3_DETENT,SimCtrl.THROTTLE1_CUT)
btnmap(Bravo.THROTLVR4_DETENT,SimCtrl.TOGGLE_FEATHER_SWITCH_1,
       action=ButtonAction.PRESS_AND_RELEASE)
btnmap(Bravo.THROTLVR5_DETENT,SimCtrl.MIXTURE1_DECR,action=ButtonAction.HOLD)

end_section()

section("Buttons.Twin")
btnmap(Bravo.THROTLVR1_DETENT,SimCtrl.THROTTLE1_CUT)
btnmap(Bravo.THROTLVR2_DETENT,SimCtrl.THROTTLE2_CUT)
btnmap(Bravo.THROTLVR3_DETENT,SimCtrl.TOGGLE_FEATHER_SWITCH_1,
       action=ButtonAction.PRESS_AND_RELEASE)
btnmap(Bravo.THROTLVR4_DETENT,SimCtrl.TOGGLE_FEATHER_SWITCH_2,
       action=ButtonAction.PRESS_AND_RELEASE)
btnmap(Bravo.THROTLVR5_DETENT,SimCtrl.MIXTURE1_DECR,action=ButtonAction.HOLD)
btnmap(Bravo.THROTLVR6_DETENT,SimCtrl.MIXTURE2_DECR,action=ButtonAction.HOLD)

end_section()

