
import streamlit as st

# ==========================================
# CONFIGURATION
# ==========================================

ROWS = 7
COLS = 9
CONNECT = 5

EMPTY = 0
YELLOW = 1
RED = 2

st.set_page_config(
    page_title="Puissance 5",
    page_icon="🔴",
    layout="wide"
)

# ==========================================
# INITIALISATION
# ==========================================

def new_board():
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]


def valid_moves(board):
    return [
        col for col in range(COLS)
        if board[0][col] == EMPTY
    ]


def drop_piece(board, col, piece):
    for row in range(ROWS - 1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = piece
            return row
    return None


# ==========================================
# DETECTION DES VICTOIRES
# ==========================================

def has_won(board, piece):

    directions = [
        (0, 1),   # Horizontal
        (1, 0),   # Vertical
        (1, 1),   # Diagonale descendante
        (1, -1)   # Diagonale montante
    ]

    for row in range(ROWS):
        for col in range(COLS):

            if board[row][col] != piece:
                continue

            for dr, dc in directions:

                end_row = row + (CONNECT - 1) * dr
                end_col = col + (CONNECT - 1) * dc

                if not (
                    0 <= end_row < ROWS
                    and 0 <= end_col < COLS
                ):
                    continue

                if all(
                    board[row + i * dr][col + i * dc] == piece
                    for i in range(CONNECT)
                ):
                    return True

    return False


def winning_move(board, col, piece):

    row = drop_piece(board, col, piece)

    if row is None:
        return False

    result = has_won(board, piece)

    board[row][col] = EMPTY

    return result


# ==========================================
# EVALUATION DES POSITIONS
# ==========================================

def score_window(window, piece):

    opponent = RED if piece == YELLOW else YELLOW

    own = window.count(piece)
    other = window.count(opponent)
    empty = window.count(EMPTY)

    if own and other:
        return 0

    if own == 5:
        return 1000000

    if own == 4 and empty == 1:
        return 12000

    if own == 3 and empty == 2:
        return 500

    if own == 2 and empty == 3:
        return 35

    if other == 4 and empty == 1:
        return -15000

    if other == 3 and empty == 2:
        return -650

    if other == 2 and empty == 3:
        return -45

    return 0


def evaluate(board, piece):

    score = 0

    center = COLS // 2

    for row in range(ROWS):

        if board[row][center] == piece:
            score += 4

        elif board[row][center] not in (EMPTY, piece):
            score -= 4

    # Horizontal

    for row in range(ROWS):
        for col in range(COLS - CONNECT + 1):

            window = [
                board[row][col + i]
                for i in range(CONNECT)
            ]

            score += score_window(window, piece)

    # Vertical

    for row in range(ROWS - CONNECT + 1):
        for col in range(COLS):

            window = [
                board[row + i][col]
                for i in range(CONNECT)
            ]

            score += score_window(window, piece)

    # Diagonales descendantes et montantes

    for row in range(ROWS - CONNECT + 1):

        for col in range(COLS - CONNECT + 1):

            window = [
                board[row + i][col + i]
                for i in range(CONNECT)
            ]

            score += score_window(window, piece)

        for col in range(CONNECT - 1, COLS):

            window = [
                board[row + i][col - i]
                for i in range(CONNECT)
            ]

            score += score_window(window, piece)

    return score


# ==========================================
# IA : MINIMAX + ALPHA-BETA
# ==========================================

def ordered_moves(board):

    center = COLS // 2

    return sorted(
        valid_moves(board),
        key=lambda col: abs(col - center)
    )


def minimax(board, depth, alpha, beta, maximizing, ai_piece):

    opponent = RED if ai_piece == YELLOW else YELLOW

    if has_won(board, ai_piece):
        return 10000000 + depth, None

    if has_won(board, opponent):
        return -10000000 - depth, None

    moves = ordered_moves(board)

    if depth == 0 or not moves:
        return evaluate(board, ai_piece), None

    best_col = moves[0]

    if maximizing:

        best_score = float("-inf")

        for col in moves:

            row = drop_piece(board, col, ai_piece)

            score, _ = minimax(
                board,
                depth - 1,
                alpha,
                beta,
                False,
                ai_piece
            )

            board[row][col] = EMPTY

            if score > best_score:
                best_score = score
                best_col = col

            alpha = max(alpha, best_score)

            if alpha >= beta:
                break

        return best_score, best_col

    else:

        best_score = float("inf")

        for col in moves:

            row = drop_piece(board, col, opponent)

            score, _ = minimax(
                board,
                depth - 1,
                alpha,
                beta,
                True,
                ai_piece
            )

            board[row][col] = EMPTY

            if score < best_score:
                best_score = score
                best_col = col

            beta = min(beta, best_score)

            if alpha >= beta:
                break

        return best_score, best_col


def choose_ai_move(board, ai_piece):

    moves = ordered_moves(board)

    if not moves:
        return None

    # Cherche une victoire immédiate

    for col in moves:

        if winning_move(board, col, ai_piece):
            return col

    # Bloque une victoire immédiate du joueur

    opponent = RED if ai_piece == YELLOW else YELLOW

    for col in moves:

        if winning_move(board, col, opponent):
            return col

    # Recherche stratégique

    _, col = minimax(
        board,
        depth=4,
        alpha=float("-inf"),
        beta=float("inf"),
        maximizing=True,
        ai_piece=ai_piece
    )

    return col if col is not None else moves[0]


# ==========================================
# GESTION DES PARTIES
# ==========================================

def init_game(player_piece, player_starts):

    st.session_state.board = new_board()

    st.session_state.player_piece = player_piece

    st.session_state.ai_piece = (
        RED if player_piece == YELLOW else YELLOW
    )

    st.session_state.turn = (
        player_piece if player_starts
        else st.session_state.ai_piece
    )

    st.session_state.last_move = None

    st.session_state.status = "playing"

    st.session_state.player_starts = player_starts

    st.session_state.message = (
        "À vous de jouer !"
        if player_starts
        else "L'IA commence..."
    )


def play_turn(col, piece):

    row = drop_piece(
        st.session_state.board,
        col,
        piece
    )

    if row is None:
        return

    st.session_state.last_move = (row, col)

    if has_won(st.session_state.board, piece):

        st.session_state.status = "won"

        st.session_state.message = (
            "Vous avez gagné ! 🎉"
            if piece == st.session_state.player_piece
            else "L'IA a gagné !"
        )

    elif not valid_moves(st.session_state.board):

        st.session_state.status = "draw"

        st.session_state.message = "Match nul !"

    else:

        st.session_state.turn = (
            RED if piece == YELLOW else YELLOW
        )

        st.session_state.message = (
            "À vous de jouer !"
            if st.session_state.turn == st.session_state.player_piece
            else "L'IA réfléchit..."
        )


# ==========================================
# AFFICHAGE DU PLATEAU
# ==========================================

def render_board(board, last_move):

    cells = []

    for row in range(ROWS):

        row_html = []

        for col in range(COLS):

            piece = board[row][col]

            color = (
                "#f5c400" if piece == YELLOW
                else "#e53935" if piece == RED
                else "#f7f9fc"
            )

            border = (
                "4px solid white"
                if last_move == (row, col)
                else "2px solid #18345b"
            )

            row_html.append(
                f"""
                <td>
                    <div class="hole"
                    style="
                    background:{color};
                    border:{border};
                    ">
                    </div>
                </td>
                """
            )

        cells.append(
            "<tr>" + "".join(row_html) + "</tr>"
        )

    table = "".join(cells)

    st.markdown(
        f"""
        <style>

        .board-wrap {{
            width:100%;
            overflow-x:auto;
        }}

        table.board {{
            border-collapse:separate;
            border-spacing:6px;
            margin:auto;
            background:#1763a6;
            padding:9px;
            border-radius:14px;
        }}

        table.board td {{
            padding:0;
        }}

        .hole {{
            width:min(7.2vw,58px);
            height:min(7.2vw,58px);
            min-width:30px;
            min-height:30px;
            border-radius:50%;
            box-sizing:border-box;
            box-shadow:inset 0 3px 6px rgba(0,0,0,.25);
        }}

        @media (max-width:600px) {{

            table.board {{
                border-spacing:3px;
                padding:5px;
            }}

            .hole {{
                width:8.4vw;
                height:8.4vw;
            }}

        }}

        </style>

        <div class="board-wrap">
            <table class="board">
                {table}
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# INTERFACE STREAMLIT
# ==========================================

st.title("🔴 Puissance 5")

st.caption(
    "Alignez 5 jetons de votre couleur "
    "horizontalement, verticalement ou en diagonale."
)

# Menu de configuration

with st.sidebar:

    st.header("Nouvelle partie")

    chosen_color = st.radio(
        "Votre couleur",
        ["Jaune", "Rouge"],
        horizontal=True
    )

    chosen_start = st.radio(
        "Qui commence ?",
        ["Moi", "L'IA"],
        horizontal=True
    )

    if st.button(
        "Lancer / recommencer",
        type="primary",
        use_container_width=True
    ):

        init_game(
            YELLOW if chosen_color == "Jaune" else RED,
            chosen_start == "Moi"
        )

        st.rerun()


# Initialisation automatique

if "board" not in st.session_state:

    init_game(YELLOW, True)


# Tour de l'IA

if (
    st.session_state.status == "playing"
    and st.session_state.turn == st.session_state.ai_piece
):

    ai_col = choose_ai_move(
        st.session_state.board,
        st.session_state.ai_piece
    )

    if ai_col is not None:

        play_turn(
            ai_col,
            st.session_state.ai_piece
        )

        st.rerun()


# Affichage du tour

player_turn = (
    st.session_state.turn
    == st.session_state.player_piece
)

if st.session_state.status == "playing":

    st.subheader(
        "Votre tour"
        if player_turn
        else "Tour de l'IA"
    )

else:

    st.subheader(st.session_state.message)

st.write(st.session_state.message)

st.markdown(
    "**Cliquez sur une colonne pour déposer votre jeton :**"
)


# Boutons de sélection des colonnes

button_cols = st.columns(COLS, gap="small")

for col, container in enumerate(button_cols):

    with container:

        disabled = (
            not player_turn
            or st.session_state.status != "playing"
            or col not in valid_moves(st.session_state.board)
        )

        if st.button(
            f"↓ {col + 1}",
            key=f"col_{col}",
            disabled=disabled,
            use_container_width=True
        ):

            play_turn(
                col,
                st.session_state.player_piece
            )

            st.rerun()


# Affichage du plateau

render_board(
    st.session_state.board,
    st.session_state.last_move
)


# Informations sur les joueurs

st.markdown(
    f"""
    Vous jouez en **{"Jaune 🟡" if st.session_state.player_piece == YELLOW else "Rouge 🔴"}**

    L'IA joue en **{"Rouge 🔴" if st.session_state.ai_piece == RED else "Jaune 🟡"}**
    """
)


# Rejouer

if st.session_state.status != "playing":

    if st.button(
        "Rejouer avec les mêmes paramètres",
        type="primary"
    ):

        init_game(
            st.session_state.player_piece,
            st.session_state.player_starts
        )

        st.rerun()


st.divider()

st.caption(
    "IA basée sur Minimax avec élagage Alpha-Bêta. "
    "Cette version est stratégique, mais n'est pas mathématiquement invincible."
)
