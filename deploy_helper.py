
import subprocess
import os

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return f"CMD: {cmd}\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}\n"
    except Exception as e:
        return f"CMD: {cmd}\nERROR: {e}\n"

log = ""
log += run_command("git add .")
log += run_command('git commit -m "Prepare for deployment: Update requirements and gitignore"')
log += run_command("git push origin main")

with open("deploy_log.txt", "w", encoding="utf-8") as f:
    f.write(log)
