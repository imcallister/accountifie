
"""
Adapted with permission from ReportLab's DocEngine framework
"""


from django.db import connection


def query(stmt, *args):
    """Execute statement (optionally with parameters) and return results.
    
    Returns list of lists


    """

    cur = connection.cursor()
    if args:
        cur.execute(stmt, args)
    else:
        cur.execute(stmt)
    data = cur.fetchall()
    cur.close()
    return data


def query_as_set(stmt, *args):
    "For one-column query, return a set of values"
    data = query(stmt, *args)
    assert len(data[0]) == 1, 'query_one_column requires a one-column query!'
    return set([row[0] for row in data])

