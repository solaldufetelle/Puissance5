import streamlit as st
import math
import copy

st.set_page_config(page_title="Puissance 5 - Arena Expert", page_icon="🎯", layout="centered")

# --- DESIGN CSS STYLE SOMBRE / GAMING AVEC EFFET DERNIER COUP ---
st.markdown("""
    <style>
    .stApp {
        background-color: #12121c;
        color: #ffffff;
    }
    div.stButton > button {
        background-color: #1e1e2f !important;
        color: white !important;
        border: 1px solid #2d2d44 !important;
        aspect-ratio: 1 / 1 !important;
        width: 100% !important;
        font-size: 26px !important;
        padding: 0px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    div.stButton > button:hover {
        background-color: #2e2e4f !important;
        border-color: #555580 !important;
    }
    /* Style spécifique pour entourer / mettre en valeur le dernier coup de l'IA */
    .ia-last-move {
        border: 3px solid #00ffff !important;
        box-shadow: 0 0 10px #00ffff !important;
    }
    </style>
""", unsafe_allow_html=True)

LIGNES = 7
COLONNES = 9
PUISSANCE = 5

VIDE = 0
RED_VAL = 1
YELLOW_VAL = 2

# --- INITIALISATION DES ÉTATS ---
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'grille' not in st.session_state:
    st.session_state.grille = [[VIDE for _ in range(COLONNES)] for _ in range(LIGNES)]
if 'history' not in st.session_state:
    st.session_state.history = []
if 'partie_terminee' not in st.session_state:
    st.session_state.partie_terminee = False
if 'player_color' not in st.session_state:
    st.session_state.player_color = "🔴 Rouge"
if 'last_ia_move' not in st.session_state:
    st.session_state.last_ia_move = None  # Stocke (ligne, col) du dernier coup de l'IA

def get_mapping():
    if st.session_state.player_color == "🔴 Rouge":
        return RED_VAL, YELLOW_VAL  # Joueur, IA
    else:
        return YELLOW_VAL, RED_VAL  # Joueur, IA

# --- FONCTIONS DU MOTEUR & STRATÉGIE AVANCÉE ---

def creer_grille():
    return [[VIDE for _ in range(COLONNES)] for _ in range(LIGNES)]

def coup_valide(grille, col):
    return grille[0][col] == VIDE

def obtenir_coups_valides(grille):
    centre = COLONNES // 2
    colonnes_triees = sorted(range(COLONNES), key=lambda x: abs(x - centre))
    return [c for c in colonnes_triees if coup_valide(grille, c)]

def jouer_coup(grille, col, jeton):
    for r in range(LIGNES - 1, -1, -1):
        if grille[r][col] == VIDE:
            grille[r][col] = jeton
            return r
    return -1

def verifier_victoire(grille, jeton):
    for r in range(LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            if all(grille[r][c + i] == jeton for i in range(PUISSANCE)):
                return True
    for r in range(LIGNES - PUISSANCE + 1):
        for c in range(COLONNES):
            if all(grille[r + i][c] == jeton for i in range(PUISSANCE)):
                return True
    for r in range(LIGNES - PUISSANCE + 1):
        for c in range(COLONNES - PUISSANCE + 1):
            if all(grille[r + i][c + i] == jeton for i in range(PUISSANCE)):
                return True
    for r in range(PUISSANCE - 1, LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            if all(grille[r - i][c + i] == jeton for i in range(PUISSANCE)):
                return True
    return False

def compter_menaces_avancees(grille, jeton):
    """Détecte les menaces multiples et les configurations de doubles menaces (fourches)."""
    count = 0
    # Horizontales
    for r in range(LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            fenetre = grille[r][c:c + PUISSANCE]
            if fenetre.count(jeton) >= 3 and fenetre.count(VIDE) >= 1:
                count += fenetre.count(jeton)
    # Verticales
    for c in range(COLONNES):
        colonne_arr = [grille[r][c] for r in range(LIGNES)]
        for r in range(LIGNES - PUISSANCE + 1):
            fenetre = colonne_arr[r:r + PUISSANCE]
            if fenetre.count(jeton) >= 3 and fenetre.count(VIDE) >= 1:
                count += fenetre.count(jeton)
    # Diagonales montantes
    for r in range(LIGNES - PUISSANCE + 1):
        for c in range(COLONNES - PUISSANCE + 1):
            fenetre = [grille[r + i][c + i] for i in range(PUISSANCE)]
            if fenetre.count(jeton) >= 3 and fenetre.count(VIDE) >= 1:
                count += fenetre.count(jeton)
    # Diagonales descendantes
    for r in range(PUISSANCE - 1, LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            fenetre = [grille[r - i][c + i] for i in range(PUISSANCE)]
            if fenetre.count(jeton) >= 3 and fenetre.count(VIDE) >= 1:
                count += fenetre.count(jeton)
    return count

def evaluer_fenetre(fenetre, jeton, ia_val, joueur_val):
    score = 0
    nb_jeton = fenetre.count(jeton)
    nb_vide = fenetre.count(VIDE)
    adversaire = joueur_val if jeton == ia_val else ia_val
    nb_adversaire = fenetre.count(adversaire)

    if nb_jeton == 5:
        score += 2000000
    elif nb_jeton == 4 and nb_vide == 1:
        score += 100000
    elif nb_jeton == 3 and nb_vide == 2:
        score += 1000
    elif nb_jeton == 2 and nb_vide == 3:
        score += 100

    if nb_adversaire == 4 and nb_vide == 1:
        score -= 90000
    elif nb_adversaire == 3 and nb_vide == 2:
        score -= 500

    return score

def evaluer_grille(grille, jeton, ia_val, joueur_val):
    score = 0
    centre_colonne = [grille[r][COLONNES // 2] for r in range(LIGNES)]
    score += centre_colonne.count(jeton) * 30

    for r in range(LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre(grille[r][c:c + PUISSANCE], jeton, ia_val, joueur_val)
    for c in range(COLONNES):
        colonne_arr = [grille[r][c] for r in range(LIGNES)]
        for r in range(LIGNES - PUISSANCE + 1):
            score += evaluer_fenetre(colonne_arr[r:r + PUISSANCE], jeton, ia_val, joueur_val)
    for r in range(LIGNES - PUISSANCE + 1):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre([grille[r + i][c + i] for i in range(PUISSANCE)], jeton, ia_val, joueur_val)
    for r in range(PUISSANCE - 1, LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre([grille[r - i][c + i] for i in range(PUISSANCE)], jeton, ia_val, joueur_val)

    # Bonus massif pour les doubles menaces et constructions croisées
    menaces_ia = compter_menaces_avancees(grille, ia_val)
    menaces_adv = compter_menaces_avancees(grille, joueur_val)

    score += menaces_ia * 5000
    score -= menaces_adv * 4500

    return score

def minimax(grille, profondeur, alpha, beta, joueur_max, ia_val, joueur_val):
    coups_valides = obtenir_coups_valides(grille)
    est_termine = (
        verifier_victoire(grille, ia_val) 
        or verifier_victoire(grille, joueur_val) 
        or len(coups_valides) == 0
    )

    if profondeur == 0 or est_termine:
        if est_termine:
            if verifier_victoire(grille, ia_val): 
                return (None, 10000000)
            elif verifier_victoire(grille, joueur_val): 
                return (None, -10000000)
            else: 
                return (None, 0)
        else:
            return (None, evaluer_grille(grille, ia_val, ia_val, joueur_val))

    if joueur_max:
        valeur = -math.inf
        meilleure_col = coups_valides[0]
        for col in coups_valides:
            temp = copy.deepcopy(grille)
            jouer_coup(temp, col, ia_val)
            score = minimax(temp, profondeur - 1, alpha, beta, False, ia_val, joueur_val)[1]
            if score > valeur:
                valeur = score
                meilleure_col = col
            alpha = max(alpha, valeur)
            if alpha >= beta: 
                break
        return meilleure_col, valeur
    else:
        valeur = math.inf
        meilleure_col = coups_valides[0]
        for col in coups_valides:
            temp_j = copy.deepcopy(grille)
            jouer_coup(temp_j, col, joueur_val)
            score = minimax(temp_j, profondeur - 1, alpha, beta, True, ia_val, joueur_val)[1]
            if score < valeur:
                valeur = score
                meilleure_col = col
            beta = min(beta, valeur)
            if alpha >= beta: 
                break
        return meilleure_col, valeur

def trouver_meilleur_coup(grille, profondeur=5):
    ia_val, joueur_val = get_mapping()
    col, _ = minimax(grille, profondeur, -math.inf, math.inf, True, ia_val, joueur_val)
    return col


# --- INTERFACE UTILISATEUR ---

st.markdown("<h2 style='text-align: center;'>🎯 PUISSANCE 5 VS IA EXPERT</h2>", unsafe_allow_html=True)

# ÉCRAN DE CONFIGURATION
if not st.session_state.game_started:
    st.markdown("---")
    st.subheader("⚙️ Paramètres de la partie")
    
    st.session_state.player_color = st.radio(
        "Choisissez votre couleur :", 
        ["🔴 Rouge", "🟡 Jaune"]
    )
    
    starting_choice = st.radio(
        "Qui commence la partie ?", 
        ["Moi (Joueur)", "L'IA"]
    )
    
    st.write("")
    if st.button("🚀 Lancer la partie", use_container_width=True):
        st.session_state.game_started = True
        st.session_state.grille = creer_grille()
        st.session_state.history = []
        st.session_state.last_ia_move = None
        st.session_state.partie_terminee = False
        
        joueur_val, ia_val = get_mapping()
        
        if starting_choice == "L'IA":
            col_ia = COLONNES // 2
            r_ia = jouer_coup(st.session_state.grille, col_ia, ia_val)
            st.session_state.last_ia_move = (r_ia, col_ia)
            
        st.rerun()

# ÉCRAN DE JEU
else:
    joueur_val, ia_val = get_mapping()
    p_color_icon = "🔴" if joueur_val == RED_VAL else "🟡"
    ia_color_icon = "🟡" if ia_val == YELLOW_VAL else "🔴"

    # En-tête style VS
    col_stat1, col_stat2, col_stat3 = st.columns([3, 1, 3])
    with col_stat1:
        st.markdown(f"<div style='text-align: center; background: #1e1e2f; padding: 8px; border-radius: 10px;'><b>Vous</b><br>{p_color_icon}</div>", unsafe_allow_html=True)
    with col_stat2:
        st.markdown("<div style='text-align: center; padding-top: 10px;'><b>VS</b></div>", unsafe_allow_html=True)
    with col_stat3:
        st.markdown(f"<div style='text-align: center; background: #1e1e2f; padding: 8px; border-radius: 10px;'><b>IA Expert</b><br>{ia_color_icon}</div>", unsafe_allow_html=True)

    st.markdown("<p style='text-align: center; color: #a0a0c0; font-size: 13px; margin-top: 8px;'>Touchez directement une colonne de la grille pour jouer ! Le dernier coup de l'IA est encadré en cyan.</p>", unsafe_allow_html=True)
    st.write("")

    # Grille interactive cliquable
    for r in range(LIGNES):
        cols = st.columns(COLONNES)
        for c in range(COLONNES):
            with cols[c]:
                val = st.session_state.grille[r][c]
                
                if val == VIDE:
                    label = "▪️"
                elif val == RED_VAL:
                    label = "🔴"
                else:
                    label = "🟡"
                
                # Vérifie si c'est le dernier coup de l'IA pour appliquer un style visuel distinct
                is_last_ia = (st.session_state.last_ia_move == (r, c))
                
                if is_last_ia and val != VIDE:
                    # Affichage distinctif pour le dernier coup de l'IA
                    st.markdown(f"<div style='text-align: center; font-size: 26px; border: 3px solid #00ffff; border-radius: 50%; background: rgba(0,255,255,0.2); aspect-ratio: 1/1; display: flex; align-items: center; justify-content: center;'>{label}</div>", unsafe_allow_html=True)
                else:
                    if st.button(label, key=f"cell_{r}_{c}", disabled=st.session_state.partie_terminee, use_container_width=True):
                        if coup_valide(st.session_state.grille, c):
                            # Sauvegarde de l'historique (incluant l'ancien dernier coup IA)
                            st.session_state.history.append((copy.deepcopy(st.session_state.grille), st.session_state.last_ia_move))
                            
                            # Coup du joueur
                            jouer_coup(st.session_state.grille, c, joueur_val)
                            
                            if verifier_victoire(st.session_state.grille, joueur_val):
                                st.session_state.partie_terminee = True
                            else:
                                # Tour de l'IA
                                col_ia = trouver_meilleur_coup(st.session_state.grille, profondeur=5)
                                if col_ia is not None:
                                    r_ia = jouer_coup(st.session_state.grille, col_ia, ia_val)
                                    st.session_state.last_ia_move = (r_ia, col_ia)
                                    if verifier_victoire(st.session_state.grille, ia_val):
                                        st.session_state.partie_terminee = True
                            st.rerun()

    st.write("")

    if st.session_state.partie_terminee:
        if verifier_victoire(st.session_state.grille, joueur_val):
            st.success("🎉 Victoire éclatante ! Vous avez battu l'IA.")
        elif verifier_victoire(st.session_state.grille, ia_val):
            st.error("💀 L'IA a remporté la partie !")

    st.write("")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("↩️ Annuler le coup", use_container_width=True, disabled=len(st.session_state.history) == 0):
            if st.session_state.history:
                prev_grille, prev_last_ia = st.session_state.history.pop()
                st.session_state.grille = prev_grille
                st.session_state.last_ia_move = prev_last_ia
                st.session_state.partie_terminee = False
                st.rerun()
    with col_btn2:
        if st.button("🔄 Paramètres / Nouvelle Partie", use_container_width=True):
            st.session_state.game_started = False
            st.session_state.partie_terminee = False
            st.session_state.history = []
            st.session_state.last_ia_move = None
            st.rerun()
