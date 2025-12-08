# config.py
import random

# --- 1. IDENTIFICADORES DE SÍMBOLOS ---
SYM_L1 = 1
SYM_L2 = 2
SYM_L3 = 3
SYM_L4 = 4
SYM_H1 = 5  # High 1
SYM_H2 = 6  # High 2
SYM_H3 = 7  # High 3
SYM_H4 = 8  # High 4
# SYM_WILD = 9  <-- ELIMINADO
SYM_SCATTER = 10    # Trigger Base
SYM_SCATTER_JP = 11 # Trigger JP (FS)

# Wilds Especiales (FS)
SYM_WILD_X1 = 12
SYM_WILD_X2 = 13
SYM_WILD_X3 = 14

BASE_GAME_SYMBOLS = [1, 2, 3, 4, 5, 6, 7, 8, 10]
FREE_SPIN_SYMBOLS = [1, 2, 3, 4, 5, 6, 7, 8, 11]

# --- 2. CONFIGURACIÓN DE GRILLA ---
ROWS = 3
COLS = 5
PAYLINES_COUNT = 25

# --- 3. PROBABILIDADES DE TRANSFORMACIÓN ---
FEATURE_WEIGHTS = [
    (SYM_H1, 1, 32.53),
    (SYM_H2, 2, 27.47),
    (SYM_H3, 2, 30.00),
    (SYM_H4, 3, 10.00)
]

# --- 4. JACKPOTS ---
JP_SEEDS = {
    "MINI": 1000.0,
    "MINOR": 2000.0,
    "MAJOR": 3000.0
}
JP_CONTRIBUTION = 0.5 

# --- 5. TABLA DE PAGOS (TUNING V19 - AJUSTE QUIRÚRGICO) ---
# CAMBIO: Mantenemos el pago de 3x igual (para no desestabilizar).
# Subimos un poco el pago de 4x y 5x en los Lows.
PAYTABLE = {
    # Low 1 y 2
    SYM_L1: {3: 10, 4: 28, 5: 70},   # Antes: 3:10, 4:25, 5:60 (Subimos +3 y +10)
    SYM_L2: {3: 10, 4: 28, 5: 70},   
    
    # Low 3 y 4
    SYM_L3: {3: 15, 4: 38, 5: 100},  # Antes: 3:15, 4:35, 5:90 (Subimos +3 y +10)
    SYM_L4: {3: 15, 4: 38, 5: 120},  # Antes: 5:110 -> 120
    
    # Highs (INTACTOS)
    SYM_H1: {3: 20, 4: 65, 5: 280}, 
    SYM_H2: {3: 30, 4: 90, 5: 500}, 
    SYM_H3: {3: 40, 4: 130, 5: 800}, 
    SYM_H4: {3: 50, 4: 220, 5: 2000}, 
    
    SYM_SCATTER: {3: 0, 4: 0, 5: 0}, 
    SYM_SCATTER_JP: {3: 0, 4: 0, 5: 0}
}

WILD_ORIGIN_MAP = {SYM_WILD_X1: SYM_H1, SYM_WILD_X2: SYM_H2, SYM_WILD_X3: SYM_H4}
WILD_PAYMENT_REF = {SYM_WILD_X1: SYM_H1, SYM_WILD_X2: SYM_H3, SYM_WILD_X3: SYM_H4}
WILD_MULTIPLIERS = {SYM_WILD_X1: 1, SYM_WILD_X2: 2, SYM_WILD_X3: 3}

# --- 6. PESOS DE LOS RIELES (CONFIGURACIÓN ESTABLE V16/V17) ---
# NO TOCAR. Esta configuración garantiza el bono 1/160 y estabilidad.
REEL_WEIGHTS_BASE = [
    # R1: 17 Lows
    {SYM_L1: 17, SYM_L2: 17, SYM_L3: 17, SYM_L4: 17, SYM_H1: 7, SYM_H2: 6, SYM_H3: 5, SYM_H4: 4, SYM_SCATTER: 2},
    # R2: 18 Lows (El freno principal)
    {SYM_L1: 18, SYM_L2: 18, SYM_L3: 17, SYM_L4: 17, SYM_H1: 7, SYM_H2: 6, SYM_H3: 5, SYM_H4: 4, SYM_SCATTER: 3},
    # R3: 18 Lows (El freno secundario)
    {SYM_L1: 18, SYM_L2: 18, SYM_L3: 17, SYM_L4: 17, SYM_H1: 8, SYM_H2: 7, SYM_H3: 6, SYM_H4: 5, SYM_SCATTER: 3},
    # R4: 17 Lows
    {SYM_L1: 17, SYM_L2: 17, SYM_L3: 17, SYM_L4: 17, SYM_H1: 8, SYM_H2: 7, SYM_H3: 6, SYM_H4: 5, SYM_SCATTER: 3},
    # R5: 12 Lows
    {SYM_L1: 12, SYM_L2: 12, SYM_L3: 12, SYM_L4: 12, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 8, SYM_SCATTER: 3}
]

# GIROS GRATIS (IGUAL A SIEMPRE):
REEL_WEIGHTS_FS = [
    {SYM_L1: 9, SYM_L2: 9, SYM_L3: 9, SYM_L4: 9, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 6, SYM_SCATTER_JP: 2},
    {SYM_L1: 9, SYM_L2: 9, SYM_L3: 9, SYM_L4: 9, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 6, SYM_SCATTER_JP: 2},
    {SYM_L1: 9, SYM_L2: 9, SYM_L3: 9, SYM_L4: 9, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 6, SYM_SCATTER_JP: 2},
    {SYM_L1: 9, SYM_L2: 9, SYM_L3: 9, SYM_L4: 9, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 6, SYM_SCATTER_JP: 2},
    {SYM_L1: 9, SYM_L2: 9, SYM_L3: 9, SYM_L4: 9, SYM_H1: 9, SYM_H2: 9, SYM_H3: 8, SYM_H4: 6, SYM_SCATTER_JP: 2}
]

PAYLINES = [
    [1, 1, 1, 1, 1], [0, 0, 0, 0, 0], [2, 2, 2, 2, 2], [0, 1, 2, 1, 0], [2, 1, 0, 1, 2],
    [0, 0, 1, 0, 0], [2, 2, 1, 2, 2], [1, 2, 2, 2, 1], [1, 0, 0, 0, 1], [1, 0, 1, 0, 1],
    [1, 2, 1, 2, 1], [0, 1, 0, 1, 0], [2, 1, 2, 1, 2], [1, 1, 0, 1, 1], [1, 1, 2, 1, 1],
    [0, 1, 1, 1, 0], [2, 1, 1, 1, 2], [0, 1, 2, 2, 2], [2, 1, 0, 0, 0], [0, 2, 0, 2, 0],
    [2, 0, 2, 0, 2], [0, 2, 2, 2, 0], [2, 0, 0, 0, 2], [0, 2, 1, 2, 0], [2, 0, 1, 0, 2]
]
FREE_SPINS_AWARDED = {3: 10, 4: 15, 5: 20}

def generate_strips(weights_config):
    strips = []
    for reel_idx in range(COLS):
        weights = weights_config[reel_idx]
        reel_strip = []
        for sym_id, count in weights.items():
            reel_strip.extend([sym_id] * count)
        random.shuffle(reel_strip)
        strips.append(reel_strip)
    return strips