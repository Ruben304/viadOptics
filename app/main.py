import subprocess
import threading
import time


# Function to start a script
def start_script(script_name, log_file):
    return subprocess.Popen(
        ["python3", script_name],
        stdout=open(log_file, 'w'),
        stderr=subprocess.STDOUT
    )


# Function to monitor processes
def monitor_processes(processes):
    try:
        while True:
            all_exited = True
            for proc in processes:
                if proc.poll() is None:  # Process is still running
                    all_exited = False
                else:
                    print(f"Process {proc.args} has exited with code {proc.returncode}")
                    if proc.returncode != 0:
                        print(f"Error: Process {proc.args} crashed. Check {proc.stdout.name} for details.")
            if all_exited:
                print("All processes have finished.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")


# Main function to setup and monitor subprocesses
# add the logging writing to the txt file
def main():
    scripts = [
        ("camera.py", "camera_log.txt"),
        ("detections.py", "detections_log.txt"),
        ("haptic.py", "haptic_log.txt"),
        ("tts.py", "tts_log.txt")
    ]

    processes = [start_script(script, log) for script, log in scripts]

    # Start monitoring in a background thread
    monitor_thread = threading.Thread(target=monitor_processes, args=(processes,))
    monitor_thread.start()

    monitor_thread.join()  # Wait for the monitoring thread to finish


if __name__ == "__main__":
    main()
