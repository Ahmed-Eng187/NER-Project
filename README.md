Markdown
# ☁️ Resume NER System – Cloud-Ready Production Environment

An advanced, production-ready AI Resume Information Extraction System built for cloud deployment. This enterprise-grade system extracts structured entities (Name, Email, Skills, Experience, Education, etc.) from PDF CVs using a fine-tuned **BERT** model optimized with **LoRA (Low-Rank Adaptation)** adapters.

---

## 🚀 Key Features

* **High-Accuracy Neural NLP:** Powered by a fine-tuned `dslim/bert-base-NER` base model utilizing LoRA adapters for efficient parameter tuning.
* **Smart Confidence Routing:** 
  * 🟢 **High Confidence:** Automatically accepted & processed.
  * 🟡 **Medium Confidence:** Flagged with system warnings.
  * 🔴 **Low Confidence:** Sent to a Human-in-the-Loop review queue.
* **Cloud-Native & Dockerized:** Multi-container architecture with containerized Frontend and Backend, configured for seamless **AWS** deployment.
* **AWS S3 Integration:** Secure and automated PDF storage utilizing **IAM roles** following the Principle of Least Privilege.
* **Enterprise Security Middleware:** Custom gateway middleware protecting against large file payloads, size limits, and securing requests via `X-API-Key` headers.
* **Streamlit Admin Dashboard:** Modern, dark-themed UI that manages both testing uploads and the human verification queue.

---

## 🛠️ Tech Stack & Architecture

* **Backend Engine:** FastAPI (Python), PyTorch, HuggingFace Transformers, PEFT (LoRA)
* **Frontend Dashboard:** Streamlit, Docker
* **Cloud Infrastructure:** AWS S3, AWS EC2/ECS, Docker Compose
* **Security & Testing:** Custom Python Middleware, PyTest (API & Load Tests)

---

## 📊 Performance Benchmark (Evaluation Metrics)

The fine-tuned sequence labeling model achieves highly robust F1 scores across token-level entity extractions:

| Metric Type | Score / F1-Matrix |
| :--- | :---: |
| **Test F1-Score** | **0.8368** |
| **Validation F1-Score** | **0.8324** |
| **Skills Extraction F1** | **0.7273** |

---

## 💻 Installation & Quickstart (Docker)

1. **Clone the Repository & Configure Environment:**
   ```bash
   git clone [https://github.com/Ahmed-Eng187/Resume_NER_System.git](https://github.com/Ahmed-Eng187/Resume_NER_System.git)
   cd Resume_NER_System
   cp .env.example .env
(Edit .env with your AWS credentials if testing remote S3 bucket uploads)

Build and Run the Containers:

Bash
docker-compose up --build -d
Access the Microservices:

🖥️ Frontend Dashboard: http://localhost:8501

⚙️ Backend API Interactive Docs: http://localhost:8000/docs

📂 Project Structure
Plaintext
Resume_NER_System/
│
├── backend/                  # FastAPI Backend API Service
│   ├── core/                 # App Config & Central Logging Setup
│   ├── middleware/           # Security Protections & File Size Limits
│   ├── models/               # Base LLM Config & LoRA Adapter Weights
│   ├── services/             # S3 Buckets & External Cloud Providers
│   └── main.py               # API Entrypoint
│
├── frontend/                 # Streamlit UI Dashboard
│   └── streamlit_app.py      # Human review interface code
│
├── docs/                     # Deployment Guide (EC2/ECS/S3) & Architecture Notes
├── tests/                    # Robust API & Load Tests (PyTest)
├── .github/workflows/        # Automated CI/CD Deployment Pipelines
└── docker-compose.yml        # Orchestration layer for local setup
🔒 Production Security Architecture
Payload Validation: Strict file verification prevents malicious code execution inside PDF streams.

IAM Strict Policies: Cloud access relies on safe role inheritance rather than storing root hardcoded keys.

Rate Limiting Guardrails: Safeguards backend resources against brute-force payload floods or large vector crashes.

👤 Author
Ahmed Hamdy

🎯 Aspiring Machine Learning Engineer & Data Analyst

🛠️ NLP | MLOps | Cloud Architecture | Python | Docker | AWS
