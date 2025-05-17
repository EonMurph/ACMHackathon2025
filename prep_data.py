from re import search
from json import dump


def get_data_dict(line: str) -> dict[str, str]:
    date = search(r'\[(.+)\s\+\d{4}\]', line).group(1)
    request = search(r'"\w+\s\/.*HTTP\/\d\.\d"|""', line).group(0)
    return_code = search(r'\s(\d{3})\s\d+', line).group(1)
    response_size = search(r'\s\d{3}\s(\d+)\s', line).group(1)
    user_agent = search(r'"[^"]*"$', line).group(0)
    return {
        'date': date,
        'request': request,
        'return_code': return_code,
        'response_size': response_size,
        'user_agent': user_agent,
    }


with open('access.log', 'r') as in_file:
    with open('prepared_access_logs.json', 'w') as out_file:
        data = {}
        for line in in_file.readlines():
            ip = search(r'\d+\.\d+\.\d+\.\d+', line).group(0)
            if ip in data:
                data[ip].append(get_data_dict(line))
            else:
                data[ip] = [get_data_dict(line)]

        dump(data, out_file, ensure_ascii=False)