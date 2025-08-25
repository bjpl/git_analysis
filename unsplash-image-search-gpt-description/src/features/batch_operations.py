"""Batch processing operations for multiple images and vocabulary extraction."""

import json
import asyncio
import aiohttp
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, AsyncIterator
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from io import StringIO, BytesIO
from PIL import Image
import requests
from openai import OpenAI


class BatchStatus(Enum):
    """Batch processing status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchType(Enum):
    """Types of batch operations."""
    IMAGE_SEARCH = "image_search"
    VOCABULARY_EXTRACTION = "vocabulary_extraction"
    IMAGE_DESCRIPTION = "image_description"
    TRANSLATION = "translation"
    COLLECTION_EXPORT = "collection_export"
    DATA_MIGRATION = "data_migration"


class Priority(Enum):
    """Processing priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class BatchItem:
    """Individual item in a batch operation."""
    id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str = "pending"
    error: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class BatchJob:
    """Batch processing job definition."""
    id: str
    name: str
    batch_type: BatchType
    items: List[BatchItem]
    status: BatchStatus
    priority: Priority
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: int = 0  # 0-100
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    settings: Dict[str, Any] = None
    results_summary: Dict[str, Any] = None
    error_log: List[str] = None
    
    def __post_init__(self):
        if self.settings is None:
            self.settings = {}
        if self.results_summary is None:
            self.results_summary = {}
        if self.error_log is None:
            self.error_log = []
        if self.total_items == 0:
            self.total_items = len(self.items)


class BatchOperations:
    """Advanced batch processing system for multiple operations."""
    
    def __init__(self, data_dir: Path, unsplash_api_key: str, openai_api_key: str):
        self.data_dir = data_dir
        self.db_path = data_dir / "batch_operations.db"
        self.results_dir = data_dir / "batch_results"
        self.temp_dir = data_dir / "batch_temp"
        
        # Create directories
        for directory in [self.results_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # API clients
        self.unsplash_api_key = unsplash_api_key
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Processing settings
        self.max_workers = 4
        self.max_retries = 3
        self.request_delay = 1.0  # Delay between API requests
        self.batch_size = 10  # Items to process in one batch
        
        # State management
        self.running_jobs: Dict[str, threading.Thread] = {}
        self.job_queues: Dict[str, queue.Queue] = {}
        self.progress_callbacks: Dict[str, List[Callable]] = {}
        
        self._init_database()
    
    def _init_database(self):
        """Initialize the batch operations database."""
        with sqlite3.connect(self.db_path) as conn:
            # Batch jobs table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_jobs (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    batch_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    started_at TEXT,
                    completed_at TEXT,
                    progress INTEGER DEFAULT 0,
                    total_items INTEGER DEFAULT 0,
                    completed_items INTEGER DEFAULT 0,
                    failed_items INTEGER DEFAULT 0,
                    settings TEXT,
                    results_summary TEXT,
                    error_log TEXT
                )
            """)
            
            # Batch items table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_items (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    output_data TEXT,
                    status TEXT DEFAULT 'pending',
                    error TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    retry_count INTEGER DEFAULT 0,
                    metadata TEXT,
                    FOREIGN KEY (job_id) REFERENCES batch_jobs (id) ON DELETE CASCADE
                )
            """)
            
            # Processing statistics table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS batch_stats (
                    date TEXT PRIMARY KEY,
                    jobs_created INTEGER DEFAULT 0,
                    jobs_completed INTEGER DEFAULT 0,
                    items_processed INTEGER DEFAULT 0,
                    total_processing_time_minutes REAL DEFAULT 0,
                    avg_items_per_minute REAL DEFAULT 0
                )
            """)
            
            conn.commit()
    
    def create_batch_job(self, name: str, batch_type: BatchType, 
                        input_items: List[Dict[str, Any]],
                        priority: Priority = Priority.NORMAL,
                        settings: Dict[str, Any] = None) -> str:
        """Create a new batch processing job."""
        import uuid
        
        job_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create batch items
        items = []
        for i, input_data in enumerate(input_items):
            item_id = f"{job_id}_{i:04d}"
            items.append(BatchItem(
                id=item_id,
                input_data=input_data
            ))
        
        # Create job
        job = BatchJob(
            id=job_id,
            name=name,
            batch_type=batch_type,
            items=items,
            status=BatchStatus.PENDING,
            priority=priority,
            created_at=now,
            total_items=len(items),
            settings=settings or {}
        )
        
        # Save to database
        self._save_job_to_db(job)
        
        return job_id
    
    def start_batch_job(self, job_id: str, callback: Optional[Callable] = None) -> bool:
        """Start processing a batch job."""
        job = self.get_batch_job(job_id)
        if not job or job.status != BatchStatus.PENDING:
            return False
        
        # Register callback
        if callback:
            self.register_progress_callback(job_id, callback)
        
        # Update status
        job.status = BatchStatus.RUNNING
        job.started_at = datetime.now().isoformat()
        self._save_job_to_db(job)
        
        # Start processing thread
        thread = threading.Thread(
            target=self._process_batch_job,
            args=(job_id,),
            daemon=True
        )
        self.running_jobs[job_id] = thread
        thread.start()
        
        return True
    
    def pause_batch_job(self, job_id: str) -> bool:
        """Pause a running batch job."""
        job = self.get_batch_job(job_id)
        if not job or job.status != BatchStatus.RUNNING:
            return False
        
        job.status = BatchStatus.PAUSED
        self._save_job_to_db(job)
        return True
    
    def resume_batch_job(self, job_id: str) -> bool:
        """Resume a paused batch job."""
        job = self.get_batch_job(job_id)
        if not job or job.status != BatchStatus.PAUSED:
            return False
        
        job.status = BatchStatus.RUNNING
        self._save_job_to_db(job)
        return True
    
    def cancel_batch_job(self, job_id: str) -> bool:
        """Cancel a batch job."""
        job = self.get_batch_job(job_id)
        if not job or job.status in [BatchStatus.COMPLETED, BatchStatus.FAILED]:
            return False
        
        job.status = BatchStatus.CANCELLED
        job.completed_at = datetime.now().isoformat()
        self._save_job_to_db(job)
        
        # Stop processing thread
        if job_id in self.running_jobs:
            # Thread will check status and exit
            pass
        
        return True
    
    def get_batch_job(self, job_id: str) -> Optional[BatchJob]:
        """Get a batch job by ID."""
        with sqlite3.connect(self.db_path) as conn:
            # Get job data
            job_row = conn.execute(
                "SELECT * FROM batch_jobs WHERE id = ?", 
                (job_id,)
            ).fetchone()
            
            if not job_row:
                return None
            
            # Get items
            item_rows = conn.execute("""
                SELECT id, input_data, output_data, status, error, 
                       start_time, end_time, retry_count, metadata
                FROM batch_items WHERE job_id = ?
                ORDER BY id
            """, (job_id,)).fetchall()
            
            items = []
            for item_row in item_rows:
                items.append(BatchItem(
                    id=item_row[0],
                    input_data=json.loads(item_row[1]),
                    output_data=json.loads(item_row[2]) if item_row[2] else None,
                    status=item_row[3],
                    error=item_row[4],
                    start_time=item_row[5],
                    end_time=item_row[6],
                    retry_count=item_row[7],
                    metadata=json.loads(item_row[8]) if item_row[8] else {}
                ))
            
            # Construct job
            return BatchJob(
                id=job_row[0],
                name=job_row[1],
                batch_type=BatchType(job_row[2]),
                items=items,
                status=BatchStatus(job_row[3]),
                priority=Priority(job_row[4]),
                created_at=job_row[5],
                started_at=job_row[6],
                completed_at=job_row[7],
                progress=job_row[8],
                total_items=job_row[9],
                completed_items=job_row[10],
                failed_items=job_row[11],
                settings=json.loads(job_row[12]) if job_row[12] else {},
                results_summary=json.loads(job_row[13]) if job_row[13] else {},
                error_log=json.loads(job_row[14]) if job_row[14] else []
            )
    
    def list_batch_jobs(self, status: Optional[BatchStatus] = None,
                       limit: int = 50) -> List[BatchJob]:
        """List batch jobs with optional status filter."""
        with sqlite3.connect(self.db_path) as conn:
            if status:
                rows = conn.execute("""
                    SELECT * FROM batch_jobs 
                    WHERE status = ?
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (status.value, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM batch_jobs 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,)).fetchall()
            
            jobs = []
            for row in rows:
                # Load basic job info without items for performance
                job = BatchJob(
                    id=row[0],
                    name=row[1],
                    batch_type=BatchType(row[2]),
                    items=[],  # Don't load items for list view
                    status=BatchStatus(row[3]),
                    priority=Priority(row[4]),
                    created_at=row[5],
                    started_at=row[6],
                    completed_at=row[7],
                    progress=row[8],
                    total_items=row[9],
                    completed_items=row[10],
                    failed_items=row[11],
                    settings=json.loads(row[12]) if row[12] else {},
                    results_summary=json.loads(row[13]) if row[13] else {},
                    error_log=json.loads(row[14]) if row[14] else []
                )
                jobs.append(job)
            
            return jobs
    
    def batch_image_search(self, queries: List[str], 
                          images_per_query: int = 10,
                          filters: Dict[str, Any] = None) -> str:
        """Create a batch job for multiple image searches."""
        input_items = []
        for query in queries:
            input_items.append({
                'query': query,
                'count': images_per_query,
                'filters': filters or {}
            })
        
        settings = {
            'images_per_query': images_per_query,
            'total_queries': len(queries),
            'filters': filters or {}
        }
        
        return self.create_batch_job(
            name=f"Batch Image Search ({len(queries)} queries)",
            batch_type=BatchType.IMAGE_SEARCH,
            input_items=input_items,
            settings=settings
        )
    
    def batch_vocabulary_extraction(self, image_urls: List[str],
                                   language: str = 'es') -> str:
        """Create a batch job for vocabulary extraction from multiple images."""
        input_items = []
        for url in image_urls:
            input_items.append({
                'image_url': url,
                'language': language
            })
        
        settings = {
            'language': language,
            'total_images': len(image_urls)
        }
        
        return self.create_batch_job(
            name=f"Batch Vocabulary Extraction ({len(image_urls)} images)",
            batch_type=BatchType.VOCABULARY_EXTRACTION,
            input_items=input_items,
            settings=settings
        )
    
    def batch_image_description(self, image_urls: List[str],
                               language: str = 'es',
                               context_notes: List[str] = None) -> str:
        """Create a batch job for generating descriptions of multiple images."""
        input_items = []
        for i, url in enumerate(image_urls):
            input_items.append({
                'image_url': url,
                'language': language,
                'context': context_notes[i] if context_notes and i < len(context_notes) else ''
            })
        
        settings = {
            'language': language,
            'total_images': len(image_urls),
            'has_context': bool(context_notes)
        }
        
        return self.create_batch_job(
            name=f"Batch Image Description ({len(image_urls)} images)",
            batch_type=BatchType.IMAGE_DESCRIPTION,
            input_items=input_items,
            settings=settings
        )
    
    def export_batch_results(self, job_id: str, 
                           format_type: str = 'json') -> Path:
        """Export batch job results to file."""
        job = self.get_batch_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{job.name.replace(' ', '_')}_{timestamp}.{format_type}"
        output_path = self.results_dir / filename
        
        if format_type == 'json':
            export_data = {
                'job': asdict(job),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
        
        elif format_type == 'csv':
            output = StringIO()
            writer = csv.writer(output)
            
            # Write job info
            writer.writerow(['Batch Job Results'])
            writer.writerow(['Job Name', job.name])
            writer.writerow(['Job Type', job.batch_type.value])
            writer.writerow(['Status', job.status.value])
            writer.writerow(['Total Items', job.total_items])
            writer.writerow(['Completed Items', job.completed_items])
            writer.writerow(['Failed Items', job.failed_items])
            writer.writerow([])
            
            # Write items
            writer.writerow(['Item ID', 'Status', 'Input', 'Output', 'Error'])
            
            for item in job.items:
                writer.writerow([
                    item.id,
                    item.status,
                    json.dumps(item.input_data)[:100],  # Truncate long data
                    json.dumps(item.output_data)[:100] if item.output_data else '',
                    item.error or ''
                ])
            
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                f.write(output.getvalue())
        
        return output_path
    
    def register_progress_callback(self, job_id: str, callback: Callable):
        """Register a progress callback for a batch job."""
        if job_id not in self.progress_callbacks:
            self.progress_callbacks[job_id] = []
        self.progress_callbacks[job_id].append(callback)
    
    def get_batch_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get batch processing statistics."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            # Job statistics
            job_stats = conn.execute("""
                SELECT COUNT(*) as total_jobs,
                       COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_jobs,
                       COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_jobs,
                       SUM(total_items) as total_items,
                       SUM(completed_items) as completed_items,
                       SUM(failed_items) as failed_items
                FROM batch_jobs
                WHERE created_at >= ? AND created_at <= ?
            """, (start_date.isoformat(), end_date.isoformat())).fetchone()
            
            # Type breakdown
            type_stats = conn.execute("""
                SELECT batch_type, COUNT(*) as count,
                       AVG(completed_items * 1.0 / total_items) as avg_success_rate
                FROM batch_jobs
                WHERE created_at >= ? AND created_at <= ?
                GROUP BY batch_type
            """, (start_date.isoformat(), end_date.isoformat())).fetchall()
            
            return {
                'period_days': days,
                'total_jobs': job_stats[0] or 0,
                'completed_jobs': job_stats[1] or 0,
                'failed_jobs': job_stats[2] or 0,
                'success_rate': (job_stats[1] / job_stats[0]) if job_stats[0] else 0,
                'total_items': job_stats[3] or 0,
                'completed_items': job_stats[4] or 0,
                'failed_items': job_stats[5] or 0,
                'item_success_rate': (job_stats[4] / job_stats[3]) if job_stats[3] else 0,
                'type_breakdown': [{
                    'type': row[0],
                    'count': row[1],
                    'avg_success_rate': row[2] or 0
                } for row in type_stats]
            }
    
    def _process_batch_job(self, job_id: str):
        """Process a batch job in a separate thread."""
        try:
            job = self.get_batch_job(job_id)
            if not job:
                return
            
            # Process items based on job type
            if job.batch_type == BatchType.IMAGE_SEARCH:
                self._process_image_search_batch(job)
            elif job.batch_type == BatchType.VOCABULARY_EXTRACTION:
                self._process_vocabulary_extraction_batch(job)
            elif job.batch_type == BatchType.IMAGE_DESCRIPTION:
                self._process_image_description_batch(job)
            elif job.batch_type == BatchType.TRANSLATION:
                self._process_translation_batch(job)
            else:
                job.status = BatchStatus.FAILED
                job.error_log.append(f"Unknown batch type: {job.batch_type}")
            
            # Finalize job
            if job.status == BatchStatus.RUNNING:
                job.status = BatchStatus.COMPLETED
            
            job.completed_at = datetime.now().isoformat()
            job.progress = 100
            
            # Calculate results summary
            job.results_summary = self._calculate_results_summary(job)
            
            self._save_job_to_db(job)
            
            # Cleanup
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
            
            # Final callback
            self._trigger_progress_callbacks(job_id, job)
            
        except Exception as e:
            # Handle job failure
            job = self.get_batch_job(job_id)
            if job:
                job.status = BatchStatus.FAILED
                job.completed_at = datetime.now().isoformat()
                job.error_log.append(f"Job failed: {str(e)}")
                self._save_job_to_db(job)
    
    def _process_image_search_batch(self, job: BatchJob):
        """Process image search batch items."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for item in job.items:
                if job.status != BatchStatus.RUNNING:
                    break
                
                future = executor.submit(self._process_image_search_item, item)
                futures.append((item, future))
            
            # Process results
            for item, future in futures:
                if job.status != BatchStatus.RUNNING:
                    break
                
                try:
                    result = future.result(timeout=60)
                    item.output_data = result
                    item.status = "completed"
                    job.completed_items += 1
                    
                except Exception as e:
                    item.error = str(e)
                    item.status = "failed"
                    job.failed_items += 1
                    job.error_log.append(f"Item {item.id}: {str(e)}")
                
                finally:
                    item.end_time = datetime.now().isoformat()
                    
                    # Update progress
                    job.progress = int((job.completed_items + job.failed_items) / job.total_items * 100)
                    self._save_job_to_db(job)
                    self._trigger_progress_callbacks(job.id, job)
                    
                    # Rate limiting
                    time.sleep(self.request_delay)
    
    def _process_image_search_item(self, item: BatchItem) -> Dict[str, Any]:
        """Process a single image search item."""
        item.start_time = datetime.now().isoformat()
        
        query = item.input_data['query']
        count = item.input_data.get('count', 10)
        filters = item.input_data.get('filters', {})
        
        # Build Unsplash API request
        headers = {"Authorization": f"Client-ID {self.unsplash_api_key}"}
        params = {
            'query': query,
            'per_page': min(count, 30),  # Unsplash max
            'orientation': filters.get('orientation'),
            'color': filters.get('color')
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(
            "https://api.unsplash.com/search/photos",
            headers=headers,
            params=params,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        images = []
        
        for photo in data.get('results', []):
            images.append({
                'id': photo['id'],
                'url': photo['urls']['regular'],
                'description': photo.get('description', ''),
                'alt_description': photo.get('alt_description', ''),
                'photographer': photo['user']['name'],
                'tags': [tag['title'] for tag in photo.get('tags', [])],
                'width': photo['width'],
                'height': photo['height']
            })
        
        return {
            'query': query,
            'total_results': data.get('total', 0),
            'images': images[:count]  # Limit to requested count
        }
    
    def _process_vocabulary_extraction_batch(self, job: BatchJob):
        """Process vocabulary extraction batch items."""
        # Similar pattern to image search but for vocabulary extraction
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for item in job.items:
                if job.status != BatchStatus.RUNNING:
                    break
                
                future = executor.submit(self._process_vocabulary_extraction_item, item)
                futures.append((item, future))
            
            # Process results (similar to image search)
            for item, future in futures:
                if job.status != BatchStatus.RUNNING:
                    break
                
                try:
                    result = future.result(timeout=120)  # Longer timeout for AI processing
                    item.output_data = result
                    item.status = "completed"
                    job.completed_items += 1
                    
                except Exception as e:
                    item.error = str(e)
                    item.status = "failed"
                    job.failed_items += 1
                    job.error_log.append(f"Item {item.id}: {str(e)}")
                
                finally:
                    item.end_time = datetime.now().isoformat()
                    
                    job.progress = int((job.completed_items + job.failed_items) / job.total_items * 100)
                    self._save_job_to_db(job)
                    self._trigger_progress_callbacks(job.id, job)
                    
                    time.sleep(self.request_delay)
    
    def _process_vocabulary_extraction_item(self, item: BatchItem) -> Dict[str, Any]:
        """Process a single vocabulary extraction item."""
        item.start_time = datetime.now().isoformat()
        
        image_url = item.input_data['image_url']
        language = item.input_data.get('language', 'es')
        
        # Generate description first
        description_prompt = "Describe this image in Spanish, focusing on objects, actions, and scene details."
        
        description_response = self.openai_client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": description_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=400
        )
        
        description = description_response.choices[0].message.content
        
        # Extract vocabulary from description
        vocab_prompt = f"""
From this Spanish text, extract useful vocabulary for language learning.
Return JSON with categories: "Sustantivos", "Verbos", "Adjetivos", "Adverbios", "Frases clave"

Text: {description}
"""
        
        vocab_response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": vocab_prompt}],
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        vocabulary = json.loads(vocab_response.choices[0].message.content)
        
        return {
            'image_url': image_url,
            'description': description,
            'vocabulary': vocabulary,
            'language': language
        }
    
    def _process_image_description_batch(self, job: BatchJob):
        """Process image description batch items."""
        # Similar pattern to vocabulary extraction
        pass
    
    def _process_translation_batch(self, job: BatchJob):
        """Process translation batch items."""
        # Similar pattern for translations
        pass
    
    def _save_job_to_db(self, job: BatchJob):
        """Save job and its items to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save job
            conn.execute("""
                INSERT OR REPLACE INTO batch_jobs 
                (id, name, batch_type, status, priority, created_at, started_at,
                 completed_at, progress, total_items, completed_items, failed_items,
                 settings, results_summary, error_log)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id, job.name, job.batch_type.value, job.status.value,
                job.priority.value, job.created_at, job.started_at, job.completed_at,
                job.progress, job.total_items, job.completed_items, job.failed_items,
                json.dumps(job.settings), json.dumps(job.results_summary),
                json.dumps(job.error_log)
            ))
            
            # Save items
            for item in job.items:
                conn.execute("""
                    INSERT OR REPLACE INTO batch_items 
                    (id, job_id, input_data, output_data, status, error, 
                     start_time, end_time, retry_count, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.id, job.id, json.dumps(item.input_data),
                    json.dumps(item.output_data) if item.output_data else None,
                    item.status, item.error, item.start_time, item.end_time,
                    item.retry_count, json.dumps(item.metadata)
                ))
    
    def _calculate_results_summary(self, job: BatchJob) -> Dict[str, Any]:
        """Calculate summary statistics for completed job."""
        total_items = len(job.items)
        completed_items = sum(1 for item in job.items if item.status == "completed")
        failed_items = sum(1 for item in job.items if item.status == "failed")
        
        # Calculate processing times
        processing_times = []
        for item in job.items:
            if item.start_time and item.end_time:
                start = datetime.fromisoformat(item.start_time)
                end = datetime.fromisoformat(item.end_time)
                processing_times.append((end - start).total_seconds())
        
        return {
            'total_items': total_items,
            'completed_items': completed_items,
            'failed_items': failed_items,
            'success_rate': completed_items / total_items if total_items > 0 else 0,
            'avg_processing_time_seconds': sum(processing_times) / len(processing_times) if processing_times else 0,
            'total_processing_time_seconds': sum(processing_times),
            'items_per_minute': len(processing_times) / (sum(processing_times) / 60) if processing_times else 0
        }
    
    def _trigger_progress_callbacks(self, job_id: str, job: BatchJob):
        """Trigger progress callbacks for a job."""
        if job_id in self.progress_callbacks:
            for callback in self.progress_callbacks[job_id]:
                try:
                    callback(job)
                except Exception as e:
                    print(f"Progress callback error: {e}")