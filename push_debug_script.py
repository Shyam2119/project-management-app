
import subprocess
import sys

def run():
    print("Checking git status...")
    r1 = subprocess.run(["git", "status"], capture_output=True, text=True)
    print(r1.stdout)
    print(r1.stderr)

    print("Checking render.yaml...")
    r2 = subprocess.run(["git", "ls-files", "render.yaml"], capture_output=True, text=True)
    print(f"File in index: {r2.stdout.strip()}")

    print("Pushing...")
    r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    print("STDOUT:", r3.stdout)
    print("STDERR:", r3.stderr)

if __name__ == "__main__":
    run()
