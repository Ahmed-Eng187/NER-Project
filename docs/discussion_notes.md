# Discussion Sheet Preparation 🎓☁️

This document prepares you for questions from your TA/Doctor during the final discussion/viva regarding the Cloud Computing & NLU aspects of the Resume NER project.

## 1. Problem Statement & Cloud Relevance
**Q: Why does this project need Cloud Computing? Why not run it locally?**
**A:** "Processing NLP models like BERT requires significant compute resources, often GPUs, which aren't available on standard client machines. By moving the system to the cloud, we achieve:
1. **Scalability:** We can handle hundreds of resumes concurrently by scaling EC2/ECS instances.
2. **Accessibility:** The Streamlit dashboard is accessible anywhere without local setup.
3. **Storage:** We utilize AWS S3 for secure, durable storage of user uploads rather than relying on volatile local disk space."

## 2. Technical Depth & Architecture
**Q: Explain your system architecture.**
**A:** "We use a microservices-inspired architecture containerized with Docker. The frontend is built with Streamlit, communicating via REST API to a FastAPI backend. The backend loads a pre-trained BERT model dynamically merged with LoRA weights. For storage, files uploaded via the frontend are pushed to AWS S3 by the backend service. We also implemented a Confidence Routing mechanism with an in-memory queue that can easily be swapped for AWS SQS in a massive-scale environment."

## 3. Machine Learning & Model Optimization
**Q: Why did you use LoRA instead of full fine-tuning?**
**A:** "Full fine-tuning of BERT requires updating ~110M parameters, which is computationally expensive and slow. LoRA (Low-Rank Adaptation) freezes the base model and only injects small rank-decomposition matrices. This reduced our trainable parameters drastically while achieving a strong Test F1 score of 0.8368, making the deployment lightweight and faster to load in a container environment."

## 4. Security & Production Readiness
**Q: How is this application secure for production?**
**A:** "We implemented multiple security layers:
1. **Middleware Size Limits:** Prevents Denial of Service (DoS) by rejecting files larger than 5MB.
2. **API Keys:** The `/parse` routes require an `X-API-Key` header.
3. **Cloud Security:** The AWS S3 bucket is private (No Public Access), and the backend uses an IAM Role with the Principle of Least Privilege (only allowed `s3:PutObject`)."

## 5. Scalability & Async Processing
**Q: What happens if 1,000 users upload a resume at the exact same time?**
**A:** "Currently, the FastAPI backend processes requests synchronously. However, the architecture is designed to transition easily to an asynchronous worker model (e.g., using Celery + Redis or AWS SQS). In a highly scaled scenario, the API would immediately return a `task_id`, push the resume to S3, and put a message on an SQS queue. A fleet of worker nodes (auto-scaled via AWS EC2 Auto Scaling Groups based on queue length) would pull messages, run inference, and update a database."

## 6. Audit Logging & Human-in-the-Loop
**Q: How do you handle errors or bad extractions?**
**A:** "We implemented a 'Human-in-the-Loop' routing system. If the model's confidence drops below 60%, the inference result is automatically routed to a Review Queue. A human operator can view these flagged CVs in the Streamlit dashboard and manually correct/approve them. Furthermore, every request generates an Audit Log entry to trace latency, routing decision, and errors for monitoring purposes."
