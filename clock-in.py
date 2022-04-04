#!/usr/bin/env python

import subprocess

UI_CMD = """
yad \
	--title "Clocker" \
	--window-icon "appointment" \
	--width 340 \
	--height 340 \
	--center \
	--text-info \
	--fontname "Monospace 10" \
	--filename example-output.txt \
	--margins 12 \
	--buttons-layout center \
	--button Worked!emblem-default:0 \
	--button Slacked!weather:1
"""


if __name__ == "__main__":
    completed_process = subprocess.run([UI_CMD], shell=True)
    print(completed_process.returncode)
