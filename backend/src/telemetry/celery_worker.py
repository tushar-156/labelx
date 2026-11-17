import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "label_tasks",
    broker=redis_url,
    backend=redis_url
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="process_batch_upload")
def process_batch_upload(batch_data: list):
    """
    Mock Celery task for processing a large batch of labels asynchronously.
    In a real implementation, this would iterate over the batch and call the rules engine.
    """
    import time
    
    # Simulate processing delay
    time.sleep(5)
    
    results = []
    for item in batch_data:
        # Mock result
        results.append({
            "message": item.get("message"),
            "status": "processed",
            "safety_score": 100
        })
        
    return {"status": "completed", "total": len(batch_data), "results": results}
