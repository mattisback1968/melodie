
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
#import cnx 

# ======================
# Connexion BDD
# ======================
def get_connection():
    # ✅ Vérification cnx MySQL
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # à adapter
        database="csv_db 6"
    )

# ======================
# Fenêtre principale
# ======================
def main_window():
    global tree
    win = tk.Tk()
    win.title("Disquaire - Tkinter MySQL")
    win.geometry("900x450")

    # --- Frame Recherche
    frm_search = tk.Frame(win)
    frm_search.pack(pady=10)

    tk.Label(frm_search, text="Artiste:").grid(row=0, column=0)
    artist_entry = tk.Entry(frm_search)
    artist_entry.grid(row=0, column=1)

    tk.Label(frm_search, text="Prix >").grid(row=0, column=2)
    price_entry = tk.Entry(frm_search, width=10)
    price_entry.grid(row=0, column=3)

    # ✅ Fonction Recherche
    def search():
        # 🔹 Supprime toutes les lignes actuelles
        for row in tree.get_children():
            tree.delete(row)
        query = "SELECT id, artist, title, format, media_condition, sleeve_condition, price FROM melodie"# WHERE 1"
        params = []
        if artist_entry.get():
            query += " AND LOWER(artist) LIKE %s"
            params.append(f"%{artist_entry.get().lower()}%")
        if price_entry.get():
            try:
                params.append(float(price_entry.get()))
                query += " AND prix > %s"
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        for r in cursor.fetchall():
            # 🔹 iid = PK pour modification/suppression invisibles
            tree.insert('', 'end', iid=r[0], values=r[1:])
        cursor.close()
        conn.close()

    tk.Button(frm_search, text="Rechercher", command=search).grid(row=0, column=4, padx=5)

    # --- Treeview
    columns = ("Artiste", "Titre", "Format", "Media_condition", "Sleeve_condition", "Prix")
    tree = ttk.Treeview(win, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10, fill="both", expand=True)

    # ======================
    # Fonctions Insérer / Modifier / Supprimer
    # ======================
    def insert_window():
        win_ins = tk.Toplevel(win)
        win_ins.title("Insérer un disque")
        labels = ["Artiste", "Titre", "Format", "Media Condition", "Sleeve Condition", "Prix"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(win_ins, text=label).grid(row=i, column=0)
            e = tk.Entry(win_ins)
            e.grid(row=i, column=1)
            entries[label] = e

        def insert():
            # ✅ Valider les champs
            try:
                prix_val = float(entries["Prix"].get())
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return
            data = (
                entries["Artiste"].get(),
                entries["Titre"].get(),
                entries["Support"].get(),
                entries["Media Condition"].get(),
                entries["Sleeve Condition"].get(),
                prix_val
            )
            conn = get_connection()
            cursor = conn.cursor()
            query = """
            INSERT INTO melodie (artist, title, format, media_condition, sleeve_condition, price)
            VALUES (%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(query, data)
            conn.commit()
            pk = cursor.lastrowid
            cursor.close()
            conn.close()
            tree.insert('', 'end', iid=pk, values=data)
            win_ins.destroy()

        tk.Button(win_ins, text="Valider", command=insert).grid(row=len(labels), column=0, columnspan=2, pady=5)

    def modify_window():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une ligne à modifier")
            return
        pk = selected[0]
        values = tree.item(pk, "values")
        win_mod = tk.Toplevel(win)
        win_mod.title("Modifier disque")
        labels = ["Artiste", "Titre", "Support", "État du support", "État de la pochette", "Prix"]
        entries = {}
        for i, label in enumerate(labels):
            tk.Label(win_mod, text=label).grid(row=i, column=0)
            e = tk.Entry(win_mod)
            e.grid(row=i, column=1)
            e.insert(0, values[i])
            entries[label] = e

        def update():
            try:
                prix_val = float(entries["Prix"].get())
            except ValueError:
                messagebox.showerror("Erreur", "Prix doit être un nombre")
                return
            data = (
                entries["Artiste"].get(),
                entries["Titre"].get(),
                entries["Support"].get(),
                entries["Media Condition"].get(),
                entries["Sleeve Condition"].get(),
                prix_val,
                pk
            )
            conn = get_connection()
            cursor = conn.cursor()
            query = """
            UPDATE melodie SET artist=%s, title=%s,format=%s, media_condition=%s, sleeve_condition=%s, price=%s
            WHERE id=%s
            """
            cursor.execute(query, data)
            conn.commit()
            cursor.close()
            conn.close()
            tree.item(pk, values=data[:-1])
            win_mod.destroy()

        tk.Button(win_mod, text="Valider", command=update).grid(row=len(labels), column=0, columnspan=2, pady=5)

    def delete_entry():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Attention", "Sélectionnez une ligne à supprimer")
            return
        pk = selected[0]
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment supprimer ce disque ?"):
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM melodie WHERE id=%s", (pk,))
            conn.commit()
            cursor.close()
            conn.close()
            tree.delete(pk)

    # --- Boutons
    frm_buttons = tk.Frame(win)
    frm_buttons.pack(pady=5)
    tk.Button(frm_buttons, text="Insérer", command=insert_window).grid(row=0, column=0, padx=5)
    tk.Button(frm_buttons, text="Modifier", command=modify_window).grid(row=0, column=1, padx=5)
    tk.Button(frm_buttons, text="Supprimer", command=delete_entry).grid(row=0, column=2, padx=5)

    win.mainloop()

if __name__ == "__main__":
    main_window()
