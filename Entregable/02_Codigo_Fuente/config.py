# config.py
import random

# --- 1. IDENTIFICADORES DE SÍMBOLOS ---
SYM_L1 = 1
SYM_L2 = 2
SYM_L3 = 3
SYM_L4 = 4
SYM_H1 = 5
SYM_H2 = 6
SYM_H3 = 7
SYM_H4 = 8
SYM_SCATTER = 10
SYM_SCATTER_JP = 11
SYM_WILD_X1 = 12
SYM_WILD_X2 = 13
SYM_WILD_X3 = 14

BASE_GAME_SYMBOLS = [1, 2, 3, 4, 5, 6, 7, 8, 10]
FREE_SPIN_SYMBOLS = [1, 2, 3, 4, 5, 6, 7, 8, 11]

# --- 2. CONFIGURACIÓN ---
ROWS = 3
COLS = 5
PAYLINES_COUNT = 25

# Pesos para la selección del símbolo especial en Free Spins
# (ID_ORIGINAL, MULTIPLICADOR, PROBABILIDAD_%)
FEATURE_WEIGHTS = [
    (SYM_H1, 1, 32.53), # Símbolo 5 se vuelve Wild x1
    (SYM_H2, 2, 27.47), # Símbolo 6 se vuelve Wild x2
    (SYM_H3, 2, 30.00), # Símbolo 7 se vuelve Wild x2
    (SYM_H4, 3, 10.00)  # Símbolo 8 se vuelve Wild x3
]

# AJUSTE CLIENTE: Premios Jackpot deben ser mayores al pago máximo de línea (1600)
# Antes: 1000, 2000, 3000
# Ahora: Escalamos para cumplir la regla.
JP_SEEDS = {"MINI": 2000.0, "MINOR": 5000.0, "MAJOR": 10000.0}
JP_CONTRIBUTION = 0.5 

# --- 3. TABLA DE PAGOS (AJUSTE FINAL "CHERRY" - TARGET 96.00%) ---
PAYTABLE = {
    # Lows 1 y 2: Se mantienen igual (Base sólida)
    SYM_L1: {3: 10, 4: 25, 5: 70},
    SYM_L2: {3: 10, 4: 25, 5: 70},
    
    # Lows 3 y 4: Pequeño empujón para sumar ese 0.4% faltante
    # Antes: 15, 38, 105 -> Ahora: 15, 40, 110
    SYM_L3: {3: 15, 4: 40, 5: 110},
    SYM_L4: {3: 15, 4: 40, 5: 110},
    
    # High 1: Ajuste micro para el 0.2% restante
    # Antes: 20, 55, 225 -> Ahora: 20, 55, 230
    SYM_H1: {3: 20, 4: 55, 5: 230},
    
    # High 2 y 3: NO TOCAR. Ya están en el punto dulce.
    SYM_H2: {3: 32, 4: 95, 5: 560},
    SYM_H3: {3: 32, 4: 95, 5: 560},
    
    # High 4: Intocable
    SYM_H4: {3: 50, 4: 200, 5: 1600},
    
    SYM_SCATTER: {3: 0, 4: 0, 5: 0},
    SYM_SCATTER_JP: {3: 0, 4: 0, 5: 0}
}

# Mapeos de Wilds
WILD_ORIGIN_MAP = {SYM_WILD_X1: SYM_H1, SYM_WILD_X2: SYM_H2, SYM_WILD_X3: SYM_H4}
# Referencia de pago: Cuando salen 5 Wilds, ¿como qué símbolo pagan?
WILD_PAYMENT_REF = {SYM_WILD_X1: SYM_H1, SYM_WILD_X2: SYM_H3, SYM_WILD_X3: SYM_H4}
WILD_MULTIPLIERS = {SYM_WILD_X1: 1, SYM_WILD_X2: 2, SYM_WILD_X3: 3}
FREE_SPINS_AWARDED = {3: 10, 4: 15, 5: 20}

# --- 4. MARCADORES DE RIELES ---
REEL_WEIGHTS_BASE = [{SYM_SCATTER: 1}] 
REEL_WEIGHTS_FS = [{SYM_SCATTER_JP: 1}]

# --- 5. LÍNEAS DE PAGO ---
PAYLINES = [
    [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [2, 2, 2, 2, 2], [0, 1, 2, 1, 0], [2, 1, 0, 1, 2],
    [0, 0, 1, 0, 0], [2, 2, 1, 2, 2], [1, 2, 2, 2, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1],
    [1, 2, 1, 2, 1], [0, 1, 0, 1, 0], [2, 1, 2, 1, 2], [1, 1, 0, 1, 1], [1, 1, 2, 1, 1],
    [0, 1, 1, 1, 0], [2, 1, 1, 1, 2], [0, 1, 2, 2, 2], [2, 1, 0, 0, 0], [0, 2, 0, 2, 0],
    [2, 0, 2, 0, 2], [0, 2, 2, 2, 0], [2, 0, 0, 0, 2], [0, 2, 1, 2, 0], [2, 0, 1, 0, 2]
]

# --- 6. RIELES FIJOS (RESTAURADOS DE V2 - TU VERSIÓN ORIGINAL) ---
FIXED_STRIPS_BASE = [
    [1, 4, 4, 1, 4, 4, 3, 6, 4, 6, 1, 3, 5, 2, 2, 3, 3, 6, 4, 2, 2, 2, 4, 7, 1, 3, 3, 8, 2, 2, 7, 1, 4, 2, 2, 4, 4, 2, 3, 4, 4, 3, 1, 6, 7, 4, 2, 8, 3, 3, 3, 5, 5, 5, 1, 1, 6, 1, 3, 1, 1, 4, 8, 1, 7, 10, 4, 3, 5, 5, 3, 2, 2, 4, 3, 2, 1, 8, 2, 3, 1, 3, 6, 5, 10, 1, 7, 4, 2, 2, 1, 1, 2, 10, 3, 3, 2, 4, 1],
    [2, 4, 4, 1, 1, 6, 3, 4, 5, 1, 4, 6, 8, 10, 3, 6, 8, 7, 2, 4, 3, 6, 2, 3, 6, 1, 6, 1, 8, 5, 5, 2, 4, 1, 3, 8, 3, 1, 7, 2, 1, 4, 7, 5, 3, 1, 4, 5, 2, 2, 3, 4, 3, 4, 3, 2, 1, 4, 2, 7, 4, 2, 4, 2, 2, 3, 1, 3, 10, 3, 1, 4, 7, 2, 3, 5, 2, 5, 1, 3, 4, 1, 1, 4, 2, 2, 1, 1, 3, 2, 4, 2, 10, 3, 3, 2, 4, 1],
    [1, 10, 2, 3, 1, 6, 2, 4, 4, 3, 1, 7, 4, 2, 1, 8, 6, 2, 8, 2, 4, 7, 8, 3, 1, 1, 2, 3, 5, 1, 6, 1, 5, 3, 3, 2, 10, 6, 2, 3, 4, 5, 3, 1, 5, 1, 2, 1, 4, 8, 2, 4, 4, 2, 8, 1, 2, 4, 5, 3, 3, 4, 2, 7, 10, 2, 6, 7, 4, 1, 4, 3, 4, 5, 7, 1, 5, 3, 3, 2, 3, 4, 4, 4, 1, 7, 6, 2, 2, 5, 3, 2, 1, 3, 3, 2, 4, 1, 3],
    [2, 4, 10, 2, 8, 4, 6, 3, 3, 3, 4, 3, 5, 2, 3, 4, 4, 1, 1, 4, 4, 8, 1, 2, 3, 3, 5, 2, 5, 1, 6, 4, 2, 1, 1, 1, 2, 7, 7, 3, 5, 1, 4, 2, 1, 10, 2, 3, 1, 4, 2, 1, 4, 5, 3, 2, 6, 10, 5, 2, 6, 2, 7, 7, 3, 1, 3, 1, 4, 1, 1, 3, 3, 7, 7, 5, 3, 3, 2, 8, 6, 4, 6, 4, 2, 8, 8, 1, 1, 4, 3, 2, 7, 2, 5, 6, 4, 1],
    [3, 6, 3, 6, 3, 1, 8, 4, 1, 8, 7, 4, 2, 2, 8, 3, 7, 1, 1, 6, 4, 10, 3, 2, 2, 5, 4, 1, 3, 4, 3, 3, 5, 10, 4, 8, 1, 2, 5, 7, 5, 2, 2, 8, 8, 8, 4, 7, 4, 3, 6, 1, 2, 4, 10, 1, 6, 3, 4, 5, 6, 6, 7, 3, 5, 5, 6, 2, 1, 4, 5, 8, 3, 7, 7, 1, 1, 2, 6, 4, 5, 1, 2, 7, 2, 4, 4, 1, 4, 1, 2, 4, 7, 3, 8, 3, 7, 1, 1]
]

FIXED_STRIPS_FS = [
    [5, 6, 1, 1, 6, 2, 7, 1, 7, 3, 11, 5, 4, 5, 7, 3, 1, 5, 4, 4, 1, 2, 2, 5, 2, 1, 5, 3, 4, 6, 4, 7, 1, 5, 7, 8, 3, 2, 3, 8, 5, 8, 8, 1, 4, 3, 6, 6, 8, 3, 8, 2, 2, 2, 7, 6, 4, 3, 11, 5, 1, 6, 7, 6, 4, 7, 3, 2, 4, 6],
    [2, 7, 2, 2, 1, 2, 4, 4, 8, 7, 6, 2, 6, 3, 4, 11, 1, 8, 7, 5, 5, 2, 6, 4, 3, 5, 4, 3, 5, 11, 6, 2, 3, 2, 8, 5, 4, 5, 8, 4, 1, 2, 6, 7, 3, 1, 5, 6, 6, 7, 8, 8, 1, 4, 3, 1, 1, 1, 3, 6, 7, 6, 1, 7, 7, 5, 4, 5, 3, 3],
    [2, 3, 3, 11, 6, 4, 1, 6, 3, 4, 8, 2, 2, 5, 5, 5, 7, 7, 7, 2, 2, 3, 3, 6, 6, 11, 1, 2, 6, 8, 2, 7, 7, 4, 3, 2, 1, 5, 5, 6, 6, 3, 5, 1, 7, 8, 8, 5, 4, 3, 4, 4, 1, 8, 4, 7, 1, 5, 8, 5, 4, 3, 2, 6, 1, 1, 7, 4, 1, 6],
    [8, 2, 5, 6, 2, 6, 4, 6, 11, 6, 6, 6, 1, 2, 5, 7, 7, 8, 1, 8, 4, 3, 4, 5, 2, 5, 3, 4, 6, 3, 4, 6, 7, 4, 4, 7, 3, 5, 2, 7, 3, 4, 7, 8, 3, 5, 1, 5, 6, 1, 2, 1, 5, 2, 3, 8, 2, 4, 2, 11, 8, 3, 3, 1, 1, 1, 1, 5, 7, 7],
    [3, 8, 2, 3, 8, 1, 6, 6, 7, 7, 4, 5, 4, 3, 4, 2, 2, 4, 5, 8, 6, 1, 6, 3, 3, 1, 5, 11, 8, 1, 3, 3, 3, 6, 2, 6, 7, 4, 1, 4, 4, 2, 7, 6, 7, 5, 7, 2, 6, 1, 2, 1, 4, 5, 6, 5, 2, 7, 2, 5, 1, 11, 5, 5, 7, 4, 8, 3, 8, 1]
]

# ... (El resto del código config.py no lo toques)
def generate_strips(weights_config):
    is_base = True
    if len(weights_config) > 0 and SYM_SCATTER_JP in weights_config[0]:
        is_base = False
    if is_base: return FIXED_STRIPS_BASE
    else: return FIXED_STRIPS_FS