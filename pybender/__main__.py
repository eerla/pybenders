import argparse
import logging
from datetime import datetime
from pathlib import Path
from pybender.render.reel_generator import ReelGenerator
from pybender.publishers.instagram_publisher import upload_from_metadata
from pybender.config.logging_config import setup_logging
import os
import json
import random

CODE_SUBJECTS = [ 
        "golang", 
        "javascript", 
        "python", 
        "regex", 
        "rust", 
    ]

IQLABS_SUBJECTS = [
    "mind_benders",# add any iqlabs specific subjects here
    "finance",
    "psychology",
]

BACKEND_SUBJECTS = [
    "docker_k8s", 
    "sql", 
    "system_design",
    "linux"
    ]

logger = logging.getLogger(__name__) 

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Generate daily Python reels")
    parser.add_argument(
        "--questions",
        type=int,
        default=1,
        help="Number of questions to generate per run"
    )
    parser.add_argument(
        "--subject",
        type=str,
        default="",
        choices=[ 
            "docker_k8s", 
            "golang", 
            "javascript", 
            "linux",
            "mind_benders",
            "python", 
            "regex", 
            "rust", 
            "sql", 
            "system_design",
            "finance",
            "psychology",
        ],
        help="Subject for the reels (default: run all subjects)"
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload generated reels to Instagram"
    )

    args = parser.parse_args()
    qs = min(1 if not args.questions else args.questions, 4)  # Cap at 4 questions per run
    subject = args.subject
    should_upload = args.upload

    if not subject:
        # run_all_subjects(upload=should_upload)
        # pick one for coding vs iqlabs
        subjects = ["python", random.choice(IQLABS_SUBJECTS), random.choice(BACKEND_SUBJECTS)]
    for subj in subjects:
        logger.info("=" * 60)
        logger.info(f"🎬 Generating reels for subject: {subj} with {qs} questions")
        logger.info("=" * 60)
        generator = ReelGenerator()
        metadata_path = generator.generate(questions_per_run=qs, subject=subj)
        logger.info(f"Metadata generated at: {metadata_path}")
        
        # Upload if requested
        if should_upload and metadata_path:
            logger.info("=" * 60)
            logger.info(f"📤 Starting Instagram upload for {subj}")
            logger.info("=" * 60)
            upload_instagram_reels(metadata_path)
    
    print("Reel generation process completed.")

    
def upload_instagram_reels(metadata_path: Path) -> dict:
    """
    Upload reels to Instagram from metadata file.
    
    Args:
        metadata_path: Path to metadata JSON file
        
    Returns:
        Upload result dictionary
    """
    metadata_file_path = Path(metadata_path).resolve()
    with open(metadata_file_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        sub = metadata.get('subject', '')
    
    if not sub:
        return {'success': False, 'error': 'Subject not found in metadata'}
    # Get credentials from environment variables (more secure)
    if sub in CODE_SUBJECTS:
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')  
        profile_username = os.getenv('INSTAGRAM_PROFILE_USERNAME')
    elif sub in IQLABS_SUBJECTS:
        username = os.getenv('IQLABS_INSTAGRAM_USERNAME')
        password = os.getenv('IQLABS_INSTAGRAM_PASSWORD')  
        profile_username = os.getenv('IQLABS_INSTAGRAM_PROFILE_USERNAME')
    elif sub in BACKEND_SUBJECTS:
        username = os.getenv('BACKEND_INSTAGRAM_USERNAME')
        password = os.getenv('BACKEND_INSTAGRAM_PASSWORD')
        profile_username = os.getenv('BACKEND_INSTAGRAM_PROFILE_USERNAME')
    else:
        return {'success': False, 'error': 'Unknown subject for credentials'}      

    if not username or not password:
        logger.error("❌ Instagram credentials not found in environment variables")
        logger.error("Set the appropriate INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables for the subject")
        return {'success': False, 'error': 'Missing credentials'}
    
    try:
        result = upload_from_metadata(
            metadata_file_path=metadata_path,
            username=username,
            password=password,
            profile_username=profile_username
        )
        
        if result['success']:
            logger.info(f"✅ Successfully uploaded {result['total_uploaded']} reels to Instagram")
            logger.info(f"   - Carousels: {result['carousel']['uploaded_count']} uploaded, {result['carousel']['failed_count']} failed")
            logger.info(f"   - Reels: {result['reel']['uploaded_count']} uploaded, {result['reel']['failed_count']} failed")
        else:
            logger.warning(f"⚠️  Upload completed with {result['total_failed']} failures")
            logger.warning(f"   - Carousels: {result['carousel']['failed_count']} failed")
            logger.warning(f"   - Reels: {result['reel']['failed_count']} failed")
            
        return result
        
    except Exception as e:
        logger.exception(f"❌ Instagram upload failed: {e}")
        return {'success': False, 'error': str(e)}

def run_all_subjects(upload: bool = False):
    """Execute main with questions=1 for each subject"""
    start_time = datetime.now()
    logger.info("Running reel generation for all subjects with 1 question each.")
    if upload:
        logger.info("📤 Instagram upload enabled")
    
    runtimes = {
        subject: None for subject in SUBJECTS
    }
    
    upload_results = {}
    failed_subjects = []

    for subject in SUBJECTS:
        subject_start_time = datetime.now()
        logger.info("=" * 50)
        logger.info(f"Generating reel for: {subject}")
        logger.info("=" * 50)
        
        try:
            generator = ReelGenerator()
            metadata_path = generator.generate(questions_per_run=1, subject=subject)
            subject_elapsed_time = (datetime.now() - subject_start_time).total_seconds() / 60
            runtimes[subject] = subject_elapsed_time
            logger.info(f"✅ {subject} generation completed in {subject_elapsed_time:.2f} minutes")
            
            # Upload if requested and generation succeeded
            if upload and metadata_path:
                logger.info("=" * 50)
                logger.info(f"📤 Uploading {subject} reels to Instagram")
                logger.info("=" * 50)
                upload_result = upload_instagram_reels(metadata_path)
                upload_results[subject] = upload_result
                
        except Exception as e:
            logger.exception(f"❌ {subject} failed: {type(e).__name__}: {e}")
            failed_subjects.append((subject, str(e)))
            runtimes[subject] = "FAILED"
    
    if failed_subjects:
        logger.warning("⚠️  Failed subjects: Trying again...")
        for subj, error in failed_subjects:
            logger.warning(f"  - {subj}: {error}")
            try:
                retry_start = datetime.now()
                generator = ReelGenerator()
                metadata_path = generator.generate(questions_per_run=1, subject=subj)
                retry_elapsed = (datetime.now() - retry_start).total_seconds() / 60
                runtimes[subj] = retry_elapsed
                logger.info(f"✅ {subj} retry succeeded in {retry_elapsed:.2f} minutes")
                
                if upload and metadata_path:
                    upload_result = upload_instagram_reels(metadata_path)
                    upload_results[subj] = upload_result
                    
            except Exception as e:
                logger.exception(f"❌ Retry failed for {subj}: {e}")
    
    # Summary
    elapsed_time = (datetime.now() - start_time).total_seconds() / 60
    logger.info("=" * 60)
    logger.info("📊 GENERATION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total time taken: {elapsed_time:.2f} minutes")
    logger.info(f"Successful: {len([r for r in runtimes.values() if r != 'FAILED'])}/{len(SUBJECTS)}")
    logger.info(f"Failed: {len(failed_subjects)}/{len(SUBJECTS)}")
    
    logger.info("Individual subject runtimes:")
    for subj, runtime in runtimes.items():
        if runtime == "FAILED":
            logger.warning(f"  {subj}: FAILED")
        else:
            logger.info(f"  {subj}: {runtime:.2f} minutes")
    
    # Upload summary
    if upload and upload_results:
        logger.info("=" * 60)
        logger.info("📤 INSTAGRAM UPLOAD SUMMARY")
        logger.info("=" * 60)
        
        total_uploaded = sum(r.get('uploaded_count', 0) for r in upload_results.values())
        total_failed = sum(r.get('failed_count', 0) for r in upload_results.values())
        
        logger.info(f"Total uploaded: {total_uploaded}")
        logger.info(f"Total failed: {total_failed}")
        
        logger.info("Per-subject upload results:")
        for subj, result in upload_results.items():
            status = "✅" if result.get('success') else "⚠️"
            logger.info(f"  {status} {subj}: {result.get('uploaded_count', 0)} uploaded, {result.get('failed_count', 0)} failed")
            
if __name__ == "__main__":
    main()