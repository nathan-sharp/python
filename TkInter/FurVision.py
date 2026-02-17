import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import time
import math

# ==============================================================================
# FURVISION PLAYER - PURE STANDARD LIBRARY EDITION
# ==============================================================================
# This version uses NO external tools (No PIL, No OpenCV, No Pygame).
# It relies entirely on Python's built-in Tkinter library.
#
# Capabilities:
# - Images: PNG and GIF only (Native Tkinter support).
# - Audio/Video: Simulation Mode (UI updates, but no actual rendering).
# ==============================================================================

class Win95Button(tk.Button):
    """A helper to create consistent Windows 95 style buttons"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.config(
            relief="raised",
            borderwidth=2,
            bg="#c0c0c0",
            activebackground="#c0c0c0"
        )

class FurVision:
    def __init__(self, root):
        self.root = root
        self.root.title("FurVision Player (Native Mode)")
        self.root.geometry("640x480")
        self.root.configure(bg="#c0c0c0")
        
        self.current_file = None
        self.media_type = None
        self.playing = False
        self.paused = False
        
        # Threads & State
        self.play_thread = None
        self.stop_event = threading.Event()
        self.image_ref = None # Keep reference to prevent GC
        self.original_image_ref = None # Store original for resizing logic

        self.setup_ui()

    def setup_ui(self):
        # --- Menu Bar ---
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)

        # --- Top Toolbar ---
        toolbar = tk.Frame(self.root, bd=1, relief="raised", bg="#c0c0c0")
        toolbar.pack(side="top", fill="x", padx=2, pady=2)

        self.btn_open = Win95Button(toolbar, text="Open", command=self.open_file, width=8)
        self.btn_open.pack(side="left", padx=2, pady=2)

        tk.Frame(toolbar, width=10, bg="#c0c0c0").pack(side="left") # Spacer

        self.btn_play = Win95Button(toolbar, text="Play", command=self.play_media, width=8, state="disabled")
        self.btn_play.pack(side="left", padx=2, pady=2)

        self.btn_pause = Win95Button(toolbar, text="Pause", command=self.pause_media, width=8, state="disabled")
        self.btn_pause.pack(side="left", padx=2, pady=2)

        self.btn_stop = Win95Button(toolbar, text="Stop", command=self.stop_media, width=8, state="disabled")
        self.btn_stop.pack(side="left", padx=2, pady=2)

        # --- Main Display Area ---
        self.display_frame = tk.Frame(self.root, bd=2, relief="sunken", bg="black")
        self.display_frame.pack(side="top", fill="both", expand=True, padx=4, pady=4)

        self.canvas = tk.Canvas(self.display_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # --- Status Bar ---
        self.statusbar = tk.Label(self.root, text="Ready (Native Mode)", bd=1, relief="sunken", anchor="w", bg="#c0c0c0", font=("Arial", 9))
        self.statusbar.pack(side="bottom", fill="x")

    def update_status(self, text):
        self.statusbar.config(text=text)

    def open_file(self):
        self.stop_media()
        
        # Pure Python Tkinter usually supports PNG and GIF well. 
        # JPG/BMP support is often missing without PIL.
        ftypes = (
            ("Supported Images", "*.png;*.gif;*.ppm;*.pgm"),
            ("Media Files (Simulated)", "*.mp3;*.wav;*.mp4;*.avi"),
            ("All Files", "*.*")
        )
        
        filename = filedialog.askopenfilename(title="Open Media", filetypes=ftypes)
        
        if filename:
            self.current_file = filename
            ext = os.path.splitext(filename)[1].lower()
            
            # --- IMAGE HANDLING ---
            if ext in ['.png', '.gif', '.ppm', '.pgm']:
                self.media_type = 'image'
                try:
                    # Load natively
                    self.original_image_ref = tk.PhotoImage(file=filename)
                    self.show_image()
                    self.update_status(f"Viewing: {os.path.basename(filename)}")
                    self.enable_controls(play=False, stop=False, pause=False)
                except tk.TclError:
                    # This happens if the specific PNG format isn't supported or it's actually a JPG renamed
                    messagebox.showerror("Format Error", "This image format is not supported by the standard library.\nPlease use PNG or GIF.")
            
            # --- AUDIO/VIDEO HANDLING (SIMULATION) ---
            elif ext in ['.mp3', '.wav', '.ogg', '.mp4', '.avi', '.mov', '.mkv']:
                # We identify the type, but we can't actually play it without libraries.
                # We will launch the "Player Simulation" instead.
                self.media_type = 'media_sim'
                self.show_placeholder_visuals()
                self.update_status(f"Loaded: {os.path.basename(filename)}")
                self.enable_controls(play=True, stop=False, pause=False)
            
            # --- UNSUPPORTED ---
            elif ext in ['.jpg', '.jpeg', '.bmp']:
                messagebox.showwarning("Restricted Format", "JPG/BMP files require external libraries (PIL).\nPlease convert to PNG to view in Native Mode.")
            else:
                messagebox.showerror("Error", "Unknown file format.")

    def enable_controls(self, play=True, stop=True, pause=True):
        self.btn_play.config(state="normal" if play else "disabled")
        self.btn_stop.config(state="normal" if stop else "disabled")
        self.btn_pause.config(state="normal" if pause else "disabled")

    def show_image(self):
        """
        Displays the image using native Tkinter tools.
        Includes a crude 'shrink to fit' using subsample (integer scaling only).
        """
        if not self.original_image_ref: return

        # Get Canvas Dimensions
        c_w = self.canvas.winfo_width()
        c_h = self.canvas.winfo_height()
        
        if c_w < 10: return # Canvas not drawn yet

        img_w = self.original_image_ref.width()
        img_h = self.original_image_ref.height()

        # Calculate integer downscale factor (Tkinter cannot do fractional resizing natively)
        # We find the smallest integer divisor that makes the image fit.
        scale_x = math.ceil(img_w / c_w)
        scale_y = math.ceil(img_h / c_h)
        scale_factor = max(scale_x, scale_y)
        
        if scale_factor < 1: scale_factor = 1

        # Resize
        try:
            if scale_factor > 1:
                self.image_ref = self.original_image_ref.subsample(scale_factor, scale_factor)
            else:
                self.image_ref = self.original_image_ref
                
            self.canvas.delete("all")
            self.canvas.create_image(c_w//2, c_h//2, image=self.image_ref, anchor="center")
        except Exception as e:
            print(f"Resize error: {e}")

    def show_placeholder_visuals(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Draw a retro style "No Signal" or Music Note
        self.canvas.create_rectangle(0, 0, w, h, fill="#000000")
        
        # Text info
        self.canvas.create_text(w//2, h//2 - 20, text="NATIVE MODE", fill="#00ff00", font=("Courier", 24, "bold"))
        self.canvas.create_text(w//2, h//2 + 20, text="Visualizing Data...", fill="white", font=("Courier", 12))
        self.canvas.create_text(w//2, h//2 + 50, text=os.path.basename(self.current_file or ""), fill="#c0c0c0", font=("Arial", 10))

    # --- PLAYER CONTROLS (SIMULATION) ---

    def play_media(self):
        if self.media_type == 'media_sim':
            if not self.playing:
                self.playing = True
                self.paused = False
                self.stop_event.clear()
                self.enable_controls(play=False, pause=True, stop=True)
                
                # Start the "Fake" player thread
                threading.Thread(target=self.simulation_loop, daemon=True).start()
            
            elif self.paused:
                self.paused = False
                self.enable_controls(play=False, pause=True, stop=True)

    def pause_media(self):
        if self.media_type == 'media_sim' and self.playing:
            self.paused = True
            self.enable_controls(play=True, pause=False, stop=True)
            self.update_status("Paused")

    def stop_media(self):
        self.playing = False
        self.paused = False
        self.stop_event.set()
        self.enable_controls(play=True, pause=False, stop=False)
        self.update_status("Stopped")
        if self.media_type == 'media_sim':
            self.show_placeholder_visuals()

    def simulation_loop(self):
        """
        Simulates playback by updating the UI and drawing random 'visualizer' bars.
        Does not actually produce sound or video.
        """
        seconds = 0
        import random
        
        while not self.stop_event.is_set():
            if self.paused:
                time.sleep(0.2)
                continue

            # Update Timer
            m, s = divmod(seconds, 60)
            time_str = f"{m:02d}:{s:02d}"
            self.update_status(f"Playing > {time_str}")
            
            # Draw fake visualizer bars
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.canvas.delete("bars") # Delete old bars
            
            bar_count = 20
            bar_w = w / bar_count
            
            for i in range(bar_count):
                bar_h = random.randint(10, 100)
                x1 = i * bar_w + 2
                y1 = h / 2 - bar_h
                x2 = x1 + bar_w - 4
                y2 = h / 2 + bar_h
                
                # Green retro bars
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="#00ff00", outline="#003300", tags="bars")

            seconds += 1
            time.sleep(1.0) # Update every second

    def show_about(self):
        msg = (
            "FurVision Player (Native Mode)\n"
            "v1.0 - Standard Library Edition\n\n"
            "This version runs without external dependencies.\n"
            "- Images: PNG/GIF Only\n"
            "- Audio/Video: Simulated Playback"
        )
        messagebox.showinfo("About", msg)

    def on_close(self):
        self.stop_media()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # Attempt to handle window resize for image rescaling
    app = FurVision(root)
    
    # Bind configure on root to handle resizing better
    root.bind("<Configure>", lambda e: app.show_image() if app.media_type == 'image' else None)
    
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()