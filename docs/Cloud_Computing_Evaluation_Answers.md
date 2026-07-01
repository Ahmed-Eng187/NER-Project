# إجابات تقييم مادة الحوسبة السحابية (Cloud Computing Evaluation)

تم إعداد هذا الملف ليطابق تماماً المعايير المطلوبة في جدول التقييم (Rubric) الخاص بمناقشة التخرج. يمكنك نسخ هذه الإجابات أو استخدامها كمرجع أثناء المناقشة لضمان الحصول على الدرجة النهائية.

---

### 1. Architecture Relevance (Is the cloud design meaningful for the project?)
**Student Response:**
Yes. The project uses heavy Machine Learning models (BERT + LoRA) which require substantial compute power and memory not typically available on edge devices. The cloud design decouples the UI (Streamlit frontend) from the intensive processing (FastAPI backend). This microservices-like architecture ensures that the ML inference doesn't block the UI, and allows the backend to be hosted on powerful GPU instances in the cloud while users can access the system globally from any browser.

### 2. Service Selection (Are chosen cloud services appropriate and justified?)
**Student Response:**
We selected **AWS S3** for document storage and **AWS EC2 / ECS** for compute. 
- S3 is justified because storing uploaded PDF resumes on a local container disk is volatile and hard to scale. S3 provides 99.999999911% durability and is highly cost-effective.
- EC2/ECS is justified because it gives us full control over the container environment, allowing us to provision specific GPU/CPU resources required by the PyTorch ML models.

### 3. Deployment / Containers (Is there a clear deployment and packaging approach?)
**Student Response:**
Yes, the entire application is fully containerized using **Docker**. We created optimized Dockerfiles for both the Frontend and the Backend, keeping the layers small (e.g., using `python:3.10-slim`). We use `docker-compose` to orchestrate the containers, link the frontend to the backend via a private network, and map environment variables seamlessly. This guarantees that the project works identically in development and production (Compute Parity).

### 4. Networking / Security (Is exposure and protection in the cloud understood?)
**Student Response:**
We implemented Security at multiple layers:
- **Application Level:** A custom FastAPI Middleware limits file uploads to a maximum of 5MB to prevent Denial of Service (DoS) attacks, and endpoints are protected via an `X-API-Key` header.
- **Cloud Level:** The AWS S3 bucket blocks all public access. The application interacts with S3 using IAM roles following the "Principle of Least Privilege" (only allowing `s3:PutObject` for resume uploads).

### 5. Storage / Data Handling (Are storage and data choices sensible?)
**Student Response:**
Instead of storing raw PDF resumes directly in a SQL database (which is an anti-pattern), we store the unstructured PDFs in an Object Storage service (**AWS S3**). We only extract the structured entities (Name, Skills, Experience) via the NER model. In a full pipeline, these structured JSON results would be saved to a fast NoSQL database like DynamoDB or DocumentDB, optimizing retrieval times and reducing storage costs.

### 6. Scalability / Reliability (Has the team considered scale and availability?)
**Student Response:**
The system is designed with horizontal scalability in mind. Because the FastAPI backend is stateless, we can deploy multiple instances behind an **Application Load Balancer (ALB)**. For future hyper-scaling, we designed the architecture to support Asynchronous Processing: instead of waiting for the NER model to finish, the backend would place a message in an **AWS SQS** queue, and background worker nodes would process the resumes asynchronously.

### 7. Monitoring / Observability (Is there a credible logging / monitoring plan?)
**Student Response:**
Yes. We implemented a **Structured Logging** strategy using Python's `logging` module, capturing essential telemetry such as `latency_ms`, `confidence` scores, and routing events. We also established a full Audit Trail for every API request. In an AWS environment, these logs are designed to be streamed to **AWS CloudWatch** (using watchtower/JSON logs) to create real-time dashboards and trigger alarms if error rates or inference latency spike.

### 8. Cost Awareness (Is there awareness of cost and free-tier feasibility?)
**Student Response:**
We have heavily optimized costs:
1. By using **LoRA** (Low-Rank Adaptation), we significantly reduced the VRAM requirements of the BERT model. This means we can deploy the inference backend on cheaper `t3.medium` or free-tier instances instead of requiring expensive dedicated GPUs.
2. We utilize AWS S3 Standard storage, which is pennies per GB, keeping our storage costs near zero for the initial scale.
3. Our containerized approach allows us to use AWS Spot Instances for worker nodes in the future, saving up to 90% on compute costs.
