from tkinter import *

root = Tk()

Button = Button(root, text="Increment")
Label = Label(root, text="0")

count = 0
def on_button_click():
    global count
    count += 1
    Label.config(text=str(count))

Button.config(command=on_button_click)
Button.pack()
Label.pack()


root.mainloop()
