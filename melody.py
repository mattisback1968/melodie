import os
import decimal
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from dotenv import load_dotenv

# ======================
# Connexion BDD
# ======================
#load_dotenv()
import psycopg2          # <-- Remplacer mysql.connector par psycopg2
#from dotenv import load_dotenv

load_dotenv()


def get_connection():

    # ✅ Connexion robuste à PostgreSQL
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "melody_db"),
        port=os.getenv("DB_PORT", "5432")
    )



# ======================
# Fenêtre principale
# ======================
#def main_window(parent_window=None): #  avant grisement fonctions si user pas admin
def main_window(parent_window=None, user_role="user"):
    global tree

    # RUSE TKINTER : Si une fenêtre existe déjà (login), on s'ouvre par-dessus sans bloquer
    if parent_window:
        win = tk.Toplevel(parent_window)
    else:
        root = tk.Tk()
        win = root

    win.title("Melody - Gestionnaire Disquaire")
    
    w = 900
    h = 550

    # Centrage de la fenêtre sur l'écran
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    win.geometry('%dx%d+%d+%d' % (w, h, x, y))

    # --- Frame Recherche
    frm_search = tk.Frame(win)
    frm_search.pack(pady=10)

    tk.Label(frm_search, text="Artiste :").grid(row=0, column=0, padx=5)
    artist_entry = tk.Entry(frm_search, width=20)
    artist_entry.grid(row=0, column=1, padx=5)

    tk.Label(frm_search, text="Titre :").grid(row=0, column=2, padx=5)
    title_entry = tk.Entry(frm_search, width=20)
    title_entry.grid(row=0, column=3, padx=5)

    tk.Label(frm_search, text="Prix >").grid(row=0, column=4, padx=5)
    price_entry = tk.Entry(frm_search, width=6)
    price_entry.grid(row=0, column=5, padx=5)

    # ✅ Fonction Recherche
    def search(event=None):
        for row in tree.get_children():
            tree.delete(row)
        query = "SELECT id, artist, title, label, support, media_condition, sleeve_condition, price FROM melodie WHERE 1=1"
        params = []
        
        if artist_entry.get():
            query += " AND LOWER(artist) LIKE %s"
            params.append(f"%{artist_entry.get().lower()}%")

        if title_entry.get():
            query += " AND LOWER(title) LIKE %s"
            params.append(f"%{title_entry.get().lower()}%")
        
        if price_entry.get():
            try:
                prix = float(price_entry.get())
                query += " AND price > %s"
                params.append(prix)
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return 

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            for r in cursor.fetchall():
                tree.insert('', 'end', iid=r[0], values=r[1:])
        except mysql.connector.Error as err:
            messagebox.showerror("Erreur DB", f"Erreur de recherche :\n{err}")
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    tk.Button(frm_search, text="Rechercher", command=search, bg="#6c757d", fg="white").grid(row=0, column=7, padx=5)
    win.bind("<Return>", search)

    # --- Treeview & Scrollbar
    columns = ("Artiste", "Titre", "Label", "Support", "État du support", "État de la pochette", "Prix")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    
    scrollbar = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(pady=10, fill="both", expand=True, padx=10)

    # --- Frame pour les boutons d'actions en bas de la grille
    frm_actions = tk.Frame(win)
    frm_actions.pack(pady=10)

    # ======================
    # SOUS-FONCTIONS : Insérer / Modifier / Supprimer
    # ======================
    def insert_window():
        win_ins = tk.Toplevel(win)
        win_ins.title("Insérer un disque")
        labels = ["Artiste", "Titre", "Label", "Support", "État du support", "État de la pochette", "Prix"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(win_ins, text=label).grid(row=i, column=0, padx=10, pady=5)
            e = tk.Entry(win_ins, width=30)
            e.grid(row=i, column=1, padx=10, pady=5)
            entries[label] = e

        def insert(event=None):
            try:
                prix = float(entries["Prix"].get())
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return
            data = (
                entries["Artiste"].get().strip(),
                entries["Titre"].get().strip(),
                entries["Label"].get().strip(),
                entries["Support"].get().strip(),
                entries["État du support"].get().strip(),
                entries["État de la pochette"].get().strip(),
                prix
            )
            try:
                conn = get_connection()
                cursor = conn.cursor()
                query = "INSERT INTO melodie (artist, title, label, support, media_condition, sleeve_condition, price) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(query, data)
                conn.commit()
                pk = cursor.lastrowid
                tree.insert('', 'end', iid=pk, values=data)
                win_ins.destroy()
                messagebox.showinfo("Succès", "Disque inséré avec succès !")
            except psycopg2.Error as err:
                messagebox.showerror("Erreur SQL", f"Échec de l'insertion :\n{err}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()

        tk.Button(win_ins, text="Valider", command=insert, bg="#198754", fg="white").grid(row=len(labels), column=0, columnspan=2, pady=10)
        win_ins.bind("<Return>", insert)

    def modify_window():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention !", "Sélectionnez une ligne à modifier")
            return
        pk = selected[0]
        values = tree.item(pk, "values")
        
        win_mod = tk.Toplevel(win)
        win_mod.title("Modifier disque")
        labels = ["Artiste", "Titre", "Label", "Support", "État du support", "État de la pochette", "Prix"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(win_mod, text=label).grid(row=i, column=0, padx=10, pady=5)
            e = tk.Entry(win_mod, width=30)
            e.grid(row=i, column=1, padx=10, pady=5)
            e.insert(0, values[i])
            entries[label] = e

        def update():
            try:
                prix_val = float(entries["Prix"].get())
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return
            data = (
                entries["Artiste"].get().strip(),
                entries["Titre"].get().strip(),
                entries["Label"].get().strip(),
                entries["Support"].get().strip(),
                entries["État du support"].get().strip(),
                entries["État de la pochette"].get().strip(),
                prix_val,
                pk
            )

            try:
                conn = get_connection()
                cursor = conn.cursor()
                query = """
                UPDATE melodie 
                SET artist=%s, title=%s, label=%s, support=%s, media_condition=%s, sleeve_condition=%s, price=%s
                WHERE id=%s
                """
                cursor.execute(query, data)
                conn.commit()
                tree.item(pk, values=data[:-1])
                win_mod.destroy()
                messagebox.showinfo("Succès", "Disque mis à jour avec succès !")
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur SQL", f"Échec de la modification :\n{err}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()

        tk.Button(win_mod, text="Valider", command=update, bg="#0d6efd", fg="white").grid(row=len(labels), column=0, columnspan=2, pady=10)

    def delete_entry():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention !", "Sélectionnez une ligne à supprimer")
            return
        pk = selected[0]
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce disque ?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM melodie WHERE id = %s", (pk,))
                conn.commit()
                tree.delete(pk)
                messagebox.showinfo("Succès", "Le disque a été retiré de la base.")
            except mysql.connector.Error as err:
                messagebox.showerror("Erreur SQL", f"Échec de la suppression :\n{err}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()

    # ======================
    # POSITIONNEMENT DES BOUTONS PRINCIPAUX
    # ======================
    # Ces boutons se trouvent bien dans main_window et s'affichent en bas de l'écran principal
    tk.Button(frm_actions, text="Ajouter un disque", command=insert_window, bg="#198754", fg="white", width=18).grid(row=0, column=0, padx=10)
    tk.Button(frm_actions, text="Modifier sélection", command=modify_window, bg="#0d6efd", fg="white", width=18).grid(row=0, column=1, padx=10)
    tk.Button(frm_actions, text="Supprimer sélection", command=delete_entry, bg="#dc3545", fg="white", width=18).grid(row=0, column=2, padx=10)

        # ==========================================
    # 🔐 SÉCURITÉ : PRINCIPE DU MOINDRE PRIVILÈGE
    # ==========================================
    # Si le profil connecté est 'admin', les boutons sont actifs ('normal')
    # Sinon, pour le profil 'user' (employé), ils sont verrouillés ('disabled')
    etat_privilege = "normal" if user_role == "admin" else "disabled"

    # Application de l'état sur vos boutons d'action :
    btn_ajouter = tk.Button(frm_actions, text="Ajouter un disque", command=insert_window, bg="#198754", fg="white", width=18, state=etat_privilege)
    btn_ajouter.grid(row=0, column=0, padx=10)

    btn_modifier = tk.Button(frm_actions, text="Modifier sélection", command=modify_window, bg="#0d6efd", fg="white", width=18, state=etat_privilege)
    btn_modifier.grid(row=0, column=1, padx=10)

    btn_supprimer = tk.Button(frm_actions, text="Supprimer sélection", command=delete_entry, bg="#dc3545", fg="white", width=18, state=etat_privilege)
    btn_supprimer.grid(row=0, column=2, padx=10)
