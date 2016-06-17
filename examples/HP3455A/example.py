#!/usr/bin/env python
#
# Copyright (c) 2012-2014 Poul-Henning Kamp <phk@phk.freebsd.dk>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

from __future__ import print_function

import os
from pyreveng import job, mem, code, listing
import pyreveng.cpu.hp_nanoproc as hp_nanoproc

def setup():

	m = mem.byte_mem(0x0000, 0x0200)
	fn = os.path.join(os.path.dirname(__file__), "1818-2270B.bin")
	m.load_binfile(0, 1, fn)

	pj = job.Job(m, "HP3455A")

	dx = hp_nanoproc.hp_nanoproc_pg()

	return pj, dx

symbols = {
	0x001E: "WAIT_CLOCK_LOW",
	0x0021: "WAIT_CLOCK_HIGH",
	0x0028: "PARITY_ERROR",
	0x002A: "WAIT_CLOCK_LOW2",
	0x0032: "SET_LATCHES",
	0x003C: "START_AUTOZERO",
	0x003E: "AUTOZERO_LOOP",
	0x004C: "ZERO_COUNTS",
	0x004C: "SET_LVIN",
	0x0052: "SET_1PLC",
	0x0055: "SET_LNRF_HPRF",
	0x0058: "SET_LVIN_OFF",
	0x005A: "INTEGRATE_LOOP",
	0x0068: "LAB_068",
	0x006D: "LAB_06D",
	0x0075: "SET_LNRF_HPRF2",
	0x0078: "SET_LVIN_OFF2",
	0x007C: "LAB_07C",
	0x0081: "GOTO_RUNDOWN1",
	0x0088: "GOTO_RUNDOWN2",
	0x008B: "OVER10V",
	0x009C: "RUNDOWN_DURING_INTEGRATE",
	0x00AD: "RUNDOWN_DURING_INTEGRATE_LOOP",
	0x00BE: "LAB_0BE",
	0x00C0: "OUTPUT_NEXT_BYTE",
	0x00C3: "OUTPUT_BIT",
	0x00C9: "OUTPUT_FIRST_BYTE",
	0x00CA: "WAIT_CLOCK_HIGH2",
	0x00D5: "SET_OUTPUT_BIT",
	0x00E9: "PATCH_0E9",
	0x00FA: "DELAY3",
	0x00FB: "DELAY2",
	0x00FF: "INTERRUPT",
	0x0110: "SIGNS_DIFFERENT",
	0x0118: "SUBTRACT_SLOW_COUNT",
	0x0130: "LOC_130",
	0x0131: "LOC_131",
	0x0136: "OUTPUT_TO_OUTGUARD",
	0x0145: "RESTART_OUTPUT",
	0x014A: "RUNDOWN",
	0x014F: "MUL8",
	0x016C: "FD_LNRF",
	0x016E: "FAST_DECREMENT_LOOP",
	0x016F: "FDL2",
	0x0177: "FD_HPRF",
	0x017B: "FI_HPRF",
	0x017F: "FI_LNRF",
	0x0184: "FAST_INCREMENT_LOOP",
	0x0185: "FIL2",
	0x018B: "END_FAST_RUNDOWN",
	0x0196: "FR_NO_OVERFLOW",
	0x019B: "SLOW_RUNDOWN",
	0x01A1: "SR_HPRS",
	0x01A5: "SR_LNRS",
	0x01A8: "SLOW_RUNDOWN_LOOP",
	0x01AB: "SUB_1AB",
	0x01BB: "LAB_1BB",
	0x01BD: "LAB_1BD",
	0x01C5: "LAB_1C5",
	0x01C6: "LAB_1C6",
	0x01C8: "LAB_1C8",
	0x01CB: "INC_PLCCTR",
	0x01D7:	"READ_OUTGUARD",
	0x01D9: "RO_LOOP",
	0x01DD: "RO_WAIT_CLOCK",
	0x01EA: "RO_ZERO_BIT",
	0x01F0:	"STARTUP",
}

def task(pj, dx):
	pj.todo(0, dx.disass)
	pj.todo(0xf7, dx.disass)
	pj.todo(0xfd, dx.disass)
	pj.todo(0xff, dx.disass)

	if True:
		for a,l in symbols.items():
			pj.set_label(a,l)
	pj.set_comment(0x000, """HP 3455A inguard ROM
The nanoprocessor takes two clocks per instruction and runs at 819.2 kHz
if 60Hz line frequency is selected.

The startup code is at 0x0FD

DEV1 bits:	REG3 bits:
0x20	LNRF	0	Autocal LNRF and HPRF only
0x10	HPRF	1	8 PLC	
0x08	HAZ	2	Autocal - no input to AtoD
0x04	HPRS	3
0x02	LNRS	4	Set device latches to values from outguard
0x01	LVIN	5
Note all device output is inverted in hardware, so the complement must be written to DEV1
""")
	pj.set_comment(0x03C, """AtoD Auto-Zero
0x14 = HAZ on, everything else off
AUTOZERO_LOOP is 16 instructions per iteration
""")
	pj.set_comment(0x05A, """Main Integration Loop
Register usage:
REG0			# PLCs
REG1
REG2
REG3			Control bits from Outguard
REG9:REG8		One PLC counter 
REG15			AtoD device bits
REG5			AtoD device bits for rundown during integration
REG13:REG12:REG11	Count

Each loop or sub-loop during integration is exactly 32 instructions
The count is shifted left by 3 after integration
During fast rundown, each loop is exactly 4 instructions and
during slow rundown, each loop is exactly 2 instructions
REG11 is set during slow rundown, REG13:REG12 are used during integration and fast rundown
The doubling of the count rate and inherent 8 bit shift give the 128:1 weighting between
fast and slow rundown.
""")

	while pj.run():
		pass

def output(pj):
	code.lcmt_flows(pj)
	listing.Listing(pj)

if __name__ == '__main__':
	pj, cx = setup()
	task(pj, cx)
	output(pj)

