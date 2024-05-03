import subprocess
import threading
import time
import sys
import os

# Function to start a script
def start_script(script_name):
    python_executable = sys.executable
    script_path = script_name
    env = os.environ.copy()
    process = subprocess.Popen(
        [python_executable, script_path],
        stdout=subprocess.DEVNULL,  # Suppress stdout
        stderr=subprocess.DEVNULL,  # Suppress stderr
        env=env
    )
    return process

# Function to monitor processes
def monitor_processes(processes):
    while True:
        all_exited = True
        for proc in processes:
            if proc.poll() is None:
                all_exited = False
            else:
                print(f"Process {proc.args} has exited with code {proc.returncode}")
                if proc.returncode != 0:
                    raise Exception(f"Error: Process {proc.args} crashed with exit code {proc.returncode}.")
        if all_exited:
            print("All processes have finished.")
            break
        time.sleep(1)

# Main function to setup and monitor subprocesses
def main():
    try:
        scripts = ["camera.py", "detections.py", "haptic.py", "tts.py"]
        processes = [start_script(script) for script in scripts]
        monitor_processes(processes)
    except Exception as e:
        print(e)
        sys.exit(1)  # Exit with error code

if __name__ == "__main__":
    main()
