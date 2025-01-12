import sqlite3
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import webbrowser

# Initialize the database
def initialize_db():
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            remember_me INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            name TEXT PRIMARY KEY,
            location TEXT,
            expiry TEXT
        )
    """)
    conn.commit()
    conn.close()

# Validate user credentials
def validate_user(email, password):
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT remember_me FROM users WHERE email = ? AND password = ?", (email, password))
    result = cursor.fetchone()
    conn.close()
    return result

# Check for remembered user
def get_remembered_user():
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE remember_me = 1")
    result = cursor.fetchone()
    conn.close()
    return result

# Register a new user
def register_user(email, password, remember_me=False):
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password, remember_me) VALUES (?, ?, ?)", (email, password, int(remember_me)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Update remember_me status
def update_remember_me(email, remember_me):
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET remember_me = ? WHERE email = ?", (int(remember_me), email))
    conn.commit()
    conn.close()

# Add a new medicine
def add_medicine_to_db(name, location, expiry):
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO medicines (name, location, expiry) VALUES (?, ?, ?)", (name, location, expiry))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Search for a medicine in the database
def search_medicine_in_db(medicine_name):
    conn = sqlite3.connect("pharmacy_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, location, expiry FROM medicines WHERE name = ?", (medicine_name,))
    result = cursor.fetchone()
    conn.close()
    return result

# Launch Google login simulation
def google_login():
    webbrowser.open("https://accounts.google.com", new=1)

# Main program UI
class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pharmacy Management System")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        # Load banner image
        try:
            self.banner_image = ImageTk.PhotoImage(Image.open("logo.jpg").resize((800, 240)))
        except FileNotFoundError:
            messagebox.showerror("Error", "Banner image not found.")
            self.banner_image = None

        # Load logo image
        try:
            self.logo_image = ImageTk.PhotoImage(Image.open("logo.png").resize((500, 200)))
        except FileNotFoundError:
            messagebox.showerror("Error", "Logo image not found.")
            self.logo_image = None

        # Frame dictionary to manage frames
        self.frames = {}

        # Create and store frames
        self.frames['login'] = self.create_login_frame()
        self.frames['main'] = None

        # Check for remembered user
        remembered_user = get_remembered_user()
        if remembered_user:
            self.launch_main_program(remembered_user[0])
        else:
            self.show_frame('login')

    def show_frame(self, frame_name):
        """Switch to the specified frame."""
        frame = self.frames.get(frame_name)
        if frame:
            frame.pack(fill="both", expand=True)
            for other_frame in self.frames.values():
                if other_frame != frame and other_frame:
                    other_frame.pack_forget()

    def create_login_frame(self):
        """Create the login frame."""
        frame = tk.Frame(self.root, bg="#f0f0f0")

        if self.banner_image:
            banner_label = tk.Label(frame, image=self.banner_image, bg="#f0f0f0")
            banner_label.pack(pady=10)

        tk.Label(frame, text="Login", font=("Arial", 20), bg="#f0f0f0").pack(pady=20)

        tk.Label(frame, text="E-mail:", anchor="w", bg="#f0f0f0").pack(fill="x", padx=20, pady=5)
        self.login_email = tk.Entry(frame)
        self.login_email.pack(fill="x", padx=20, pady=5)

        tk.Label(frame, text="Password:", anchor="w", bg="#f0f0f0").pack(fill="x", padx=20, pady=5)
        self.login_password = tk.Entry(frame, show="*")
        self.login_password.pack(fill="x", padx=20, pady=5)

        # Remember Me checkbox
        self.remember_me_var = tk.IntVar()
        tk.Checkbutton(frame, text="Remember me", variable=self.remember_me_var, bg="#f0f0f0").pack(pady=5)

        # Buttons
        button_frame = tk.Frame(frame, bg="#f0f0f0")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Sign In", command=self.handle_login, bg="#4CAF50", fg="white").pack(side="left", padx=5, expand=True)
        tk.Button(button_frame, text="Sign Up", command=self.open_signup_window, bg="#2196F3", fg="white").pack(side="left", padx=5, expand=True)
        tk.Button(button_frame, text="Google", command=google_login, bg="#DB4437", fg="white").pack(side="left", padx=5, expand=True)

        tk.Button(frame, text="Forgot Password?", fg="blue", bd=0, cursor="hand2", command=self.forgot_password, bg="#f0f0f0").pack(pady=5)

        return frame

    def handle_login(self):
        """Handle user login."""
        email = self.login_email.get().strip()
        password = self.login_password.get().strip()
        remember_me = self.remember_me_var.get()

        result = validate_user(email, password)
        if result:
            update_remember_me(email, remember_me)
            self.launch_main_program(email)
        else:
            messagebox.showerror("Invalid Credentials", "The email or password you entered is incorrect.")

    def forgot_password(self):
        """Handle the forgot password process."""
        self.reset_password_window()

    def reset_password_window(self):
        """Open a password reset window."""
        reset_window = tk.Toplevel(self.root)
        reset_window.title("Reset Password")
        reset_window.geometry("300x250")

        tk.Label(reset_window, text="Reset Password", font=("Arial", 20)).pack(pady=20)

        tk.Label(reset_window, text="E-mail:").pack(pady=5)
        email_entry = tk.Entry(reset_window)
        email_entry.pack(pady=5)

        tk.Label(reset_window, text="New Password:").pack(pady=5)
        new_password_entry = tk.Entry(reset_window, show="*")
        new_password_entry.pack(pady=5)

        def reset_password():
            email = email_entry.get().strip()
            new_password = new_password_entry.get().strip()

            if email and new_password:
                conn = sqlite3.connect("pharmacy_system.db")
                cursor = conn.cursor()
                cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
                user_exists = cursor.fetchone()
                if user_exists:
                    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Password has been reset successfully!")
                    reset_window.destroy()
                else:
                    messagebox.showerror("Error", "No account found with this email address.")
                    conn.close()
            else:
                messagebox.showerror("Error", "All fields are required.")

        tk.Button(reset_window, text="Reset Password", command=reset_password, bg="#4CAF50", fg="white").pack(pady=20)

    def open_signup_window(self):
        """Open the signup window."""
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")
        signup_window.geometry("300x300")

        tk.Label(signup_window, text="Sign Up", font=("Arial", 20)).pack(pady=20)

        tk.Label(signup_window, text="E-mail:").pack(pady=5)
        email_entry = tk.Entry(signup_window)
        email_entry.pack(pady=5)

        tk.Label(signup_window, text="Password:").pack(pady=5)
        password_entry = tk.Entry(signup_window, show="*")
        password_entry.pack(pady=5)

        remember_me_var = tk.IntVar()
        tk.Checkbutton(signup_window, text="Remember me", variable=remember_me_var).pack(pady=5)

        def register():
            email = email_entry.get().strip()
            password = password_entry.get().strip()
            remember_me = remember_me_var.get()

            if email and password:
                if register_user(email, password, remember_me):
                    messagebox.showinfo("Success", "Registration successful!")
                    signup_window.destroy()
                else:
                    messagebox.showerror("Error", "User already exists!")
            else:
                messagebox.showerror("Error", "All fields are required.")

        tk.Button(signup_window, text="Register", command=register, bg="#4CAF50", fg="white").pack(pady=10)

    def launch_main_program(self, user_email):
        """Launch the main program."""
        if not self.frames.get('main'):
            self.frames['main'] = self.create_main_frame(user_email)
        self.show_frame('main')

    def create_main_frame(self, user_email):
        """Create the main program frame."""
        frame = tk.Frame(self.root, bg="#f0f0f0")

        if self.logo_image:
            logo_label = tk.Label(frame, image=self.logo_image, bg="#f0f0f0")
            logo_label.pack(pady=10)

        tk.Label(frame, text=f"Welcome, {user_email}", font=("Arial", 20), bg="#f0f0f0").pack(pady=20)

        # Search box
        tk.Label(frame, text="Search for a Medicine:", font=("Arial", 14), bg="#f0f0f0").pack(pady=10)
        search_frame = tk.Frame(frame, bg="#f0f0f0")
        search_frame.pack(pady=5)

        search_entry = tk.Entry(search_frame, width=30)
        search_entry.pack(side="left", padx=5)

        def search_medicine():
            medicine_name = search_entry.get().strip()
            if medicine_name:
                result = search_medicine_in_db(medicine_name)
                if result:
                    messagebox.showinfo(
                        "Medicine Found",
                        f"Name: {result[0]}\nLocation: {result[1]}\nExpiry Date: {result[2]}",
                    )
                else:
                    messagebox.showerror("Not Found", "No medicine found with that name.")
            else:
                messagebox.showerror("Error", "Please enter a medicine name.")

        tk.Button(search_frame, text="Search", command=search_medicine, bg="#4CAF50", fg="white").pack(side="left", padx=5)

        tk.Button(frame, text="Add Medicine", command=self.add_medicine_window, bg="#4CAF50", fg="white").pack(pady=20)

        return frame

    def add_medicine_window(self):
        """Open a new window for adding medicines."""
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Medicine")
        add_window.geometry("300x200")

        tk.Label(add_window, text="Medicine Name:").pack(pady=5)
        med_name = tk.Entry(add_window)
        med_name.pack(pady=5)

        tk.Label(add_window, text="Location:").pack(pady=5)
        med_loc = tk.Entry(add_window)
        med_loc.pack(pady=5)

        tk.Label(add_window, text="Expiry Date (YYYY-MM-DD):").pack(pady=5)
        med_expiry = tk.Entry(add_window)
        med_expiry.pack(pady=5)

        def save_medicine():
            name, loc, expiry = med_name.get(), med_loc.get(), med_expiry.get()
            if name and loc and expiry:
                if add_medicine_to_db(name, loc, expiry):
                    messagebox.showinfo("Success", "Medicine added successfully!")
                    add_window.destroy()
                else:
                    messagebox.showerror("Error", "Medicine already exists!")
            else:
                messagebox.showerror("Error", "All fields are required.")

        tk.Button(add_window, text="Save", command=save_medicine, bg="#4CAF50", fg="white").pack(pady=10)

if __name__ == "__main__":
    initialize_db()
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()
