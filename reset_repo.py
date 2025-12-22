
import os
import shutil
import subprocess
import time

def run_cmd(cmd):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"FAILED: {cmd}")
        print(res.stderr)
        return False
    print("SUCCESS")
    return True

def cleanup():
    # Remove files
    for root, dirs, files in os.walk("."):
        for f in files:
            if f.startswith("debug_") or f.startswith("diagnose_") or f.endswith(".log") or f.endswith(".txt") or f.endswith(".info"):
                if f == "requirements.txt" or f == "CMakeLists.txt": continue # Keep important ones
                try:
                    os.remove(os.path.join(root, f))
                    print(f"Deleted {f}")
                except Exception as e:
                    print(f"Could not delete {f}: {e}")
    
    # Remove .git
    if os.path.exists(".git"):
        try:
            # Grant permission to delete if read-only
            def on_rm_error(func, path, exc_info):
                import stat
                os.chmod(path, stat.S_IWRITE)
                os.unlink(path)
            
            shutil.rmtree(".git", onerror=on_rm_error)
            print("Deleted .git folder")
        except Exception as e:
            print(f"Failed to delete .git: {e}")
            # Try shell fallback
            subprocess.run("rmdir /s /q .git", shell=True)

def main():
    cleanup()
    
    # Git sequence
    cmds = [
        "git init",
        "git branch -M main",
        "git add .",
        'git commit -m "Initial commit"',
        "git remote add origin https://github.com/Shyam2119/project-management-app.git",
        "git push -u origin main --force"
    ]
    
    for cmd in cmds:
        if not run_cmd(cmd):
            break

if __name__ == "__main__":
    main()
