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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
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

    # --- SÉCURITÉ : Vérifier si la colonne Motif_Annulation existe (Migration) ---
    cursor.execute("PRAGMA table_info(transactions)")
    colonnes = [info[1] for info in cursor.fetchall()]
    if "Motif_Annulation" not in colonnes:
        cursor.execute("ALTER TABLE transactions ADD COLUMN Motif_Annulation TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            emp_id TEXT PRIMARY KEY,
            nom TEXT,
            cle_acces TEXT
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM employes")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """
            INSERT INTO employes (emp_id, nom, cle_acces) VALUES (?, ?, ?)
        """,
            [("EMP001", "Awa", "1234"), ("EMP002", "Moussa", "abcd")],
        )
    conn.commit()
    conn.close()


def db_ajouter_transaction(tx_id, date, service, type_op, montant, telephone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO transactions (ID, Date, Service, Type, Montant, Client_Tel, Agent, Statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (tx_id, date, service, type_op, montant, telephone, "Aucun", "En attente"),
    )
    conn.commit()
    conn.close()


def db_lire_transactions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    return df


def db_mettre_a_jour_statut(tx_id, nouveau_statut, agent, motif=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE transactions 
        SET Statut = ?, Agent = ?, Motif_Annulation = ? 
        WHERE ID = ?
    """,
        (nouveau_statut, agent, motif, tx_id),
    )
    conn.commit()
    conn.close()


def db_lire_employes():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM employes", conn)
    conn.close()
    return df


def db_ajouter_employe(emp_id, nom, cle_acces):
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO employes (emp_id, nom, cle_acces) VALUES (?, ?, ?)",
            (emp_id, nom, cle_acces),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def db_supprimer_employe(emp_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employes WHERE emp_id = ?", (emp_id,))
    conn.commit()
    conn.close()


init_db()

# -------------------------------------------------------------------------
# 🎨 STYLE CSS (MIS À JOUR AVEC LE THÈME CATPPUCCIN PASTEL)
# -------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'Inter', sans-serif; 
        color: #cdd6f4; /* Catppuccin Text */
    }
    
    /* --- SPLASH SCREEN --- */

    .full-screen-loader {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        /* On remet ton ancienne image de pirogue avec un léger filtre sombre pastel */
        background-image: linear-gradient(rgba(30, 30, 46, 0.4), rgba(30, 30, 46, 0.8)), url("https://i.imgur.com/XWvlWeK.jpeg");
        background-size: cover; background-position: center; z-index: 99999;
        display: flex; flex-direction: column; align-items: center; justify-content: center; color: #cdd6f4;
    }
    .loader-content {
        text-align: center; background: rgba(24, 24, 37, 0.75); padding: 40px; border-radius: 20px; box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        backdrop-filter: blur(5px); /* Petit effet flou moderne derrière le texte */
    }
    
    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #11111b !important; /* Catppuccin Crust */
        background-image: none !important;
    }
    .sidebar-profile-img {
        display: block; margin: 0 auto 15px auto; width: 100px; height: 100px; border-radius: 50%; object-fit: cover; 
        border: 3px solid #b4bfe2; /* Catppuccin Lavender */
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .profile-box {
        background: #181825; /* Catppuccin Mantle */
        border: 1px solid #313244; /* Catppuccin Surface0 */
        border-radius: 12px; padding: 20px; text-align: center;
    }
    
    /* --- INTERFACE PRINCIPALE --- */
    .stApp {
        background-color: #1e1e2e !important; /* Catppuccin Base */
        background-image: none !important;
    }
    .brand-hero { text-align: center; padding: 60px 0 40px 0; }
    .hero-title { color: #cba6f7; font-weight: 800; font-size: 4rem !important; margin-bottom: 10px !important; letter-spacing: -1px; } /* Catppuccin Mauve */
    .hero-slogan { color: #89b4fa !important; font-weight: 700; letter-spacing: 10px; font-size: 1.6rem; text-transform: uppercase; margin-bottom: 35px !important; } /* Catppuccin Blue */
    
    /* --- BOUTONS --- */
    .stButton > button {
        background: linear-gradient(135deg, #cba6f7 0%, #89b4fa 100%) !important; /* Dégradé Mauve vers Bleu */
        color: #11111b !important; font-weight: 700; border-radius: 10px; padding: 15px 25px; border: none;
        box-shadow: 0 4px 15px rgba(203, 166, 247, 0.2);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #b4bfe2 0%, #74c7ec 100%) !important;
        color: #11111b !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- GESTION DES SESSIONS ---
if "chargement_termine" not in st.session_state:
    st.session_state.chargement_termine = False
if "en_cours_de_validation" not in st.session_state:
    st.session_state.en_cours_de_validation = False
if "temp_transaction" not in st.session_state:
    st.session_state.temp_transaction = {}

# --- SPLASH SCREEN ---
if not st.session_state.chargement_termine:
    st.markdown(
        '<div class="full-screen-loader"><div class="loader-content"><h1 style="font-size: 4rem; color: #cba6f7;">SUNU KOOPAR</h1><p style="letter-spacing: 6px; color: #89b4fa; text-transform: uppercase;">Chargement...</p></div></div>',
        unsafe_allow_html=True,
    )
    time.sleep(1.2)
    st.session_state.chargement_termine = True
    st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<img src="https://www.w3schools.com/howto/img_avatar.png" class="sidebar-profile-img">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="profile-box"><p style="color:#89b4fa; font-weight:700;">👤 ESPACE COMPTE</p>',
        unsafe_allow_html=True,
    )
    profil = st.selectbox(
        "Profil",
        ["— Choisir —", "Client", "Employé", "Administrateur"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("🇸🇳 SUNU KOOPAR v2.5")

# --- HEADER ---
st.markdown(
    '<div class="brand-hero"><h1 class="hero-title">SUNU KOOPAR</h1><p class="hero-slogan">Rapide, Simple et Efficace</p></div>',
    unsafe_allow_html=True,
)

# 1. CLIENT
if profil == "Client":
    st.header("📱 Espace Client")
    col1, col2 = st.columns(2)
    with col1:
        service = st.selectbox(
            "Service",
            ["Wave", "Orange Money", "Wizall", "Touch Point", "Djamo"],
            disabled=st.session_state.en_cours_de_validation,
        )
        try:
            if service == "Wave":
                st.image("wave.png", width=100)
            elif service == "Orange Money":
                st.image("images/orange_money.jpg", width=100)
            elif service == "Touch Point":
                st.image("touch_point.png", width=100)
            elif service == "wizall":
                st.image("wizall.png", width=100)
            elif service == "djamo":
                st.image("djamo.png", width=100)
        except:
            st.info(f"Image {service} non trouvée.")
    with col2:
        type_op = st.radio(
            "Opération",
            ["Dépôt", "Retrait"],
            disabled=st.session_state.en_cours_de_validation,
        )

    montant = st.number_input(
        "Montant",
        min_value=100,
        step=100,
        value=1000,
        disabled=st.session_state.en_cours_de_validation,
    )
    telephone = st.text_input(
        "Téléphone",
        placeholder="7xxxxxxxx",
        disabled=st.session_state.en_cours_de_validation,
    )

    if not st.session_state.en_cours_de_validation:
        if st.button("Valider la demande", use_container_width=True):
            if len(telephone) == 9 and telephone.startswith("7"):
                tx_id = f"TX-{random.randint(1000,9999)}"
                db_ajouter_transaction(
                    tx_id,
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    service,
                    type_op,
                    montant,
                    telephone,
                )
                st.success("Demande envoyée !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Numéro invalide.")

# 2. EMPLOYÉ
elif profil == "Employé":
    st.header("💼 Espace Employé")
    cle = st.text_input("Clé d'accès", type="password")
    df_emp = db_lire_employes()
    if cle and not df_emp[df_emp["cle_acces"] == cle].empty:
        nom_agent = df_emp[df_emp["cle_acces"] == cle].iloc[0]["nom"]
        st.success(f"Connecté : {nom_agent}")
        df_t = db_lire_transactions()
        attente = df_t[df_t["Statut"] == "En attente"]
        if not attente.empty:
            st.dataframe(attente, use_container_width=True)
            id_t = attente.iloc[-1]["ID"]
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Valider", use_container_width=True):
                    db_mettre_a_jour_statut(id_t, "Validé", nom_agent)
                    st.rerun()
            with col_b:
                motif = st.text_input("Motif si annulation")
                if st.button("❌ Annuler", use_container_width=True):
                    if motif:
                        db_mettre_a_jour_statut(id_t, "Annulé", nom_agent, motif)
                        st.rerun()
                    else:
                        st.warning("Saisissez un motif.")
        else:
            st.info("Rien en attente.")

# 3. ADMIN
elif profil == "Administrateur":
    st.header("🛡️ Admin")
    user = st.text_input("User")
    pwd = st.text_input("PWD", type="password")
    if user == "kuromi" and pwd == "password":
        t1, t2 = st.tabs(["📊 Transactions", "👥 Équipe"])
        with t1:
            df = db_lire_transactions()
            if not df.empty:
                # --- PREPARATION DES COURBES ---
                df["Date_dt"] = pd.to_datetime(df["Date"])
                df["Flux"] = df.apply(
                    lambda x: x["Montant"] if x["Type"] == "Dépôt" else -x["Montant"],
                    axis=1,
                )

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("📈 Flux Financier")
                    # Courbe en Mauve Catppuccin
                    st.line_chart(df.set_index("Date_dt")["Flux"], color="#cba6f7")
                with c2:
                    st.write("👷 Activité Agents")
                    if "Agent" in df.columns:
                        # Histogramme en Bleu Lavande Catppuccin
                        st.bar_chart(df["Agent"].value_counts(), color="#b4bfe2")
                with c3:
                    st.write("❌ Annulations par motif")
                    annuls = df[df["Statut"] == "Annulé"]
                    if not annuls.empty:
                        # Histogramme des annulations en Rouge Pastel (Peach/Flamingo)
                        st.bar_chart(
                            annuls["Motif_Annulation"].value_counts(), color="#f5e0dc"
                        )

                st.dataframe(df, use_container_width=True)
            else:
                st.info("Base vide.")
        with t2:
            df_liste_employes = db_lire_employes()
            st.dataframe(df_liste_employes, use_container_width=True)

            st.markdown("---")
            col_ajouter, col_retirer = st.columns(2)

            with col_ajouter:
                st.subheader("➕ Ajouter un employé")
                new_id = st.text_input("Identifiant unique (ex: EMP003)", key="add_id")
                new_nom = st.text_input("Nom de l'employé", key="add_nom")
                new_cle = st.text_input(
                    "Clé d'accès / Mot de passe", type="password", key="add_cle"
                )

                if st.button("Créer le compte", use_container_width=True):
                    if new_id and new_nom and new_cle:
                        success = db_ajouter_employe(new_id, new_nom, new_cle)
                        if success:
                            st.success(f"✨ {new_nom} ajouté avec succès !")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Cet identifiant unique existe déjà.")
                    else:
                        st.warning("Veuillez remplir tous les champs.")

            with col_retirer:
                st.subheader("🗑️ Retirer un employé")
                if not df_liste_employes.empty:
                    options_employes = [
                        f"{row['emp_id']} - {row['nom']}"
                        for _, row in df_liste_employes.iterrows()
                    ]
                    employe_selectionne = st.selectbox(
                        "Sélectionner l'employé à révoquer", options_employes
                    )

                    id_cible = employe_selectionne.split(" - ")[0]

                    if st.button("Supprimer définitivement", use_container_width=True):
                        db_supprimer_employe(id_cible)
                        st.error(f"🔴 {employe_selectionne} a été retiré du système.")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.info("Aucun employé inscrit dans le système.")