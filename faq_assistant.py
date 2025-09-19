# -*- coding: utf-8 -*-
"""Assistant FAQ interactif - Luxuria Studio"""

import logging
from datetime import datetime
from typing import List, Dict
from assistant_pdg import AssistantPDG

logging.basicConfig(level=logging.INFO, format="[FAQ] %(message)s")

class FAQAssistant:
    def __init__(self) -> None:
        self.questions_posees: List[str] = []
        self.base_faq: Dict[str, str] = {
            "paiement": "Les paiements se font via carte bancaire ou virement. Une facture est générée automatiquement.",
            "design": "Vous pouvez créer un design en entrant des mots-clés ou en utilisant l'assistant gratuit.",
            "croquis": "Les croquis générés sont basés sur vos instructions. Vous pouvez les personnaliser librement.",
            "pdf": "Les documents PDF sont générés automatiquement une fois le paiement validé.",
            "matériaux": "Nous suggérons des matériaux haut de gamme : marbre, bois noble, laiton, verre trempé, etc.",
            "assistance": "L'assistance est gratuite pour les croquis. Pour un accompagnement complet, un forfait est proposé.",
        }

    def poser_question(self, question: str) -> str:
        question = question.lower().strip()
        horodatage = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.questions_posees.append(f"{horodatage} - {question}")

        for mot_cle, reponse in self.base_faq.items():
            if mot_cle in question:
                logging.info(f"Question : {question}\nRéponse : {reponse}")
                return reponse

        reponse_par_defaut = "Je n'ai pas encore de réponse précise à cette question, mais notre équipe peut vous aider sous 24h."
        logging.info(f"Question : {question}\nRéponse : {reponse_par_defaut}")
        return reponse_par_defaut

    def suggestions_faq(self) -> List[str]:
        suggestions = list(self.base_faq.keys())
        logging.info("Suggestions de questions fréquentes :")
        for s in suggestions:
            logging.info(f"- {s.capitalize()}")
        return suggestions

    def historique(self) -> List[str]:
        logging.info("Historique des questions posées :")
        for q in self.questions_posees:
            logging.info(f"- {q}")
        return self.questions_posees

# === Orchestration centralisée
def run():
    assistant = FAQAssistant()
    assistant.poser_question("Comment fonctionne le paiement ?")
    assistant.suggestions_faq()
    assistant.historique()

AssistantPDG.register("faq_assistant", run)
