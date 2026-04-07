"""
Background Task Manager
=======================
Tracks processing tasks by task_id with thread-safe progress updates.
Used for large-file async processing pipelines.
"""
import threading
import time
import uuid
from typing import Optional

# ─── In-Memory Task Store ────────────────────────────────────────────────────
_tasks: dict = {}
_lock = threading.Lock()

STAGES = [
    "uploading",
    "reading",
    "cleaning",
    "scoring",
    "analytics",
    "completed",
]

STAGE_MESSAGES = {
    "uploading":  "Uploading file...",
    "reading":    "Reading dataset...",
    "cleaning":   "Running cleaning pipeline...",
    "scoring":    "Calculating quality score...",
    "analytics":  "Generating analytics report...",
    "completed":  "Completed ✓",
}

STAGE_PROGRESS = {
    "uploading":  5,
    "reading":    20,
    "cleaning":   45,
    "scoring":    65,
    "analytics":  85,
    "completed":  100,
}


def create_task(dataset_id: Optional[int] = None) -> str:
    task_id = str(uuid.uuid4())
    with _lock:
        _tasks[task_id] = {
            "task_id":    task_id,
            "dataset_id": dataset_id,
            "stage":      "uploading",
            "progress":   5,
            "message":    STAGE_MESSAGES["uploading"],
            "result":     None,
            "error":      None,
            "created_at": time.time(),
        }
    return task_id


def update_task(task_id: str, stage: str, result=None, error=None):
    with _lock:
        if task_id not in _tasks:
            return
        _tasks[task_id]["stage"]    = stage
        _tasks[task_id]["progress"] = STAGE_PROGRESS.get(stage, 0)
        _tasks[task_id]["message"]  = STAGE_MESSAGES.get(stage, stage)
        if result is not None:
            _tasks[task_id]["result"] = result
        if error is not None:
            _tasks[task_id]["error"] = error


def set_dataset_id(task_id: str, dataset_id: int):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id]["dataset_id"] = dataset_id


def get_task(task_id: str) -> Optional[dict]:
    with _lock:
        return dict(_tasks.get(task_id, {}))


def fail_task(task_id: str, error: str):
    with _lock:
        if task_id in _tasks:
            _tasks[task_id]["stage"]   = "failed"
            _tasks[task_id]["error"]   = error
            _tasks[task_id]["message"] = f"Failed: {error}"


def cleanup_old_tasks(max_age_seconds: int = 3600):
    """Remove tasks older than max_age_seconds."""
    now = time.time()
    with _lock:
        stale = [tid for tid, t in _tasks.items()
                 if now - t["created_at"] > max_age_seconds]
        for tid in stale:
            del _tasks[tid]
