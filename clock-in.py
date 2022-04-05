#!/usr/bin/env python

import os
import random
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
    hours = '04:30'

    worked = "Worked:"
    left = "Left:\t"
    surplus = "Surplus:"

    left_or_surplus_today = surplus
    left_or_surplus_week = left

    info = f"""
        <span size="large"><b>\tToday\n</b></span>
        <span size="medium">\t\t{worked}\t\t\t07:28</span>
        <span size="medium">\t\t{left_or_surplus_today}\t\t\t05:28</span>
        \n
        <span size="large"><b>\tWeek\n</b></span>
        <span size="medium">\t\t\{worked}\t\t\t07:28</span>
        <span size="medium">\t\t{left_or_surplus_week}\t\t\t05:28</span>
        \n
    """

    cmd = f"""
        yad \
            --title "Clock In" \
            --window-icon "appointment" \
            --width 340 \
            --height 240 \
            --center \
            --text '{info}' \
            --buttons-layout center \
            --button 'Add {hours}'!bookmark-new:0 \
            --button "Didn't work"!find-location-symbolic:1 \
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
