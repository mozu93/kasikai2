import tkinter as tk

try:
    print("Attempting to create a simple GUI window.")
    root = tk.Tk()
    root.title("GUI Test")
    root.geometry("300x200")
    label = tk.Label(root, text="This is a test window.")
    label.pack(pady=20)
    print("Window created. Starting mainloop...")
    root.mainloop()
    print("Mainloop finished.")
except Exception as e:
    print(f"An error occurred: {e}")
