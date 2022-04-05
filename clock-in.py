#!/usr/bin/env python

import os
import json
import random
import subprocess
from datetime import datetime, timedelta, time, date
from enum import IntEnum
from typing import Optional


class Config:
    hours_in_week: float = 36.0
    hours_in_work_day: float = 9.0
    work_days = list(range(4))  # Monday is 0.
    virtual_midnight = time(hour=2, minute=0)
    state_file = "/home/bartkl/state.json"


class State:
    def __init__(self, filepath):
        self._state = {}
        self.filepath = filepath
        self.read()

    @property
    def state(self):
        return self._state

    def read(self):
        with open(self.filepath) as f:
            self._state = json.load(f)

    def sync(self):
        with open(self.filepath, mode="w") as g:
            json.dumps(g)


class Activity(IntEnum):
    WORK = 0
    SLACK = 1


class Dialog:
    def __init__(self, state, config):
        self.state = state
        self.config = config

    def run_ui(self):
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
                --entry-label='\tCorrection:\t\t\t' \
                --buttons-layout spread \
                --button 'Add'!bookmark-new:0 \
                --button "Didn't work"!find-location-symbolic:1
        """

        completed_process = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE)

        try:
            return Activity(completed_process.returncode), completed_process
        except ValueError:
            return

    def handle_activity(self, activity: Activity, proc):
        print(activity)
        print(proc.stdout)

    # Start-up.
    def update_time_worked_week(self):
        """Every Monday at virtual midnight, the week balance will be updated.

        There's no keeping track of missed weeks or something like that, so
        keep that in mind.
        """

        last_action = datetime.isoformat(self.state["lastAction"]) 

        if last_action <= DateHelpers().get_last_monday_at_virtual_midnight():
            self.state["timeWorkedWeek"] -= contract
            self.state["lastAction"] = datetime.isoformat(datetime.now())


    def update_time_worked_day(self):
        """Every day at virtual midnight, the day balance will be reset.
        """

        last_action = datetime.isoformat(self.state["lastAction"])

        if last_action <= DateHelpers().get_today_at_virtual_midnight(self.config.virtual_midnight):
            self.state["timeWorkedToday"] = 0.00

            # Also takes care of the daily priming:
            self.state["lastAction"] = datetime.isoformat(datetime.now()) 

    # On click.
    def handle_add_btn(self, time_worked):
        time_worked_today += time_worked
        time_worked_week += time_worked
        last_action = now()

    def handle_didnt_work_btn(self):
        last_action = now()


class DateHelpers:
    @staticmethod
    def get_last_monday_virtual_midnight(virtual_midnight_time):
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
                virtual_midnight_time.hour,
                virtual_midnight_time.minute) - timedelta(days=today_at_virtual_midnight.weekday())

    @staticmethod
    def get_today_virtual_midnight(virtual_midnight_time):
        today = date.today()

        return datetime(
            today.year,
            today.month,
            today.day,
            virtual_midnight_time.hour,
            virtual_midnight_time.minute)


def main():
    config = Config()
    state = State(config.state_file)
    # daily_balance = timedelta(hours=1, minutes=10, seconds=3)
    # weekly_balance = timedelta(hours=12, minutes=10, seconds=3)
    dialog = Dialog(config, state)
    activity, proc = dialog.run_ui()
    dialog.handle_activity(activity, proc)


if __name__ == "__main__":
    main()
