import accountifie.query.remote_server_status


def backend_lpq(qstring):
    return accountifie.query.remote_server_status.lpq()


def ledger_stats(company_id, qstring):
    return accountifie.query.remote_server_status.gl_stats(company_id)