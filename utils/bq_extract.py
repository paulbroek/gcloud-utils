"""
    bq_extract.py

    extract tables from Big Query to pandas dataframe format
    like: billing

    more info on how to set up gcloud service account, see github.com/paulbroek/gcloud-utils/README.md

    run file:

        conda activate py38
        export GOOGLE_APPLICATION_CREDENTIALS="/home/paul/Downloads/service-account-file.json" && ipy bq_extract.py -i

    or add the environment variable to ~/.bashrc or ~/.zshrc
"""

from typing import Optional, Union, Tuple, List
import argparse
import logging

import pandas as pd

from google.cloud import bigquery

logger = logging.getLogger(__name__) # 'root' 'main'

BILLING_TABLE_NAME = 'BILLING_TABLE_NAME'


def query_stackoverflow(cl):

    query_job = cl.query(
        """
        SELECT
          CONCAT(
            'https://stackoverflow.com/questions/',
            CAST(id as STRING)) as url,
          view_count
        FROM `bigquery-public-data.stackoverflow.posts_questions`
        WHERE tags like '%google-bigquery%'
        ORDER BY view_count DESC
        LIMIT 10"""
    )

    return query_job.result()  # Waits for job to complete.


@timet
def query_billing_all(cl):

    query_job = cl.query(
        """
        SELECT *
        FROM `BILLING_TABLE_NAME`
        ORDER BY export_time ASC
        """
    )

    return query_job.result()


@timet
def query_billing(cl, cols='*', orderBy='export_time', n=100_000):

    assert isinstance(cols, str)
    assert isinstance(n, int)

    query_job = cl.query(
        """
        SELECT {} 
        FROM {}
        ORDER BY {} ASC
        LIMIT {}
        """.format(cols, BILLING_TABLE_NAME, orderBy, n)
    )

    return query_job.result()


@timet
def query_billing_nonzero(cl, cols='*', orderBy='export_time', n=100_000):
    """ query all nonzero billing rows """

    assert isinstance(cols, str)
    assert isinstance(n, int)

    query_job = cl.query(
        """
        SELECT {} 
        FROM {}
        WHERE cost > 0
        ORDER BY {} ASC
        LIMIT {}
        """.format(cols, BILLING_TABLE_NAME, orderBy, n)
    )

    return query_job.result()


@timet
def to_pandas(res, ixCol: Optional='export_time') -> pd.DataFrame:

    df = res.to_dataframe()

    if ixCol is not None:
        assert ixCol in df.columns, f"{ixCol=} not in df.columns"

        # set datetimeindex
        df.index = df[ixCol]

    return df


def cost_by_month(df) -> pd.DataFrame:

    return df


def unnest_dict(df, col, key, assign=True) -> Union[str, Tuple[str, pd.Series]]:
    """ converts 

        project  {'id': 'ob-train', 'number': '653959998010'

        to 

        project_id      'ob_train'
    """

    assert isinstance(df, pd.DataFrame)

    if len(df) > 0:
        assert col in df.columns
        some_row = df.iloc[0]
        assert isinstance(some_row[col], dict)
        assert key in some_row[col], f"{key=} not in {some_row[col]}"

    newColName = f'{col}_{key}'

    newCol = df[col].map(lambda x: x[key])

    if assign:
        df = df.assign(**{newColName: newCol})

        print(f'{df.shape=}')

        return newColName

    return newColName, newCol


def assign_cols(df, unnestList) -> Tuple[List[str], pd.DataFrame]:
    """
        convert list of ('col','key') tuples to list of new col names and assigned dataframe
    """

    assert isinstance(df, pd.DataFrame)
    assert isinstance(unnestList, list)

    nameColTuples = list(map(lambda x: unnest_dict(df, *x, assign=False), unnestList))

    addedCols = [n[0] for n in nameColTuples]

    return addedCols, df.assign(**dict(nameColTuples))


def reduce_view(df) -> pd.DataFrame:
    """ return a compact view of df, since BigQuery returns 19 columns and nested dictionaries """

    df = df.copy()

    df['usage_duration'] = df['usage_end_time'] - df['usage_start_time']
    df['usage_secs'] = df['usage_duration'].dt.total_seconds()
    df['usage_hours'] = df['usage_secs'] / 3600

    df['cumCost'] = df['cost'].cumsum()

    # several ways to create nested columns, see unnest_dict()
    # df['project_id'] = df['project'].map(lambda x: x['id'])
    # df['project_id'] = unnest_dict(df, 'project', 'id', assign=False)

    unnestList = [('project','id'), ('service','description'), ('sku','description'), ]

    # apply unnest_dict to al parameters in unnestList
    addedCols, df = assign_cols(df, unnestList)

    # what cols to keep
    keepCols = addedCols + ['usage_hours', 'cost', 'cumCost']
    # view = df.loc[:, ['project_id', 'usage_hours','cost']]
    view = df.loc[:, keepCols]

    return view


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

        return CLI


if __name__ == "__main__":
    
    from rarc.utils.decorators import timeit, timet
    from rarc.utils.log import setup_logger

    parser      = ArgParser.get_parser()
    args        = parser.parse_args()

    log_fmt     = "%(asctime)s - %(module)-16s - %(lineno)-4s - %(funcName)-16s - %(levelname)-7s - %(message)s"  #name
    log_level   = getattr(logging, args.verbosity.upper())
    logger      = setup_logger(cmdLevel=log_level, saveFile=args.file, savePandas=1, fmt=log_fmt, multiLine=1)


    client = bigquery.Client()

    # ress = query_billing(client, cols='*', n=100_000)
    ress = query_billing_nonzero(client, cols='*', orderBy='usage_end_time', n=100_000)
    # ress = query_billing_nonzero(client, cols='*', orderBy='export_time', n=100_000)
    # ress = query_billing_nonzero(client, cols='*', orderBy='cost', n=100_000)
    # ress = query_billing(client, cols='export_time, cost', n=100_000)

    # df = to_pandas(ress, ixCol='export_time')
    df = to_pandas(ress, ixCol='usage_end_time')

    total_cost = df.cost.sum()

    nrow = len(df)
    NROW = 'nrow' if nrow == 1 else 'nrows'

    logger.info(f'got {nrow} {NROW}')
    logger.info(f'total cost is {total_cost:.2f} $')

    view = reduce_view(df)
    # view = view.sort_values('cost')
    view = view.sort_index()

    # get a summary of top (summed) costs
    by_service = view.groupby('service_description')
    by_description = view.groupby('sku_description')
    # costs = by_description['cost'].sum().sort_values()
    costs = by_description.agg({'usage_hours': ['sum', 'max'], 'cost': 'sum'})
    costs = costs.sort_values(('cost','sum'))
    # optional flattening of column names
    costs.columns = costs.columns.map('_'.join).str.strip('_')

    # display floats, not scientific numbers
    pd.set_option('display.float_format', lambda x: '%.5f' % x)
    costs['cost_sum_pct'] = costs['cost_sum'] / costs['cost_sum'].sum()

    # usgcols = ['usage_hours_sum', 'usage_hours_max']
    usgcols = costs.filter(regex='^usage.+').columns
    costs[usgcols] = costs[usgcols].astype(int)

    # create cols with stars that visualize the pct
    costs['cost_pct'] = '*' # choose any char
    star_width = 10
    nstar = pd.cut(costs.cost_sum_pct, star_width, labels=range(star_width))
    costs['cost_pct'] = costs['cost_pct'].str.repeat(nstar)

    with pd.option_context('display.colheader_justify','left'):
        print('\n', costs)
