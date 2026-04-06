from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from rate_limiter import is_allowed
from gemini_client import client, MODEL
from redis_client import redis_client

import uuid
import json

app = FastAPI()


# 🔥 Streaming chat endpoint
@app.post("/chat")
async def chat(user_id: str, message: str):
    if not is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    def stream():
        try:
            response = client.models.generate_content_stream(
                model=MODEL,
                contents=message
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            yield f"\nError: {str(e)}"

    return StreamingResponse(stream(), media_type="text/plain")


# ⚡ Async queue endpoint
@app.post("/chat_async")
def chat_async(user_id: str, message: str, priority: str = "medium"):
    if not is_allowed(user_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    task_id = str(uuid.uuid4())

    job_data = {
        "task_id": task_id,
        "message": message,
        "status": "pending",
        "retries": 0,
        "priority": priority
    }

    redis_client.set(task_id, json.dumps(job_data))

    # 🔥 CRITICAL LINE
    redis_client.rpush(f"queue:{priority}", json.dumps(job_data))

    return {"task_id": task_id}


# 📦 Get async result
@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = redis_client.get(task_id)

    if not result:
        return {"status": "not_found"}

    return json.loads(result)

@app.get("/metrics")
def get_metrics():
    processed = int(redis_client.get("metrics:processed") or 0)
    failed = int(redis_client.get("metrics:failed") or 0)
    total_time = float(redis_client.get("metrics:total_time") or 0)

    avg_time = total_time / processed if processed > 0 else 0

    return {
        "processed_jobs": processed,
        "failed_jobs": failed,
        "avg_processing_time_sec": avg_time,
        "queue_sizes": {
            "high": redis_client.llen("queue:high"),
            "medium": redis_client.llen("queue:medium"),
            "low": redis_client.llen("queue:low"),
            "dead": redis_client.llen("queue:dead")
        }
    }