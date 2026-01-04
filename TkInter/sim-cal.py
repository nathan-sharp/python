import tkinter as tk
from tkinter import messagebox

def calculate():
    try:
        # 1. Get the text from the entry boxes and convert to floating point numbers
        val1 = float(n1.get())
        val2 = float(n2.get())
        
        # 2. Get the selected operation from the dropdown
        op = operation_var.get()
        
        # 3. Perform the math based on the selection
        if op == "Add":
            res = val1 + val2
        elif op == "Subtract":
            res = val1 - val2
        elif op == "Multiply":
            res = val1 * val2
        elif op == "Divide":
            if val2 == 0:
                result_label.config(text="Result: Cannot divide by zero")
                return
            res = val1 / val2
        else:
            res = "Select Operation"

        # 4. Update the Result Label
        # We round to 2 decimal places for cleanliness
        result_label.config(text=f"Result: {round(res, 2)}")

    except ValueError:
        # Handle cases where the user didn't type a valid number
        result_label.config(text="Result: Error (Invalid Input)")
        messagebox.showerror("Input Error", "Please enter valid numbers.")

# --- UI SETUP ---
master = tk.Tk()
master.title("Simple Calculator")
master.geometry("400x150") # Optional: Set a reasonable default size

# Labels for inputs
tk.Label(master, text='First Number').grid(row=0, column=0, padx=10, pady=5)
tk.Label(master, text='Second Number').grid(row=1, column=0, padx=10, pady=5)

# Input Entry Boxes
n1 = tk.Entry(master)
n2 = tk.Entry(master)
n1.grid(row=0, column=1, padx=10, pady=5)
n2.grid(row=1, column=1, padx=10, pady=5)

# Dropdown (OptionMenu) for Operation
operations = ["Add", "Subtract", "Multiply", "Divide"]
operation_var = tk.StringVar(master)
operation_var.set(operations[0]) # Set default value

# Create the dropdown menu
op_menu = tk.OptionMenu(master, operation_var, *operations)
op_menu.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
tk.Label(master, text='Operation').grid(row=2, column=0, padx=10, pady=5)

# Calculate Button
# This triggers the 'calculate' function defined above
calc_btn = tk.Button(master, text="Calculate", command=calculate)
calc_btn.grid(row=3, column=1, sticky="ew", padx=10, pady=10)

# Result Label
result_label = tk.Label(master, text="Result: ", font=("Arial", 12, "bold"))
result_label.grid(row=4, column=0, columnspan=2, pady=10)

master.mainloop()
