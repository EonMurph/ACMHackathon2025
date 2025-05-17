from user_agents import parse
from re import search
from ACMHackathon2025.prep_data import get_data_dict

def process_data():
    data = []
    req_amounts = {}
    endpoint_success = {}
    traffic = {}
    device_type = {}
    status_codes = []
    request_freq = {}
    with open("logs.log", "r") as file:
        for line in file:
            data.append(line.strip("\n").split(" - "))

    for d in data:
        ip = d[0]
        status = int(d[3])
        size = int(d[4])
        endpoint = d[2].split(" ")[1] if d[2] != '""' else None
        device = parse(d[5]).device.family


        status_codes.append(status)
        
        if device not in device_type:
            device_type[device] = 1
        else:
            device_type[device] += 1
            
        # req freq
        if ip not in request_freq:
            request_freq[ip] = None
        

        # traffic
        if ip not in traffic:
            traffic[ip] = 1
        else:
            traffic[ip] += 1 

        # endpoint 
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
    categories = [f"{status // 100}00s" for status in status_codes]
    c = set(categories)
    category_counts = {k:categories.count(k) for k in c}


    req_amounts = dict(sorted(req_amounts.items(), key=lambda x: x[1], reverse=True))
    return req_amounts, endpoint_success, traffic, device_type, category_counts

if __name__=="__main__":
    process_data()