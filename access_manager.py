# access_manager.py

from assistant_pdg import AssistantPDG

# Fonctions d'accès exposées depuis assistant_pdg
verifier_admin = AssistantPDG.verifier_acces  # Utilise les identifiants admin
verifier_acces = lambda token: token == AssistantPDG.API_KEY

def get_admin_credentials() -> dict:
    return {
        "id": AssistantPDG.ADMIN_ID,
        "password": AssistantPDG.ADMIN_MDP
    }

def get_api_key() -> str:
    return AssistantPDG.API_KEY

class AccessManager:
    """Gestionnaire d'accès Luxuria [-] vérifie les identifiants et la clé API."""

    @staticmethod
    def verifier_admin_local(id_admin: str, mdp_admin: str) -> bool:
        return verifier_admin(id_admin, mdp_admin)

    @staticmethod
    def verifier_cle_api(token: str) -> bool:
        return verifier_acces(token)

    @staticmethod
    def initialiser_admin() -> dict:
        creds = get_admin_credentials()
        token = get_api_key()
        admin_valide = verifier_admin(creds["id"], creds["password"])
        cle_valide = verifier_acces(token)
        return {
            "admin_valide": admin_valide,
            "cle_valide": cle_valide
        }

# Orchestration centralisée
def run():
    print("=== Test AccessManager ===")
    status = AccessManager.initialiser_admin()
    print(" - Admin valide :", status["admin_valide"])
    print(" - Clé API valide :", status["cle_valide"])

# Enregistrement dans l’orchestrateur
AssistantPDG.register("access_manager", run)
