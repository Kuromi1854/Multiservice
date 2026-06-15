import streamlit as st
import pandas as pd
from datetime import datetime
import random
import sqlite3
import hashlib
import os

# 1. CONFIGURATION
st.set_page_config(page_title="SUNU KOOPAR PRO", page_icon="🏦", layout="wide")

DB_NAME = "sunu_koopar_pro.db"
LIMITE_TRANSACTION = 500000  # Plafond de 500 000 FCFA


# 2. FONCTIONS DE SÉCURITÉ (HACHAGE & VÉRIFICATION)
def hacher_mdp(mot_de_passe, sel=None):
    if not sel:
        sel = os.urandom(16).hex()
    encod_mdp = (mot_de_passe + sel).encode("utf-8")
    hachage = hashlib.sha256(encod_mdp).hexdigest()
    return f"{sel}${hachage}"


def verifier_mdp(mot_de_passe, mdp_stocke):
    try:
        if "$" not in mdp_stocke:
            return mot_de_passe == mdp_stocke
        sel, hachage_original = mdp_stocke.split("$")
        encod_mdp = (mot_de_passe + sel).encode("utf-8")
        nouveau_hachage = hashlib.sha256(encod_mdp).hexdigest()
        return nouveau_hachage == hachage_original
    except Exception:
        return False


def valider_numero_senegal(numero):
    numero = numero.strip().replace(" ", "")
    if (
        len(numero) == 9
        and numero.isdigit()
        and numero[:2] in ["77", "76", "75", "78", "70"]
    ):
        return numero
    return None


# 3. INITIALISATION DE LA BASE
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                ID TEXT PRIMARY KEY, Date TEXT, Service TEXT, Type TEXT, 
                Montant INTEGER, Frais REAL, Client_Tel TEXT, Agent TEXT, Statut TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS utilisateurs (
                Identifiant TEXT PRIMARY KEY, MotDePasse TEXT, Nom TEXT, Role TEXT, Telephone TEXT
            )
        """)
        cursor.execute(
            "DELETE FROM utilisateurs WHERE Identifiant IN ('admin', 'emp1', '771234567')"
        )
        cursor.execute(
            "INSERT OR REPLACE INTO utilisateurs VALUES ('admin', ?, 'Directeur Général', 'Administrateur', 'Pas de numéro')",
            (hacher_mdp("admin123"),),
        )
        cursor.execute(
            "INSERT OR REPLACE INTO utilisateurs VALUES ('emp1', ?, 'Fatou Caissière', 'Employé', 'Pas de numéro')",
            (hacher_mdp("emp123"),),
        )
        cursor.execute(
            "INSERT OR REPLACE INTO utilisateurs VALUES ('771234567', ?, 'Ibrahima Diallo', 'Client', '771234567')",
            (hacher_mdp("client123"),),
        )
        conn.commit()


# --- REQUÊTES & LOGIQUE MÉTIER ---
def calculer_solde_client(telephone):
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(
            "SELECT Type, Montant, Frais FROM transactions WHERE Client_Tel = ? AND Statut = 'Validé'",
            conn,
            params=(telephone,),
        )
    if df.empty:
        return 0.0
    depots = df[df["Type"].isin(["Dépôt", "Transfert Reçu"])]["Montant"].sum()
    retraits = (
        df[df["Type"] == "Retrait"]
        .apply(lambda r: r["Montant"] + r["Frais"], axis=1)
        .sum()
    )
    transferts_sortants = (
        df[df["Type"] == "Transfert Envoyé"]
        .apply(lambda r: r["Montant"] + r["Frais"], axis=1)
        .sum()
    )
    achats_credit = df[df["Type"] == "Achat Crédit"]["Montant"].sum()
    return float(depots - retraits - transferts_sortants - achats_credit)


def verifier_connexion_sql(identifiant, mdp):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT Identifiant, MotDePasse, Nom, Role, Telephone FROM utilisateurs WHERE Identifiant = ?",
            (identifiant,),
        )
        compte = cursor.fetchone()
        if compte and verifier_mdp(mdp, compte[1]):
            return (compte[0], compte[2], compte[3], compte[4])
        return None


def ajouter_utilisateur_sql(identifiant, mdp, nom, role, telephone):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            conn.cursor().execute(
                "INSERT INTO utilisateurs VALUES (?, ?, ?, ?, ?)",
                (identifiant, hacher_mdp(mdp), nom, role, telephone),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def modifier_mdp_sql(identifiant, nouveau_mdp):
    with sqlite3.connect(DB_NAME) as conn:
        conn.cursor().execute(
            "UPDATE utilisateurs SET MotDePasse = ? WHERE Identifiant = ?",
            (hacher_mdp(nouveau_mdp), identifiant),
        )
        conn.commit()


def ajouter_transaction_sql(
    tx_id,
    date,
    service,
    type_op,
    montant,
    frais,
    telephone,
    agent_nom,
    statut="En attente",
):
    with sqlite3.connect(DB_NAME) as conn:
        conn.cursor().execute(
            "INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                tx_id,
                date,
                service,
                type_op,
                montant,
                frais,
                telephone,
                agent_nom,
                statut,
            ),
        )
        conn.commit()


def changer_statut_transaction_sql(tx_id, nouveau_statut):
    with sqlite3.connect(DB_NAME) as conn:
        conn.cursor().execute(
            "UPDATE transactions SET Statut = ? WHERE ID = ?", (nouveau_statut, tx_id)
        )
        conn.commit()


def recuperer_transactions_sql():
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query("SELECT * FROM transactions ORDER BY Date DESC", conn)


def recuperer_utilisateurs_par_role(role):
    with sqlite3.connect(DB_NAME) as conn:
        return pd.read_sql_query(
            "SELECT Identifiant, Nom, Telephone FROM utilisateurs WHERE Role = ?",
            conn,
            params=(role,),
        )


init_db()

# VARIABLES DE SESSION
for key, default in {
    "authentifie": False,
    "utilisateur_id": None,
    "utilisateur_nom": None,
    "role": None,
    "telephone_client": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ==================================================================
# INJECTION DESIGN ET ARRIÈRE-PLANS (MONUMENT DE LA RENAISSANCE)
# ==================================================================
IMG_MONUMENT = "https://images.unsplash.com/photo-1596130097721-6b21bcbe4be7?q=80&w=1920&auto=format&fit=crop"
IMG_PIROGUE = "https://images.unsplash.com/photo-1528127269322-539801943592?q=80&w=1920&auto=format&fit=crop"

if not st.session_state.authentifie:
    # DESIGN POUR L'ÉCRAN DE CONNEXION (ARRIÈRE-PLAN : MONUMENT DE LA RENAISSANCE)
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{
            background: linear-gradient(rgba(15, 23, 42, 0.55), rgba(15, 23, 42, 0.65)), url("{IMG_MONUMENT}");
            background-size: cover;
            background-position: center 30%;
            background-attachment: fixed;
        }}
        .hero-title {{ color: #ffffff; font-weight: 800; font-size: 3rem; text-align: center; text-shadow: 3px 3px 10px rgba(0,0,0,0.8); margin-top: 10px; }}
        .hero-slogan {{ color: #fbbf24; font-weight: 700; text-transform: uppercase; text-align: center; margin-bottom: 25px; letter-spacing: 2px; text-shadow: 1px 1px 5px rgba(0,0,0,0.7); }}
        
        /* Conteneur de formulaire adapté au monument */
        div[data-testid="stForm"] {{
            background-color: rgba(15, 23, 42, 0.85) !important;
            border: 2px solid #fbbf24 !important; /* Bordure dorée comme le monument */
            border-radius: 12px;
            padding: 25px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.6);
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )
else:
    # DESIGN INTERNE (ARRIÈRE-PLAN : PIROGUE TRADITIONNELLE)
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
        .stApp {{
            background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.9)), url("{IMG_PIROGUE}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .hero-title {{ color: #ffffff; font-weight: 800; font-size: 2.5rem; text-shadow: 2px 2px 5px rgba(0,0,0,0.5); }}
        div[data-testid="stMetricWidget"], .stDataFrame, div[data-testid="stForm"] {{
            background-color: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px !important;
        }}
        </style>
    """,
        unsafe_allow_html=True,
    )

# ==========================================
# GESTION DES ACCÈS
# ==========================================
if not st.session_state.authentifie:
    st.markdown(
        '<h1 class="hero-title">🏦 SUNU KOOPAR PRO</h1>', unsafe_allow_html=True
    )
    st.markdown(
        '<p class="hero-slogan">Système Bancaire Mobile Sécurisé • Sénégal</p>',
        unsafe_allow_html=True,
    )

    st.warning(
        "🛠️ Espace Développeur : Si les identifiants bloquent, clique ci-dessous pour entrer."
    )
    if st.button("🚀 FORCER LA CONNEXION ADMIN (BYPASS)", use_container_width=True):
        st.session_state.authentifie = True
        st.session_state.utilisateur_id = "admin"
        st.session_state.utilisateur_nom = "Directeur Général (Mode Secours)"
        st.session_state.role = "Administrateur"
        st.session_state.telephone_client = "Pas de numéro"
        st.success("Accès forcé réussi !")
        st.rerun()

    st.write("---")

    tab_log, tab_sign = st.tabs(["🔑 Se connecter", "📝 S'inscrire (Nouveau Compte)"])

    with tab_log:
        with st.form("form_auth"):
            id_input = st.text_input("Identifiant ou Numéro de Téléphone").strip()
            mdp_input = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                compte_valide = verifier_connexion_sql(id_input, mdp_input)
                if compte_valide:
                    st.session_state.authentifie = True
                    st.session_state.utilisateur_id = compte_valide[0]
                    st.session_state.utilisateur_nom = compte_valide[1]
                    st.session_state.role = compte_valide[2]
                    st.session_state.telephone_client = compte_valide[3]
                    st.success("Connexion réussie !")
                    st.rerun()
                else:
                    st.error("Identifiant ou mot de passe incorrect.")

    with tab_sign:
        with st.form("form_creer_compte"):
            nom_new = st.text_input("Prénom et Nom")
            tel_new = st.text_input("Numéro Sénégalais (Ex: 77XXXXXXX)")
            mdp_new = st.text_input("Code Secret", type="password")
            if st.form_submit_button("Créer mon compte"):
                num_propre = valider_numero_senegal(tel_new)
                if not num_propre:
                    st.error("Format incorrect (9 chiffres attendus).")
                elif len(mdp_new) < 4:
                    st.error("Le code doit faire au moins 4 caractères.")
                elif nom_new:
                    if ajouter_utilisateur_sql(
                        num_propre, mdp_new, nom_new, "Client", num_propre
                    ):
                        st.success(f"Compte créé ! Connectez-vous avec : {num_propre}")
                    else:
                        st.error("Ce numéro est déjà enregistré.")

# ==========================================
# MODE CONNECTÉ
# ==========================================
else:
    with st.sidebar:
        st.header(f"👤 {st.session_state.utilisateur_nom}")
        st.caption(f"Rôle : {st.session_state.role}")
        st.write("---")

        if st.session_state.role == "Administrateur":
            menu = st.radio(
                "Navigation",
                [
                    "📊 Rapports & Big Data",
                    "✅ Flux d'approbation",
                    "👥 Gestion Utilisateurs",
                ],
            )
        elif st.session_state.role == "Employé":
            menu = st.radio(
                "Navigation", ["📥 Guichet Dépôt/Retrait", "📋 Historique de Caisse"]
            )
        else:
            menu = st.radio(
                "Navigation",
                [
                    "💰 Mon Portefeuille",
                    "💸 Transfert Express",
                    "📱 Recharge de Crédit",
                    "📜 Relevé de compte",
                ],
            )

        st.write("---")
        if st.button("🚪 Déconnexion"):
            st.session_state.authentifie = False
            st.rerun()

    st.markdown(
        '<h1 class="hero-title">🏦 SUNU KOOPAR PRO</h1>', unsafe_allow_html=True
    )

    # --- ESPACE ADMINISTRATEUR ---
    if st.session_state.role == "Administrateur":
        df_tx = recuperer_transactions_sql()
        if menu == "📊 Rapports & Big Data":
            st.subheader("📊 Performances Globales du Réseau")
            if df_tx.empty:
                st.info("Aucune transaction enregistrée pour le moment.")
            else:
                valides = df_tx[df_tx["Statut"] == "Validé"]
                kpi1, kpi2, kpi3 = st.columns(3)
                kpi1.metric("Volume Global", f"{valides['Montant'].sum():,} FCFA")
                kpi2.metric("Commissions Réseau", f"{valides['Frais'].sum():,} FCFA")
                kpi3.metric(
                    "Flux en attente", f"{len(df_tx[df_tx['Statut'] == 'En attente'])}"
                )
                st.write("---")
                st.markdown("**Répartition des flux par service**")
                st.bar_chart(df_tx.groupby("Service")["Montant"].sum())

        elif menu == "✅ Flux d'approbation":
            st.subheader("✅ Validation des Transactions de Caisse")
            en_attente = (
                df_tx[df_tx["Statut"] == "En attente"]
                if not df_tx.empty
                else pd.DataFrame()
            )
            if en_attente.empty:
                st.success("Toutes les opérations sont traitées.")
            else:
                st.dataframe(en_attente, use_container_width=True)
                with st.form("action_validation"):
                    tx_id_sel = st.selectbox(
                        "Choisir l'ID de la transaction", en_attente["ID"].tolist()
                    )
                    choix = st.radio("Action", ["Validé", "Refusé"])
                    if st.form_submit_button("Confirmer la décision"):
                        changer_statut_transaction_sql(tx_id_sel, choix)
                        st.success("Statut mis à jour.")
                        st.rerun()

        elif menu == "👥 Gestion Utilisateurs":
            st.subheader("👥 Enregistrer un nouvel Employé ou Admin")
            with st.form("admin_creation"):
                role_new = st.selectbox(
                    "Rôle à attribuer", ["Employé", "Administrateur"]
                )
                nom_form = st.text_input("Nom de l'agent")
                id_form = st.text_input("Identifiant de connexion (ex: emp2)")
                mdp_form = st.text_input("Mot de passe", type="password")
                if st.form_submit_button("Créer le compte"):
                    if ajouter_utilisateur_sql(
                        id_form, mdp_form, nom_form, role_new, "Pas de numéro"
                    ):
                        st.success("Le compte a été créé.")
                    else:
                        st.error("Cet identifiant existe déjà.")

    # --- ESPACE EMPLOYÉ ---
    elif st.session_state.role == "Employé":
        if menu == "📥 Guichet Dépôt/Retrait":
            st.subheader("📥 Enregistrer une opération client")
            df_cli = recuperer_utilisateurs_par_role("Client")
            if df_cli.empty:
                st.warning("Aucun client enregistré.")
            else:
                with st.form("operation_guichet"):
                    op_service = st.selectbox(
                        "Réseau cible", ["Wave", "Orange Money", "Free Money"]
                    )
                    op_type = st.selectbox("Type d'opération", ["Dépôt", "Retrait"])
                    op_montant = st.number_input(
                        "Montant (FCFA)",
                        min_value=100,
                        max_value=LIMITE_TRANSACTION,
                        step=500,
                    )
                    client_choisi = st.selectbox(
                        "Sélectionner le Client",
                        [
                            f"{r['Telephone']} - {r['Nom']}"
                            for _, r in df_cli.iterrows()
                        ],
                    )

                    if st.form_submit_button("Soumettre à l'Administrateur"):
                        tel_c = client_choisi.split(" - ")[0]
                        frais_calcules = (
                            op_montant * 0.01 if op_type == "Retrait" else 0.0
                        )
                        if op_type == "Retrait" and calculer_solde_client(tel_c) < (
                            op_montant + frais_calcules
                        ):
                            st.error("Solde du client insuffisant pour ce retrait.")
                        else:
                            t_id = f"TX-{random.randint(100000, 999999)}"
                            ajouter_transaction_sql(
                                t_id,
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                op_service,
                                op_type,
                                op_montant,
                                frais_calcules,
                                tel_c,
                                st.session_state.utilisateur_nom,
                            )
                            st.success(f"Demande {t_id} envoyée avec succès.")

        elif menu == "📋 Historique de Caisse":
            st.subheader("📋 Vos saisies de la journée")
            df_tx = recuperer_transactions_sql()
            mes_saisies = (
                df_tx[df_tx["Agent"] == st.session_state.utilisateur_nom]
                if not df_tx.empty
                else pd.DataFrame()
            )
            st.dataframe(mes_saisies, use_container_width=True)

    # --- ESPACE CLIENT ---
    elif st.session_state.role == "Client":
        solde_c = calculer_solde_client(st.session_state.telephone_client)
        df_tx = recuperer_transactions_sql()
        mes_tx = (
            df_tx[df_tx["Client_Tel"] == st.session_state.telephone_client]
            if not df_tx.empty
            else pd.DataFrame()
        )

        if menu == "💰 Mon Portefeuille":
            st.subheader("💼 Votre espace financier")
            st.metric("Solde actuel", f"{solde_c:,} FCFA")
            st.write("---")
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={st.session_state.telephone_client}"
            st.image(qr_url, caption="Votre QR Code de réception")

        elif menu == "💸 Transfert Express":
            st.subheader("💸 Faire un virement instantané")
            with st.form("form_transfert"):
                dest = st.text_input("Numéro du destinataire").strip()
                montant_env = st.number_input(
                    "Montant à envoyer", min_value=100, max_value=LIMITE_TRANSACTION
                )
                if st.form_submit_button("Envoyer"):
                    frais = montant_env * 0.01
                    if solde_c < (montant_env + frais):
                        st.error("Solde insuffisant.")
                    elif dest == st.session_state.telephone_client:
                        st.error("Opération impossible.")
                    else:
                        t_id = f"TR-{random.randint(100000, 999999)}"
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ajouter_transaction_sql(
                            t_id,
                            now,
                            "Direct",
                            "Transfert Envoyé",
                            montant_env,
                            frais,
                            st.session_state.telephone_client,
                            "Système",
                        )
                        ajouter_transaction_sql(
                            t_id + "-R",
                            now,
                            "Direct",
                            "Transfert Reçu",
                            montant_env,
                            0,
                            dest,
                            "Système",
                            "Validé",
                        )
                        st.success("Virement effectué.")
                        st.rerun()

        elif menu == "📱 Recharge de Crédit":
            st.subheader("📱 Recharger un téléphone")
            with st.form("form_credit"):
                operateur = st.selectbox("Réseau", ["Orange", "Free", "Expresso"])
                tel_r = st.text_input(
                    "Numéro de ligne", value=st.session_state.telephone_client
                )
                montant_r = st.number_input(
                    "Montant du crédit", min_value=100, max_value=5000, value=500
                )
                if st.form_submit_button("Acheter le crédit"):
                    if solde_c < montant_r:
                        st.error("Solde insuffisant.")
                    else:
                        t_id = f"CR-{random.randint(100000, 999999)}"
                        ajouter_transaction_sql(
                            t_id,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            operateur,
                            "Achat Crédit",
                            montant_r,
                            0.0,
                            st.session_state.telephone_client,
                            "Système",
                            "Validé",
                        )
                        st.success("Crédit envoyé !")
                        st.rerun()

        elif menu == "📜 Relevé de compte":
            st.subheader("📜 Vos dernières activités")
            st.dataframe(
                mes_tx[["ID", "Date", "Service", "Type", "Montant", "Statut"]],
                use_container_width=True,
            )