from datetime import datetime


def parse_time(value):
    return datetime.fromisoformat(value)


def summarize(release):
    tables = release["tables"]
    cutoff = release["cutoff"]
    incoming = sum(row['count'] for row in tables['margins'] if row['direction'] == 'in')
    outgoing = sum(row['count'] for row in tables['margins'] if row['direction'] == 'out')
    return {'incoming': incoming, 'outgoing': outgoing, 'imbalance': incoming-outgoing, 'sampled_paths': sum(row['sample_count'] for row in tables['paths']), 'closed_links': sum(not row['allowed'] for row in tables['links'])}
