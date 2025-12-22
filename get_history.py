
import subprocess

def debug_log():
    result = subprocess.run("git log -n 10 --oneline", shell=True, capture_output=True, text=True)
    print(result.stdout)
    with open("git_history.txt", "w", encoding="utf-8") as f:
        f.write(result.stdout)

debug_log()
