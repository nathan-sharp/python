import time
import sys
import threading
import select
from decimal import Decimal, getcontext

# Set a time limit (in seconds)
TIME_LIMIT = 60  # Adjust as needed

try:
    import msvcrt  # Windows
    def is_key_pressed():
        return msvcrt.kbhit()
    
    def get_key():
        return msvcrt.getch().decode('utf-8')
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

def listen_for_exit():
    global stop_flag
    while True:
        key = get_key()
        if key.lower() == 'x':
            stop_flag = True
            break

def calculate_pi():
    global stop_flag
    stop_flag = False
    listener_thread = threading.Thread(target=listen_for_exit, daemon=True)
    listener_thread.start()
    
    digits = 1
    getcontext().prec = 10000  # Increase precision limit
    getcontext().Emax = 999999  # Increase exponent max limit
    C = 426880 * Decimal(10005).sqrt()
    K = Decimal(6 * (0) + 1)
    M = Decimal(1)
    X = -262537412640768000.0  # Use float to prevent overflow
    L = Decimal(13591409)
    S = L
    
    start_time = time.time()
    operations = 0
    
    print("Starting Pi Calculation Benchmark... Press 'x' to stop.")
    while not stop_flag:
        K += 12
        M *= Decimal(K ** 3) / Decimal((digits + 1) ** 3)  # Ensure M remains Decimal
        X *= -262537412640768000.0  # Keep X as float to avoid Decimal overflow
        L += 545140134
        S += (M * L) / Decimal(X)
        operations += 6  # Estimated floating-point operations per iteration
        
        elapsed_time = time.time() - start_time
        if elapsed_time >= TIME_LIMIT:
            stop_flag = True
            break
        
        flops = operations / elapsed_time if elapsed_time > 0 else 0
        
        # Update output dynamically
        sys.stdout.write(f"\rDigits Calculated: {digits} | FLOPS: {flops:.2f} | Time Elapsed: {elapsed_time:.2f}s")
        sys.stdout.flush()
        
        digits += 1
    
    # pi = C / S  # Uncomment to show full pi number
    print("\nBenchmark Complete!")
    print(f"Total Time Elapsed: {elapsed_time:.2f} seconds")
    # print(f"Calculated Pi: {str(pi)[:digits]}")  # Uncomment to show full pi number

if __name__ == "__main__":
    calculate_pi()
