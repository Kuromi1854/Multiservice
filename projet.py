import streamlit as st
import pandas as pd
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="MultiCash Tracker by Djiwana's group", page_icon="🏦", layout="wide")

# --- SIMULATION BASE DE DONNÉES (À remplacer par SQL plus tard) ---
# Clés d'accès des employés
@st.cache_data
def load_employees():
    return pd.DataFrame({
        "emp_id": ["EMP001", "EMP002", "EMP003"],
        "nom": ["Djiwana", "Bamba", "Hashley"],
        "cle_acces": ["1234", "abcd", "hello"]
    })

# Historique des transactions
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=[
        "Date", "Service", "Type", "Montant", "Client_Tel", "Agent", "Statut"
    ])

# --- INTERFACE GRAPHIQUE PRINCIPALE ---
st.title("🏦 MultiCash Tracker")
st.caption("Plateforme centralisee de suivi de transactions (Wave, Orange Money, Wizall)")

# Sélection du profil
profil = st.sidebar.selectbox("Qui êtes-vous ?", ["— Choisir un profil —", "Client", "Employé", "Administrateur"])

# -------------------------------------------------------------------------
# 1. INTERFACE CLIENT
# -------------------------------------------------------------------------
if profil == "Client":
    st.header("📱 Espace Client")
    st.subheader("Sélectionnez votre service et votre opération")
    
    col1, col2 = st.columns(2)
    
    with col1:
        service = st.selectbox("Choisissez l'application", ["Wave", "Orange Money", "Wizall", "Djamo"])
        if service == "Wave":
            st.image("images/wave.png", width= 120)
        elif service == "Orange Money":
            st.image("images/orange_money.jpg", width= 120)
        elif service == "Wizall":
            st.image("images/wizall.png", width= 120)
        elif service == "Djamo":
            st.image("images/djamo.png", width= 120)
    with col2:
        type_op = st.radio("Opération", ["Dépôt (Insérer)", "Retrait"])
        
    montant = st.number_input("Montant (FCFA)", min_value=100, step=100)
    telephone = st.text_input("Numéro de téléphone")
    
    if st.button("Valider la demande", use_container_width=True):
        if telephone:
            # Enregistrement temporaire (Statut: En attente de validation par l'employé)
            nouvelle_trans = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Service": service,
                "Type": type_op,
                "Montant": montant,
                "Client_Tel": telephone,
                "Agent": "En attente",
                "Statut": "En attente"
            }])
            st.session_state.transactions = pd.concat([st.session_state.transactions, nouvelle_trans], ignore_index=True)
            st.success(f"Demande de {type_op} de {montant} FCFA via {service} envoyée à l'agent.")
        else:
            st.error("Veuillez entrer un numéro de téléphone valide.")

# -------------------------------------------------------------------------
# 2. INTERFACE EMPLOYÉ
# -------------------------------------------------------------------------
elif profil == "Employé":
    st.header("💼 Espace Employé")
    
    # Authentification par clé d'accès
    cle_saisie = st.text_input("Entrez votre clé d'accès", type="password")
    df_emp = load_employees()
    
    if cle_saisie:
        agent_actif = df_emp[df_emp["cle_acces"] == cle_saisie]
        
        if not agent_actif.empty:
            nom_agent = agent_actif.iloc[0]["nom"]
            st.success(f"Bienvenue, {nom_agent} !")
            
            # Gestion des transactions du point de vente
            st.subheader("Demandes clients en attente de validation")
            df_trans = st.session_state.transactions
            
            attente = df_trans[df_trans["Statut"] == "En attente"]
            if not attente.empty:
                st.dataframe(attente)
                # Option pour valider la dernière transaction pour l'exemple
                if st.button("Valider la dernière transaction en attente"):
                    idx = attente.index[-1]
                    st.session_state.transactions.at[idx, "Statut"] = "Validé"
                    st.session_state.transactions.at[idx, "Agent"] = nom_agent
                    st.rerun()
            else:
                st.info("Aucune transaction en attente.")
        else:
            st.error("Clé d'accès incorrecte.")

# -------------------------------------------------------------------------
# 3. INTERFACE ADMINISTRATEUR
# -------------------------------------------------------------------------
elif profil == "Administrateur":
    st.header("🛡️ Panneau d'Administration")
    
    # Formulaire d'identification complet
    nom_admin = st.text_input("Nom d'utilisateur Admin")
    mot_de_passe = st.text_input("Mot de passe Admin", type="password")
    
    # Vérification des identifiants demandés
    if nom_admin == "kuromi" and mot_de_passe == "password":
        st.success(f"Bienvenue, {nom_admin}. Accès accordé.")
        
        st.subheader("📈 Historique des Transactions de la Journée")
        if not st.session_state.transactions.empty:
            st.dataframe(st.session_state.transactions)
            
            # Petit dashboard de fin de journée avec Pandas
            st.subheader("📊 Résumé des flux")
            df_valide = st.session_state.transactions[st.session_state.transactions["Statut"] == "Validé"]
            
            if not df_valide.empty:
                total_depots = df_valide[df_valide["Type"] == "Dépôt (Insérer)"]["Montant"].sum()
                total_retraits = df_valide[df_valide["Type"] == "Retrait"]["Montant"].sum()
                
                c1, c2 = st.columns(2)
                c1.metric("Total Dépôts", f"{total_depots} FCFA")
                c2.metric("Total Retraits", f"{total_retraits} FCFA")
            else:
                st.info("Aucune transaction validée pour le moment.")
        else:
            st.info("Aucune transaction enregistrée aujourd'hui.")
            
    elif nom_admin or mot_de_passe:
        # Message d'erreur si l'un des champs est rempli mais ne correspond pas
        st.error("Nom d'utilisateur ou mot de passe incorrect.")