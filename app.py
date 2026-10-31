import streamlit as st
import math
import copy

st.set_page_config(page_title="Puissance 5 - Arena Expert", page_icon="🎯", layout="centered")

# --- DESIGN CSS STYLE SOMBRE / GAMING AVEC PIONS MAXI TAILLE ---
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
        font-size: 44px !important;  /* Tous les pions en très grand format */
        line-height: 1 !important;
        padding: 0px !important;
        border-radius: 50% !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.4);
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
if 'last_ia_move' not in st.session_state:
    st.session_state.last_ia_move = None

def get_mapping():
    if st.session_state.player_color == "🔴 Rouge":
        return RED_VAL, YELLOW_VAL  # Joueur, IA
    else:
        return YELLOW_VAL, RED_VAL  # Joueur, IA

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
        for c in range(COLON
