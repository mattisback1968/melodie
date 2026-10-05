# -*- coding: utf-8 -*-
import os
import hashlib
import tkinter as tk
from tkinter import messagebox
import psycopg2  # Connecteur PostgreSQL obligatoire
from dotenv import load_dotenv

load_dotenv()

# 1. Connexion exclusive à PostgreSQL via votre .env
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "melody_db"),
        port=os.getenv("DB_PORT", "5432")
    )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def open_main_app_window(user_role):
    try:
        import melody
        root.withdraw() # Cache la fenetre de login
        # Envoie le role à la fenetre principale de melody.py
        melody.main_window(parent_window=root, user_role=user_role)
    except ImportError:
        messagebox.showerror("Erreur", "Le fichier 'melody.py' est introuvable.")

# 2. L'inscription corrigée (Plus aucun connecteur MySQL ici)
def sign_up():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Erreur", "Tous les champs sont obligatoires !")
        return

    hashed_pwd = hash_password(password)

    try:
        conn = connect_db() # Appelle la connexion Postgres
        cursor = conn.cursor()

        # Vérifier si l'utilisateur existe déjà sous Postgres
        cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            messagebox.showerror("Erreur", "Nom d'utilisateur deja utilise !")
            return

        # Insertion : PostgreSQL appliquera son DEFAULT 'user' automatiquement
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed_pwd)
        )
        conn.commit()
        messagebox.showinfo("Succes", f"Utilisateur {username} cree avec succes !")
        
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)

    except psycopg2.Error as err: # ✅ Intercepte uniquement les erreurs Postgres
        messagebox.showerror("Erreur DB", f"Impossible d'inscrire l'utilisateur dans PostgreSQL :\n{err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

# 3. La connexion corrigée (Lit le rôle)
def sign_in():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Erreur", "Tous les champs sont obligatoires !")
        return

    hashed_pwd = hash_password(password)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Récupération du rôle
        cursor.execute(
            "SELECT role FROM users WHERE username = %s AND password = %s", 
            (username, hashed_pwd)
        )
        user_record = cursor.fetchone()

        if user_record:
            role_recupere = user_record[0] # Extrait le texte 'admin' ou 'user'
            messagebox.showinfo("Succes", f"Bienvenue {username} !\nProfil : {role_recupere}")
            open_main_app_window(user_role=role_recupere)
        else:
            messagebox.showerror("Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

    except psycopg2.Error as err: # ✅ Intercepte uniquement les erreurs Postgres
        messagebox.showerror("Erreur DB", f"Erreur d'authentification PostgreSQL :\n{err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()



# --- FENÊTRE PRINCIPALE GRAPHIQUE ---
root = tk.Tk()
root.title("Melody - Authentification")
root.geometry("350x150")
root.resizable(False, False)

# Widgets de l'interface
tk.Label(root, text="Nom d'utilisateur").grid(row=0, column=0, padx=10, pady=15, sticky="e")
entry_username = tk.Entry(root, width=25)
entry_username.grid(row=0, column=1, padx=10, pady=15)

tk.Label(root, text="Mot de passe").grid(row=1, column=0, padx=10, pady=5, sticky="e")
entry_password = tk.Entry(root, show="*", width=25)
entry_password.grid(row=1, column=1, padx=10, pady=5)

# Boutons d'actions
btn_signup = tk.Button(root, text="S'inscrire", command=sign_up, width=12)
btn_signup.grid(row=2, column=0, padx=15, pady=15, sticky="w")

btn_signin = tk.Button(root, text="Se connecter", command=sign_in, width=12, bg="#0d6efd", fg="white")
btn_signin.grid(row=2, column=1, padx=15, pady=15, sticky="e")

root.mainloop()
