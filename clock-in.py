#!/usr/bin/env python

import os
import json
import random
import subprocess
from datetime import datetime, timedelta, time, date
from enum import IntEnum
from typing import Optional


# Config.
HOURS_IN_WEEK = 36.0
HOURS_IN_WORK_DAY = 9.0
WORK_DAYS = list(range(4))  # Monday is 0.
VIRTUAL_MIDNIGHT = time(hour=2, minute=0)

STATE_FILE = "/home/bartkl/state.json"

# State.
with open(STATE_FILE) as f:
    STATE = json.load(f)


# Code.
class Activity(IntEnum):
    WORK = 0
    SLACK = 1


def run_clock_in_dialog(daily_balance, weekly_balance) -> Optional[Activity]:
    worked = "Worked:"
    left = "Left:\t"
    surplus = "Surplus:"

    left_or_surplus_today = surplus
    left_or_surplus_week = left

    info = (
        f'<span size="large"><b>Week\n</b></span>\n'
        f'\t<span size="medium">{worked}\t\t\t07:28</span>\n'
        f'\t<span size="medium">{left_or_surplus_week}\t\t\t05:28</span>\n'
        f'\n'
        f'<span size="large"><b>Today</b></span>\n\n'
        f'\t<span size="medium">{worked}\t\t\t07:28</span>\n'
        f'\t<span size="medium">{left_or_surplus_today}\t\t\t05:28</span>\n'
        f'\n'
    )
    cmd = f"""
        yad \
            --title "Clock In" \
            --window-icon "appointment" \
            --borders 15 \
            --text-align left \
            --width 340 \
            --height 240 \
            --center \
            --text '{info}' \
            --entry \
                --entry-label='\tHours\t\t\t' \
                --entry-text='4:32' \
            --buttons-layout spread \
            --button 'Add'!bookmark-new:0 \
            --button "Didn't work"!find-location-symbolic:1 \
    """

    completed_process = subprocess.run([cmd], shell=True)

    try:
        return Activity(completed_process.returncode)
    except ValueError:
        return

# Date functions.
def get_last_monday_virtual_midnight():
    today_at_virtual_midnight = get_today_virtual_midnight()
    # If it's Monday and past virtual midnight, today is our day.
    if (
            today_at_virtual_midnight.weekday() == 0 and
            datetime.now() >= today_at_virtual_midnight):
        return today_at_virtual_midnight
    else:
        return datetime(
            today_at_virtual_midnight.year,
            today_at_virtual_midnight.month,
            today_at_virtual_midnight.day,
            VIRTUAL_MIDNIGHT.hour,
            VIRTUAL_MIDNIGHT.minute) - timedelta(days=today_at_virtual_midnight.weekday())


def get_today_virtual_midnight():
    today = date.today()
    return datetime(
        today.year,
        today.month,
        today.day,
        VIRTUAL_MIDNIGHT.hour,
        VIRTUAL_MIDNIGHT.minute)

# Start-up.
def update_time_worked_week(state):
    """Every Monday at virtual midnight, the week balance will be updated.

    There's no keeping track of missed weeks or something like that, so
    keep that in mind.
    """

    last_action = datetime.isoformat(state["lastAction"]) 

    if last_action <= get_last_monday_at_virtual_midnight():
        state["timeWorkedWeek"] -= contract
        state["lastAction"] = datetime.isoformat(datetime.now())


def update_time_worked_day(state):
    """Every day at virtual midnight, the day balance will be reset.
    """

    last_action = datetime.isoformat(state["lastAction"])

    today = date.today()
    today_at_virtual_midnight

    if last_action <= get_today_at_virtual_midnight():
        state["timeWorkedToday"] = 0.00
        state["lastAction"] = datetime.isoformat(datetime.now()) # Also takes care of the daily priming!

def main():
    daily_balance = timedelta(hours=1, minutes=10, seconds=3)
    weekly_balance = timedelta(hours=12, minutes=10, seconds=3)
    activity = run_clock_in_dialog(daily_balance, weekly_balance)



if __name__ == "__main__":
    main()
