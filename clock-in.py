#!/usr/bin/env python

import os
import subprocess
from tempfile import NamedTemporaryFile
from enum import IntEnum
from typing import Optional


class Activity(IntEnum):
    WORK = 0
    SLACK = 1


def generate_overview() -> str:
    text_file = NamedTemporaryFile(delete=False).name
    with open("example-output.txt") as g, open(text_file, mode="w") as f:
        f.write(g.read())

    return text_file


def run_clock_in_dialog(overview_file) -> Optional[Activity]:
    cmd = f"""
        yad \
            --title "Clock In" \
            --window-icon "appointment" \
            --width 340 \
            --height 340 \
            --center \
            --text-info \
            --fontname "Monospace 10" \
            --filename {overview_file} \
            --margins 12 \
            --buttons-layout center \
            --button Register!bookmark-new:0 \
            --button Calibrate!find-location-symbolic:1
    """

    completed_process = subprocess.run([cmd], shell=True)

    try:
        return Activity(completed_process.returncode)
    except ValueError:
        return


def main():
    overview_file = generate_overview()
    activity = run_clock_in_dialog(overview_file)


    # Clean-up.

    os.unlink(overview_file)  # Remove tempfile.



if __name__ == "__main__":
    main()
