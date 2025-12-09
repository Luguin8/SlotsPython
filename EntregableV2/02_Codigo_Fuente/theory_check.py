import csv
import config # Usamos config solo para leer la Tabla de Pagos y Reglas
import itertools

def load_strips_from_csv(filename):
    strips = [[], [], [], [], []] # 5 Rieles vacios
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            
            # Buscamos donde empiezan los datos
            start_reading = False
            for row in reader:
                if not row: continue
                # Detectar encabezado
                if "Position" in row[0] and "Reel 1" in row[1]:
                    start_reading = True
                    continue
                
                if start_reading:
                    # Fila de datos: [Pos, R1, R2, R3, R4, R5]
                    # Formato ejemplo: "1 - Low 1"
                    if len(row) < 6: continue
                    
                    for i in range(5):
                        cell = row[i+1] # Columna 1 a 5 son los rieles
                        if cell and "-" in cell:
                            # Extraer solo el ID (lo que esta antes del guion)
                            try:
                                sym_id = int(cell.split("-")[0].strip())
                                strips[i].append(sym_id)
                            except:
                                pass
    except FileNotFoundError:
        print(f"Error: No se encontro el archivo {filename}")
        print("Asegurate de ejecutar esto desde la carpeta correcta o ajustar la ruta.")
        return []
        
    return strips

def calculate_theoretical_rtp():
    print("==================================================")
    print("   VALIDACIÓN MATEMÁTICA DESDE CSV (PAR SHEET)    ")
    print("==================================================")
    
    # --- 1. CARGAR DATOS DESDE LOS CSV GENERADOS ---
    # Ajusta la ruta si tus CSV estan en otra carpeta relativa
    path_base = "../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_BASE.csv"
    path_fs = "../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_FS.csv"
    
    print(f"Leyendo: {path_base}...")
    strips_base = load_strips_from_csv(path_base)
    print(f"Leyendo: {path_fs}...")
    strips_fs = load_strips_from_csv(path_fs)
    
    if not strips_base or not strips_fs:
        print("ERROR CRITICO: No se pudieron cargar los rieles.")
        return

    reel_lengths = [len(s) for s in strips_base]
    bet = config.PAYLINES_COUNT
    
    print(f"[METADATA]")
    print(f"Rieles Base Leídos: {reel_lengths}")
    print(f"Apuesta:            {bet} creditos")
    print("-" * 50)

    # --- 2. MATEMÁTICA DE SCATTERS (VENTANA DESLIZANTE) ---
    reel_scatter_probs = [] 
    
    for col in range(5):
        strip = strips_base[col]
        L = len(strip)
        counts = {0:0, 1:0, 2:0, 3:0}
        
        for i in range(L):
            window = [strip[(i + r) % L] for r in range(config.ROWS)]
            sc_in_window = window.count(config.SYM_SCATTER)
            counts[sc_in_window] += 1
            
        probs = {k: v/L for k, v in counts.items()}
        reel_scatter_probs.append(probs)

    # Convolución
    total_dist = reel_scatter_probs[0]
    for i in range(1, 5):
        current_probs = reel_scatter_probs[i]
        new_dist = {}
        for k1, p1 in total_dist.items():
            for k2, p2 in current_probs.items():
                total_k = k1 + k2
                combined_p = p1 * p2
                new_dist[total_k] = new_dist.get(total_k, 0) + combined_p
        total_dist = new_dist

    prob_trigger = 0
    expected_fs_awarded_per_spin = 0
    
    for k, p in total_dist.items():
        if k >= 3:
            prob_trigger += p
            awarded = config.FREE_SPINS_AWARDED.get(k, 0)
            expected_fs_awarded_per_spin += (p * awarded)
            
    bonus_freq = 1 / prob_trigger if prob_trigger > 0 else 0
    avg_fs_per_trigger = expected_fs_awarded_per_spin / prob_trigger if prob_trigger > 0 else 0

    print(f"[JUEGO BASE - TRIGGER]")
    print(f"Probabilidad Bono:  {prob_trigger:.6f} ({prob_trigger*100:.2f}%)")
    print(f"Frecuencia Teórica: 1 cada {bonus_freq:.2f} giros")
    print(f"Promedio FS dados:  {avg_fs_per_trigger:.2f} giros")
    print("-" * 50)

    # --- 3. RTP JUEGO BASE ---
    total_base_ev = 0
    base_sym_counts = []
    
    for col in range(5):
        counts = {}
        for s in strips_base[col]:
            counts[s] = counts.get(s, 0) + 1
        base_sym_counts.append(counts)

    for sym_id, payouts in config.PAYTABLE.items():
        if sym_id in [config.SYM_SCATTER, config.SYM_SCATTER_JP]: continue
        
        p_sym = [base_sym_counts[i].get(sym_id, 0) / reel_lengths[i] for i in range(5)]
        
        p5 = p_sym[0]*p_sym[1]*p_sym[2]*p_sym[3]*p_sym[4]
        p4 = p_sym[0]*p_sym[1]*p_sym[2]*p_sym[3]*(1-p_sym[4])
        p3 = p_sym[0]*p_sym[1]*p_sym[2]*(1-p_sym[3])
        
        sym_ev = (p5 * payouts.get(5,0)) + (p4 * payouts.get(4,0)) + (p3 * payouts.get(3,0))
        total_base_ev += sym_ev

    rtp_base_percent = total_base_ev * 100
    print(f"[JUEGO BASE - PAGOS]")
    print(f"RTP Base (Lineas):  {rtp_base_percent:.2f}%")
    print("-" * 50)

    # --- 4. RTP GIROS GRATIS ---
    print(f"[GIROS GRATIS - MATEMÁTICA]")
    
    fs_weighted_ev = 0
    fs_counts_raw = []
    fs_lengths = [len(s) for s in strips_fs]
    for col in range(5):
        counts = {}
        for s in strips_fs[col]:
            counts[s] = counts.get(s, 0) + 1
        fs_counts_raw.append(counts)

    for feat in config.FEATURE_WEIGHTS:
        orig_id, mult, prob_percent = feat
        scenario_weight = prob_percent / 100.0
        scenario_ev = 0
        
        for sym_id, payouts in config.PAYTABLE.items():
            if sym_id in [config.SYM_SCATTER, config.SYM_SCATTER_JP]: continue
            
            p_hit = []
            p_pure = []
            target_is_wild = (sym_id == orig_id)
            
            for i in range(5):
                count_sym = fs_counts_raw[i].get(sym_id, 0)
                count_wild_origin = fs_counts_raw[i].get(orig_id, 0)
                L = fs_lengths[i]
                
                if target_is_wild:
                    p_hit.append(count_wild_origin / L)
                    p_pure.append(0)
                else:
                    p_hit.append((count_sym + count_wild_origin) / L)
                    p_pure.append(count_sym / L)
            
            prob5_total = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*p_hit[4]
            prob5_pure  = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*p_pure[4]
            prob5_mix   = prob5_total - prob5_pure
            
            prob4_total = p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*(1-p_hit[4])
            prob4_pure  = p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*(1-p_pure[4])
            prob4_mix   = prob4_total - prob4_pure
            
            prob3_total = p_hit[0]*p_hit[1]*p_hit[2]*(1-p_hit[3])
            prob3_pure  = p_pure[0]*p_pure[1]*p_pure[2]*(1-p_pure[3])
            prob3_mix   = prob3_total - prob3_pure
            
            pay_sym = 0
            pay_sym += (prob5_pure * payouts.get(5,0)) + (prob5_mix * payouts.get(5,0) * mult)
            pay_sym += (prob4_pure * payouts.get(4,0)) + (prob4_mix * payouts.get(4,0) * mult)
            pay_sym += (prob3_pure * payouts.get(3,0)) + (prob3_mix * payouts.get(3,0) * mult)
            
            scenario_ev += pay_sym

        fs_weighted_ev += (scenario_ev * scenario_weight)

    avg_win_per_fs = fs_weighted_ev * 25
    print(f"Ganancia Media por Giro Gratis: {avg_win_per_fs:.2f} creditos")
    
    rtp_bonus_percent = (expected_fs_awarded_per_spin * avg_win_per_fs) / bet * 100
    print(f"RTP Bonus (Feature): {rtp_bonus_percent:.2f}%")
    
    # --- 5. TOTAL ---
    rtp_jp_contrib = (config.JP_CONTRIBUTION / bet) * 100
    rtp_total = rtp_base_percent + rtp_bonus_percent + rtp_jp_contrib
    
    print("-" * 50)
    print(f"RTP Base:    {rtp_base_percent:.2f}%")
    print(f"RTP Bonus:   {rtp_bonus_percent:.2f}%")
    print(f"RTP Jackpot: {rtp_jp_contrib:.2f}%")
    print(f"RTP TOTAL:   {rtp_total:.2f}%")
    print("==================================================")

if __name__ == "__main__":
    calculate_theoretical_rtp()