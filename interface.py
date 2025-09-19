# -*- coding: utf-8 -*-
"""Interface graphique principale - Luxuria Studio"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import assistant_pdg  # ✅ Orchestrateur unique

class LuxuriaInterface(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Luxuria - Accueil")
        self.geometry("400x300")
        self.configure(bg="#f5f5f5")
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Bienvenue sur Luxuria", font=("Arial", 16), bg="#f5f5f5").pack(pady=20)

        boutons = [
            ("Accès Client", LuxuriaInterface.acces_client),
            ("Nouveau Client", LuxuriaInterface.nouveau_client),
            ("Accès Administrateur", LuxuriaInterface.acces_admin)
        ]

        for texte, action in boutons:
            tk.Button(self, text=texte, command=action, width=30).pack(pady=8)

    @staticmethod
    def acces_client():
        identifiant = simpledialog.askstring("Client", "Identifiant :")
        cle = simpledialog.askstring("Client", "Clé d'accès :")
        if not identifiant or not cle:
            messagebox.showerror("Erreur", "Champs requis manquants.")
            return
        if assistant_pdg.verifier_access(role="client", identifiant=identifiant, cle=cle):
            assistant_pdg.ouvrir_interface(role="client", identifiant=identifiant)
        else:
            messagebox.showerror("Erreur", "Accès client refusé.")

    @staticmethod
    def nouveau_client():
        assistant_pdg.demarrer_inscription(role="client")
        messagebox.showinfo("Nouveau Client", "Inscription lancée.")

    @staticmethod
    def acces_admin():
        identifiant = simpledialog.askstring("Administrateur", "Identifiant :")
        mdp = simpledialog.askstring("Administrateur", "Mot de passe :", show="*")
        if not identifiant or not mdp:
            messagebox.showerror("Erreur", "Champs requis manquants.")
            return
        if assistant_pdg.verifier_access(role="admin", identifiant=identifiant, mot_de_passe=mdp):
            assistant_pdg.ouvrir_interface(role="admin", identifiant=identifiant)
        else:
            messagebox.showerror("Erreur", "Accès administrateur refusé.")

# === Orchestration graphique
def run():
    LuxuriaInterface().mainloop()
