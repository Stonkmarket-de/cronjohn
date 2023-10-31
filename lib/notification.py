import os
import time
import pickle
import apprise
import argparse
from datetime import datetime
from dotenv import load_dotenv


def send_cron(title="cron", body="", important=False):
    apobj = apprise.Apprise()

    botname = "Cronitor"
    image = IMAGE_URL

    apobj.add(
        f"https://discord.com/api/webhooks/{DISCORD_ID}/{DISCORD_TOKEN}?botname={botname}&avatar_url={image}"
    )

    if important:
        body = body + "\n\n\n:octagonal_sign: " + DISCORD_ADMIN

    apobj.notify(
        body=body,
        title=title,
    )


if __name__ == "__main__":
    load_dotenv()

    IMAGE_URL = os.environ.get("IMAGE_URL")
    DISCORD_ID = os.environ.get("DISCORD_ID")
    DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
    TIMESTAMP_FILE = ".timestamp."
    DISCORD_ADMIN = os.environ.get("DISCORD_ADMIN")

    my_parser = argparse.ArgumentParser()

    my_parser.add_argument(
        "-s",
        "--start",
        action="store_true",
        help="Use before the start of a cronjob in crontab like: cronitor.py -s && blah.sh",
    )

    my_parser.add_argument(
        "-e",
        "--end",
        action="store_true",
        help="Use after a cronjob in crontab like: blah.sh && cronitor -e",
    )

    my_parser.add_argument(
        "-n",
        "--notify",
        action="store_true",
        help="Use as a standalone cron notification in crontab like: 10 * * * * crontior.py -n",
    )

    my_parser.add_argument(
        "-sn",
        "--start-name",
        type=str,
        help="Enter the name of the cronjob you are about to run.",
    )

    my_parser.add_argument(
        "-en",
        "--end-name",
        type=str,
        help="Enter the name of the cronjob you just finished.",
    )

    my_parser.add_argument(
        "-nn", "--notify-name", type=str, help="Custom script name for --notify"
    )

    my_parser.add_argument(
        "-id", "--file-id", type=str, help="Enter an ID for the timestamp file."
    )

    options = my_parser.parse_args()
    parsed_options = vars(options)

    tmp_file = TIMESTAMP_FILE + parsed_options["file_id"]

    if parsed_options["start"]:
        timestamp = time.time()
        human_timestamp = datetime.fromtimestamp(timestamp)

        f = open(tmp_file, "wb")
        pickle.dump(timestamp, f)
        f.close()

        text = f"Script: **{parsed_options.get('start_name')}**\n:alarm_clock:Time: {human_timestamp}"
        send_cron(
            title=f"**Started {parsed_options['file_id']}** :airplane_departure:",
            body=text,
        )

    if parsed_options["end"]:
        timestamp = time.time()
        human_timestamp = datetime.fromtimestamp(timestamp)

        if os.path.exists(TIMESTAMP_FILE + parsed_options["file_id"]):
            f = open(tmp_file, "rb")
            starting_stamp = pickle.load(f)
            f.close()

            converted_starting = datetime.fromtimestamp(starting_stamp)
            text = f"Script: **{parsed_options.get('end_name')}**\n:alarm_clock:Time: {human_timestamp}\nDuration: {human_timestamp - converted_starting}"
        else:
            text = f"Script: **{parsed_options.get('end_name')}**\n:alarm_clock:Time: {human_timestamp}"

        send_cron(
            title=f"**Ended {parsed_options['file_id']}**:airplane_arriving:", body=text
        )

        if os.path.exists(TIMESTAMP_FILE + parsed_options["file_id"]):
            os.remove(TIMESTAMP_FILE + parsed_options["file_id"])

    if parsed_options["notify"]:
        text = f'{parsed_options["notify_name"]}'
        send_cron(title="Notify:alarm_clock:", body=text)
