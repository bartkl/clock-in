#!/usr/bin/env python

import subprocess


def run_clock_in_dialog():
    cmd = """
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
    return subprocess.run([cmd], shell=True)




if __name__ == "__main__":
    completed_process = run_clock_in_dialog()
    print(completed_process.returncode)
