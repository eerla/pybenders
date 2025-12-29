import argparse
from datetime import datetime
from pybender.render.reel_generator import ReelGenerator
import traceback

def main():
    parser = argparse.ArgumentParser(description="Generate daily Python reels")
    parser.add_argument(
        "--questions",
        type=int,
        default=2,
        help="Number of questions to generate per run"
    )
    parser.add_argument(
        "--subject",
        type=str,
        default="python",
        choices=[
            "python", "sql", "regex", "system_design", "linux", 
            "docker_k8s", "javascript", "rust", "golang"],
        help="Subject for the reels (default: python)"
    )

    args = parser.parse_args()

    generator = ReelGenerator()
    generator.generate(questions_per_run=args.questions, subject=args.subject)
    
def run_all_subjects():
    """Execute main with questions=1 for each subject"""
    start_time = datetime.now()
    print("Running reel generation for all subjects with 1 question each.")
    subjects = [ 
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
    # subjects = ["rust"]
    runtimes = {
        subject: None for subject in subjects
    }
    
    failed_subjects = []

    for subject in subjects:
        subject_start_time = datetime.now()
        print(f"\n{'='*50}")
        print(f"Generating reel for: {subject}")
        print(f"{'='*50}")
        
        try:
            generator = ReelGenerator()
            generator.generate(questions_per_run=1, subject=subject)
            subject_elapsed_time = (datetime.now() - subject_start_time).total_seconds() / 60
            runtimes[subject] = subject_elapsed_time
            print(f"✅ {subject} completed in {subject_elapsed_time:.2f} minutes")
        except Exception as e:
            print(f"❌ {subject} failed: {type(e).__name__}: {e}")
            print(traceback.format_exc())
            failed_subjects.append((subject, str(e)))
            runtimes[subject] = "FAILED"
    
    # Summary
    elapsed_time = (datetime.now() - start_time).total_seconds() / 60
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Total time taken: {elapsed_time:.2f} minutes")
    print(f"\nSuccessful: {len([r for r in runtimes.values() if r != 'FAILED'])}/{len(subjects)}")
    print(f"Failed: {len(failed_subjects)}/{len(subjects)}")
    
    if failed_subjects:
        print("\n❌ Failed subjects:")
        for subj, error in failed_subjects:
            print(f"  - {subj}: {error}")
    
    print("\nIndividual subject runtimes:")
    for subj, runtime in runtimes.items():
        if runtime == "FAILED":
            print(f"  {subj}: FAILED")
        else:
            print(f"  {subj}: {runtime:.2f} minutes")
            
if __name__ == "__main__":
    run_all_subjects()
