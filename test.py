import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random
import sqlite3

# Configuration de la page
st.set_page_config(page_title="SUNU KOOPAR", page_icon="🏦", layout="wide")

# -------------------------------------------------------------------------
# 🗄️ CONFIGURATION ET FONCTIONS DE LA BASE DE DONNÉES SQL
# -------------------------------------------------------------------------
DB_NAME = "koopar.db"

def init_db():
    """Crée les tables des transactions et des employés si elles n'existent pas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Table des transactions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            ID TEXT PRIMARY KEY,
            Date TEXT,
            Service TEXT,
            Type TEXT,
            Montant REAL,
            Client_Tel TEXT,
            Agent TEXT,
            Statut TEXT,
            Motif_Annulation TEXT
        )
    """)
    # Table des employés
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            emp_id TEXT PRIMARY KEY,
            nom TEXT,
            cle_acces TEXT
        )
    """)
    
    # Insertion des employés par défaut si la table est complètement vide
    cursor.execute("SELECT COUNT(*) FROM employes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO employes (emp_id, nom, cle_acces) VALUES (?, ?, ?)
        """, [("EMP001", "Awa", "1234"), ("EMP002", "Moussa", "abcd")])
        
    conn.commit()
    conn.close()

def db_ajouter_transaction(tx_id, date, service, type_op, montant, telephone):
    """Insère une nouvelle demande de transaction en attente."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (ID, Date, Service, Type, Montant, Client_Tel, Agent, Statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (tx_id, date, service, type_op, montant, telephone, "En attente", "En attente"))
    conn.commit()
    conn.close()

def db_lire_transactions():
    """Récupère toutes les transactions sous forme de DataFrame Pandas."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df

def db_mettre_a_jour_statut(tx_id, nouveau_statut, agent, motif=None):
    """Met à jour le statut d'une transaction (Validation ou Annulation)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions 
        SET Statut = ?, Agent = ?, Motif_Annulation = ? 
        WHERE ID = ?
    """, (nouveau_statut, agent, motif, tx_id))
    conn.commit()
    conn.close()

# --- NOUVELLES FONCTIONS DE GESTION DES EMPLOYÉS ---
def db_lire_employes():
    """Récupère la liste de tous les employés."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM employes", conn)
    conn.close()
    return df

def db_ajouter_employe(emp_id, nom, cle_acces):
    """Ajoute un nouvel employé dans la base de données."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO employes (emp_id, nom, cle_acces) VALUES (?, ?, ?)", (emp_id, nom, cle_acces))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False  # L'identifiant existe déjà

def db_supprimer_employe(emp_id):
    """Supprime un employé à partir de son identifiant."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employes WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()

# Initialisation automatique de la base SQL au lancement
init_db()

# -------------------------------------------------------------------------
# 🎨 STYLE CSS (SPLASH SCREEN PLEIN ÉCRAN NET & INTERFACE TRÈS AÉRÉE)
# -------------------------------------------------------------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    /* --- SPLASH SCREEN PLEIN ÉCRAN --- */
    .full-screen-loader {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-image: linear-gradient(rgba(0,0,0,0.2), rgba(0,0,0,0.7)), url("https://i.imgur.com/XWvlWeK.jpeg");
        background-size: cover;
        background-position: center;
        z-index: 99999;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: white;
    }

    .loader-content {
        text-align: center;
        background: rgba(0, 0, 0, 0.55);
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.5);
    }

    /* --- SIDEBAR & PROFIL --- */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(rgba(15, 23, 42, 0.94), rgba(2, 6, 23, 0.98)), 
                          url("https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1000");
        background-size: cover;
        background-position: center;
    }

    .sidebar-profile-img {
        display: block;
        margin: 0 auto 15px auto;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #fbbf24;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    .profile-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }

    /* --- INTERFACE PRINCIPALE PLUS AÉRÉE --- */
    .stApp {
        background-image: linear-gradient(135deg, rgba(30, 41, 59, 0.92) 0%, rgba(15, 23, 42, 0.96) 100%),
                          url("https://images.unsplash.com/photo-1542831371-29b0f74f9713?q=80&w=1000");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .brand-hero {
        text-align: center;
        padding: 80px 0 60px 0;
    }
    
    .hero-title {
        color: white;
        font-weight: 800;
        font-size: 4rem !important;
        margin-bottom: 20px !important;
        letter-spacing: -1px;
    }
    
    .hero-slogan {
        color: #fbbf24 !important;
        font-weight: 700;
        letter-spacing: 10px;
        font-size: 1.6rem;
        text-transform: uppercase;
        margin-bottom: 35px !important;
    }

    .hero-caption {
        color: #94a3b8 !important;
        font-size: 1.25rem;
        max-width: 850px;
        margin: 0 auto;
        line-height: 1.8;
    }

    .stButton > button {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        color: #020617 !important;
        font-weight: 700;
        border-radius: 10px;
        padding: 15px 25px;
        border: none;
        box-shadow: 0 10px 20px -5px rgba(217, 119, 6, 0.3);
    }
    </style>"""
    ,
    unsafe_allow_html=True
)

# --- INITIALISATION DE SESSION DE L'INTERFACE ---
if "chargement_termine" not in st.session_state:
    st.session_state.chargement_termine = False

if "code_sms_genere" not in st.session_state:
    st.session_state.code_sms_genere = None
if "en_cours_de_validation" not in st.session_state:
    st.session_state.en_cours_de_validation = False
if "temp_transaction" not in st.session_state:
    st.session_state.temp_transaction = {}
if "ancien_profil" not in st.session_state:
    st.session_state.ancien_profil = "— Choisir un profil —"

# -------------------------------------------------------------------------
# ⌛ SPLASH SCREEN PLEIN ÉCRAN
# -------------------------------------------------------------------------
if not st.session_state.chargement_termine:
    st.markdown("""
        <div class="full-screen-loader">
            <div class="loader-content">
                <h1 style="font-size: 4rem; margin: 0 0 10px 0; text-shadow: 2px 2px 15px rgba(0,0,0,0.6); color: white;">SUNU KOOPAR</h1>
                <p style="letter-spacing: 6px; font-weight: 700; color: #fbbf24; margin-bottom: 30px; text-transform: uppercase;">Rapide, Simple et Efficace</p>
                <div id="progress-container"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1.2, 1.6, 1.2])
    with col_b2:
        barre = st.progress(0)
        time.sleep(0.4)
        barre.progress(25)
        time.sleep(0.3)
        barre.progress(80)
        time.sleep(0.3)
        barre.progress(100)
        time.sleep(0.2)

    st.session_state.chargement_termine = True
    st.rerun()

# -------------------------------------------------------------------------
# 🏦 APPLICATION PRINCIPALE
# -------------------------------------------------------------------------
else:
    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <img src="https://www.w3schools.com/howto/img_avatar.png" class="sidebar-profile-img">
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="profile-box"><p style="color:#fbbf24; font-weight:700; margin-bottom:10px;">👤 ESPACE COMPTE</p>', unsafe_allow_html=True)
        profil = st.selectbox("Choisir un profil", ["— Choisir un profil —", "Client", "Employé", "Administrateur"], label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.caption("🇸🇳 SUNU KOOPAR v2.1")

    if profil != st.session_state.ancien_profil:
        st.session_state.en_cours_de_validation = False
        st.session_state.code_sms_genere = None
        st.session_state.temp_transaction = {}
        st.session_state.ancien_profil = profil

    # --- EN-TÊTE CENTRAL ---
    st.markdown("""
        <div class="brand-hero">
            <div style="background: linear-gradient(135deg, #FFE066 0%, #F59E0B 50%, #B45309 100%); color: #020617; width: 85px; height: 85px; border-radius: 24px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 2.3rem; margin: 0 auto 30px auto; box-shadow: 0 20px 40px -10px rgba(245, 158, 11, 0.4);">SK</div>
            <h1 class="hero-title">SUNU KOOPAR</h1>
            <p class="hero-slogan">Rapide, Simple et Efficace</p>
            <p class="hero-caption">La solution sénégalaise pour gérer vos transactions Wave, Orange Money et Wizall en un seul endroit.</p>
        </div>
        """, unsafe_allow_html=True)

    # 1. INTERFACE CLIENT
    if profil == "Client":
        st.header("📱 Espace Client")
        
        col1, col2 = st.columns(2)
        with col1:
            service = st.selectbox("Application", ["Wave", "Orange Money", "Wizall", "Touch Point", "Djamo"], disabled=st.session_state.en_cours_de_validation)
            if service == "Wave": st.image("images/wave.png")
            elif service =="Orange Money": st.image("images/orange_money.jpg")
            elif service == "Wizall": st.image("images/wizall.png")
            elif service == "Djamo": st.image("images/djamo.png")
            elif service == "Touch Point": st.image("images/touch_point.png")
        with col2:
            type_op = st.radio("Opération", ["Dépôt", "Retrait"], disabled=st.session_state.en_cours_de_validation)
            
        if st.session_state.en_cours_de_validation:
            st.number_input("Montant (FCFA)", value=st.session_state.temp_transaction["Montant"], disabled=True)
            st.text_input("Numéro de téléphone", value=st.session_state.temp_transaction["Client_Tel"], disabled=True)
        else:
            montant = st.number_input("Montant (FCFA)", min_value=100, step=100, value=1000)
            telephone = st.text_input("Numéro de téléphone", help="Doit obligatoirement commencer par un 7 et contenir 9 chiffres au total.")
        
        st.caption("⚠️ *Le numéro doit impérativement commencer par un **7** et contenir exactement **9 chiffres**.*")
        
        if not st.session_state.en_cours_de_validation:
            if st.button("Demander le code de validation SMS", use_container_width=True):
                if telephone.isdigit() and len(telephone) == 9 and telephone.startswith("7"):
                    st.session_state.code_sms_genere = str(random.randint(1000, 9999))
                    st.session_state.en_cours_de_validation = True
                    st.session_state.temp_transaction = {
                        "Service": service,
                        "Type": type_op,
                        "Montant": montant,
                        "Client_Tel": telephone
                    }
                    st.rerun()
                else:
                    st.error("❌ Erreur : Le numéro doit comporter 9 chiffres et commencer par un 7.")

        else:
            st.markdown("---")
            st.info(f"📱 **[SIMULATION SMS]** Le code secret envoyé sur le numéro {st.session_state.temp_transaction['Client_Tel']} est : **{st.session_state.code_sms_genere}**")
            
            code_saisi = st.text_input("👉 Entrez le code à 4 chiffres ci-dessus pour confirmer", max_chars=4, type="password", key="input_otp")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Confirmer et Valider la demande", use_container_width=True):
                    if code_saisi == st.session_state.code_sms_genere:
                        tx_id = f"TX-{datetime.now().strftime('%M%S')}"
                        t_data = st.session_state.temp_transaction
                        
                        # 💾 SAUVEGARDE DANS LA BASE SQL
                        db_ajouter_transaction(
                            tx_id=tx_id,
                            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            service=t_data["Service"],
                            type_op=t_data["Type"],
                            montant=t_data["Montant"],
                            telephone=t_data["Client_Tel"]
                        )
                        
                        st.success(f"✅ Transaction {tx_id} enregistrée en Base SQL avec succès !")
                        st.session_state.en_cours_de_validation = False
                        st.session_state.code_sms_genere = None
                        st.session_state.temp_transaction = {}
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.error("❌ Code incorrect. Veuillez recopier le code indiqué juste au-dessus.")
            
            with col_btn2:
                if st.button("Annuler la demande", use_container_width=True):
                    st.session_state.en_cours_de_validation = False
                    st.session_state.code_sms_genere = None
                    st.session_state.temp_transaction = {}
                    st.rerun()

    # 2. INTERFACE EMPLOYÉ
    elif profil == "Employé":
        st.header("💼 Espace Employé")
        cle_saisie = st.text_input("Entrez votre clé d'accès", type="password")
        
        # 🔄 LECTURE DEPUIS LA TABLE SQL DES EMPLOYÉS
        df_emp = db_lire_employes()
        
        if cle_saisie:
            agent_actif = df_emp[df_emp["cle_acces"] == cle_saisie]
            if not agent_actif.empty:
                nom_agent = agent_actif.iloc[0]["nom"]
                st.success(f"Bienvenue, {nom_agent} !")
                
                # 🔄 LECTURE DEPUIS LA BASE SQL
                df_trans = db_lire_transactions()
                
                if not df_trans.empty:
                    attente = df_trans[df_trans["Statut"] == "En attente"]
                else:
                    attente = pd.DataFrame()
                
                if not attente.empty:
                    st.dataframe(attente, use_container_width=True)
                    
                    choix = st.radio("Action sur la dernière transaction :", ["Valider", "Annuler"])
                    idx_last_row = attente.index[-1]
                    id_trans_cible = attente.at[idx_last_row, "ID"]
                    
                    if choix == "Valider":
                        if st.button("Confirmer la validation", use_container_width=True):
                            # 💾 MISE À JOURS SQL
                            db_mettre_a_jour_statut(id_trans_cible, "Validé", nom_agent)
                            st.success("Transaction validée et sauvegardée en base SQL !")
                            time.sleep(1)
                            st.rerun()
                            
                    elif choix == "Annuler":
                        motif = st.text_input("Motif de l'annulation :")
                        if st.button("Confirmer l'annulation", use_container_width=True):
                            if motif:
                                # 💾 MISE À JOUR SQL
                                db_mettre_a_jour_statut(id_trans_cible, "Annulé", nom_agent, motif)
                                st.error("Transaction annulée !")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.warning("Veuillez saisir un motif pour annuler.")
                else:
                    st.info("Aucune transaction en attente dans la base de données.")
            else:
                st.error("Clé d'accès incorrecte.")

    # 3. INTERFACE ADMINISTRATEUR
    elif profil == "Administrateur":
        st.header("🛡️ Panneau d'Administration")
        nom_admin = st.text_input("Nom d'utilisateur Admin")
        mot_de_passe = st.text_input("Mot de passe Admin", type="password")
        
        if nom_admin == "kuromi" and mot_de_passe == "password":
            st.success(f"Bienvenue, {nom_admin}. Accès accordé.")
            
            # Utilisation d'onglets pour séparer proprement la vue financière, l'analyse visuelle et la gestion d'équipe
            tab_finance, tab_analyse, tab_equipe = st.tabs(["📊 Suivi des Transactions", "📈 Analyses & Courbes", "👥 Gestion des Employés"])
            
            with tab_finance:
                # 🔄 LECTURE DE TOUTES LES TRANSACTIONS DEPUIS SQL
                toutes_les_transactions = db_lire_transactions()
                
                if not toutes_les_transactions.empty:
                    st.dataframe(toutes_les_transactions, use_container_width=True)
                    df_valide = toutes_les_transactions[toutes_les_transactions["Statut"] == "Validé"]
                
                    if not df_valide.empty:
                        total_depots = df_valide[df_valide["Type"] == "Dépôt"]["Montant"].sum()
                        total_retraits = df_valide[df_valide["Type"] == "Retrait"]["Montant"].sum()
                        c1, c2 = st.columns(2)
                        c1.metric("Total Dépôts", f"{int(total_depots):,} FCFA")
                        c2.metric("Total Retraits", f"{int(total_retraits):,} FCFA")
                    else:
                        st.info("Aucune transaction validée pour le moment.")
                else:
                    st.info("La base de données est vide.")
                    
            with tab_analyse:
                st.subheader("📈 Tableaux de Bord Visuels")
                toutes_les_transactions = db_lire_transactions()
                df_valide = toutes_les_transactions[toutes_les_transactions["Statut"] == "Validé"] if not toutes_les_transactions.empty else pd.DataFrame()

                if not df_valide.empty:
                    # Préparation des dates au format simple (AAAA-MM-JJ) pour des axes clairs
                    df_valide = df_valide.copy()
                    df_valide['Jour'] = df_valide['Date'].str.split(' ').str[0]

                    col_chart1, col_chart2 = st.columns(2)

                    with col_chart1:
                        st.markdown("#### 🔄 Flux Quotidiens : Dépôts vs Retraits")
                        # Pivot table pour croiser les flux par jour et par type (Dépôt / Retrait)
                        df_flux = df_valide.pivot_table(index='Jour', columns='Type', values='Montant', aggfunc='sum').fillna(0)
                        # Affichage de la courbe d'activité financière globale
                        st.line_chart(df_flux, use_container_width=True)

                    with col_chart2:
                        st.markdown("#### 💼 Volumes Financiers Traités par Employé")
                        # Pivot table pour croiser les montants par jour et par Agent
                        df_agents = df_valide[df_valide['Agent'] != 'En attente'].pivot_table(index='Jour', columns='Agent', values='Montant', aggfunc='sum').fillna(0)
                        if not df_agents.empty:
                            # Affichage de la courbe de performance par employé
                            st.line_chart(df_agents, use_container_width=True)
                        else:
                            st.info("Pas encore de données d'employés assignés.")
                else:
                    st.info("Veuillez valider des transactions pour générer les courbes d'analyses graphiques.")
                    
            with tab_equipe:
                st.subheader("👨‍💼 Équipe actuelle")
                df_liste_employes = db_lire_employes()
                st.dataframe(df_liste_employes, use_container_width=True)
                
                col_add, col_del = st.columns(2)
                
                with col_add:
                    st.markdown("### ➕ Ajouter un employé")
                    new_id = st.text_input("Identifiant Unique (ex: EMP003)", key="add_id")
                    new_nom = st.text_input("Nom de l'employé", key="add_nom")
                    new_cle = st.text_input("Clé d'accès / Mot de passe", type="password", key="add_cle")
                    
                    if st.button("Créer le compte", use_container_width=True):
                        if new_id and new_nom and new_cle:
                            success = db_ajouter_employe(new_id, new_nom, new_cle)
                            if success:
                                st.success(f"✨ {new_nom} a été ajouté à la base SQL !")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Cet Identifiant Unique existe déjà.")
                        else:
                            st.warning("Veuillez remplir tous les champs.")
                            
                with col_del:
                    st.markdown("### 🗑️ Retirer un employé")
                    if not df_liste_employes.empty:
                        # Liste déroulante des employés à supprimer sous format "ID - Nom"
                        liste_choix = [f"{row['emp_id']} - {row['nom']}" for _, row in df_liste_employes.iterrows()]
                        employe_a_supprimer = st.selectbox("Sélectionner l'employé à révoquer", liste_choix)
                        
                        id_cible = employe_a_supprimer.split(" - ")[0]
                        
                        if st.button("Supprimer définitivement", use_container_width=True):
                            db_supprimer_employe(id_cible)
                            st.error(f"🔴 Employé {employe_a_supprimer} retiré du système.")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.info("Aucun employé à supprimer.")
                        
        elif nom_admin or mot_de_passe:
            st.error("Nom d'utilisateur ou mot de passe incorrect.")