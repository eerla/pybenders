import argparse
from datetime import datetime
from pathlib import Path
from pybender.render.reel_generator import ReelGenerator
from pybender.publishers.instagram_publisher import upload_reels_from_metadata
import traceback
import os

SUBJECTS = [ 
        "docker_k8s", 
        "golang", 
        "javascript", 
        "linux", 
        "python", 
        "regex", 
        "rust", 
        "sql", 
        "system_design"
    ]

def main():
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
            "python", 
            "regex", 
            "rust", 
            "sql", 
            "system_design"
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
        run_all_subjects(upload=should_upload)
    else:
        generator = ReelGenerator()
        metadata_path = generator.generate(questions_per_run=qs, subject=subject)
        print(f"metadata generated at: {metadata_path}")
        
        # Upload if requested
        if should_upload and metadata_path:
            print(f"\n{'='*60}")
            print(f"📤 Starting Instagram upload for {subject}")
            print(f"{'='*60}\n")
            upload_instagram_reels(metadata_path)
    
def upload_instagram_reels(metadata_path: Path) -> dict:
    """
    Upload reels to Instagram from metadata file.
    
    Args:
        metadata_path: Path to metadata JSON file
        
    Returns:
        Upload result dictionary
    """
    # Get credentials from environment variables (more secure)
    username = os.getenv('INSTAGRAM_USERNAME', 'e.reels2529@gmail.com')
    password = os.getenv('INSTAGRAM_PASSWORD', 'Eerlas_2529')
    
    if not username or not password:
        print("❌ Instagram credentials not found in environment variables")
        print("Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD environment variables")
        return {'success': False, 'error': 'Missing credentials'}
    
    try:
        result = upload_reels_from_metadata(
            metadata_file_path=metadata_path,
            username=username,
            password=password
        )
        
        if result['success']:
            print(f"\n✅ Successfully uploaded {result['uploaded_count']} reels to Instagram")
        else:
            print(f"\n⚠️  Upload completed with {result['failed_count']} failures")
            
        return result
        
    except Exception as e:
        print(f"❌ Instagram upload failed: {e}")
        print(traceback.format_exc())
        return {'success': False, 'error': str(e)}

def run_all_subjects(upload: bool = False):
    """Execute main with questions=1 for each subject"""
    start_time = datetime.now()
    print(f"Running reel generation for all subjects with 1 question each.")
    if upload:
        print("📤 Instagram upload enabled")
    
    runtimes = {
        subject: None for subject in SUBJECTS
    }
    
    upload_results = {}
    failed_subjects = []

    for subject in SUBJECTS:
        subject_start_time = datetime.now()
        print(f"\n{'='*50}")
        print(f"Generating reel for: {subject}")
        print(f"{'='*50}")
        
        try:
            generator = ReelGenerator()
            metadata_path = generator.generate(questions_per_run=1, subject=subject)
            subject_elapsed_time = (datetime.now() - subject_start_time).total_seconds() / 60
            runtimes[subject] = subject_elapsed_time
            print(f"✅ {subject} generation completed in {subject_elapsed_time:.2f} minutes")
            
            # Upload if requested and generation succeeded
            if upload and metadata_path:
                print(f"\n{'='*50}")
                print(f"📤 Uploading {subject} reels to Instagram")
                print(f"{'='*50}\n")
                upload_result = upload_instagram_reels(metadata_path)
                upload_results[subject] = upload_result
                
        except Exception as e:
            print(f"❌ {subject} failed: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            failed_subjects.append((subject, str(e)))
            runtimes[subject] = "FAILED"
    
    if failed_subjects:
        print("\n⚠️  Failed subjects: Trying again...")
        for subj, error in failed_subjects:
            print(f"  - {subj}: {error}")
            try:
                retry_start = datetime.now()
                generator = ReelGenerator()
                metadata_path = generator.generate(questions_per_run=1, subject=subj)
                retry_elapsed = (datetime.now() - retry_start).total_seconds() / 60
                runtimes[subj] = retry_elapsed
                print(f"✅ {subj} retry succeeded in {retry_elapsed:.2f} minutes")
                
                if upload and metadata_path:
                    upload_result = upload_instagram_reels(metadata_path)
                    upload_results[subj] = upload_result
                    
            except Exception as e:
                print(f"❌ Retry failed for {subj}: {e}")
    
    # Summary
    elapsed_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n{'='*60}")
    print("📊 GENERATION SUMMARY")
    print(f"{'='*60}")
    print(f"Total time taken: {elapsed_time:.2f} minutes")
    print(f"\nSuccessful: {len([r for r in runtimes.values() if r != 'FAILED'])}/{len(SUBJECTS)}")
    print(f"Failed: {len(failed_subjects)}/{len(SUBJECTS)}")
    
    print("\nIndividual subject runtimes:")
    for subj, runtime in runtimes.items():
        if runtime == "FAILED":
            print(f"  {subj}: FAILED")
        else:
            print(f"  {subj}: {runtime:.2f} minutes")
    
    # Upload summary
    if upload and upload_results:
        print(f"\n{'='*60}")
        print("📤 INSTAGRAM UPLOAD SUMMARY")
        print(f"{'='*60}")
        
        total_uploaded = sum(r.get('uploaded_count', 0) for r in upload_results.values())
        total_failed = sum(r.get('failed_count', 0) for r in upload_results.values())
        
        print(f"Total uploaded: {total_uploaded}")
        print(f"Total failed: {total_failed}")
        
        print("\nPer-subject upload results:")
        for subj, result in upload_results.items():
            status = "✅" if result.get('success') else "⚠️"
            print(f"  {status} {subj}: {result.get('uploaded_count', 0)} uploaded, {result.get('failed_count', 0)} failed")
            
if __name__ == "__main__":
    main()