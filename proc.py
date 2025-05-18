from user_agents import parse

def process_data(logs, start_date, end_date, ip_picked='all'):
    req_amounts = {} # dict[ip, bytesize]
    endpoint_success = {} # dict[endpoint, list[success, fails]]
    traffic = {} # dict[ip, num_requests]
    device_type = {} # dict[device_type, num_requests]
    status_codes = []
    
    # # split the logs line wise into lists
    # with open("logs.log", "r") as file:
    #     for line in file:
    #         data.append(line.strip("\n").split(" - "))

    for ip in logs:
        for log in logs[ip]:
            # split variables
            if (ip == ip_picked and ip_picked != 'all') or ip_picked == 'all':
                status = int(log['return_code'])
                status_codes.append(status)
            size = int(log['response_size'])
            endpoint = log['request'].split(" ")[1] if log['request'] != '""' else None
            device = parse(log['user_agent']).device.family

            
            # device pie chart data
            if (ip == ip_picked and ip_picked != 'all') or ip_picked == 'all':
                if device not in device_type:
                    device_type[device] = 1
                else:
                    device_type[device] += 1
                

            # traffic
            if ip not in traffic:
                traffic[ip] = 1
            else:
                traffic[ip] += 1 

            # endpoint 
            if (ip == ip_picked and ip_picked != 'all') or ip_picked == 'all':
                if endpoint not in endpoint_success and endpoint is not None:
                    endpoint_success[endpoint] = [0, 0]
                elif endpoint in endpoint_success and endpoint is not None:
                    if status == 200:
                        endpoint_success[endpoint][0] += 1
                    if status > 200:
                        endpoint_success[endpoint][1] += 1

            # cumulative request sizes
            if ip in req_amounts:
                req_amounts[ip] += size
            else:
                req_amounts[ip] = size
            
    # Group status codes into categories (200s, 300s, 400s, 500s)
    categories = [status for status in status_codes]
    # get unique categories
    c = set(categories)
    # get count dictionary where the value is the status code i.e. 200's, 500's and the value is the count
    category_counts = {k:categories.count(k) for k in c}
    req_amounts = dict(sorted(req_amounts.items(), key=lambda x: x[1], reverse=True))

    # returning all the data, append to the end of the list, or can change the order, but make sure to unpack correctly in the app
    return req_amounts, endpoint_success, traffic, device_type, category_counts, logs

# if __name__=="__main__":
    # process_data(date)