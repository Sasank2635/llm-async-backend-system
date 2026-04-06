from redis_client import redis_client
from gemini_client import client, MODEL
import signal
import json
import time

MAX_RETRIES = 3
BASE_TIMEOUT = 20  # base timeout in seconds


def timeout_handler(signum, frame):
    raise Exception("Timeout occurred")


# ✅ Register signal handler ONCE (important)
signal.signal(signal.SIGALRM, timeout_handler)


def get_task():
    for queue in ["queue:high", "queue:medium", "queue:low"]:
        size = redis_client.llen(queue)
        # optional debug:
        # print(f"Checking {queue}, size={size}")

        task = redis_client.lpop(queue)
        if task:
            print(f"Got task from {queue}")
            return task
    return None


def process_queue():
    print("Worker started...")

    while True:
        task = get_task()

        if task:
            data = json.loads(task)
            task_id = data["task_id"]
            message = data["message"]
            retries = data.get("retries", 0)
            priority = data.get("priority", "medium")

            print(f"Processing task: {task_id} (retry {retries})")

            start_time = time.time()

            try:
                # 🔥 Adaptive timeout
                timeout = BASE_TIMEOUT + (retries * 10)
                print(f"Timeout set to: {timeout}s")

                signal.alarm(timeout)

                # update status
                data["status"] = "processing"
                redis_client.set(task_id, json.dumps(data))

                # 🔥 Gemini call
                response = client.models.generate_content(
                    model=MODEL,
                    contents=message
                )

                signal.alarm(0)  # cancel timeout

                duration = time.time() - start_time

                # ✅ Success
                data["status"] = "completed"
                data["result"] = response.text
                data["processing_time"] = duration

                redis_client.set(task_id, json.dumps(data))

                # 📊 Metrics
                redis_client.incr("metrics:processed")
                redis_client.incrbyfloat("metrics:total_time", duration)

                print(f"✅ Completed task: {task_id} in {duration:.2f}s")

            except Exception as e:
                signal.alarm(0)

                retries += 1
                data["retries"] = retries

                print(f"❌ Error: {e}")

                if retries < MAX_RETRIES:
                    print(f"🔁 Retrying task: {task_id}")

                    # 🔥 Exponential backoff
                    backoff = 2 ** retries
                    print(f"⏳ Backoff: {backoff}s")
                    time.sleep(backoff)

                    redis_client.rpush(
                        f"queue:{priority}",
                        json.dumps(data)
                    )

                else:
                    print(f"💀 Task failed permanently: {task_id}")

                    # ❌ Failed
                    data["status"] = "failed"
                    data["error"] = str(e)

                    redis_client.set(task_id, json.dumps(data))

                    # 💀 Dead Letter Queue
                    redis_client.rpush("queue:dead", json.dumps(data))

                    # 📊 Metrics
                    redis_client.incr("metrics:failed")

        time.sleep(0.5)  # reduced CPU usage


if __name__ == "__main__":
    process_queue()