import streamlit as st
import math
import copy

st.set_page_config(page_title="Puissance 5", page_icon="🔴", layout="centered")

# CSS pour des cases carrées et des jetons bien grands qui remplissent toute la case
st.markdown("""
    <style>
    div.stButton > button {
        aspect-ratio: 1 / 1 !important;
        width: 100% !important;
        font-size: 38px !important;
        padding: 0px !important;
        border-radius: 8px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

LIGNES = 7
COLONNES = 9
PUISSANCE = 5

VIDE = 0
JOUEUR = 1   # Vous (Rouge)
IA = 2       # L'IA (Jaune)

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

def evaluer_fenetre(fenetre, jeton):
    score = 0
    adversaire = JOUEUR if jeton == IA else IA
    nb_jeton = fenetre.count(jeton)
    nb_vide = fenetre.count(VIDE)
    nb_adversaire = fenetre.count(adversaire)

    if nb_jeton == 5:
        score += 1000000
    elif nb_jeton == 4 and nb_vide == 1:
        score += 50000
    elif nb_jeton == 3 and nb_vide == 2:
        score += 500
    elif nb_jeton == 2 and nb_vide == 3:
        score += 50

    if nb_adversaire == 4 and nb_vide == 1:
        score -= 40000
    elif nb_adversaire == 3 and nb_vide == 2:
        score -= 100

    return score

def evaluer_grille(grille, jeton):
    score = 0
    centre_colonne = [grille[r][COLONNES // 2] for r in range(LIGNES)]
    score += centre_colonne.count(jeton) * 20

    for r in range(LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre(grille[r][c:c + PUISSANCE], jeton)
    for c in range(COLONNES):
        colonne_arr = [grille[r][c] for r in range(LIGNES)]
        for r in range(LIGNES - PUISSANCE + 1):
            score += evaluer_fenetre(colonne_arr[r:r + PUISSANCE], jeton)
    for r in range(LIGNES - PUISSANCE + 1):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre([grille[r + i][c + i] for i in range(PUISSANCE)], jeton)
    for r in range(PUISSANCE - 1, LIGNES):
        for c in range(COLONNES - PUISSANCE + 1):
            score += evaluer_fenetre([grille[r - i][c + i] for i in range(PUISSANCE)], jeton)
    return score

def minimax(grille, profondeur, alpha, beta, joueur_max):
    coups_valides = obtenir_coups_valides(grille)
    est_termine = verifier_victoire(grille, IA) or verifier_victoire(grille, JOUEUR) or len(coups_valides) == 0

    if profondeur == 0 or est_termine:
        if est_termine:
            if verifier_victoire(grille, IA): return (None, 10000000)
            elif verifier_victoire(grille, JOUEUR): return (None, -10000000)
            else: return (None, 0)
        else:
            return (None, evaluer_grille(grille, IA))

    if joueur_max:
        valeur = -math.inf
        meilleure_col = coups_valides[0]
        for col in coups_valides:
            temp = copy.deepcopy(grille)
            jouer_coup(temp, col, IA)
            score = minimax(temp, profondeur - 1, alpha, beta, False)[1]
            if score > valeur:
                valeur = score
                meilleure_col = col
            alpha = max(alpha, valeur)
            if alpha >= beta: break
        return meilleure_col, valeur
    else:
        valeur = math.inf
        meilleure_col = coups_valides[0]
        for col in coups_valides:
            temp_j = copy.deepcopy(grille)
            jouer_coup(temp_j, col, JOUEUR)
            score = minimax(temp_j, profondeur - 1, alpha, beta, True)[1]
            if score < valeur:
                valeur = score
                meilleure_col = col
            beta = min(beta, valeur)
            if alpha >= beta: break
        return meilleure_col, valeur

def trouver_meilleur_coup(grille, profondeur=5):
    col, _ = minimax(grille, profondeur, -math.inf, math.inf, True)
    return col

# --- INTERFACE UTILISATEUR STREAMLIT ---

st.title("🎯 Puissance 5")

if 'grille' not in st.session_state:
    st.session_state.grille = creer_grille()
if 'partie_gagnee' not in st.session_state:
    st.session_state.partie_gagnee = False

# Affichage de la grille en cases carrées avec de grands jetons
for r in range(LIGNES):
    cols = st.columns(COLONNES)
    for c in range(COLONNES):
        with cols[c]:
            val = st.session_state.grille[r][c]
            
            if val == VIDE:
                label = "⬛"
            elif val == 1:
                label = "🔴"
            else:
                label = "🟡"
                
            disabled = (val != VIDE) or st.session_state.partie_gagnee
            
            if st.button(label, key=f"cell_{r}_{c}", disabled=disabled, use_container_width=True):
                if coup_valide(st.session_state.grille, c):
                    jouer_coup(st.session_state.grille, c, JOUEUR)
                    if verifier_victoire(st.session_state.grille, JOUEUR):
                        st.session_state.partie_gagnee = True
                    else:
                        col_ia = trouver_meilleur_coup(st.session_state.grille, profondeur=5)
                        if col_ia is not None:
                            jouer_coup(st.session_state.grille, col_ia, IA)
                            if verifier_victoire(st.session_state.grille, IA):
                                st.session_state.partie_gagnee = True
                    st.rerun()

if st.session_state.partie_gagnee:
    if verifier_victoire(st.session_state.grille, JOUEUR):
        st.success("🎉 Incroyable, vous avez gagné !")
    elif verifier_victoire(st.session_state.grille, IA):
        st.error("💀 L'IA a gagné !")

st.write("")
if st.button("🔄 Nouvelle Partie", use_container_width=True):
    st.session_state.grille = creer_grille()
    st.session_state.partie_gagnee = False
    st.rerun()
