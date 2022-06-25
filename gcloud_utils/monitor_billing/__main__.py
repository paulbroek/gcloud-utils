"""monitor_billing.py, monitor Google Cloud billing through BigQuery.

file can run inside docker container and send messages to slack when a threshold billing value is exceeded

TODO:
    - autodetect large delta billing events
    - use argparse for CLI args (done)
    - also alert on high daily amounts (done)
    - now you're using while loop to poll bigquery continuously, but maybe it is better to send trigger events from bq directly when delta_sum_costs exceeds a threshold

RUN:
    conda activate py38
    export GOOGLE_APPLICATION_CREDENTIALS="/home/paul/Downloads/service-account-file.json" && ipy monitor_billing.py -i

    for testing:
        ipy monitor_billing.py -i -- --usd_threshold 0      --seconds 5     -v info

    to run in production (see `docker-compose.yml`, one dir up):
        ipy monitor_billing.py -i -- --usd_threshold 0.5    --seconds 3600  -v info
"""

import argparse
import logging
import os
from datetime import datetime, timedelta
from time import sleep
from typing import Optional

import pandas as pd
from google.cloud import bigquery
from rarc_utils.log import setup_logger
from rarc_utils.misc import load_yaml
from slackclient import SlackClient

from ..bq_extract import query_billing_nonzero, to_pandas
from ..settings import GCLOUD_CONFIG_FILE

logger = logging.getLogger(__name__)

cfgFile = os.environ.get(GCLOUD_CONFIG_FILE)
config = load_yaml(cfgFile)
token = config["slack"]["api_key"]

sc = SlackClient(token)


def slack_message(message, channel) -> None:
    """Send message to Slack.

    usage:
        slack_message('test123', '#general')
    """
    sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message,
        username="Paul",
        icon_emoji=":robot_face:",
    )


class MonitorBilling:
    """MonitorBilling class, application class that can query Big Query continuously.

    and log updates on total cost and/or cost per day
    """

    def __init__(self):

        self.last_cost: float = 0
        self.niter: int = 0
        self.cost_col: str = "cost"
        self.df: Optional[pd.DataFrame] = None

    def run(self):
        """Run the App."""
        cost_col = self.cost_col
        while True:

            now = datetime.utcnow()
            month_ago = now - timedelta(days=30)
            day_ago = now - timedelta(days=1)
            ress = query_billing_nonzero(
                client,
                cols="*",
                orderBy="usage_end_time",
                fromDate=month_ago,
                n=100_000,
            )

            self.df = df = to_pandas(ress, ixCol="usage_end_time")

            past_month_cost = df[cost_col].sum()
            delta_cost = past_month_cost - self.last_cost if self.niter > 0 else 0
            past_day_sel = df.loc[day_ago:, :]
            past_day_cost = past_day_sel[cost_col].sum() if len(past_day_sel) > 0 else 0

            nrow = len(df)
            NROW = "nrow" if nrow == 1 else "nrows"

            logger.info(f"got {nrow} {NROW}")
            logger.info(f"{past_month_cost=:.2f} $   {past_day_cost=:.2f} $")

            # possible notify
            if delta_cost >= args.usd_threshold:
                msg = f"over past {args.seconds} secs: \n{delta_cost=:.2f}$ exceeds usd_threshold={args.usd_threshold:.2f}$"
                logger.warning(msg)

                slack_message(msg, "#notifications")

            self.last_cost = past_month_cost
            sleep(args.seconds)
            self.niter += 1


class ArgParser:
    """create CLI parser."""

    @staticmethod
    def get_parser():
        """Add CLIs to parser."""
        CLI = argparse.ArgumentParser()
        CLI.add_argument(
            "-v",
            "--verbosity",
            type=str,
            default="info",
            help="choose debug log level: DEBUG, INFO, WARNING, ERROR, CRITICAL",
        )
        CLI.add_argument(
            "-f", "--file", action="store_true", default=False, help="save log to file"
        )
        CLI.add_argument(
            "-s", "--seconds", type=int, default=3600, help="poll every n seconds"
        )
        CLI.add_argument(
            "-t",
            "--usd_threshold",
            type=float,
            default=1,
            help="notify user if delta_cost exceeds usd_threshold",
        )

        return CLI


if __name__ == "__main__":

    parser = ArgParser.get_parser()
    args = parser.parse_args()

    log_fmt = "%(asctime)s - %(module)-16s - %(lineno)-4s - %(funcName)-16s - %(levelname)-7s - %(message)s"  # name
    log_level = getattr(logging, args.verbosity.upper())
    logger = setup_logger(
        cmdLevel=log_level, saveFile=args.file, savePandas=1, fmt=log_fmt, multiLine=1
    )

    logger.info(f"{args=}")

    client = bigquery.Client()
    monitorb = MonitorBilling()

    monitorb.run()
