
import subprocess

def run_debug():
    cmd1 = ["git", "remote", "get-url", "origin"]
    cmd2 = ["git", "ls-tree", "HEAD", "render.yaml"]
    
    print("--- Remote ---")
    r1 = subprocess.run(cmd1, capture_output=True, text=True)
    print(r1.stdout)
    
    print("--- ls-tree ---")
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    print(r2.stdout)
    print(r2.stderr)

run_debug()
