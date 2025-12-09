# theory_check_final.py
import csv
import config

# --- FUNCIÓN DE CARGA DE CSV ---
def load_strips_from_csv(filename):
    strips = [[], [], [], [], []]
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            start = False
            for row in reader:
                if not row: continue
                if "Pos" in row[0] or "Position" in row[0]:
                    start = True
                    continue
                if start and len(row) > 1:
                    # R1 ID está en col 1, R2 ID en col 3, etc.
                    for reel_idx in range(5):
                        col_idx = 1 + (reel_idx * 2)
                        if col_idx < len(row):
                            try:
                                val = int(row[col_idx])
                                strips[reel_idx].append(val)
                            except: pass
    except Exception as e:
        print(f"Error cargando CSV: {e}")
        return []
    return strips

# --- LÓGICA MATEMÁTICA ---
def calculate_base_rtp(strips):
    print("[CALCULANDO RTP JUEGO BASE DESDE CSV]")
    reel_lengths = [len(s) for s in strips]
    print(f"Longitud Rieles Base: {reel_lengths}")
    
    counts = []
    for col in range(5):
        c = {}
        for s in strips[col]: c[s] = c.get(s, 0) + 1
        counts.append(c)
        
    total_ev = 0
    for sym_id, payouts in config.PAYTABLE.items():
        if sym_id in [10, 11]: continue
        
        p = [counts[i].get(sym_id, 0) / reel_lengths[i] for i in range(5)]
        
        p5 = p[0]*p[1]*p[2]*p[3]*p[4]
        p4 = p[0]*p[1]*p[2]*p[3]*(1-p[4])
        p3 = p[0]*p[1]*p[2]*(1-p[3])
        
        ev = (p5 * payouts.get(5,0)) + (p4 * payouts.get(4,0)) + (p3 * payouts.get(3,0))
        total_ev += ev
        
    rtp_base = total_ev * 100 # Multiplicado por lineas y dividido por apuesta se cancelan
    print(f"RTP Base: {rtp_base:.2f}%")
    return rtp_base

def calculate_fg_ev(strips, special_sym, multiplier):
    reel_lengths = [len(s) for s in strips]
    counts = []
    for col in range(5):
        c = {}
        for s in strips[col]: c[s] = c.get(s, 0) + 1
        counts.append(c)
        
    scenario_ev = 0
    for sym_id, payouts in config.PAYTABLE.items():
        if sym_id in [10, 11]: continue
        is_wild = (sym_id == special_sym)
        p_hit = []
        p_pure = []
        
        for i in range(5):
            c_sym = counts[i].get(sym_id, 0)
            c_wild = counts[i].get(special_sym, 0)
            L = reel_lengths[i]
            if is_wild:
                p_hit.append(c_wild / L)
                p_pure.append(0)
            else:
                p_hit.append((c_sym + c_wild) / L)
                p_pure.append(c_sym / L)
        
        p5_tot = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*p_hit[4]
        p5_pur = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*p_pure[4] if not is_wild else 0
        p5_mix = p5_tot - p5_pur
        
        p4_tot = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*(1-p_hit[4])
        p4_pur = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*(1-p_pure[4]) if not is_wild else 0
        p4_mix = p4_tot - p4_pur
        
        p3_tot = p_hit[0]*p_hit[1]*p_hit[2]*(1-p_hit[3])
        p3_pur = p_pure[0]*p_pure[1]*p_pure[2]*(1-p_pure[3]) if not is_wild else 0
        p3_mix = p3_tot - p3_pur
        
        pay = 0
        if is_wild:
            pay += p5_tot * payouts.get(5,0) * multiplier
            pay += p4_tot * payouts.get(4,0) * multiplier
            pay += p3_tot * payouts.get(3,0) * multiplier
        else:
            pay += (p5_pur * payouts.get(5,0)) + (p5_mix * payouts.get(5,0) * multiplier)
            pay += (p4_pur * payouts.get(4,0)) + (p4_mix * payouts.get(4,0) * multiplier)
            pay += (p3_pur * payouts.get(3,0)) + (p3_mix * payouts.get(3,0) * multiplier)
        scenario_ev += pay
        
    return scenario_ev * config.PAYLINES_COUNT

def calculate_trigger(strips):
    probs = []
    for col in range(5):
        L = len(strips[col])
        C = strips[col].count(config.SYM_SCATTER)
        p_none = ((L-C)/L) * ((L-C-1)/(L-1)) * ((L-C-2)/(L-2))
        probs.append(1.0 - p_none)
        
    dist = {0: 1.0}
    for p in probs:
        new_dist = {}
        for k, val in dist.items():
            new_dist[k] = new_dist.get(k, 0) + val * (1-p)
            new_dist[k+1] = new_dist.get(k+1, 0) + val * p
        dist = new_dist
        
    prob = dist.get(3,0) + dist.get(4,0) + dist.get(5,0)
    avg_spins = 0
    if prob > 0:
        avg_spins = (dist.get(3,0)*10 + dist.get(4,0)*15 + dist.get(5,0)*20) / prob
    print(f"Prob Trigger (Desde CSV): {prob:.6f}")
    return prob, avg_spins

def run():
    print("=== VALIDACIÓN FINAL (CSVs + MATH V3) ===")
    
    # 1. Cargar CSVs
    base_strips = load_strips_from_csv("Entregable_Reel_Strips_BASE.csv")
    fs_strips = load_strips_from_csv("Entregable_Reel_Strips_FS.csv")
    
    if not base_strips or not fs_strips:
        print("ERROR: No se encontraron los CSV. Ejecuta export.py primero.")
        return

    # 2. Calcular
    rtp_base = calculate_base_rtp(base_strips)
    
    weighted_ev = 0
    print("-" * 40)
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, prob_pct = feat
        ev = calculate_fg_ev(fs_strips, sym_id, mult)
        weighted_ev += ev * (prob_pct/100)
    
    print(f"EV Ponderado FS: {weighted_ev:.2f}")
    
    p_trig, avg_spins = calculate_trigger(base_strips)
    rtp_feature = (p_trig * avg_spins * weighted_ev / config.PAYLINES_COUNT) * 100
    print(f"RTP Feature: {rtp_feature:.2f}%")
    
    rtp_jp = (config.JP_CONTRIBUTION / config.PAYLINES_COUNT) * 100
    
    total = rtp_base + rtp_feature + rtp_jp
    print("="*40)
    print(f"RTP TOTAL: {total:.2f}%")
    print("="*40)

if __name__ == "__main__":
    run()