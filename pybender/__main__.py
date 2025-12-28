import argparse
from datetime import datetime
from pybender.render.reel_generator import ReelGenerator

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
        "python", "sql", "regex", "system_design", "linux"
        ,"docker_k8s", "javascript", "rust", "golang"
    ]
    
    runtimes = {
        subject: None for subject in subjects
    }

    try:
        for subject in subjects[0:1]:
            subject_start_time = datetime.now()
            print(f"\nGenerating reel for: {subject}")
            generator = ReelGenerator()
            generator.generate(questions_per_run=1, subject=subject)
            subject_elapsed_time = (datetime.now() - subject_start_time).total_seconds() / 60
            runtimes[subject] = subject_elapsed_time
            print(f"Time taken for {subject}: {subject_elapsed_time:.2f} minutes")

        print("\nAll subjects processed.")
    except OSError as e:
        if "WinError 6" in str(e):
            print("\nAll subjects processed (ignoring subprocess cleanup warning).")
        else:
            raise
    finally:
        elapsed_time = (datetime.now() - start_time).total_seconds() / 60
        print(f"Total time taken: {elapsed_time:.2f} minutes")
        print("Individual subject runtimes:", runtimes)

if __name__ == "__main__":
    main()
    # run_all_subjects()
    # Uncomment below to run all subjects:
    # run_all_subjects()



# import sys
# print("RUNNING __main__.py")
# print("sys.path:", sys.path)
# python -m pybender --questions 1 --subject python