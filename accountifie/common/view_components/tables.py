import json
import logging
import importlib


logger = logging.getLogger('default')


def bstrap_table(table_name):
    try:
        tbl_module = importlib.import_module('tables.bstrap_tables')
        return getattr(tbl_module, table_name)
    except:
        pass

    try:
        tbl_module = importlib.import_module('accountifie.reporting.bstrap_tables.common')
        return getattr(tbl_module, table_name)
    except:
        logger.error("couldn't find bootstrap table def %s" % table_name)
        return None

