# === Module : admin (fusionné)



# Orchestration centralisée
from assistant_pdg import AssistantPDG

def run():
    print("Module exécuté via AssistantPDG")

AssistantPDG.register("luxuria_admin", run)
