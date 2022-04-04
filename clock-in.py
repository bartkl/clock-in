#!/usr/bin/env python

import subprocess
from enum import IntEnum


class Activity(IntEnum):
    WORK = 0
    SLACK = 1


def run_clock_in_dialog() -> Activity:
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

    completed_process = subprocess.run([cmd], shell=True)

    return Activity(completed_process.returncode)



if __name__ == "__main__":
    print(run_clock_in_dialog())
