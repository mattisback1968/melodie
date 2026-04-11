import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import hashlib

# Connexion MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="csv_db 6"
    )

# Hash du mot de passe (simple SHA-256)
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fonction inscription nouvel utilisateur
def sign_up():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Erreur", "Tous les champs sont obligatoires !")
        return

    hashed_pwd = hash_password(password)

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Vérifier si user existe
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Nom d'utilisateur déjà utilisé !")
            return

        # Insertion
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_pwd)
        )
        conn.commit()

        messagebox.showinfo("Succès", "Inscription réussie !")

        root.destroy() # ferme sign-up
        open_login_window() # retourne à login

    except mysql.connector.Error as err:
        messagebox.showerror("Erreur DB", f"{err}")

    finally:
        cursor.close()
        conn.close()

# Fonction connexion utilisateur existant
def sign_in():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Erreur", "Tous les champs sont obligatoires !")
        return

    hashed_pwd = hash_password(password)

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Vérifier si user existe et si oui si mot de passe correct
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Nom d'utilisateur déjà utilisé ! Vérifiez votre mot de passe")
            return

        # Insertion
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_pwd)
        )
        conn.commit()

        messagebox.showinfo("Succès", "Connexion établie !")

        root.destroy() # ferme sign-up
        open_login_window() # retourne à login

    except mysql.connector.Error as err:
        messagebox.showerror("Erreur DB", f"{err}")

    finally:
        cursor.close()
        conn.close()

# Fenêtre login
def open_login_window():
    login = tk.Tk()
    login.title("Login")
    tk.Label(login, text="Fenêtre de connexion").pack(padx=20, pady=20)
    login.mainloop()

#fenêtre sign-up pour nouvel utilisateur
def open_sign_up_window():
    login = tk.Tk()
    login.title("Sign up")
    tk.Label(login, text="Fenêtre d'inscription").pack(padx=20, pady=20)
    login.mainloop()

"""#fenêtre sign-in pour utilisateur existant
def open_login_window(): 
    login = tk.Tk()
    login.title("Login")
    tk.Label(login, text="Fenêtre de connexion").pack(padx=20, pady=20)
    login.mainloop()"""

# Fenêtre globale inscription ou connexion
root = tk.Tk()
root.title("Connexion ou inscription")
root.geometry("350x150")

tk.Label(root, text="Nom d'utilisateur").grid(row=0, column=0, padx=10, pady=5)
entry_username = tk.Entry(root)
entry_username.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Mot de passe").grid(row=1, column=0, padx=10, pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.grid(row=1, column=1, padx=10, pady=5)

tk.Button(root, text="S'inscrire", command=sign_up).grid(row=2, column=0, columnspan=1, pady=10) #bouton nouvel utilisateur
tk.Button(root, text="Se connecter", command=sign_in).grid(row=2, column=1, columnspan=2, pady=10) #bouton pour utilisateur existant

root.mainloop()