"""
alpha.py -- Honeycomb Alpha Button Mappings
Version 20210616-0-726d3a5

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

   # Left Yoke arm - 1 trigger, 1 pushbutton, 2 up btns, 2 down btns, 1 POV hat

   LY_TRIG = 0,            # Left Yoke arm, TRIGger
   LY_WHITE = 1,           # Left Yoke arm, White button
   LY_QBL_U = 4,           # Left Yoke arm, Quad Bottom Left button w/ action Up
   LY_QTL_D = 5,           # Left Yoke arm, Quad Top Left button w/ action Down
   LY_QBR_U = 6,           # Left Yoke arm, Quad Bottom Right button w/ action Up
   LY_QTR_D = 7,           # Left Yoke arm, Quad Top Right button w/ action Down
   LY_HAT_U = 32,          # Left Yoke arm, Hat switch w/ action Up
   LY_HAT_UR = 33,         # Left Yoke arm, Hat switch w/ action Up and Right
   LY_HAT_R = 34,          # Left Yoke arm, Hat switch w/ action Right
   LY_HAT_DR = 35,         # Left Yoke arm, Hat switch w/ action Down and Right
   LY_HAT_D = 36,          # Left Yoke arm, Hat switch w/ action Down
   LY_HAT_DL = 37,         # Left Yoke arm, Hat switch w/ action Down and Left
   LY_HAT_L = 38,          # Left Yoke arm, Hat switch w/ action Left
   LY_HAT_UL = 39,         # Left Yoke arm, Hat switch w/ action Up and Left

   # Right Yoke arm - 2 pushbuttons, 2 right buttons, 2 left buttons
   RY_WHITE = 2,           # Right Yoke arm, White button
   RY_RED = 3,             # Right Yoke arm, Red button
   RY_QTL_R = 8,           # Right Yoke arm, Quad Top Left button w/ action Right
   RY_QTR_L = 9,           # Right Yoke arm, Quad Top Right button w/ action Left
   RY_QBL_R = 10,          # Right Yoke arm, Quad Bottom Left button w/ action Right
   RY_QBR_L = 11,          # Right Yoke arm, Quad Bottom Right button w/ action Left

   # Mid-panel rockers (2 groups of 2)
   ROCKER_1_ON = 12,
   ROCKER_1_OFF = 13,
   ROCKER_2_ON = 14,
   ROCKER_2_OFF = 15,
   ROCKER_3_ON = 16,
   ROCKER_3_OFF = 17,
   ROCKER_4_ON = 18,
   ROCKER_4_OFF = 19,
   MASTER_ALT_ON = 12,
   MASTER_ALT_OFF = 13,
   MASTER_BAT_ON = 14,
   MASTER_BAT_OFF = 15,
   AVIONICS_BUS1_ON = 16,
   AVIONICS_BUS1_OFF = 17,
   AVIONICS_BUS2_ON = 18,
   AVIONICS_BUS2_OFF = 19,

   # Lower left toggles (5)
   TOGGLE_1_ON = 20,
   TOGGLE_1_OFF = 21,
   TOGGLE_2_ON = 22,
   TOGGLE_2_OFF = 23,
   TOGGLE_3_ON = 24,
   TOGGLE_3_OFF = 25,
   TOGGLE_4_ON = 26,
   TOGGLE_4_OFF = 27,
   TOGGLE_5_ON = 28,
   TOGGLE_5_OFF = 29,
   BCN_ON = 20,
   BCN_OFF = 21,
   LAND_ON = 22,
   LAND_OFF = 23,
   TAXI_ON = 24,
   TAXI_OFF = 25,
   NAV_ON = 26,
   NAV_OFF = 27,
   STROBE_ON = 28,
   STROBE_OFF = 29,

   # Lower right 5 position rotary selector
   ROTARYSEL_1 = 30,
   ROTARYSEL_2 = 31,
   ROTARYSEL_3 = 132,
   ROTARYSEL_4 = 133,
   ROTARYSEL_5 = 134,
   MAG_OFF = 30,
   MAG_R = 31,
   MAG_L = 132,
   MAG_BOTH = 133,
   MAG_START = 134
)
