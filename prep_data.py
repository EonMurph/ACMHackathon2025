from re import search
from json import dump

with open('access.log', 'r') as in_file:
    with open('prepared_access_logs.json', 'w') as out_file:
        data = {}
        for line in in_file.readlines():
            ip = search(r'\d+\.\d+\.\d+\.\d+', line).group(0)
            date = search(r'\[(.+)\]', line).group(1)
            request = search(r'"\w+\s\/.*HTTP\/\d\.\d"|""', line).group(0)
            return_code = search(r'\s(\d{3})\s\d+', line).group(1)
            response_size = search(r'\s\d{3}\s(\d+)\s', line).group(1)
            user_agent = search(r'"[^"]*"$', line).group(0)
            if ip in data:
                data[ip].append(
                    {
                        'date': date,
                        'request': request,
                        'return_code': return_code,
                        'response_size': response_size,
                        'user_agent': user_agent,
                    }
                )
            else:
                data[ip] = [
                    {
                        'date': date,
                        'request': request,
                        'return_code': return_code,
                        'response_size': response_size,
                        'user_agent': user_agent,
                    }
                ]

        dump(data, out_file, ensure_ascii=False)
