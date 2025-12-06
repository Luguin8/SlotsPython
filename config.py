# config.py
import random

# --- 1. IDENTIFICADORES DE SÍMBOLOS (CONSTANTES) ---
SYM_L1 = 1  # Low 1
SYM_L2 = 2  # Low 2
SYM_L3 = 3  # Low 3
SYM_L4 = 4  # Low 4
SYM_H1 = 5  # High 1 (Transformable Wild x1)
SYM_H2 = 6  # High 2 (Transformable Wild x2)
SYM_H3 = 7  # High 3 (Transformable Wild x2)
SYM_H4 = 8  # High 4 (Transformable Wild x3)
SYM_WILD = 9        # Wild del Juego Base
SYM_SCATTER = 10    # Scatter (Trigger Free Spins)
SYM_SCATTER_JP = 11 # Scatter Jackpot (Solo aparece en Free Spins)

# Lista de símbolos disponibles para el JUEGO BASE
# Nota: Excluimos el SYM_SCATTER_JP (11) porque ese solo sale en los bonos.
BASE_GAME_SYMBOLS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# --- 2. CONFIGURACIÓN DE GRILLA ---
ROWS = 3
COLS = 5

# --- 3. PROBABILIDADES DE SELECCIÓN (FEATURE) ---
# Probabilidad de que cada símbolo High se convierta en Wild al entrar al bono.
# Formato: (ID_Simbolo, Multiplicador, Peso_Porcentual)
FEATURE_WEIGHTS = [
    (SYM_H1, 1, 32.53),
    (SYM_H2, 2, 27.47),
    (SYM_H3, 2, 30.00),
    (SYM_H4, 3, 10.00)
]

# --- 4. TABLA DE PAGOS (PAYTABLE - DUMMY) ---
# Definimos valores "convenientes" ascendentes para empezar.
# Formato: { ID: { Cantidad: Pago } }
PAYTABLE = {
    SYM_L1: {3: 5, 4: 10, 5: 20},
    SYM_L2: {3: 5, 4: 10, 5: 25},
    SYM_L3: {3: 10, 4: 20, 5: 40},
    SYM_L4: {3: 10, 4: 25, 5: 50},
    SYM_H1: {3: 20, 4: 50, 5: 100},
    SYM_H2: {3: 30, 4: 75, 5: 150},
    SYM_H3: {3: 40, 4: 100, 5: 200},
    SYM_H4: {3: 50, 4: 150, 300: 500}, # Top Symbol (Paga más)
    SYM_WILD: {5: 800},   # Pago por 5 Wilds naturales
    SYM_SCATTER: {3: 0, 4: 0, 5: 0}, 
    SYM_SCATTER_JP: {3: 0, 4: 0, 5: 0}
}

# --- 5. LÍNEAS DE PAGO (25 LÍNEAS FIJAS) ---
# Cada lista representa las filas a leer en los rodillos 0, 1, 2, 3, 4.
# 0 = Arriba, 1 = Medio, 2 = Abajo.
PAYLINES = [
    [1, 1, 1, 1, 1], # 1. Centro
    [0, 0, 0, 0, 0], # 2. Arriba
    [2, 2, 2, 2, 2], # 3. Abajo
    [0, 1, 2, 1, 0], # 4. V invertida
    [2, 1, 0, 1, 2], # 5. V normal
    [0, 0, 1, 0, 0], # 6
    [2, 2, 1, 2, 2], # 7
    [1, 2, 2, 2, 1], # 8
    [1, 0, 0, 0, 1], # 9
    [1, 0, 1, 0, 1], # 10
    [1, 2, 1, 2, 1], # 11
    [0, 1, 0, 1, 0], # 12
    [2, 1, 2, 1, 2], # 13
    [1, 1, 0, 1, 1], # 14
    [1, 1, 2, 1, 1], # 15
    [0, 1, 1, 1, 0], # 16
    [2, 1, 1, 1, 2], # 17
    [0, 1, 2, 2, 2], # 18
    [2, 1, 0, 0, 0], # 19
    [0, 2, 0, 2, 0], # 20
    [2, 0, 2, 0, 2], # 21
    [0, 2, 2, 2, 0], # 22
    [2, 0, 0, 0, 2], # 23
    [0, 2, 1, 2, 0], # 24
    [2, 0, 1, 0, 2], # 25
]

# --- 6. GENERADOR DE RODILLOS DUMMY ---
# Esto es vital. Generamos 5 "cintas" de 100 símbolos al azar.
# En la Sesión 4, reemplazaremos esto con "Tuning" manual para ajustar el RTP.
def generate_dummy_strips():
    strips = []
    for _ in range(COLS):
        # Generamos 100 símbolos aleatorios por rodillo
        strip = [random.choice(BASE_GAME_SYMBOLS) for _ in range(100)]
        strips.append(strip)
    return strips