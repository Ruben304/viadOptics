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
    log_file = open(f"{script_name}.log", "w")  # Open log file for writing
    process = subprocess.Popen(
        [python_executable, script_path],
        stdout=log_file,  # Redirect stdout to log file
        stderr=log_file,  # Redirect stderr to log file
        env=env
    )
    return process

# Function to monitor processes
def monitor_processes(processes):
    try:
        while True:
            all_exited = True
            for proc in processes:
                if proc.poll() is None:
                    all_exited = False
                else:
                    print(f"Process {proc.args} has exited with code {proc.returncode}")
                    if proc.returncode != 0:
                        print(f"Error: Process {proc.args} crashed.")
            if all_exited:
                print("All processes have finished.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

# Main function to setup and monitor subprocesses
def main():

    scripts = [
        "camera.py",
        "detections.py",
        "haptic.py",
        "tts.py"
    ]


    processes = [start_script(script) for script in scripts]

    # Start monitoring in a background thread
    monitor_thread = threading.Thread(target=monitor_processes, args=(processes,))
    monitor_thread.start()

    monitor_thread.join()  # Wait for the monitoring thread to finish

if __name__ == "__main__":
    main()
