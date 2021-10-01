"""
    monitor_billing.py

    monitor Google Cloud billing through BigQuery
    file can run inside docker container and send messages to slack when a threshold billing value is exceeded

    TODO:

        - autodetect large delta billing events
        - use argparse for CLI args (done)
        - also alert on high daily amounts
        - now you use while loop to poll bigquery continuously, or is it better to send trigger events from bq when delta_sum_costs exceeds a threshold

    RUN:

        conda activate py38
        export GOOGLE_APPLICATION_CREDENTIALS="/home/paul/Downloads/service-account-file.json" && ipy monitor_billing.py -i

        ipy monitor_billing.py -i -- --usd_threshold 0 --seconds 5 -v info
"""

from typing import Optional, Union, Tuple, List
import argparse
import logging
from time import sleep

import pandas as pd

from google.cloud import bigquery

# from rarc.utils.decorators import timeit, timet
# from rarc.utils.log import setup_logger
from rarc.slack_notifications import slack_message
from bq_extract import query_billing_nonzero, to_pandas

logger = logging.getLogger(__name__) # 'root' 'main'


from slackclient import SlackClient

token = 'SLACK_API_KEY'
sc = SlackClient(token)
    
# slack_message('test123', '#general')
def slack_message(message, channel):
    sc.api_call('chat.postMessage', channel=channel, 
                text=message, username='Paul',
                icon_emoji=':robot_face:')


class MonitorBilling:

    def __init__(self):

        self.last_cost = 0
        self.niter = 0

    def run(self):
        
        while True:

            ress = query_billing_nonzero(client, cols='*', orderBy='usage_end_time', n=100_000)

            df = to_pandas(ress, ixCol='usage_end_time')

            total_cost = df.cost.sum()
            delta_cost = total_cost - self.last_cost if self.niter > 0 else 0

            nrow = len(df)
            NROW = 'nrow' if nrow == 1 else 'nrows'

            logger.info(f'got {nrow} {NROW}')
            logger.info(f'total cost is {total_cost:.2f} $')

            # possible notify
            if delta_cost >= args.usd_threshold:
                msg = f'over past {args.seconds} secs: \n{delta_cost=:.2f}$ exceeds usd_threshold={args.usd_threshold:.2f}$'
                logger.warning(msg)

                slack_message(msg, '#notifications')

            self.last_cost = total_cost
            sleep(args.seconds)
            self.niter += 1


class ArgParser():
    """ create CLI parser """

    @staticmethod
    def get_parser():

        CLI=argparse.ArgumentParser()
        CLI.add_argument(
          "-v", "--verbosity", 
          type=str,         
          default='info',
          help="choose debug log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"
        )
        CLI.add_argument(
          "-f", "--file", 
          action='store_true',         
          default=False,
          help="save log to file"
        )
        CLI.add_argument(
          "-s", "--seconds", 
          type=int,
          default=3600,
          help="poll every n seconds"
        )
        CLI.add_argument(
          "-t", "--usd_threshold", 
          type=float,
          default=1,
          help="notify user if delta_cost exceeds usd_threshold"
        )

        return CLI


if __name__ == '__main__':

    parser      = ArgParser.get_parser()
    args        = parser.parse_args()

    log_fmt     = "%(asctime)s - %(module)-16s - %(lineno)-4s - %(funcName)-16s - %(levelname)-7s - %(message)s"  #name
    log_level   = getattr(logging, args.verbosity.upper())
    # logger      = setup_logger(cmdLevel=log_level, saveFile=args.file, savePandas=1, fmt=log_fmt, multiLine=1)
    logger      = logging.basicConfig(level=log_level)

    client      = bigquery.Client()
    monitorb    = MonitorBilling()

    monitorb.run()
