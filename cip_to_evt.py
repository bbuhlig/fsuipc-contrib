#!/usr/bin/python3
"""
cip_to_evt -- Convert mobiflight CIP file to FSUIPC7 evt files
Version 20210607-0-12da26b

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

This python3.6+ script parses the file "mobiflight-msfs2020_eventids.cip.txt"
whose contents are downloaded from the URL...

https://bitbucket.org/mobiflight/mobiflightfc/src/master/Presets/msfs2020_eventids.cip

... and generates as many *.evt files in the current directory as is
necessary to expose all the events in the CIP file.

The expectation is that the script is executed with the
mobiflight-msfs2020_eventids.cip.txt file in the current directory.
The *.evt files will be generated in the current directory, and should
be copied into the FSUIPC7 installation directory. Once FSUIPC7 is started
they should become assignable custom control events. 

"""


import re
import sys

module = 'MobiFlight'
shortpfx = 'MB'

cur_group = None
evt_ofh = None
n_ev_files = 0
n_evts = None

cid_fn = 'mobiflight-msfs2020_eventids.cip.txt'
cid_ifh = open(cid_fn,"r")

for line in map(str.rstrip, cid_ifh):
   m = re.match(r'(.*):GROUP',line)
   if m:
      cur_group=m.group(1)
   elif cur_group and cur_group != "STANDARD":
      if n_evts == None:
         fn = f'{n_ev_files:03}_{shortpfx}.evt'
         evt_ofh = open(fn,"w")
         evt_ofh.write(f"[Events]\n")
         n_evts = 0
         n_ev_files = n_ev_files + 1

      d = f'{n_evts}={module}.{line}\n'
      evt_ofh.write(d)
      n_evts = n_evts + 1
      if n_evts > 255:
         n_evts = None   
