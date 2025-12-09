# theory_check_v2.py
import csv
import config
import itertools

def load_strips_from_csv(filename):
    # Lógica robusta para leer el nuevo formato de export.py (ID separado de Nombre)
    # Columnas: Pos, R1_ID, R1_Name, R2_ID, R2_Name...
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
                    # Riel 1 está en col 1 (ID), Riel 2 en col 3 (ID), etc.
                    # Indices: 1, 3, 5, 7, 9
                    for reel_idx in range(5):
                        col_idx = 1 + (reel_idx * 2)
                        if col_idx < len(row):
                            try:
                                val = int(row[col_idx])
                                strips[reel_idx].append(val)
                            except: pass
    except: return []
    return strips

def calculate_scenario_rtp(strips, source_id, multiplier):
    # Calcula el EV de un escenario donde source_id se vuelve Wild con Multiplier
    # Retorna: EV por giro (valor esperado de ganancia en creditos)
    
    reel_lengths = [len(s) for s in strips]
    counts = []
    for col in range(5):
        c = {}
        for s in strips[col]:
            c[s] = c.get(s, 0) + 1
        counts.append(c)
        
    total_scenario_ev = 0
    
    for sym_id, payouts in config.PAYTABLE.items():
        if sym_id in [10, 11]: continue
        
        # Lógica Wild:
        # Si sym_id == source_id (el especial), solo paga como Wild puro.
        # Si no, el Wild (source_id) lo reemplaza.
        
        p_hit = [] # Probabilidad de (Simbolo O Wild)
        p_pure = [] # Probabilidad de (Solo Simbolo)
        
        is_special = (sym_id == source_id)
        
        for i in range(5):
            count_sym = counts[i].get(sym_id, 0)
            count_wild = counts[i].get(source_id, 0) # El 'source' actúa como Wild
            L = reel_lengths[i]
            
            if is_special:
                # El símbolo especial SE CONVIRTIÓ en wild.
                # Ya no existe como símbolo regular.
                # P(Hit) = P(Wild)
                p_hit.append(count_wild / L)
                p_pure.append(0) 
            else:
                # Símbolo normal
                p_hit.append((count_sym + count_wild) / L)
                p_pure.append(count_sym / L)
        
        # Combinatoria 5, 4, 3
        p5_tot = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*p_hit[4]
        p5_pur = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*p_pure[4]
        p5_mix = p5_tot - p5_pur
        
        p4_tot = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*(1-p_hit[4])
        p4_pur = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*(1-p_pure[4])
        p4_mix = p4_tot - p4_pur
        
        p3_tot = p_hit[0]*p_hit[1]*p_hit[2]*(1-p_hit[3])
        p3_pur = p_pure[0]*p_pure[1]*p_pure[2]*(1-p_pure[3])
        p3_mix = p3_tot - p3_pur
        
        pay = 0
        pay += (p5_pur * payouts.get(5,0)) + (p5_mix * payouts.get(5,0) * multiplier)
        pay += (p4_pur * payouts.get(4,0)) + (p4_mix * payouts.get(4,0) * multiplier)
        pay += (p3_pur * payouts.get(3,0)) + (p3_mix * payouts.get(3,0) * multiplier)
        
        total_scenario_ev += pay
        
    return total_scenario_ev * config.PAYLINES_COUNT

def run_analysis():
    print("--- CÁLCULO TEÓRICO V2 (4 ESCENARIOS) ---")
    
    strips_fs = load_strips_from_csv("Entregable_Reel_Strips_FS.csv")
    if not strips_fs or not strips_fs[0]:
        # Fallback si no encuentra el CSV, usa config directo (útil para debug)
        strips_fs = config.FIXED_STRIPS_FS
        print("Usando Rieles Internos (Config)")
    else:
        print("Usando Rieles del CSV")

    # 1. Calcular EV de cada escenario
    weighted_ev_sum = 0
    
    print(f"{'Escenario':<10} | {'Mult':<5} | {'Prob %':<10} | {'EV (Creditos)':<15}")
    print("-" * 50)
    
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, prob = feat
        # sym_id es el símbolo que se convierte en Wild (ej: 5)
        # mult es el multiplicador (ej: 1)
        
        ev_scenario = calculate_scenario_rtp(strips_fs, sym_id, mult)
        
        contribution = ev_scenario * (prob / 100.0)
        weighted_ev_sum += contribution
        
        print(f"Sym {sym_id:<6} | x{mult:<4} | {prob:<10} | {ev_scenario:.4f}")

    print("-" * 50)
    print(f"EV Ponderado (Avg Win per Free Spin): {weighted_ev_sum:.4f}")
    
    # Aquí deberías conectar con el Trigger Probability del Base Game 
    # para sacar el RTP Final, pero el cliente quería ver este desglose específico.
    # Si quieres el RTP Final, necesitaríamos el script completo anterior integrado.

if __name__ == "__main__":
    run_analysis()