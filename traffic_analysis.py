from datetime import datetime, timedelta
from json import load as json_load

with open('prepared_access_logs.json', 'r') as in_file:
    log_lines = json_load(in_file)


def get_num_requests(logs, ip: str) -> int:
    return len(logs[ip])


def convert_to_datetime(date: str) -> datetime:
    return datetime.strptime(date, '%d/%b/%Y:%H:%M:%S')


def get_dates(logs, ip: str) -> list[datetime]:
    dates = []
    for request in logs[ip]:
        date = request['date']
        dates.append(convert_to_datetime(date))

    return dates


def get_requests_from_date(logs, start_date: datetime, end_date: datetime = None):
    if end_date is None:
        end_date = start_date
    end_date += timedelta(hours=23, minutes=59, seconds=59)
    requests = {}
    for ip in logs:
        for request in logs[ip]:
            date = convert_to_datetime(request['date'])
            if date >= start_date and date <= end_date:
                if ip in requests:
                    requests[ip].append(request)
                else:
                    requests[ip] = [request]

    return requests


def get_return_codes(logs, ip: str):
    return_codes = {}
    for request in logs[ip]:
        return_code = request['return_code']
        key = return_code[0] + '00'
        if key in return_codes:
            return_codes[key].append(request)
        else:
            return_codes[key] = [request]

    return return_codes


def get_successes_from_ip(logs, ip: str):
    results = {'success': 0, 'fail': 0}

    return_codes = get_return_codes(logs, ip)
    for return_code in return_codes:
        if return_code == '200':
            results['success'] = len(return_codes[return_code])
        else:
            results['fail'] += len(return_codes[return_code])

    return results


def get_request_types(logs, ip: str):
    types = {}

    for request in logs[ip]:
        type = request['request'].split(' ')[0][1:]
        if type in types:
            types[type].append(request)
        else:
            types[type] = [request]

    return types


def get_most_common_error(logs, ip: str):
    return_codes = {}
    for request in logs[ip]:
        return_code = request['return_code']
        if return_code[0] == '2':
            continue
        if return_code in return_codes:
            return_codes[return_code] += 1
        else:
            return_codes[return_code] = 1

    return return_codes


def get_most_common_error_total(logs):
    return_codes = {}
    for ip in logs:
        ip_return_codes = get_most_common_error(logs, ip)
        for return_code in ip_return_codes:
            if return_code in return_codes:
                return_codes[return_code] += ip_return_codes[return_code]
            else:
                return_codes[return_code] = ip_return_codes[return_code]

    return return_codes
