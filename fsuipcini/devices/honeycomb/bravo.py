"""
bravo.py -- Honeycomb Bravo Button Mappings
Version 20210616-0-2c874dc

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
ButtonMappings = dict(

   # Top Left - 5 position Rotary Selector
   ROTARYSEL_1 = 16,
   ROTARYSEL_2 = 17,
   ROTARYSEL_3 = 18,
   ROTARYSEL_4 = 19,
   ROTARYSEL_5 = 20,
   BUGSEL_IAS = 16,
   BUGSEL_CRS = 17,
   BUGSEL_HDG = 18,
   BUGSEL_VS = 19,
   BUGSEL_ALT = 20,

   # Top Middle - AP function buttons (7)
   FN1 = 0,
   FN2 = 1,
   FN3 = 2,
   FN4 = 3,
   FN5 = 4,
   FN6 = 5,
   FN7 = 6,
   HDG = 0,
   NAV = 1,
   APR = 2,
   REV = 3,
   ALT = 4,
   CRS = 5,
   IAS = 6,
   ROTENC_SEL = 6,       # Rotary Encoder's primary "selection" button
   ROTENC_SEL_1L = 6,    #  ... shall be 1st function button to its Left
   ROTENC_SEL_2L = 5,    # Rotary Encoder's secondary "selection" button is 2nd to its Left
   ROTENC_SEL_3L = 4,    # Rotary Encoder's tertiary "selection" button is 3rd to its Left

   # Top Right - Rotary encoder
   ROTENC_INCR = 12,
   ROTENC_DECR = 13,

   # Top Right - Autopilot button
   AP  = 7,
   FN8 = 7,
   ROTENC_SEL_R =  7,    # Rotary Encoder's alternate "selection" button on its right

   # Middle Left - Gear Lever
   GEAR_UP = 30,
   GEAR_DOWN = 31,

   # Middle Center - Rocker switches (7)
   ROCKER_1_ON  = 133,
   ROCKER_1_OFF = 134,
   ROCKER_2_ON  = 135,
   ROCKER_2_OFF = 136,
   ROCKER_3_ON  = 137,
   ROCKER_3_OFF = 138,
   ROCKER_4_ON  = 139,
   ROCKER_4_OFF = 140,
   ROCKER_5_ON  = 141,
   ROCKER_5_OFF = 142,
   ROCKER_6_ON  = 143,
   ROCKER_6_OFF = 144,
   ROCKER_7_ON  = 145,
   ROCKER_7_OFF = 146,

   # Middle Right - Flaps Lever
   FLAPS_DOWN = 14,
   FLAPS_UP = 15,
   LEVER_DOWN = 14,
   LEVER_UP = 15,

   # Lower Left - Trim Wheel
   TRIMWHEEL_DOWN = 21,
   TRIMWHEEL_UP = 22,

   # Throttle switches - Engine reverser
   THROTLVR2_REVERSER = 8,
   THROTLVR3_REVERSER = 9,
   THROTLVR4_REVERSER = 10,
   THROTLVR5_REVERSER = 11,

   # Throttle switches - TakeOff / Go-Around
   THROTLVR1_AND_2_TOGA = 28,
   THROTLVR3_TOGA = 29,
   THROTLVR4_TOGA = 147,

   # Throttle switches - Lower throttle lever detents
   THROTLVR1_DETENT = 23,
   THROTLVR2_DETENT = 24,
   THROTLVR3_DETENT = 25,
   THROTLVR4_DETENT = 26,
   THROTLVR5_DETENT = 27,
   THROTLVR6_DETENT = 132
)
