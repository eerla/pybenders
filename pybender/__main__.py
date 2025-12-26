import argparse
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
    print("Running reel generation for all subjects with 1 question each.")
    subjects = [
        "python", "sql", "regex", "system_design", "linux", 
        "docker_k8s", "javascript", "rust", "golang"
    ]
    for subject in subjects:
        print(f"\nGenerating reel for: {subject}")
        generator = ReelGenerator()
        generator.generate(questions_per_run=1, subject=subject)


if __name__ == "__main__":
    # main()
    run_all_subjects()
    # Uncomment below to run all subjects:
    # run_all_subjects()



# import sys
# print("RUNNING __main__.py")
# print("sys.path:", sys.path)
# python -m pybender --questions 1