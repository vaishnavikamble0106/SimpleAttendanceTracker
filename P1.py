import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import datetime

conn = sqlite3.connect('attendance.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS attendees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        roll_no INTEGER,
        date TEXT,
        subjects TEXT
    )
''')
conn.commit()

class AttendanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Simple Attendance Tracker")
        self.root.geometry("1000x500")
        self.root.configure(bg='light blue')  
        
        self.font_style = ("Arial", 26)  
        self.create_widgets()
        
    def create_widgets(self):
        # Styling options
        label_bg = '#f0f0f0'
        entry_bg = '#ffffff'
        btn_bg = '#4CAF50'
        btn_fg = '#ffffff'
        label_fg = '#000000'
        
        
        tk.Label(self.root, text="Name:", bg=label_bg, fg=label_fg, font=self.font_style).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = tk.Entry(self.root, bg=entry_bg, font=self.font_style)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

       
        tk.Label(self.root, text="Roll No:", bg=label_bg, fg=label_fg, font=self.font_style).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.roll_entry = tk.Entry(self.root, bg=entry_bg, font=self.font_style)
        self.roll_entry.grid(row=1, column=1, padx=10, pady=10)

        
        tk.Label(self.root, text="Date:", bg=label_bg, fg=label_fg, font=self.font_style).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.date_entry = tk.Entry(self.root, bg=entry_bg, font=self.font_style)
        self.date_entry.grid(row=2, column=1, padx=10, pady=10)
        self.date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        
        
        tk.Label(self.root, text="Subjects:", bg=label_bg, fg=label_fg, font=self.font_style).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        
        subject_frame = tk.Frame(self.root, bg=label_bg)
        subject_frame.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        canvas = tk.Canvas(subject_frame, bg=label_bg, width=300, height=100)
        scrollbar = tk.Scrollbar(subject_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=label_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        self.subjects = ["Python", "ML/NLP", "JS", "Java", "MySQL"]
        self.subject_vars = {subject: tk.BooleanVar() for subject in self.subjects}
        for i, subject in enumerate(self.subjects):
            chk = tk.Checkbutton(scrollable_frame, text=subject, variable=self.subject_vars[subject], bg=label_bg, font=self.font_style)
            chk.pack(anchor="w")

        
        self.add_btn = tk.Button(self.root, text="Add Attendee", command=self.add_attendee, bg=btn_bg, fg=btn_fg, font=self.font_style)
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)
        
        
        self.view_btn = tk.Button(self.root, text="View Attendees", command=self.view_attendees, bg=btn_bg, fg=btn_fg, font=self.font_style)
        self.view_btn.grid(row=4, column=2, columnspan=2, pady=10)

    def validate_inputs(self):
        name = self.name_entry.get().strip()
        roll_no = self.roll_entry.get().strip()
        date = self.date_entry.get().strip()
        subjects = [subject for subject, var in self.subject_vars.items() if var.get()]

        if not name or not roll_no or not date or not subjects:
            messagebox.showerror("Input Error", "All fields must be filled out.")
            return False
        
        if not name.replace(' ', '').isalpha():
            messagebox.showerror("Input Error", "Name must contain only letters and spaces.")
            return False
        
        if not roll_no.isdigit():
            messagebox.showerror("Input Error", "Roll No must be a positive number.")
            return False

        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
            return False

        return True

    def add_attendee(self):
        if not self.validate_inputs():
            return

        name = self.name_entry.get().strip()
        roll_no = int(self.roll_entry.get().strip())
        date = self.date_entry.get().strip()
        subjects = ", ".join([subject for subject, var in self.subject_vars.items() if var.get()])

        c.execute("INSERT INTO attendees (name, roll_no, date, subjects) VALUES (?, ?, ?, ?)", (name, roll_no, date, subjects))
        conn.commit()

        messagebox.showinfo("Success", "Attendee added successfully!")
        self.clear_entries()

    def clear_entries(self):
        self.name_entry.delete(0, tk.END)
        self.roll_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        for var in self.subject_vars.values():
            var.set(False)
    
    def view_attendees(self):
        view_window = tk.Toplevel(self.root)
        view_window.title("View Attendees")
        view_window.geometry("600x300")
        view_window.configure(bg='#f0f0f0')  
        
        tree = ttk.Treeview(view_window, columns=("ID", "Name", "Roll No", "Date", "Subjects"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Name", text="Name")
        tree.heading("Roll No", text="Roll No")
        tree.heading("Date", text="Date")
        tree.heading("Subjects", text="Subjects")
        tree.pack(fill=tk.BOTH, expand=True)
        
        c.execute("SELECT * FROM attendees")
        for row in c.fetchall():
            tree.insert('', tk.END, values=row)

        def delete_selected():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showerror("Error", "No item selected")
                return
            item = tree.item(selected_item)
            attendee_id = item['values'][0]
            if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this attendee?"):
                c.execute("DELETE FROM attendees WHERE id = ?", (attendee_id,))
                conn.commit()
                tree.delete(selected_item)
                messagebox.showinfo("Success", "Attendee deleted successfully!")

        delete_btn = tk.Button(view_window, text="Delete Selected", command=delete_selected, bg='#ff0000', fg='#ffffff', font=self.font_style)
        delete_btn.pack(pady=10)
        
    def confirm_quit(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.root.destroy()

root = tk.Tk()
app = AttendanceTracker(root)
root.mainloop()
