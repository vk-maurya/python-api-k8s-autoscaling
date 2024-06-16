# Scaling a Python API using Docker and Kubernetes

This repository contains the code and instructions for creating, dockerizing, deploying, and scaling a simple Python API using Docker and Kubernetes. The project is divided into four parts:

1. Simple Python API creation and dockerization
2. Setting up Minikube locally
3. Deploying and scaling the API using Kubernetes
4. Testing the Kubernetes setup

## Table of Contents
I wrote details blog explain things in more detailed way. please explore blog also.
- [Prerequisites](#prerequisites)
- [Part 1: Simple Python API Creation and Dockerization](#part-1-simple-python-api-creation-and-dockerization) : <a href="https://medium.com/@vkmauryavk/python-api-scaling-with-kubernetes-dockerization-1-4-f961900336b3"> Blog link </a>
- [Part 2: Setting Up Minikube Locally](#part-2-setting-up-minikube-locally) : <a href="https://medium.com/@vkmauryavk/python-api-scaling-with-kubernetes-minikube-setup-2-3-171161b7fac4"> Blog link </a>
- [Part 3: Deploying and Scaling the API using Kubernetes](#part-3-deploying-and-scaling-the-api-using-kubernetes) : <a href="https://medium.com/@vkmauryavk/python-api-scaling-with-kubernetes-deployment-3-3-55990d30ea0e"> Blog link </a>
- [Part 4: Testing the Kubernetes Setup](#part-4-testing-the-kubernetes-setup) : <a href="https://medium.com/@vkmauryavk/python-api-scaling-with-kubernetes-testing-4-4-90d1699d48ad"> Blog link </a>
- [Useful Kubernetes Commands](#useful-kubernetes-commands)


## Prerequisites

Before you start, make sure you have the following installed on your machine:
- Docker
- Python 3.x

## Part 1: Simple Python API Creation and Dockerization

### API Creation

Create a simple Python API using Flask. The API has three endpoints:
- `/`: Returns a greeting message along with the hostname and IP address of the server.
- `/reverse`: Reverses the text provided in the request body.
- `/cpu-intensive`: Simulates a CPU-intensive task.

### Dockerization

Create a Dockerfile to containerize the Python API.

```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install Flask

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

### Building and Pushing the Docker Image

```sh
docker build -t your_dockerhub_username/python-api .
docker login
docker push your_dockerhub_username/python-api
```

## Part 2: Setting Up Minikube Locally

### Installing Minikube

Follow the instructions on the [Minikube releases page](https://github.com/kubernetes/minikube/releases) to install Minikube.

### Starting Minikube

```sh
minikube start
```

### Installing kubectl

Follow the instructions on the [Kubernetes documentation](https://kubernetes.io/docs/tasks/tools/install-kubectl/) to install kubectl.

## Part 3: Deploying and Scaling the API using Kubernetes

### Creating a Namespace

```sh
kubectl create namespace python-api-namespace
```

### Creating a Deployment

Create a `deployment.yaml` file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-k8s-api
  namespace: python-api-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-k8s-api
  template:
    metadata:
      labels:
        app: python-k8s-api
    spec:
      containers:
      - name: python-k8s-api
        image: your_dockerhub_username/python-api
        ports:
        - containerPort: 5000
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
```

Apply the deployment:

```sh
kubectl apply -f deployment.yaml
```

### Creating a Service

Create a `service.yaml` file:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-k8s-api-service
  namespace: python-api-namespace
spec:
  type: LoadBalancer
  selector:
    app: python-k8s-api
  ports:
    - protocol: TCP 
      port: 80 
      targetPort: 5000
      nodePort: 30080
```

Apply the service:

```sh
kubectl apply -f service.yaml
```

### Horizontal Pod Autoscaler (HPA)

Create an `hpa.yaml` file:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: python-k8s-api-hpa
  namespace: python-api-namespace
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: python-k8s-api
  minReplicas: 2
  maxReplicas: 4
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 5
    scaleUp:
      stabilizationWindowSeconds: 5
```

Apply the HPA:

```sh
kubectl apply -f hpa.yaml
```

## Part 4: Testing the Kubernetes Setup

### Testing Script

Create a `test_api.py` file:

```python
import requests
import concurrent.futures
import csv
import random
import time
import argparse

# Define the URLs and payloads for the requests
url_hello = 'http://192.168.49.2:30080/'
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
        all_keys update(item.keys())
    
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
    save_to_csv(responses, filename=f'concurrent_requests_{argument.cpu_intensive}.csv')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cpu-intensive', default=False, type=lambda x: x == 'True')
    argument = parser.parse_args()

    if argument.cpu_intensive:
        url_cpu_intensive = 'http://192.168.49.2:30080/cpu-intensive'
        requests.get(url_cpu_intensive)
    
    time.sleep(5)
    main()
```

### Running the Script

To run the script, execute the following commands:

```sh
python test_api.py --cpu-intensive False
python test_api.py --cpu-intensive True
```

**Note:**
- If you run the script with `--cpu-intensive False`, you will see only two IP addresses in the response CSV.
- If you run the script with `--cpu-intensive True`, you will see up to four IP addresses in the response CSV, indicating that the Horizontal Pod Autoscaler (HPA) has scaled the pods based on CPU utilization.

## Useful Kubernetes Commands

Here are some useful Kubernetes commands for managing and monitoring your deployment:

```sh
kubectl get pods -n python-api-namespace
kubectl get hpa -n python-api-namespace
kubectl describe hpa python-k8s-api-hpa -n python-api-namespace
kubectl get service -n python-api-namespace
kubectl get deployment -n python-api-namespace
kubectl get events -n python-api-namespace
```

## Conclusion

This repository contains the complete solution for creating, dockerizing, deploying, and scaling a Python API using Docker and Kubernetes. By following the instructions in this README, you can set up and test the entire system on your local machine.
