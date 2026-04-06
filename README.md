Working UI:-
https://llm-async-backend-system-wn2jtbqdzpanat3eh5a6jj.streamlit.app/

# 🧠 LLM Backend System (Async + Queue + Priority)

![UI](screenshots/ui.png)

A production-grade backend system for LLM applications using FastAPI, Redis, and Gemini API.
Designed to handle high-concurrency AI workloads with reliability, scalability, and observability.

---

## 🚀 Features

- ⚡ Async request handling (non-blocking API)
- 🧠 Gemini LLM integration (latest SDK)
- 📦 Redis-based job queue (producer-consumer architecture)
- 🔁 Retry mechanism for fault tolerance
- ⏱ Timeout handling to prevent worker blocking
- 🎯 Priority queues (high / medium / low)
- 💀 Dead Letter Queue (DLQ) for failed jobs
- 📊 Metrics (processing time, failures, queue size)
- ⚙️ Multi-worker scaling (horizontal scaling)
- 🎨 Streamlit UI for interaction

---

## 🏗 Architecture


Client (Streamlit UI)

↓

FastAPI Backend

↓

Redis (Queue + Job Store)

↓

Workers (Parallel)

↓

Gemini API



## 🧪 API Endpoints

### 🔥 POST `/chat`

Streaming response from LLM

### ⚡ POST `/chat_async`

Submit async job → returns `task_id`

### 📦 GET `/result/{task_id}`

Fetch job status:

- pending
- processing
- completed
- failed

### 📊 GET `/metrics`

System metrics:

- processed jobs
- failed jobs
- average processing time
- queue sizes

---

## ⚙️ Run Locally

### 1. Start Redis

redis-server


### 2. Start FastAPI server

uvicorn main:app --reload --port 8252


### 3. Start worker(s)

python queue_worker.py


(Optional: run multiple workers for scaling)

### 4. Run Streamlit UI

streamlit run app.py


---
## 🧠 Example Workflow

1. User sends request via UI  
2. API pushes job to Redis queue  
3. Worker picks job and calls Gemini API  
4. Result stored in Redis  
5. UI polls result and displays response
---
## 📊 Example Metrics Output

```json
{
  "processed_jobs": 10,
  "failed_jobs": 1,
  "avg_processing_time_sec": 1.2,
  "queue_sizes": {
    "high": 0,
    "medium": 1,
    "low": 0,
    "dead": 1
  }
}
```


📁 Project Structure

llm-chat-api/
├── app.py                # Streamlit UI
├── main.py               # FastAPI backend
├── queue_worker.py       # Worker (async processing)
├── redis_client.py       # Redis connection
├── rate_limiter.py       # Rate limiting logic
├── gemini_client.py      # Gemini API integration
├── requirements.txt
├── .env.example
├── README.md
└── screenshots/
