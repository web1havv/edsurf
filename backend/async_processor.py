"""
Async Video Processing System for Render.com
Handles long-running video generation tasks with proper timeout management
"""

import asyncio
import threading
import uuid
import time
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import json

logger = logging.getLogger(__name__)

@dataclass
class ProcessingJob:
    job_id: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = 0  # 0-100
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    task_type: str = "case_study_video"  # 'case_study_video', 'article_reel', etc.
    parameters: Optional[Dict[str, Any]] = None

class AsyncVideoProcessor:
    """
    Handles async video processing with job tracking
    Designed to work within Render's timeout constraints
    """
    
    def __init__(self):
        self.jobs: Dict[str, ProcessingJob] = {}
        self.processing_threads: Dict[str, threading.Thread] = {}
        self.max_concurrent_jobs = 2  # Limit for free tier
        self.job_timeout = 300  # 5 minutes max per job
        
    def create_job(self, task_type: str, parameters: Dict[str, Any]) -> str:
        """Create a new processing job"""
        job_id = str(uuid.uuid4())
        job = ProcessingJob(
            job_id=job_id,
            status='pending',
            created_at=datetime.now(),
            task_type=task_type,
            parameters=parameters
        )
        
        self.jobs[job_id] = job
        logger.info(f"📝 Created job {job_id} for {task_type}")
        
        # Start processing in background thread
        self._start_processing(job_id)
        
        return job_id
    
    def _start_processing(self, job_id: str):
        """Start processing job in background thread"""
        if len(self.processing_threads) >= self.max_concurrent_jobs:
            logger.warning(f"⚠️ Max concurrent jobs reached, queuing job {job_id}")
            return
        
        def process_job():
            try:
                job = self.jobs[job_id]
                job.status = 'processing'
                job.started_at = datetime.now()
                job.progress = 10
                
                logger.info(f"🚀 Starting processing for job {job_id}")
                
                # Execute the appropriate processing function
                if job.task_type == 'case_study_video':
                    result = self._process_case_study_video(job)
                elif job.task_type == 'article_reel':
                    result = self._process_article_reel(job)
                else:
                    raise ValueError(f"Unknown task type: {job.task_type}")
                
                # Mark as completed
                job.status = 'completed'
                job.completed_at = datetime.now()
                job.progress = 100
                job.result = result
                
                logger.info(f"✅ Job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"❌ Job {job_id} failed: {str(e)}")
                job = self.jobs[job_id]
                job.status = 'failed'
                job.completed_at = datetime.now()
                job.error = str(e)
                
            finally:
                # Clean up thread reference
                if job_id in self.processing_threads:
                    del self.processing_threads[job_id]
        
        # Start the thread
        thread = threading.Thread(target=process_job, daemon=True)
        self.processing_threads[job_id] = thread
        thread.start()
    
    def _process_case_study_video(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process case study video generation"""
        try:
            params = job.parameters
            job.progress = 20
            
            # Step 1: Extract/process content
            logger.info(f"📚 Step 1: Processing content for job {job.job_id}")
            if params.get('file_path'):
                from case_study_processor import process_case_study_file
                case_study_data = process_case_study_file(params['file_path'], params.get('speaker_pair'))
            else:
                from case_study_processor import process_case_study_text
                case_study_data = process_case_study_text(params['text'], params.get('speaker_pair'))
            
            job.progress = 40
            
            # Step 2: Generate audio
            logger.info(f"🎵 Step 2: Generating audio for job {job.job_id}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            from conversational_tts import generate_conversational_voiceover
            audio_path, timing_data = loop.run_until_complete(
                loop.run_in_executor(None, generate_conversational_voiceover, 
                                   case_study_data["script"], None, params.get('speaker_pair'))
            )
            loop.close()
            
            job.progress = 70
            
            # Step 3: Generate video
            logger.info(f"🎬 Step 3: Generating video for job {job.job_id}")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            from opencv_video_generator import create_background_video_with_speaker_overlays
            video_path = loop.run_until_complete(
                loop.run_in_executor(None, create_background_video_with_speaker_overlays,
                                   case_study_data["script"], audio_path, None, None, 
                                   params.get('speaker_pair'), timing_data)
            )
            loop.close()
            
            job.progress = 90
            
            # Step 4: Save files and prepare response
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Ensure outputs directory exists
            os.makedirs("outputs", exist_ok=True)
            
            # Generate filenames
            audio_filename = f"case_study_audio_{timestamp}_{job.job_id[:8]}.wav"
            video_filename = f"case_study_video_{timestamp}_{job.job_id[:8]}.mp4"
            
            # Copy files to outputs directory
            import shutil
            audio_output_path = os.path.join("outputs", audio_filename)
            video_output_path = os.path.join("outputs", video_filename)
            
            shutil.copy2(audio_path, audio_output_path)
            shutil.copy2(video_path, video_output_path)
            
            # Clean up temporary files
            try:
                os.remove(audio_path)
                os.remove(video_path)
            except:
                pass
            
            job.progress = 100
            
            return {
                "content": case_study_data["content"],
                "summary": case_study_data["summary"],
                "script": case_study_data["script"],
                "speaker_pair": params.get('speaker_pair'),
                "processed_at": case_study_data["processed_at"],
                "audio_url": f"/download/{audio_filename}",
                "video_url": f"/download/{video_filename}",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Case study video processing failed: {str(e)}")
            raise
    
    def _process_article_reel(self, job: ProcessingJob) -> Dict[str, Any]:
        """Process article reel generation"""
        # Similar implementation for article reels
        # This would handle the article reel processing
        pass
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and result"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        
        # Convert datetime objects to strings for JSON serialization
        result = asdict(job)
        for key, value in result.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif value is None:
                result[key] = None
        
        return result
    
    def cleanup_old_jobs(self):
        """Clean up jobs older than 1 hour"""
        cutoff_time = datetime.now() - timedelta(hours=1)
        
        jobs_to_remove = []
        for job_id, job in self.jobs.items():
            if job.created_at < cutoff_time:
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            logger.info(f"🗑️ Cleaned up old job {job_id}")

# Global instance
async_processor = AsyncVideoProcessor()
