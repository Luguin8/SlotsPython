import csv
import config

def load_strips_from_csv(filename):
    """Lee los rieles del CSV para asegurar que validamos lo entregado."""
    strips = [[], [], [], [], []]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            start_reading = False
            for row in reader:
                if not row: continue
                if "Position" in row[0]:
                    start_reading = True
                    continue
                if start_reading and len(row) >= 6:
                    for i in range(5):
                        cell = row[i+1]
                        if cell and "-" in cell:
                            try:
                                sym_id = int(cell.split("-")[0].strip())
                                strips[i].append(sym_id)
                            except: pass
    except FileNotFoundError:
        print(f"[ERROR] No se encontró {filename}. Ejecuta export.py primero.")
        return []
    return strips

def calculate_rtp_base(strips, paytable):
    """Calcula el RTP del Juego Base (Sin Wilds)."""
    reel_lengths = [len(s) for s in strips]
    total_combinations = reel_lengths[0] * reel_lengths[1] * reel_lengths[2] * reel_lengths[3] * reel_lengths[4]
    total_ev = 0.0
    
    # Probabilidad de cada símbolo por riel
    sym_probs = []
    for col in range(5):
        counts = {}
        for s in strips[col]:
            counts[s] = counts.get(s, 0) + 1
        probs = {k: v / reel_lengths[col] for k, v in counts.items()}
        sym_probs.append(probs)

    # Sumar EV de cada símbolo pagador
    for sym_id, payouts in paytable.items():
        if sym_id in [config.SYM_SCATTER, config.SYM_SCATTER_JP]: continue
        
        # Probabilidades de que aparezca el símbolo en cada riel
        p = [sym_probs[i].get(sym_id, 0) for i in range(5)]
        
        # Probabilidad exacta de 5, 4 y 3 en línea
        prob_5 = p[0] * p[1] * p[2] * p[3] * p[4]
        prob_4 = p[0] * p[1] * p[2] * p[3] * (1 - p[4])
        prob_3 = p[0] * p[1] * p[2] * (1 - p[3])
        
        ev = (prob_5 * payouts.get(5,0)) + (prob_4 * payouts.get(4,0)) + (prob_3 * payouts.get(3,0))
        total_ev += ev

    # El EV total se multiplica por líneas activas (25) pero se divide por la apuesta total (25)
    # Matemáticamente se cancelan, así que total_ev * 100 es el RTP directo.
    return total_ev * 100

def calculate_rtp_fs_scenario(strips, paytable, wild_transform_id, wild_multiplier):
    """
    Calcula el RTP de un ESCENARIO específico de Free Spins.
    Regla: El 'wild_transform_id' desaparece y se vuelve Wild.
    """
    reel_lengths = [len(s) for s in strips]
    
    # 1. Mapear probabilidades considerando la transformación a Wild
    sym_probs = []
    wild_probs = [] # Probabilidad de Wild por riel
    
    for col in range(5):
        counts = {}
        w_count = 0
        for s in strips[col]:
            # Si es el símbolo elegido, cuenta como Wild
            if s == wild_transform_id:
                w_count += 1
            else:
                counts[s] = counts.get(s, 0) + 1
        
        probs = {k: v / reel_lengths[col] for k, v in counts.items()}
        sym_probs.append(probs)
        wild_probs.append(w_count / reel_lengths[col])

    scenario_ev = 0.0
    
    # 2. Calcular pagos para cada símbolo (incluyendo pagos mixtos con Wild)
    for sym_id, payouts in paytable.items():
        # Ignoramos Scatters y el símbolo que se convirtió en Wild (ya no existe como tal)
        if sym_id in [config.SYM_SCATTER, config.SYM_SCATTER_JP, wild_transform_id]: continue
        
        p_sym = [sym_probs[i].get(sym_id, 0) for i in range(5)]
        p_wild = wild_probs 
        
        # Probabilidad de HIT (Símbolo O Wild)
        p_hit = [(p_sym[i] + p_wild[i]) for i in range(5)]
        # Probabilidad PURA (Solo Símbolo, sin Wild) -> Para pagar x1
        p_pure = [p_sym[i] for i in range(5)]
        
        # 5 of a kind
        prob5_total = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*p_hit[4]
        prob5_pure  = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*p_pure[4]
        prob5_wild  = prob5_total - prob5_pure # Combinaciones que usan al menos 1 wild
        
        # 4 of a kind
        prob4_total = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*(1-p_hit[4])
        prob4_pure  = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*(1-p_pure[4])
        prob4_wild  = prob4_total - prob4_pure
        
        # 3 of a kind
        prob3_total = p_hit[0]*p_hit[1]*p_hit[2]*(1-p_hit[3])
        prob3_pure  = p_pure[0]*p_pure[1]*p_pure[2]*(1-p_pure[3])
        prob3_wild  = prob3_total - prob3_pure
        
        # EV del Símbolo = (Pagos Puros) + (Pagos con Wild * Multiplicador)
        term5 = (prob5_pure * payouts.get(5,0)) + (prob5_wild * payouts.get(5,0) * wild_multiplier)
        term4 = (prob4_pure * payouts.get(4,0)) + (prob4_wild * payouts.get(4,0) * wild_multiplier)
        term3 = (prob3_pure * payouts.get(3,0)) + (prob3_wild * payouts.get(3,0) * wild_multiplier)
        
        scenario_ev += (term5 + term4 + term3)
        
    # 3. Calcular pago de línea de SOLO WILDS (5 Wilds)
    # Regla: 5 Wilds pagan como el símbolo transformado original * Multiplicador
    original_payout_5 = paytable[wild_transform_id][5]
    prob_5_wilds = wild_probs[0]*wild_probs[1]*wild_probs[2]*wild_probs[3]*wild_probs[4]
    
    wild_line_ev = prob_5_wilds * original_payout_5 * wild_multiplier
    scenario_ev += wild_line_ev

    return scenario_ev * 100

# --- MODIFICACIÓN CLAVE EN MAIN ---
def main():
    print("=== VALIDACIÓN MATEMÁTICA TEÓRICA (PAR SHEET) ===")
    
    # 1. Cargar Rieles
    strips_base = load_strips_from_csv("../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_BASE.csv")
    strips_fs = load_strips_from_csv("../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_FS.csv")
    
    if not strips_base or not strips_fs: return

    # 2. RTP JUEGO BASE
    rtp_base = calculate_rtp_base(strips_base, config.PAYTABLE)
    print(f"\n[1] RTP JUEGO BASE: {rtp_base:.4f}%")
    
    # 3. FRECUENCIA DE BONO
    l_base = [len(s) for s in strips_base]
    sc_counts = [s.count(config.SYM_SCATTER) for s in strips_base]
    sc_probs = []
    for c, l in zip(sc_counts, l_base):
        p_single = c / l
        p_window = 1 - (1 - p_single) ** config.ROWS
        sc_probs.append(p_window)

    # Probabilidad Trigger
    dist = {0: 1.0}
    for p in sc_probs:
        new_dist = {}
        for k, prob_val in dist.items():
            new_dist[k] = new_dist.get(k, 0) + prob_val * (1-p)
            new_dist[k+1] = new_dist.get(k+1, 0) + prob_val * p
        dist = new_dist
        
    prob_trigger = sum(v for k,v in dist.items() if k >= 3)
    avg_fs_awarded = 0
    if prob_trigger > 0:
        w_sum = sum(v * config.FREE_SPINS_AWARDED.get(k, 0) for k,v in dist.items() if k >= 3)
        avg_fs_awarded = w_sum / prob_trigger
        
    print(f"[2] PROBABILIDAD DE BONO: {prob_trigger:.6f} (1 en {1/prob_trigger:.1f})")

    # 4. RTP FREE SPINS - AQUÍ ESTÁ EL CAMBIO DE ETIQUETAS
    print(f"\n[3] ANÁLISIS DE GIROS GRATIS (EV y Contribución):")
    weighted_fs_rtp = 0
    
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, weight_pct = feat
        probability = weight_pct / 100.0
        
        # Este valor (ej: 532%) es el Retorno por cada 100 apostados DENTRO del bono
        rtp_scenario_ev = calculate_rtp_fs_scenario(strips_fs, config.PAYTABLE, sym_id, mult)
        
        contribution = rtp_scenario_ev * probability
        weighted_fs_rtp += contribution
        
        # CAMBIO DE TEXTO: Clarificar que es EV (Expected Value) por Escenario
        print(f"    - Escenario {sym_id} (x{mult}): EV Interno = {rtp_scenario_ev:.2f}% (Peso: {weight_pct}%)")
        
    # Cálculo Final Explicado
    # RTP_Contribution = (EV_Promedio_Bono * Giros_Promedio) * Probabilidad_Entrada
    # Nota: weighted_fs_rtp ya es % de retorno por giro.
    
    rtp_bonus_total = weighted_fs_rtp * avg_fs_awarded * prob_trigger
    
    print(f"    --------------------------------------------------")
    print(f"    EV Promedio por Giro Gratis: {weighted_fs_rtp:.2f}% (Pay per Spin)")
    print(f"    Giros Promedio por Bono:     {avg_fs_awarded:.2f}")
    print(f"    Probabilidad de Entrada:     {prob_trigger:.6f}")
    print(f"    -> CONTRIBUCIÓN RTP BONUS:   {rtp_bonus_total:.4f}%")

    # 5. RTP JACKPOT
    rtp_jackpot = ((config.JP_CONTRIBUTION * 3) / config.PAYLINES_COUNT) * 100
    print(f"\n[4] RTP JACKPOT (3 x {config.JP_CONTRIBUTION}): {rtp_jackpot:.2f}%")
    
    # 6. TOTAL
    rtp_final = rtp_base + rtp_bonus_total + rtp_jackpot
    print("-" * 40)
    print(f"RTP TEÓRICO FINAL: {rtp_final:.2f}%")
    print("-" * 40)

if __name__ == "__main__":
    main()