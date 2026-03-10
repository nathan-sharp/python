import time
import sys
import multiprocessing
import os
from decimal import Decimal, getcontext

def calculate_pi_worker(stop_event, queue, is_primary, core_id, ops_array):
    """Worker process that calculates high-precision Pi and updates its own operation speed."""
    getcontext().prec = 100000  
    getcontext().Emax = 999999
    
    # Initialize Chudnovsky algorithm variables using pure INTEGERS
    K = 6
    M = 1
    L = 13591409
    X = 1
    S = Decimal(13591409)
    k = 1
    
    operations = 0
    start_time = time.time()
    
    while not stop_event.is_set():
        M = (K**3 - 16*K) * M // (k**3)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / Decimal(X)
        
        K += 12
        k += 1
        operations += 15 # Estimated math operations per iteration
        
        # Every core updates its own speed in the shared array
        if k % 5 == 0:
            elapsed = time.time() - start_time
            ops_per_sec = operations / elapsed if elapsed > 0 else 0
            ops_array[core_id] = ops_per_sec
            
            # Only the primary core handles the queue for the UI digits/time
            if is_primary:
                digits = k * 14
                queue.put((digits, elapsed))
            
    if is_primary:
        # Final calculation step
        C = 426880 * Decimal(10005).sqrt()
        pi = C / S
        queue.put(str(pi)[:(k*14)])

def main():
    print("--- Pi-Mark CPU Stress Test & Calculator ---")
    
    try:
        duration = float(input("Enter duration to run the stress test (in seconds): "))
    except ValueError:
        print("Invalid input. Defaulting to 60 seconds.")
        duration = 60.0
        
    save_output = input("Output the final calculated Pi to a .txt file? (y/n): ").strip().lower() == 'y'
    
    cores = os.cpu_count() or 1
    print(f"\nStarting benchmark on {cores} CPU cores to maximize resource usage...")
    
    stop_event = multiprocessing.Event()
    queue = multiprocessing.Queue()
    
    # Create a shared memory array of 'doubles' (floats) sized to the number of cores
    # This allows all worker processes to report their speed simultaneously
    ops_array = multiprocessing.Array('d', cores)
    processes = []
    
    for i in range(cores):
        is_primary = (i == 0)
        p = multiprocessing.Process(target=calculate_pi_worker, args=(stop_event, queue, is_primary, i, ops_array))
        p.start()
        processes.append(p)
        
    start_time = time.time()
    last_digits = 0
    
    try:
        while time.time() - start_time < duration:
            # Drain queue to keep digits updated
            while not queue.empty():
                item = queue.get()
                if isinstance(item, tuple):
                    last_digits, _ = item
            
            # Sum the operations per second from ALL cores
            total_ops_per_sec = sum(ops_array)
            
            # Note: We now label it "Total Ops/sec" because we switched to ultra-accurate Integer math 
            # rather than floating point math in the previous step.
            sys.stdout.write(f"\rDigits Calculated: ~{last_digits} | Total Ops/sec ({cores} Cores): {total_ops_per_sec:.2f} | Time Elapsed: {(time.time() - start_time):.2f}s ")
            sys.stdout.flush()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nEarly exit requested by user.")
        
    stop_event.set()
    
    total_ops_per_sec = sum(ops_array)
    sys.stdout.write(f"\rDigits Calculated: ~{last_digits} | Total Ops/sec ({cores} Cores): {total_ops_per_sec:.2f} | Time Elapsed: {(time.time() - start_time):.2f}s \n")
    print("\nBenchmark Complete! Finalizing Pi calculation (this may take a moment)...")
    
    final_pi = None
    while True:
        try:
            item = queue.get(timeout=3)
            if isinstance(item, str):
                final_pi = item
                break
        except Exception:
            break
            
    for p in processes:
        p.join()
        
    if final_pi:
        if save_output:
            filename = "pi_output.txt"
            with open(filename, "w") as f:
                f.write(final_pi)
            print(f"\nSuccess! Calculated Pi has been saved to '{filename}'.")
            print(f"Total precise digits calculated: {len(final_pi) - 2}")
        else:
            print("\nPi calculation finished successfully (output not saved to file).")
    else:
        print("\nFailed to retrieve final Pi calculation.")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
