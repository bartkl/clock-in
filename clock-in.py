#!/usr/bin/env python

import json
import os
import random
import subprocess
import time
from collections import UserDict
from datetime import datetime, timedelta, date, time as datetime_time
from enum import IntEnum
from typing import Optional


class Config:
    hours_in_week: float = 36.0
    hours_in_work_day: float = 9.0
    # work_days = list(range(4))  # Monday is 0.
    virtual_midnight = datetime_time(hour=2, minute=0)
    state_file = "/home/bartkl/state.json"


class State(UserDict):
    defaults = {
        "lastActionAt": "2022-04-01T17:26:41.472487",
        "timeWorkedWeek": 0.0,
        "timeWorkedToday": 0.0,
    }

    @classmethod
    def from_file(cls, filepath):
        state = cls._read(filepath)
        return cls(state, filepath)

    def __init__(self, data, filepath):
        super().__init__(data)
        self.filepath = filepath

    @classmethod
    def _read(cls, filepath):
        with open(filepath) as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = {**cls.defaults}

            return data

    def read(self):
        with open(self.filepath) as f:
            try:
                self._data = json.load(f)
            except json.decoder.JSONDecodeError:
                self._data = {**self.defaults}

    def write(self):
        with open(self.filepath, mode="w") as g:
            json.dump(self.data, g)


class Activity(IntEnum):
    WORK = 0
    SLACK = 1
    NOTHING = 2


class Dialog:
    def __init__(self, config, state):
        self.state = state
        self.config = config

        # Startup maintenance.
        self.update_time_worked()

    def run_ui(self):
        worked_label = "Worked:"
        left_label = "Left:\t"
        surplus_label = "Surplus:"

        hours_in_week = self.config.hours_in_week * 3600
        hours_in_work_day = self.config.hours_in_work_day * 3600

        worked_week = self.state["timeWorkedWeek"] * 3600
        worked_today = self.state["timeWorkedToday"] * 3600
        hours_left_week = hours_in_week - worked_week
        hours_left_today = hours_in_work_day - worked_today

        # TODO: `int` gooit veel te veel weg.
        worked_week_fmtd = DateHelpers().format_duration(int(worked_week))
        worked_today_fmtd = DateHelpers().format_duration(int(worked_today))
        hours_left_week_fmtd = DateHelpers().format_duration(int(hours_left_week))
        hours_left_today_fmtd = DateHelpers().format_duration(int(hours_left_today))

        print(worked_today)
        print(worked_today_fmtd)
        
        left_or_surplus_week_label = left_label if hours_left_week >= 0 else surplus_label
        left_or_surplus_today_label = left_label if hours_left_today >= 0 else surplus_label

        info = (
            f'<span size="large"><b>Week\n</b></span>\n'
            f'\t<span size="medium">{worked_label}\t\t\t{worked_week_fmtd}</span>\n'
            f'\t<span size="medium">{left_or_surplus_week_label}\t\t\t{hours_left_week_fmtd}</span>\n'
            f'\n'
            f'<span size="large"><b>Today</b></span>\n\n'
            f'\t<span size="medium">{worked_label}\t\t\t{worked_today_fmtd}</span>\n'
            f'\t<span size="medium">{left_or_surplus_today_label}\t\t\t{hours_left_today_fmtd}</span>\n'
            f'\n'
        )

        # TODO: Correction entry.
        # --entry \
        # --entry-label='\tCorrection:\t\t\t' \

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
                --buttons-layout spread \
                --button 'Add'!bookmark-new:0 \
                --button "Didn't work"!find-location-symbolic:1
        """

        completed_process = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE)

        try:
            return Activity(completed_process.returncode), completed_process
        except ValueError:
            return Activity.NOTHING, completed_process

    def handle_activity(self, activity: Activity, proc):
        if activity == Activity.WORK:
            last_action = datetime.fromisoformat(self.state["lastActionAt"])
            worked = (datetime.now() - last_action).total_seconds() / 3600.0
            self.state["timeWorkedToday"] += worked

            self.update_last_action_at(datetime.now())

        elif activity == Activity.SLACK:
            self.update_last_action_at(datetime.now())

    # Start-up.
    def update_time_worked(self):
        """Update time worked.

        There's no keeping track of missed weeks or something like that, so
        keep that in mind.
        """

        updated = False
        last_action = datetime.fromisoformat(self.state["lastActionAt"]) 

        # Every Monday at virtual midnight, the week balance will be updated.
        if last_action <= DateHelpers().get_last_monday_virtual_midnight(self.config.virtual_midnight):
            self.state["timeWorkedWeek"] = 0.0
            updated = True

        # Every day at virtual midnight, the day balance will be reset.
        if last_action <= DateHelpers().get_today_virtual_midnight(self.config.virtual_midnight):
            self.state["timeWorkedToday"] = 0.0
            updated = True

        if updated:
            # Update last action. Also takes care of the daily priming:
            self.update_last_action_at(datetime.now())

    def update_last_action_at(self, dts):
        self.state["lastActionAt"] = datetime.isoformat(datetime.now())
        self.state.write()


class DateHelpers:
    @staticmethod
    def get_last_monday_virtual_midnight(virtual_midnight_time):
        today_at_virtual_midnight = DateHelpers().get_today_virtual_midnight(virtual_midnight_time)

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

    @staticmethod
    def format_duration(t):
        t = abs(t)
        hours = t // 3600
        minutes = (t % 3600) * 60

        return f"{hours:02}:{minutes:02}"


def main():
    config = Config()
    state = State.from_file(config.state_file)

    dialog = Dialog(config, state)
    activity, proc = dialog.run_ui()

    dialog.handle_activity(activity, proc)


if __name__ == "__main__":
    main()
