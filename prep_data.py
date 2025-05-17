from re import search

with open("access.log", "r") as in_file:
    with open("prepared_access_logs", "w") as out_file:
        for line in in_file.readlines():
            ip = search(r'\d+\.\d+\.\d+\.\d+', line).group(0)
            date = search(r'\[(.+)\]', line).group(1)
            request = search(r'"\w+\s\/.*HTTP\/\d\.\d"|""', line).group(0)
            return_code = search(r'\s(\d{3})\s\d+', line).group(1)
            response_size = search(r'\s\d{3}\s(\d+)\s', line).group(1)
            user_agent = search(r'"[^"]*"$', line).group(0)
            new_line = " - ".join([ip, date, request, return_code, response_size, user_agent])
            out_file.write(new_line + "\n")
