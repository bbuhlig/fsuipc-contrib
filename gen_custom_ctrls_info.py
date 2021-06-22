#!/usr/bin/python3
"""
gen_custom_ctrls_info -- Generate custom control info file
Version 20210621-0-5f0348e

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

... as well as FSUIPC7.ini and custom event files in the FSUIPC7 install
directory, to produce an information file for custom events similar to the
"Controls List for MSFS Build 999.txt" file in the FSUIPC7 documents
directory. Such a file may be useful in mapping joystick and key actions to
custom control events.

The generated file is named "custom_ctrls_info.tsv.txt", because the format
of the file is tab-separated values for ease of import into a spreadsheet.
Another difference from the format of "Controls List for MSFS Build 999.txt",
includes an additional column identifying a Mobiflight CID "Group" definition
of each custom control event.

The expectation is that the script is executed in the FSUIPC7 directory,
where both the mobiflight-msfs2020_eventids.cip.txt file, the FSUIPC7.ini
file, and all the linked *.evt files referred to in the FSUIPC7.ini directory
can be found.

"""
import configparser
import re
import sys

# Output
desc_fn = 'custom_ctrls_info.tsv.txt'


# Build group dict
cid_fn = 'mobiflight-msfs2020_eventids.cip.txt'
module = 'MobiFlight'
grp_dict = dict()

with open(cid_fn,"r") as cid_ifh:
   cur_group = None
   for line in map(str.rstrip, cid_ifh):
      m = re.match(r'(.*):GROUP',line)
      if m:
         cur_group=m.group(1)
         re.sub(r'[ \t]','_',cur_group)
      elif cur_group:
         grp_dict[f'{module}.{line}']=cur_group

config = configparser.ConfigParser(strict=False)
config.read('FSUIPC7.ini')

ctrl_base = 32768

with open(desc_fn,"w",newline='\r\n') as desc_ofh:
   desc_ofh.write(f'{"Ctrl#":<5.5}\t{"Event":<70.70}\tGroup\n') #Header
   desc_ofh.write(f'{"=" * 5:<5.5}\t{"=" * 70:<70.70}\t{"=" * 15}\n')

   for _i, evt_fn_base in config.items('EventFiles'):
      with open(f'{evt_fn_base}.evt',"r") as evt_ifh:
         for line in map(str.rstrip, evt_ifh):
            m = re.match(r'(?P<ctrl_num>\d+)=(?P<evt>\S+)',line)
            if m:
               grp = grp_dict.get(m.group('evt'),None)
               ctrl = ctrl_base + int(m.group("ctrl_num"))
               desc_ofh.write(f'{ctrl:<5}\t{m.group("evt"):<70.70}\t{grp}\n')

         ctrl_base = ctrl_base + 256
