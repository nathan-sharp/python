import time
import sys
import multiprocessing
import threading
import os
import queue
from decimal import Decimal, getcontext

# --- Cross-Platform Keyboard Listener ---
try:
    import msvcrt  # Windows
    def get_key():
        return msvcrt.getch().decode('utf-8', errors='ignore')
except ImportError:
    import termios
    import tty
    def get_key():
        old_settings = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        return key

def key_listener(stop_event):
    """Background thread that listens for an exit key without blocking the main loop."""
    while not stop_event.is_set():
        key = get_key().lower()
        if key == 'x' or key == '\x1b':  # '\x1b' is the Escape key
            stop_event.set()
            break

def calculate_pi_worker(stop_event, final_queue, is_primary, core_id, ops_array, shared_digits):
    """Worker process: highly optimized inner loop and lock-free metric updates."""
    getcontext().prec = 100000  
    getcontext().Emax = 999999
    
    K = 6
    M = 1
    L = 13591409
    X = 1
    S = Decimal(13591409)
    k = 1
    
    # Pre-allocate large constants OUTSIDE the loop to save CPU cycles
    C_ADD = 545140134
    C_MULT = -262537412640768000
    
    operations = 0
    start_time = time.time()
    last_snapshot_time = start_time
    
    while not stop_event.is_set():
        M = (K**3 - 16*K) * M // (k**3)
        L += C_ADD
        X *= C_MULT
        S += Decimal(M * L) / Decimal(X)
        
        K += 12
        k += 1
        operations += 15 
        
        if k % 5 == 0:
            elapsed = time.time() - start_time
            ops_array[core_id] = operations / elapsed if elapsed > 0 else 0
            
            if is_primary:
                shared_digits.value = k * 14
                # Send a periodic snapshot so the main process can autosave safely.
                if elapsed - (last_snapshot_time - start_time) >= 10:
                    C = 426880 * Decimal(10005).sqrt()
                    pi_snapshot = C / S
                    final_queue.put(("snapshot", str(pi_snapshot)[:(k*14)]))
                    last_snapshot_time = time.time()
            
    if is_primary:
        C = 426880 * Decimal(10005).sqrt()
        pi = C / S
        final_queue.put(("final", str(pi)[:(k*14)]))

def main():
    print("--- Pi-Mark CPU Stress Test & Calculator (Optimized) ---")
    
    # 1. Ask user for duration, defaulting to infinite if blank
    duration_input = input("Enter duration in seconds (leave blank to run until stopped): ").strip()
    
    if not duration_input:
        duration = float('inf')
        print("Mode: Infinite (Press 'x', 'Esc', or 'Ctrl+C' to stop)")
    else:
        try:
            duration = float(duration_input)
            print(f"Mode: Timed ({duration} seconds. Press 'x', 'Esc', or 'Ctrl+C' to stop early)")
        except ValueError:
            print("Invalid input. Defaulting to Infinite mode.")
            duration = float('inf')
            
    save_output = input("Output the final calculated Pi to a .txt file? (y/n): ").strip().lower() == 'y'
    
    cores = os.cpu_count() or 1
    print(f"\nStarting benchmark on {cores} CPU cores...")
    
    stop_event = multiprocessing.Event()
    final_queue = multiprocessing.Queue()
    
    ops_array = multiprocessing.Array('d', cores)
    shared_digits = multiprocessing.Value('i', 0) 
    
    processes = []
    
    # Start the background keyboard listener AFTER inputs are collected
    listener = threading.Thread(target=key_listener, args=(stop_event,), daemon=True)
    listener.start()
    
    for i in range(cores):
        is_primary = (i == 0)
        p = multiprocessing.Process(
            target=calculate_pi_worker, 
            args=(stop_event, final_queue, is_primary, i, ops_array, shared_digits)
        )
        p.start()
        processes.append(p)
        
    start_time = time.time()
    final_pi = None
    latest_pi_snapshot = None
    autosave_filename = "pi_output.txt"
    next_autosave_time = 10.0
    autosave_file_created = False
    
    try:
        while time.time() - start_time < duration:
            # Break early if the background listener caught an 'x' or 'Esc'
            if stop_event.is_set():
                print("\n\nExit key pressed.")
                break
                
            current_digits = shared_digits.value
            total_ops_per_sec = sum(ops_array)
            elapsed = time.time() - start_time

            # Drain any pending snapshots/final value from the worker queue.
            while True:
                try:
                    item = final_queue.get_nowait()
                except queue.Empty:
                    break

                if isinstance(item, tuple) and len(item) == 2:
                    msg_type, payload = item
                    if msg_type in ("snapshot", "final"):
                        latest_pi_snapshot = payload
                        if msg_type == "final":
                            final_pi = payload
                elif isinstance(item, str):
                    # Backward compatibility for older message format.
                    latest_pi_snapshot = item
                    final_pi = item

            if save_output and elapsed >= next_autosave_time:
                if not autosave_file_created:
                    with open(autosave_filename, "w") as f:
                        f.write(latest_pi_snapshot or "")
                    autosave_file_created = True
                    print(f"\nAutosave started: '{autosave_filename}' created at {elapsed:.1f}s.")
                elif latest_pi_snapshot:
                    with open(autosave_filename, "w") as f:
                        f.write(latest_pi_snapshot)
                    print(f"\nAutosave updated at {elapsed:.1f}s.")
                next_autosave_time += 10.0
            
            sys.stdout.write(f"\rDigits Calculated: ~{current_digits} | Total Ops/sec ({cores} Cores): {total_ops_per_sec:.2f} | Time Elapsed: {elapsed:.2f}s ")
            sys.stdout.flush()
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        # Catch Ctrl+C explicitly
        print("\n\nCtrl+C detected.")
        
    stop_event.set()
    
    # Final display update
    total_ops_per_sec = sum(ops_array)
    sys.stdout.write(f"\rDigits Calculated: ~{shared_digits.value} | Total Ops/sec ({cores} Cores): {total_ops_per_sec:.2f} | Time Elapsed: {(time.time() - start_time):.2f}s \n")
    print("\nBenchmark Complete! Finalizing Pi calculation (this may take a moment)...")
    
    while True:
        try:
            item = final_queue.get(timeout=3)
            if isinstance(item, tuple) and len(item) == 2:
                msg_type, payload = item
                if msg_type in ("snapshot", "final"):
                    latest_pi_snapshot = payload
                    if msg_type == "final":
                        final_pi = payload
                        break
            elif isinstance(item, str):
                final_pi = item
                latest_pi_snapshot = item
                break
        except Exception:
            break
            
    for p in processes:
        p.join()
        
    if final_pi:
        if save_output:
            with open(autosave_filename, "w") as f:
                f.write(final_pi)
            print(f"\nSuccess! Calculated Pi has been saved to '{autosave_filename}'.")
            print(f"Total precise digits calculated: {len(final_pi) - 2}")
        else:
            print("\nPi calculation finished successfully (output not saved to file).")
    else:
        print("\nFailed to retrieve final Pi calculation.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
