#  Deploying Web-Scraping by Cloud DevOps Workflow using VS Code

This project demonstrates a complete DevOps pipeline using Docker, Kubernetes (via Minikube), AWS EKS, IAM, AWS Lambda, and AWS SDK — all developed and managed inside **Visual Studio Code**.

---

##   Prerequisites

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- [GitHub CLI (optional)](https://cli.github.com/)
- AWS Account
- IAM user with proper permissions
- GitHub repository linked

---

##  1. Docker in VS Code

###  Install Extensions


### 🛆 Build and Run a Docker Container

```bash
# Build the Docker image
docker build -t python-jupyter-app .

# Run the container
docker run -p 8080:8080 jupyter-notebook
```

###  Dockerfile
```dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py

EXPOSE 8888

CMD ["python", "app.py"]
```

### requirements.txt
```
flask
pandas
jupyter
numpy
```

You can use the Docker extension sidebar in VS Code to view containers, images, logs, etc.

---

##  2. Minikube & Kubernetes in VS Code

###  Install Extensions

- Kubernetes (official) extension
- YAML (for syntax highlighting)

###  Start Minikube and Deploy

```bash
# Start Minikube
minikube start
mimikube status

# Loading Docker image with minikube
minikube image load python-jupyter-app

# Set kubectl context
kubectl config use-context minikube

# Apply your deployment
kubectl apply -f python-jupyter-app.deployment.yaml
kubectl apply -f python-jupyter-app.service.yaml

#To restart kubectl again
kubectl rollout restart deployment python-jupyter-deployment

#To check pods
kubectl get pods

#To run the application
minikube service python-juypter-service --url

#To check errors
kubectl logs <pod name>
```

###  python-jupyter-app.deployment.yaml
```yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-jupyter-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: python-jupyter-app
  template:
    metadata:
      labels:
        app: python-jupyter-app
    spec:
      containers:
      - name: python-jupyter-app
        image: python-jupyter-app
        imagePullPolicy: Never

        ports:
        - containerPort: 9999
    
```

###  python-jupyter-app.service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: python-jupyter-service
spec:
  type: NodePort
  selector:
    app: python-jupyter-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9999
  
```

### app.py

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask running in Kubernetes!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
```

---

##  3. AWS EKS & IAM in VS Code


###  **Step 1: Ensure Your Docker Image is Ready**

Make sure your Dockerfile is working and builds correctly.

#### Example `Dockerfile` for Jupyter notebook:
```dockerfile
As mentioned above.
```

Build your Docker image:
```bash
docker build -t jupyter-notebook:latest .
```

---

### 🔹 **Step 2: Push Docker Image to Amazon ECR**

1. **Go to AWS Console > ECR**
   - Create a new repository (e.g., `jupyter-notebook`)

2. **Authenticate and Push from Terminal:**
   ```bash
   aws ecr get-login-password --region your-region | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
   ```

3. **Tag and Push:**
   ```bash
   docker tag jupyter-notebook:latest <aws_account_id>.dkr.ecr.<region>.amazonaws.com/jupyter-notebook:latest

   docker push <aws_account_id>.dkr.ecr.<region>.amazonaws.com/jupyter-notebook:latest
   ```

---

### 🔹 **Step 3: Create Your EKS Cluster (Console or eksctl)**

#### Option A: **Using AWS Console**
1. Go to **EKS > Clusters > Create Cluster**
2. Choose name, role, and networking settings
3. Create a Node Group (EC2 worker nodes)

#### Option B: **Using `eksctl` (faster)**
```yaml
# cluster-config.yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: jupyter-cluster
  region: us-east-1
nodeGroups:
  - name: ng-1
    instanceType: t3.medium
    desiredCapacity: 2
```
Run:
```bash
eksctl create cluster -f cluster-config.yaml
```

---

### 🔹 **Step 4: Configure kubectl to Access Your Cluster**

```bash
aws eks --region us-east-1 update-kubeconfig --name jupyter-cluster
kubectl get nodes
```

---

### 🔹 **Step 5: Deploy Your Notebook App with YAML**

#### Example `jupyter-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jupyter-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: jupyter
  template:
    metadata:
      labels:
        app: jupyter
    spec:
      containers:
      - name: jupyter
        image: <aws_account_id>.dkr.ecr.<region>.amazonaws.com/jupyter-notebook:latest
        ports:
        - containerPort: 8888
---
apiVersion: v1
kind: Service
metadata:
  name: jupyter-service
spec:
  selector:
    app: jupyter
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8888
  type: LoadBalancer
```

Apply it:
```bash
kubectl apply -f jupyter-deployment.yaml
kubectl get svc
```

After a minute or two, you'll see an external IP in the service. You can open that in your browser and access the notebook.

---



### ✅ Setup AWS CLI

```bash
aws configure
# Provide your AWS Access Key, Secret Key, region (e.g. us-east-1), and output format
```

### 🔧 Create IAM Role

- Use IAM to create a role with EKS and EC2 access
- Attach policies like `AmazonEKSClusterPolicy`, `AmazonEKSWorkerNodePolicy`, `AmazonEC2ContainerRegistryReadOnly`

### ⚙️ EKS Setup (using eksctl)

```bash
eksctl create cluster --name jupyter-cluster --region us-east-1 --nodes 2
```

Update kubeconfig:

```bash
aws eks --region us-east-1 update-kubeconfig --name jupyter-cluster
```

---

##  4. AWS Lambda 


###  Folder Structure Example

```
lambda/
├── lambda_function.py
├── requirements.txt
```

---

###  Sample Code: `lambda_function.py`

```python
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from AWS Lambda!'
    }
```

---

###  Deploying to AWS Manually (Using AWS CLI)

#### Step 1: Zip Your Lambda Code

```bash
zip function.zip lambda_function.py
```

If you have dependencies:

```bash
pip install -r requirements.txt -t package/
cd package
zip -r ../function.zip .
cd ..
zip -g function.zip lambda_function.py
```

---

#### Step 2: Update Code in AWS Lambda

```bash
aws lambda update-function-code \
  --function-name MyLambdaFunction \
  --zip-file fileb://function.zip
```


##  5. Using AWS SDK (`boto3`) in a Python File

---

#### 1. Install `boto3`

In your terminal:

```bash
pip install boto3
```

---


#### 📁 Upload a File to S3

```python
import boto3
from botocore.exceptions import ClientError

# Replace with your region
region = 'us-east-1'  # or 'ap-south-1', 'us-west-2', etc.
bucket_name = 'tejaswi-bucket-2002'  # Make sure this is unique globally

# Initialize session
session = boto3.session.Session(region_name=region)
s3 = session.client('s3')

try:
    if region == 'us-east-1':
        s3.create_bucket(Bucket=bucket_name)
    else:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )
    print(f'✅ Bucket "{bucket_name}" created successfully in {region}')
except ClientError as e:
    if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
        print(f'ℹ️ Bucket "{bucket_name}" already exists and is owned by you.')
    else:
        print(f'❌ Failed to create bucket: {e}')

```

---

##  5. GitHub Actions CI/CD Pipeline

###  File Structure

```
.github/
└── workflows/
    └── aws-deploy.yml
```

###  .github/workflows/aws-deploy.yml

```yaml
name: Deploy to AWS Lambda

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install Dependencies
      run: |
        pip install boto3

    - name: Deploy Lambda (using AWS CLI)
      run: |
        zip function.zip lambda_function.py
        aws lambda update-function-code --function-name MyLambdaFunction \
          --zip-file fileb://function.zip
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        AWS_REGION: us-east-1
```

---

##  AWS Secrets in GitHub

1. Go to your repo → Settings → Secrets and variables → Actions
2. Add:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`


### Terraform Infrastructure Setup

This project contains Terraform code to provision infrastructure using [Terraform](https://www.terraform.io/).


## ⚙️ Usage

1. **Initialize Terraform**

```bash
terraform init
```

2. **Format Code (optional)**

```bash
terraform fmt
```

3. **Plan Infrastructure Changes**

```bash
terraform plan
```

4. **Apply Infrastructure**

```bash
terraform apply
```

5. **Destroy Infrastructure**

```bash
terraform destroy
```



##  Clean Up

```bash
terraform destroy
```

---
