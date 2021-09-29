"""
    bq_extract.py

    extract tables from Big Query to pandas dataframe format
"""

import pandas as pd

from google.cloud import bigquery


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

    results = query_job.result()  # Waits for job to complete.

    return results 


def query_billing(cl):

    query_job = cl.query(
        """
        SELECT * 
        FROM `BILLING_TABLE_NAME`
        ORDER BY export_time ASC
        """
    )

    return query_job.result()


def to_pandas(res, ixCol='export_time') -> pd.DataFrame:

    df = res.to_dataframe()

    if ixCol is not None:
        assert ixCol in df.columns, f"{ixCol=} not in df.columns"

        # set datetimeindex
        df.index = df[ixCol]

    return df


if __name__ == "__main__":

    client = bigquery.Client()

    ress = query_billing(client)

    df = to_pandas(ress)

    total_cost = df.cost.sum()

    print(f'current cost is {total_cost:.2f} $')
