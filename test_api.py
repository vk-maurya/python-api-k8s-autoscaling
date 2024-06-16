import requests
import concurrent.futures
import csv
import random
import time
import argparse

# Define the URLs and payloads for the requests
url_hello = 'http://192.168.49.2:30080/' # ip address we got using command `minikube ip` and port we have mentioned in the service
url_reverse = 'http://192.168.49.2:30080/reverse'
payload_list = ['Hello world', 'Python is awesome', 'Flask is fun', 'Docker is cool']
payloads = [{'text': f'Payload {payload_list[random.randint(0,3)]}'} for i in range(100)]

def make_request(url, payload=None):
    try:
        if payload:
            response = requests.post(url, json=payload)
        else:
            response = requests.get(url)
        
        # Check if the response is JSON
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {'error': 'Invalid JSON response', 'content': response.text}
    except requests.RequestException as e:
        return {'error': str(e)}

def save_to_csv(data, filename='concurrent_requests.csv'):
    # Determine the set of all keys present in the responses
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=list(all_keys))
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    responses = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:

        # Make concurrent POST requests to the reverse endpoint
        future_reverse = [executor.submit(make_request, url_reverse, payload) for payload in payloads]
        for future in concurrent.futures.as_completed(future_reverse):
            responses.append(future.result())

    # Save responses to CSV
    save_to_csv(responses, filename=f'concurrent_requests_CPU_Intensive_{argument.cpu_intensive}.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cpu-intensive', default=False, type=lambda x: x == 'True')
    argument = parser.parse_args()

    if argument.cpu_intensive:
        url_cpu_intensive = 'http://192.168.49.2:30080/cpu-intensive'
        requests.get(url_cpu_intensive)
    
    time.sleep(5)
    main()
