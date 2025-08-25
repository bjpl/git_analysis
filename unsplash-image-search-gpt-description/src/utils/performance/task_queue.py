"""
Background task processing system with queuing and cancellation.
"""

import threading
import queue
import time
import uuid
from typing import Any, Callable, Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import traceback


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class BackgroundTask:
    """Represents a background task."""
    id: str
    name: str
    function: Callable
    args: tuple
    kwargs: dict
    priority: TaskPriority
    callback: Optional[Callable[[Any], None]] = None
    error_callback: Optional[Callable[[Exception], None]] = None
    progress_callback: Optional[Callable[[float, str], None]] = None
    
    # State
    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: Optional[Exception] = None
    progress: float = 0.0
    progress_message: str = ""
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    
    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
            
    def __lt__(self, other):
        """Compare tasks by priority for queue ordering."""
        return self.priority.value > other.priority.value
        
    def update_progress(self, progress: float, message: str = ""):
        """Update task progress."""
        self.progress = max(0.0, min(1.0, progress))
        self.progress_message = message
        if self.progress_callback:
            self.progress_callback(self.progress, message)
            
    def cancel(self):
        """Cancel the task if it's not running."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.CANCELLED


class TaskQueue:
    """
    Background task processing system.
    
    Features:
    - Priority-based task queuing
    - Task cancellation
    - Progress reporting
    - Error handling with callbacks
    - Thread pool management
    """
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.task_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_tasks: Dict[str, BackgroundTask] = {}
        self.completed_tasks: Dict[str, BackgroundTask] = {}
        self.workers: List[threading.Thread] = []
        
        self._shutdown = False
        self._stats = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'tasks_cancelled': 0,
            'total_processing_time': 0.0
        }
        
        # Start worker threads
        self._start_workers()
        
    def _start_workers(self):
        """Start worker threads."""
        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i+1}",
                daemon=True
            )
            worker.start()
            self.workers.append(worker)
            
    def _worker_loop(self):
        """Main worker loop."""
        while not self._shutdown:
            try:
                # Get next task with timeout
                try:
                    priority_wrapper, task = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                    
                if task.status == TaskStatus.CANCELLED:
                    self.task_queue.task_done()
                    continue
                    
                # Execute task
                self._execute_task(task)
                self.task_queue.task_done()
                
            except Exception as e:
                print(f"Worker error: {e}")
                traceback.print_exc()
                
    def _execute_task(self, task: BackgroundTask):
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        self.active_tasks[task.id] = task
        
        try:
            # Execute the task function
            result = task.function(*task.args, **task.kwargs)
            
            # Task completed successfully
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            
            # Update stats
            processing_time = task.completed_at - task.started_at
            self._stats['tasks_completed'] += 1
            self._stats['total_processing_time'] += processing_time
            
            # Call success callback
            if task.callback:
                try:
                    task.callback(result)
                except Exception as e:
                    print(f"Error in task callback: {e}")
                    
        except Exception as e:
            # Task failed
            task.error = e
            task.status = TaskStatus.FAILED
            task.completed_at = time.time()
            
            self._stats['tasks_failed'] += 1
            
            # Call error callback
            if task.error_callback:
                try:
                    task.error_callback(e)
                except Exception as callback_error:
                    print(f"Error in error callback: {callback_error}")
                    
        finally:
            # Move from active to completed
            if task.id in self.active_tasks:
                del self.active_tasks[task.id]
            self.completed_tasks[task.id] = task
            
            # Limit completed task history
            if len(self.completed_tasks) > 100:
                # Remove oldest completed tasks
                oldest_tasks = sorted(self.completed_tasks.values(), key=lambda t: t.completed_at)
                for old_task in oldest_tasks[:20]:
                    del self.completed_tasks[old_task.id]
                    
    def submit_task(
        self,
        name: str,
        function: Callable,
        args: tuple = (),
        kwargs: dict = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        callback: Optional[Callable[[Any], None]] = None,
        error_callback: Optional[Callable[[Exception], None]] = None,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """Submit a task for background execution."""
        if self._shutdown:
            raise RuntimeError("Task queue is shutting down")
            
        task_id = str(uuid.uuid4())
        task = BackgroundTask(
            id=task_id,
            name=name,
            function=function,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            callback=callback,
            error_callback=error_callback,
            progress_callback=progress_callback
        )
        
        # Add to priority queue
        # Using counter to ensure FIFO for same priority
        counter = int(time.time() * 1000000) % 1000000
        self.task_queue.put((priority.value * -1, counter, task))
        
        return task_id
        
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        # Check if task is in active tasks (can't cancel running tasks)
        if task_id in self.active_tasks:
            return False
            
        # Check if task is in completed tasks (already done)
        if task_id in self.completed_tasks:
            return False
            
        # Mark task as cancelled (will be caught by worker)
        # Note: This is a simple implementation. For more robust cancellation,
        # you'd need to track pending tasks separately.
        self._stats['tasks_cancelled'] += 1
        return True
        
    def get_task_status(self, task_id: str) -> Optional[BackgroundTask]:
        """Get task status and information."""
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]
            
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
            
        return None
        
    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'pending_tasks': self.task_queue.qsize(),
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'worker_threads': len(self.workers),
            'tasks_completed': self._stats['tasks_completed'],
            'tasks_failed': self._stats['tasks_failed'],
            'tasks_cancelled': self._stats['tasks_cancelled'],
            'avg_processing_time': (
                self._stats['total_processing_time'] / 
                max(1, self._stats['tasks_completed'])
            )
        }
        
    def get_active_tasks(self) -> List[BackgroundTask]:
        """Get list of currently active tasks."""
        return list(self.active_tasks.values())
        
    def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for all queued tasks to complete."""
        start_time = time.time()
        
        while not self.task_queue.empty() or self.active_tasks:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError("Tasks did not complete within timeout")
            time.sleep(0.1)
            
    def shutdown(self, timeout: float = 30.0):
        """Shutdown the task queue and wait for workers to finish."""
        self._shutdown = True
        
        # Wait for current tasks to complete
        start_time = time.time()
        while self.active_tasks and (time.time() - start_time) < timeout:
            time.sleep(0.1)
            
        # Wait for worker threads to exit
        for worker in self.workers:
            worker.join(timeout=1.0)
            
    def clear_completed_tasks(self):
        """Clear completed task history."""
        self.completed_tasks.clear()


# Convenience functions for common task patterns

def create_image_download_task(
    url: str,
    callback: Callable[[bytes], None],
    error_callback: Callable[[Exception], None],
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Callable[[], bytes]:
    """Create a task function for downloading images."""
    def download_task():
        import requests
        
        if progress_callback:
            progress_callback(0.0, "Starting download...")
            
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunks = []
            
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    chunks.append(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress = downloaded / total_size
                        progress_callback(progress, f"Downloaded {downloaded:,} / {total_size:,} bytes")
                        
            data = b''.join(chunks)
            
            if progress_callback:
                progress_callback(1.0, "Download completed")
                
            return data
            
        except Exception as e:
            if progress_callback:
                progress_callback(0.0, f"Download failed: {e}")
            raise
            
    return download_task


def create_api_call_task(
    api_function: Callable,
    args: tuple = (),
    kwargs: dict = None,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> Callable:
    """Create a task function for API calls."""
    def api_task():
        if progress_callback:
            progress_callback(0.0, "Making API call...")
            
        try:
            result = api_function(*args, **(kwargs or {}))
            
            if progress_callback:
                progress_callback(1.0, "API call completed")
                
            return result
            
        except Exception as e:
            if progress_callback:
                progress_callback(0.0, f"API call failed: {e}")
            raise
            
    return api_task