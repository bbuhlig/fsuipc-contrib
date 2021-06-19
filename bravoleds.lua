--[[
bravoleds - FSUIPC event-based manager of Honeycomb Bravo LEDs
Version 20210619-0-8ea211c

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
SimVar = {
  _ReadFuncs = {UB=ipc.readUB,UW=ipc.readUW,UD=ipc.readUD},
  _WriteFuncs = {UB=ipc.writeUB,UW=ipc.writeUW,UD=ipc.writeUD}
}

SimVar.__index = SimVar
SimVar._OffsetDict = {}

function SimVar.new(offset,typecode,autoupdate,update_cb)
  local self = setmetatable({}, SimVar)
  self._offset = offset
  self._typecode = typecode
  self.value = nil

  if (autoupdate) then
     SimVar._OffsetDict[self._offset] = self
     self._update_cb = update_cb
     event.offset(self._offset,self._typecode,"SimVar._OffsetEvent")
  end

  return self
end

function SimVar.readOffset(self)
  readfunc = SimVar._ReadFuncs[self._typecode]
  self.value = readfunc(self._offset)
  return self.value
end

function SimVar.get(self)
  if self.value == nil then
    self:readOffset()
  end
  return self.value
end

function SimVar.isTrue(self)
  return self:get() ~= 0
end

function SimVar.set(self,value)
  writefunc = SimVar._WriteFuncs[self._typecode]
  self.value = value
  return writefunc(self._offset,value)
end


function SimVar._OffsetEvent(offset,value)
  obj=SimVar._OffsetDict[offset]
  if obj ~= nil then
     obj.value=value
     if obj._update_cb ~= nil then
        obj:_update_cb()
     end
  end 
end


SimVar.new(0x07BC,"UD",true,function(self) set_led(AUTO_PILOT,self:isTrue()) end) -- AUTOPILOT MASTER
SimVar.new(0x07C4,"UD",true,function(self) set_led(NAV,self:isTrue()) end) -- AUTOPILOT NAV1 LOCK
SimVar.new(0x07C8,"UD",true,function(self) set_led(HDG,self:isTrue()) end) -- AUTOPILOT HEADING LOCK
SimVar.new(0x07D8,"UD",true,function(self) set_led(ALT,self:isTrue()) end) -- AUTOPILOT ALTITUDE HOLD
SimVar.new(0x07DC,"UD",true,function(self) set_led(IAS,self:isTrue()) end) -- AUTOPILOT AIRPSEED HOLD
SimVar.new(0x07E4,"UD",true,function(self) set_led(IAS,self:isTrue()) end) -- AUTOPILOT MACH HOLD
SimVar.new(0x07F4,"UD",true,function(self) set_led(IAS,self:isTrue(),true) end) -- AUTOPILOT RPM HOLD
SimVar.new(0x07EC,"UD",true,function(self) set_led(VS,self:isTrue()) end) -- AUTOPILOT VERTICAL HOLD
SimVar.new(0x07FC,"UD",true,function(self) set_led(APR,self:isTrue(),true) end) -- AUTOPILOT GLIDESLOPE HOLD
SimVar.new(0x0800,"UD",true,function(self) set_led(APR,self:isTrue()) end) -- AUTOPILOT APPROACH HOLD
SimVar.new(0x0804,"UD",true,function(self) set_led(REV,self:isTrue()) end) -- AUTOPILOT BACKCOURSE HOLD

GearIsRetractable = SimVar.new(0x060C,"UB",true)
ParkingBrakeIsSet = SimVar.new(0x0BC8,"UW",true,function(self)
  set_led(PARKING_BRAKE,ParkingBrakeIsSet:isTrue(),not SimIsOnGround)
  MCFCondition(MCF_ParkingBrakeSetInAir,(ParkingBrakeIsSet:isTrue() and not SimIsOnGround:isTrue()))
  upd_master_caution_warning()
end)
SimIsOnGround = SimVar.new(0x0366,"UW",true,function(self)
  manage_all_gear_leds(LeftGearIsDown,CenterGearIsDown,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
  set_led(PARKING_BRAKE,ParkingBrakeIsSet:isTrue(),not SimIsOnGround:isTrue())
  MCFCondition(MCF_ParkingBrakeSetInAir,(ParkingBrakeIsSet:isTrue() and not SimIsOnGround:isTrue()))
  upd_master_caution_warning()
end)
GearHandleIsDown = SimVar.new(0x0BE8,"UD",true,function(self)
  manage_all_gear_leds(LeftGearIsDown,CenterGearIsDown,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
  MCFCondition(MCF_GearInTransOnGround, (SimIsOnGround:isTrue() and not GearHandleIsDown:isTrue() and GearIsRetractable:isTrue()))
  upd_master_caution_warning()
end)
CenterGearIsDown = SimVar.new(0x0BEC,"UD",true,function(self)
  manage_gear_led(GEAR_CNTR,CenterGearIsDown,GearHandleIsDown,SimIsOnGround)
  upd_master_caution_warning()
end)
RightGearIsDown = SimVar.new(0x0BF0,"UD",true,function(self)
  manage_gear_led(GEAR_RIGHT,RightGearIsDown,GearHandleIsDown,SimIsOnGround)
  upd_master_caution_warning()
end)
LeftGearIsDown = SimVar.new(0x0BF4,"UD",true,function(self)
  manage_gear_led(GEAR_LEFT,LeftGearIsDown,GearHandleIsDown,SimIsOnGround)
  upd_master_caution_warning()
end)


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
   if (GearIsRetractable:isTrue()) then
      if (gear_is_failed) then
         set_gear_led(gear_id,GEARIND_RED,(not (gear_is_down:isTrue() and control_is_down:isTrue())))
      else
         if ((not gear_is_down:isTrue()) and (not control_is_down:isTrue())) then
            set_gear_led(gear_id,GEARIND_OFF)
         else
            set_gear_led(gear_id,GEARIND_GREEN,(gear_is_down:isTrue() ~= control_is_down:isTrue()))
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

function upd_master_caution_warning()
   MCFCondition(MCF_GearStateDiff, ((LeftGearIsDown:isTrue() ~= RightGearIsDown:isTrue()) or (LeftGearIsDown:isTrue() ~= CenterGearIsDown:isTrue())))

   set_led(MASTER_CAUTION,(MasterCautionFlags~=0),(not MasterCautionAck))
   set_led(MASTER_WARNING,(MasterWarningFlags~=0),(not MasterWarningAck))
end

