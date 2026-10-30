import streamlit as st
import math
import copy

# Configuration de la page pour mobile
st.set_page_config(page_title="Puissance 5 - Assistant IA", page_icon="🔴")


# Configuration de la grille 9x7
LIGNES = 7
COLONNES = 9
PUISSANCE = 5

VIDE = 0
JOUEUR = 1   # Vous (Rouge)
IA = 2       # L'IA (Jaune)

# --- FONCTIONS DU MOTEUR ---

def creer_grille():
    return [[VIDE for _ in range(COLONNES)] for _ in range(LIGNES)]

def coup_valide(grille, col):
    return grille[0][col] == VIDE

def obtenir_coups_valides(grille):
    return [c for c in range(COLONNES) if coup_valide(grille, c)]

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

    if nb_jeton == 5: score += 100000
    elif nb_jeton == 4 and nb_vide == 1: score += 1000
    elif nb_jeton == 3 and nb_vide == 2: score += 50
    elif nb_jeton == 2 and nb_vide == 3: score += 10

    if nb_adversaire == 4 and nb_vide == 1: score -= 80000
    elif nb_adversaire == 3 and nb_vide == 2: score -= 100
    return score

def evaluer_grille(grille, jeton):
    score = 0
    centre_colonne = [grille[r][COLONNES // 2] for r in range(LIGNES)]
    score += centre_colonne.count(jeton) * 8

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
            temp = copy.deepcopy(grille)
            jouer_coup(temp, col, JOUEUR)
            score = minimax(temp, profondeur - 1, alpha, beta, True)[1]
            if score < valeur:
                valeur = score
                meilleure_col = col
            beta = min(beta, valeur)
            if alpha >= beta: break
        return meilleure_col, valeur

def trouver_meilleur_coup(grille, profondeur=4):
    col, _ = minimax(grille, profondeur, -math.inf, math.inf, True)
    return col

# --- INTERFACE UTILISATEUR STREAMLIT ---

st.title("🎯 Puissance 5 - Assistant IA")
st.markdown("Posez vos jetons (🔴) et laissez l'IA (🟡) vous contrer ou jouer son coup.")

# Initialisation de l'état de la partie
if 'grille' not in st.session_state:
    st.session_state.grille = creer_grille()
if 'partie_gagnee' not in st.session_state:
    st.session_state.partie_gagnee = False

# Affichage du plateau sous forme de grille de texte/emojis
symboles = {0: "⬛", 1: "🔴", 2: "🟡"}

plateau_str = ""
for r in range(LIGNES):
    ligne_str = "".join([symboles[st.session_state.grille[r][c]] for c in range(COLONNES)])
    st.markdown(f"<div style='text-align: center; font-size: 24px; letter-spacing: 5px;'>{ligne_str}</div>", unsafe_allow_html=True)

st.write("---")

# Boutons pour jouer dans les colonnes (de 1 à 9)
st.markdown("### 🕹️ Choisir une colonne pour jouer (Votre coup 🔴)")
cols_ui = st.columns(COLONNES)

for c in range(COLONNES):
    with cols_ui[c]:
        if st.button(f"{c+1}", key=f"btn_{c}", disabled=st.session_state.partie_gagnee):
            if coup_valide(st.session_state.grille, c):
                # Coup du joueur
                jouer_coup(st.session_state.grille, c, JOUEUR)
                
                if verifier_victoire(st.session_state.grille, JOUEUR):
                    st.session_state.partie_gagnee = True
                    st.success("🎉 Vous avez gagné !")
                else:
                    # Tour de l'IA
                    with st.spinner("L'IA réfléchit..."):
                        col_ia = trouver_meilleur_coup(st.session_state.grille, profondeur=4)
                        if col_ia is not None:
                            jouer_coup(st.session_state.grille, col_ia, IA)
                            if verifier_victoire(st.session_state.grille, IA):
                                st.session_state.partie_gagnee = True
                                st.error("💀 L'IA a gagné !")
                st.rerun()

st.write("")
if st.button("🔄 Nouvelle Partie"):
    st.session_state.grille = creer_grille()
    st.session_state.partie_gagnee = False
    st.rerun()
  
