import streamlit as st
import math
import copy

st.set_page_config(page_title="Puissance 5 - Arena", page_icon="🎯", layout="centered")

# --- DESIGN CSS STYLE SOMBRE / GAMING AVEC CASES RONDES ---
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

def get_mapping():
    if st.session_state.player_color == "🔴 Rouge":
        return RED_VAL, YELLOW_VAL  # Joueur, IA
    else:
        return YELLOW_VAL, RED_VAL  # Joueur, IA

# --- FONCTIONS DU MOTEUR ---

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

def evaluer_fenetre(fenetre, jeton, ia_val, joueur_val):
    score = 0
    nb_jeton = fenetre.count(jeton)
    nb_vide = fenetre.count(VIDE)
    adversaire = joueur_val if jeton == ia_val else ia_val
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

def evaluer_grille(grille, jeton,
