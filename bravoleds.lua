--[[
bravoleds - FSUIPC event-based manager of Honeycomb Bravo LEDs
Version 20210616-1-0f791d2

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

This code tries to manage the Bravo LEDs according to FSUIPC offset
events received, for example turning the gear LEDs green upon receiving
the OFFSET_GEAR_*_POSITION offset events indicating that the gear is
down.  There is support to set particular LEDs solid on, solid off, and
blinking. There is also stub support for updating the master warning and
caution lights based on individual detected problematic conditions in
absence of any access to events that directly provide what might be shown
in the aircraft e.g. through Lvars.

To be clear, the support in here as of this date is incomplete.  I wrote this
more or less as a learning exercise about the capabilities of FSUIPC Lua
plugins and the Bravo hardware, but I'm more of a VR Flight Sim user these days
and hence the state of Bravo LEDs is of lesser concern for me, so I might not
able to help anyone picking up this work as much as I might regarding some of
my other contributions. Nonetheless the ideas in here could be a helpful place
to start for some users trying to get the Bravo LEDs to work through FSUIPC.

The code is derived from information in the thread
https://forum.simflight.com/topic/91463-how-to-approach-controlling-leds-in-joystick
Thanks to Cool Dan Luke and Pete Dowson for their knowledge sharing.


]]


-- LED codes:
HDG              =0x00000001
NAV              =0x00000002
APR              =0x00000004
REV              =0x00000008
ALT              =0x00000010
VS               =0x00000020
IAS              =0x00000040
AUTO_PILOT       =0x00000080
GEARIND_OFF      = 0
GEARIND_GREEN    = 1
GEARIND_RED      = 2
GEAR_LEFT        =0x00000100
GEAR_LEFT_GREEN  =0x00000100
GEAR_LEFT_RED    =0x00000200
GEAR_CNTR        =0x00000400
GEAR_CNTR_GREEN  =0x00000400
GEAR_CNTR_RED    =0x00000800
GEAR_RIGHT       =0x00001000
GEAR_RIGHT_GREEN =0x00001000
GEAR_RIGHT_RED   =0x00002000
MASTER_WARNING   =0x00004000
ENGINE_FIRE      =0x00008000
LOW_OIL_PRESSURE =0x00010000
LOW_FUEL_PRESSURE=0x00020000
ANTI_ICE         =0x00040000
STARTER_ENGAGED  =0x00080000
APU              =0x00100000
MASTER_CAUTION   =0x00200000
VACUUM           =0x00400000
LOW_HYD_PRESSURE =0x00800000
AUX_FUEL_PUMP    =0x01000000
PARKING_BRAKE    =0x02000000
LOW_VOLTS        =0x04000000
DOOR             =0x08000000

_flash=0
_state=0

dev, rd, wrf, wr, init = com.openhid(0x294B,0x1901,0,0)
if dev == 0 then
  ipc.log("bravoleds: Could not open device")
  ipc.exit()
end

function _update()

  com.writefeature(dev,
                   string.char(0,
                               logic.And(0xFF,_state),
                               logic.And(0xFF,logic.Shr(_state,8)),
                               logic.And(0xFF,logic.Shr(_state,16)),
                               logic.And(0xFF,logic.Shr(_state,24))
                               ),
                   wrf)
end

function _flash_toggle()
   _state=logic.Xor(_state,_flash)
   _update()
end

function _start()
   event.terminate('_stop')
   event.sim(CLOSE,'_stop')
   event.timer(500, '_flash_toggle')
end

function _stop()
   event.cancel('_flash_toggle')
   _flash=0
   _state=0
   _update()
end

function set_led(sw,is_on,do_flash)
  if (is_on) then
     if (do_flash) then
        _flash=logic.Or(_flash,sw)
     else
        _state=logic.Or(_state,sw)
        _flash=logic.And(_flash,logic.Not(sw))
     end
  else
     _state=logic.And(_state,logic.Not(sw))
     _flash=logic.And(_flash,logic.Not(sw))
  end
end

function set_gear_led(sw,color,do_flash)
   set_led(sw*GEARIND_GREEN,(color == GEARIND_GREEN),do_flash)
   set_led(sw*GEARIND_RED,(color == GEARIND_RED),do_flash)
end

_start()

-- Example:
--set_gear_led(GEAR_RIGHT+GEAR_CNTR,GEARIND_GREEN) -- solid green
--set_led(GEAR_LEFT_RED,true) -- solid red
--set_led(MASTER_WARNING,true,true) -- flashing


--------- Event responses below

OFFSET_AUTOPILOT_MASTER=0x07BC
OFFSET_AUTOPILOT_NAV1_LOCK=0x07C4
OFFSET_AUTOPILOT_HEADING_LOCK=0x07C8
OFFSET_AUTOPILOT_ALTITUDE_HOLD=0x07D8
OFFSET_AUTOPILOT_AIRSPEED_HOLD=0x07DC
OFFSET_AUTOPILOT_MACH_HOLD=0x07E4
OFFSET_AUTOPILOT_VERTICAL_HOLD=0x07EC
OFFSET_AUTOPILOT_RPM_HOLD=0x07F4
OFFSET_AUTOPILOT_GLIDESLOPE_HOLD=0x07FC
OFFSET_AUTOPILOT_APPROACH_HOLD=0x0800
OFFSET_AUTOPILOT_BACKCOURSE_HOLD=0x0804

OFFSET_IS_GEAR_RETRACTABLE=0x060C
OFFSET_GEAR_HANDLE_POSITION=0x0BE8
OFFSET_GEAR_CENTER_POSITION=0x0BEC
OFFSET_GEAR_RIGHT_POSITION=0x0BF0
OFFSET_GEAR_LEFT_POSITION=0x0BF4

OFFSET_BRAKE_PARKING_POSITION=0x0BC8
OFFSET_SIM_ON_GROUND=0x0366

OFFSET_GENERAL_ENG_ANTI_ICE_POSITION_1=0x08B2
OFFSET_GENERAL_ENG_ANTI_ICE_POSITION_2=0x094A


MCF_GearInTransOnGround=0x00000001
MCF_GearStateDiff=0x00000002
MCF_ParkingBrakeSetInAir=0x00000004
-- L FUEL LOW (<3 gal)
-- R FUEL LOW (<3 gal)
-- LOW VOLTS (<24 V)
-- PITOT FAIL (inop)
-- PITOT OFF (?)


MWF_GearFailedLeft=0x00000100
MWF_GearFailedCenter=0x00000400
MWF_GearFailedRight=0x00001000

-- OIL PRES LO  (<25psi)
-- FUEL PRES LOW (<14 psi)
-- FUEL PRES HIGH (>35 psi)
-- ALTERNATOR (failed, battery is only electrical source)
-- STARTER ENGD
-- DOOR OPEN
-- TRIM FAIL (Autopilot auto trim is inoperative)

MasterCautionFlags=0
MasterCautionAck=false
MasterWarningFlags=0
MasterWarningAck=false

ParkingBrakeIsSet=true;
SimIsOnGround=true;
GearIsRetractable=false;
GearHandleIsDown=true;
LeftGearIsDown=true;
RightGearIsDown=true;
CenterGearIsDown=true;

SetBits = logic.Or
function ClearBits(flags,bits)
   return logic.And(flags,logic.Not(bits))
end
function MCFClear(bits) MasterCautionFlags=ClearBits(MasterCautionFlags,bits) end
function MCFSet(bits)
   if logic.And(MasterCautionFlags,bits) ~= 0 then MasterCautionAck = false end
   MasterCautionFlags=SetBits(MasterCautionFlags,bits)
end
function MCFCondition(bits,condition) if condition then MCFSet(bits) else MCFClear(bits) end end
function MWFClear(bits) MasterWarningFlags=ClearBits(MasterWarningFlags,bits) end
function MWFSet(bits)
   if logic.And(MasterWarningFlags,bits) ~= 0 then MasterWarningAck = false end
   MasterWarningFlags=SetBits(MasterWarningFlags,bits)
end
function MWFCondition(bits,condition) if condition then MWFSet(bits) else MWFClear(bits) end end

function manage_gear_led(gear_id,gear_is_down,control_is_down,sim_is_on_ground,gear_is_failed)
   if (GearIsRetractable) then
      if (gear_is_failed) then
         set_gear_led(gear_id,GEARIND_RED,(not (gear_is_down and control_is_down)))
      else
         if ((not gear_is_down) and (not control_is_down)) then
            set_gear_led(gear_id,GEARIND_OFF)
         else
            set_gear_led(gear_id,GEARIND_GREEN,(gear_is_down ~= control_is_down))
         end
      end
   else
      set_gear_led(gear_id,GEARIND_OFF)
   end

   MWFCondition(gear_id, gear_is_failed)
end

function manage_all_gear_leds(l_dn,c_dn,r_dn,ctrl_dn,on_gnd,l_fail,c_fail,r_fail)
  manage_gear_led(GEAR_LEFT,l_dn,ctrl_dn,on_gnd,l_fail)
  manage_gear_led(GEAR_CNTR,c_dn,ctrl_dn,on_gnd,c_fail)
  manage_gear_led(GEAR_RIGHT,r_dn,ctrl_dn,on_gnd,r_fail)
end

function offset_event(offset,value)
   if (offset == OFFSET_AUTOPILOT_MASTER) then set_led(AUTO_PILOT,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_HEADING_LOCK) then set_led(HDG,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_NAV1_LOCK) then set_led(NAV,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_APPROACH_HOLD) then set_led(APR,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_GLIDESLOPE_HOLD) then set_led(APR,(value~=0),true)
   elseif (offset == OFFSET_AUTOPILOT_BACKCOURSE_HOLD) then set_led(REV,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_ALTITUDE_HOLD) then set_led(ALT,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_VERTICAL_HOLD) then set_led(VS,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_AIRSPEED_HOLD) or (offset == OFFSET_AUTOPILOT_MACH_HOLD) then
      set_led(IAS,(value~=0))
   elseif (offset == OFFSET_AUTOPILOT_RPM_HOLD) then set_led(IAS,(value~=0),true)
   elseif (offset == OFFSET_IS_GEAR_RETRACTABLE) then GearIsRetractable=(value~=0)
   elseif (offset == OFFSET_GEAR_HANDLE_POSITION) then
      GearHandleIsDown=(value~=0)
      manage_all_gear_leds(LeftGearIsDown,CenterGearIsDown,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
      MCFCondition(MCF_GearInTransOnGround, (SimIsOnGround and not GearHandleIsDown and GearIsRetractable))
   elseif (offset == OFFSET_GEAR_CENTER_POSITION) then
      CenterGearIsDown=(value~=0)
      manage_gear_led(GEAR_CNTR,CenterGearIsDown,GearHandleIsDown,SimIsOnGround)
   elseif (offset == OFFSET_GEAR_RIGHT_POSITION) then
      RightGearIsDown=(value~=0)
      manage_gear_led(GEAR_RIGHT,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
   elseif (offset == OFFSET_GEAR_LEFT_POSITION) then
      LeftGearIsDown=(value~=0)
      manage_gear_led(GEAR_LEFT,LeftGearIsDown,GearHandleIsDown,SimIsOnGround)
   elseif (offset == OFFSET_BRAKE_PARKING_POSITION) then
      ParkingBrakeIsSet=(value~=0)
      set_led(PARKING_BRAKE,ParkingBrakeIsSet,not SimIsOnGround)
      MCFCondition(MCF_ParkingBrakeSetInAir,(ParkingBrakeIsSet and not SimIsOnGround))
   elseif (offset == OFFSET_SIM_ON_GROUND) then
      SimIsOnGround=(value~=0)
      manage_all_gear_leds(LeftGearIsDown,CenterGearIsDown,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
      set_led(PARKING_BRAKE,ParkingBrakeIsSet,not SimIsOnGround)
      MCFCondition(MCF_ParkingBrakeSetInAir,(ParkingBrakeIsSet and not SimIsOnGround))
   end

   -- manage master caution and master warning
   MCFCondition(MCF_GearStateDiff, ((LeftGearIsDown ~= RightGearIsDown) or (LeftGearIsDown ~= CenterGearIsDown)))

   set_led(MASTER_CAUTION,(MasterCautionFlags~=0),(not MasterCautionAck))
   set_led(MASTER_WARNING,(MasterWarningFlags~=0),(not MasterWarningAck))
end

event.offset(OFFSET_SIM_ON_GROUND,"UW","offset_event")

event.offset(OFFSET_AUTOPILOT_MASTER,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_HEADING_LOCK,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_NAV1_LOCK,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_APPROACH_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_GLIDESLOPE_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_BACKCOURSE_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_ALTITUDE_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_VERTICAL_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_AIRSPEED_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_MACH_HOLD,"UD","offset_event")
event.offset(OFFSET_AUTOPILOT_RPM_HOLD,"UD","offset_event")
event.offset(OFFSET_GEAR_HANDLE_POSITION,"UD","offset_event")
event.offset(OFFSET_GEAR_CENTER_POSITION,"UD","offset_event")
event.offset(OFFSET_GEAR_RIGHT_POSITION,"UD","offset_event")
event.offset(OFFSET_GEAR_LEFT_POSITION,"UD","offset_event")
event.offset(OFFSET_BRAKE_PARKING_POSITION,"UW","offset_event")
