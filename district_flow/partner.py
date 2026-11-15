from datetime import datetime


def parse_time(value):
    return datetime.fromisoformat(value)


def operate(path, payload, release):
    if path != '/v1/matrix-check':
        raise LookupError('矩阵接口不存在')
    window = payload['window']
    allowed = {(row['origin'],row['destination']):row['allowed'] for row in release['tables']['links'] if row['window']==window}
    totals = {}
    violations = []
    for cell in payload['cells']:
        key = (cell['origin'],cell['destination'])
        if cell['count'] < 0 or not allowed.get(key,False) and cell['count'] != 0:
            violations.append(list(key))
        for direction, district in [('out',key[0]),('in',key[1])]:
            totals[(direction,district)] = totals.get((direction,district),0)+cell['count']
    differences = [dict(district=row['district'],direction=row['direction'],difference=totals.get((row['direction'],row['district']),0)-row['count']) for row in release['tables']['margins'] if row['window']==window]
    return {'violations':violations,'differences':differences,'revision':release['revision']}
