import subprocess
import re
import sys
from models import Line
import os


def is_root():
    return os.geteuid() == 0


def is_writeable(file_path) -> bool:
    return os.access(file_path, os.W_OK)


def is_file_exist(file_path) -> bool:
    return os.path.exists(file_path)


def get_os() -> str:
    if sys.platform == "win32":
        return "win"

    if sys.platform == "linux":
        return "nux"


def run_as_cron(command):
    run_as = None
    if sys.platform != "win32" and len(command) > 1 and is_root():
        try:
            id_or_error = subprocess.check_output(
                ["id", "-u", command[0]], stderr=subprocess.DEVNULL
            )
            user_id = id_or_error.decode("utf-8").strip()
            if user_id.isdigit():
                run_as = command[0]
                command = command[1:]
        except subprocess.CalledProcessError:
            run_as = "root"

    return command, run_as


def is_command_complex(cron_line: str) -> bool:
    is_complex = False
    chanin_symbols = [";", "|", "||", "&&"]
    if chanin_symbols in cron_line:
        is_complex = True

    return is_complex


def is_command_meta(cron_line: str) -> bool:
    is_meta = False
    chanin_symbols = ["cron.hourly", "cron.daily", "cron.weekly", "cron.monthly"]
    if chanin_symbols in cron_line:
        is_meta = True

    return is_meta


def is_six_field_cron_expression(split_line):
    def match_regex(pattern, value):
        return re.match(pattern, value) is not None

    match_digit_or_wildcard = match_regex(r"^[-,?*/0-9]+$", split_line[5])
    match_day_of_week_string_range = match_regex(
        r"^(Mon|Tue|Wed|Thr|Fri|Sat|Sun)(-(Mon|Tue|Wed|Thr|Fri|Sat|Sun))?$",
        split_line[5],
    )
    match_day_of_week_string_list = match_regex(
        r"^((Mon|Tue|Wed|Thr|Fri|Sat|Sun),?)+$", split_line[5]
    )

    return (
        match_digit_or_wildcard
        or match_day_of_week_string_range
        or match_day_of_week_string_list
    )


def get_crontab():
    try:
        if get_os() == "nux":
            crons = []

            crontab_output = subprocess.check_output(
                ["crontab", "-l"], universal_newlines=True
            )

            cron_file_content = crontab_output.splitlines()

            for line_number, full_line in enumerate(cron_file_content, start=1):
                if not full_line.startswith("#"):
                    new_cron = Line()
                    new_cron.line_number = line_number
                    new_cron.full_line = full_line.strip()

                    split_line = re.split(r"\s+", new_cron.full_line)

                    if len(split_line) == 1 and "=" in split_line[0]:
                        # this is an env line
                        env_export = split_line[0].split("=")
                        if env_export[0] == "TZ" or env_export[0] == "CRON_TZ":
                            tz_name = env_export[1]
                            new_cron.tiemzone = tz_name
                    elif len(split_line) > 0 and split_line[0].startswith("@"):
                        # Handling for special cron @keyword
                        new_cron.cron_expression = split_line[0]
                        new_cron.command_to_run = split_line[1:]
                    elif len(split_line) >= 6:
                        six_field_syntax = len(
                            split_line
                        ) >= 7 and is_six_field_cron_expression(split_line)
                        if six_field_syntax:
                            new_cron.cron_expression = " ".join(split_line[0:6])
                            new_cron.command_to_run = split_line[6:]
                        else:
                            new_cron.cron_expression = " ".join(split_line[0:5])
                            new_cron.command_to_run = split_line[5:]

                    if new_cron.command_to_run:
                        command, run_as = run_as_cron(new_cron.command_to_run)
                        new_cron.command_to_run = " ".join(command)
                        new_cron.run_as = run_as

                        if (
                            len(command) > 1
                            and command[0].startswith("cronjon")
                            and command[1] == "exec"
                        ):
                            new_cron.code = command[2]
                            new_cron.command_to_run = command[3:]

                    crons.append(new_cron)

            return crons

    except subprocess.CalledProcessError as e:
        print(f"Error retrieving crontab for the current user: {e.output}")
        return []


def main():
    crontab_entries = get_crontab()

    for cron in crontab_entries:
        print(f"{cron.__dict__}")


if __name__ == "__main__":
    main()
