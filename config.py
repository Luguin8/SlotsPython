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

PAYLINES_COUNT = 25

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
    # Lows: Se quedan igual, son para mantener al jugador vivo.
    SYM_L1: {3: 5, 4: 10, 5: 25},
    SYM_L2: {3: 5, 4: 10, 5: 30},
    SYM_L3: {3: 10, 4: 20, 5: 50},
    SYM_L4: {3: 10, 4: 25, 5: 60},
    
    # Highs: Aumentamos el "Techo" de ganancias (5 of a kind)
    SYM_H1: {3: 20, 4: 50, 5: 150}, 
    SYM_H2: {3: 30, 4: 75, 5: 250}, # Antes 200
    SYM_H3: {3: 40, 4: 100, 5: 500},# Antes 300 (Subida fuerte)
    SYM_H4: {3: 50, 4: 150, 5: 1000},# Antes 500 (DOBLE: Ahora paga 40x apuesta)
    
    # El Wild: Lo volvemos un premio Jackpot natural
    SYM_WILD: {5: 3000},   # Antes 1500. Sacar 5 Wilds debe ser épico.
    
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

# IDs para los Wilds Especiales de Free Spins
# Esto nos permite saber por cuánto multiplicar la ganancia
SYM_WILD_X1 = 12  # Viene del H1 (ID 5)
SYM_WILD_X2 = 13  # Viene del H2 (ID 6) o H3 (ID 7)
SYM_WILD_X3 = 14  # Viene del H4 (ID 8)

# Mapeo: Qué Wild corresponde a qué Símbolo original (Para la regla de 5 Wilds)
WILD_ORIGIN_MAP = {
    SYM_WILD_X1: SYM_H1,
    SYM_WILD_X2: SYM_H2, # Nota: H2 y H3 comparten multiplicador pero quizás queramos trackear origen
    SYM_WILD_X3: SYM_H4
}

# Mapeo de Multiplicadores: Cuánto multiplica cada Wild especial
WILD_MULTIPLIERS = {
    SYM_WILD_X1: 1,
    SYM_WILD_X2: 2,
    SYM_WILD_X3: 3,
    SYM_WILD: 1 # El Wild base multiplica x1
}

# Cantidad de Free Spins por Scatters (Estándar de industria, ajustable)
FREE_SPINS_AWARDED = {3: 10, 4: 15, 5: 20}

# --- 6. DEFINICIÓN DE RODILLOS PONDERADOS (TUNING V1) ---
# En lugar de random puro, definimos cuántas veces aparece cada ID en el rodillo.
# Objetivo: Bajar la frecuencia de Scatters para que el bono salga 1 cada 120 giros aprox.

# --- EN config.py (Tuning V6 - Potenciando el Final) ---

REEL_WEIGHTS = [
    # RODILLO 1
    # Bajamos un pelo más la "basura" (L1/L2 a 10) para dar espacio a calidad.
    {
        SYM_L1: 10, SYM_L2: 10, SYM_L3: 9,  SYM_L4: 9,
        SYM_H1: 5,  SYM_H2: 4,  SYM_H3: 4,  SYM_H4: 3,  # +1 H3 y H4
        SYM_WILD: 2,
        SYM_SCATTER: 2   
    },
    # RODILLO 2
    # Mantenemos la agresividad de 3 Scatters aquí. Funciona bien.
    {
        SYM_L1: 11, SYM_L2: 11, SYM_L3: 10, SYM_L4: 10,
        SYM_H1: 5,  SYM_H2: 4,  SYM_H3: 3,  SYM_H4: 3,
        SYM_WILD: 2,
        SYM_SCATTER: 3   
    },
    # RODILLO 3
    # Pivote estable.
    {
        SYM_L1: 11, SYM_L2: 11, SYM_L3: 10, SYM_L4: 10,
        SYM_H1: 5,  SYM_H2: 5,  SYM_H3: 4,  SYM_H4: 3,
        SYM_WILD: 4,     
        SYM_SCATTER: 2   
    },
    # RODILLO 4
    # CAMBIO CRÍTICO: Scatter sube a 2. Wilds suben a 5.
    {
        SYM_L1: 10, SYM_L2: 10, SYM_L3: 9,  SYM_L4: 9,
        SYM_H1: 5,  SYM_H2: 5,  SYM_H3: 4,  SYM_H4: 4,  # + Highs
        SYM_WILD: 5,     # + Wilds (Antes 3/4)
        SYM_SCATTER: 2   # +1 Scatter (Para buscar 15 Giros Gratis)
    },
    # RODILLO 5
    # El rodillo que paga grande.
    {
        SYM_L1: 10, SYM_L2: 10, SYM_L3: 9,  SYM_L4: 9,
        SYM_H1: 5,  SYM_H2: 5,  SYM_H3: 5,  SYM_H4: 5,  # + Highs
        SYM_WILD: 5,     # + Wilds
        SYM_SCATTER: 2   
    }
]
def generate_dummy_strips():
    """
    Ahora genera strips basados en los pesos definidos arriba.
    """
    strips = []
    for reel_idx in range(COLS):
        weights = REEL_WEIGHTS[reel_idx]
        reel_strip = []
        
        # Construimos la lista plana (ej: [1,1,1,1, 2,2,2...])
        for sym_id, count in weights.items():
            reel_strip.extend([sym_id] * count)
            
        # Mezclamos la tira para que los símbolos no estén todos juntos
        random.shuffle(reel_strip)
        strips.append(reel_strip)
        
    return strips