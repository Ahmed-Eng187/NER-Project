# Deployment Guide

This guide outlines the steps required to deploy the Resume NER System to a production environment on AWS.

## 1. Prerequisites
- AWS Account with billing enabled.
- AWS CLI installed and configured on your local machine.
- Docker installed on the target machine.

## 2. AWS S3 Bucket Setup
The application uses S3 to store uploaded resumes before processing.
1. Navigate to the **AWS S3 Console**.
2. Click **Create bucket**.
3. Name the bucket (e.g., `resume-ner-production-bucket`).
4. Ensure **Block all public access** is ON.
5. Create the bucket.

## 3. IAM User Setup
Create an IAM User with programmatic access to upload to S3:
1. Go to **IAM** -> **Users** -> **Add users**.
2. Create user (e.g., `resume-ner-app`).
3. Attach policies directly. Create an inline policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::resume-ner-production-bucket/resumes/*"
        }
    ]
}
```
4. Generate an **Access Key ID** and **Secret Access Key**. Add these to your `.env` file.

## 4. EC2 Deployment (Docker Compose)
For a straightforward cloud deployment, we will use a single EC2 instance running Docker Compose.

1. Launch an EC2 Instance:
   - **AMI**: Ubuntu Server 22.04 LTS or Deep Learning AMI (if using GPU).
   - **Instance Type**: `t3.medium` (minimum for CPU) or `g4dn.xlarge` (for GPU inference).
   - **Security Group**: Allow Inbound TCP on ports `22` (SSH), `8000` (Backend API), and `8501` (Frontend).

2. SSH into the instance:
```bash
ssh -i "your-key.pem" ubuntu@<ec2-public-ip>
```

3. Install Docker & Docker Compose:
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose -y
```

4. Clone the repository and configure:
```bash
git clone <your-repo-url>
cd final_proj
cp .env.example .env
# nano .env (update keys)
```

5. Start the Application:
```bash
sudo docker-compose up --build -d
```

## 5. Domain & HTTPS (Optional but Recommended)
To secure the application for production:
- Set up an **Application Load Balancer (ALB)** in AWS.
- Point the ALB to the EC2 instance on ports 8000/8501.
- Attach an ACM Certificate to the ALB to enable HTTPS (Port 443).
