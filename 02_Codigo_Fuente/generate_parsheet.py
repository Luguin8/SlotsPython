import xlsxwriter
import config

# Función auxiliar para calcular matemática combinatoria (tomada de theory_check)
def calculate_fs_ev(strips, paytable, wild_id, mult):
    reel_lengths = [len(s) for s in strips]
    # Mapear probabilidades
    sym_probs = []
    wild_probs = []
    for col in range(5):
        counts = {}
        w_count = 0
        for s in strips[col]:
            if s == wild_id: w_count += 1
            else: counts[s] = counts.get(s, 0) + 1
        probs = {k: v / reel_lengths[col] for k, v in counts.items()}
        sym_probs.append(probs)
        wild_probs.append(w_count / reel_lengths[col])

    total_ev = 0.0
    for sym, pays in paytable.items():
        if sym in [config.SYM_SCATTER, config.SYM_SCATTER_JP, wild_id]: continue
        p_hit = [(sym_probs[i].get(sym, 0) + wild_probs[i]) for i in range(5)]
        p_pure = [sym_probs[i].get(sym, 0) for i in range(5)]
        
        # Probabilidades exactas
        prob5 = (p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*p_hit[4])
        prob5_pure = (p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*p_pure[4])
        prob5_wild = prob5 - prob5_pure
        
        prob4 = (p_hit[0]*p_hit[1]*p_hit[2]*p_hit[3]*(1-p_hit[4]))
        prob4_pure = (p_pure[0]*p_pure[1]*p_pure[2]*p_pure[3]*(1-p_pure[4]))
        prob4_wild = prob4 - prob4_pure
        
        prob3 = (p_hit[0]*p_hit[1]*p_hit[2]*(1-p_hit[3]))
        prob3_pure = (p_pure[0]*p_pure[1]*p_pure[2]*(1-p_pure[3]))
        prob3_wild = prob3 - prob3_pure
        
        # Pagos
        ev = 0
        ev += (prob5_pure * pays.get(5,0)) + (prob5_wild * pays.get(5,0) * mult)
        ev += (prob4_pure * pays.get(4,0)) + (prob4_wild * pays.get(4,0) * mult)
        ev += (prob3_pure * pays.get(3,0)) + (prob3_wild * pays.get(3,0) * mult)
        total_ev += ev
        
    # Pago solo Wilds
    p5_wilds = wild_probs[0]*wild_probs[1]*wild_probs[2]*wild_probs[3]*wild_probs[4]
    original_pay = paytable[wild_id][5]
    total_ev += (p5_wilds * original_pay * mult)
    
    return total_ev * 100 # Retorno en %

def generate_excel_parsheet():
    filename = "../01_Excels_Rieles_Pagos/Slot_Parsheet_Teorico.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    
    # Estilos
    bold = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
    header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#366092', 'border': 1, 'align': 'center'})
    cell = workbook.add_format({'border': 1})
    percent = workbook.add_format({'num_format': '0.00%', 'border': 1})
    num_fmt = workbook.add_format({'num_format': '0.00', 'border': 1})
    
    # --- 1. HOJA RESUMEN ---
    ws_summ = workbook.add_worksheet("Resumen RTP")
    ws_summ.set_column('A:B', 25)
    
    ws_summ.write(0, 0, "PARÁMETRO", header)
    ws_summ.write(0, 1, "VALOR", header)
    
    # Aquí usamos fórmulas simples para sumar, mostrando transparencia
    ws_summ.write(1, 0, "RTP Teórico Total", bold)
    ws_summ.write_formula(1, 1, "=B4+B5+B6", percent, 0.9617) 
    
    ws_summ.write(3, 0, "RTP Juego Base", cell)
    ws_summ.write(3, 1, 0.4634, percent) # Valor de theory_check
    
    ws_summ.write(4, 0, "RTP Free Spins (Ponderado)", cell)
    ws_summ.write_formula(4, 1, "='Desglose Free Spins'!E8", percent, 0.4383) # Link a la hoja de FS
    
    ws_summ.write(5, 0, "RTP Jackpot", cell)
    ws_summ.write(5, 1, 0.0600, percent)
    
    ws_summ.write(7, 0, "Contribución Jackpot", cell)
    ws_summ.write(7, 1, config.JP_CONTRIBUTION)
    ws_summ.write(8, 0, "Apuesta Base", cell)
    ws_summ.write(8, 1, config.PAYLINES_COUNT)

    # --- 2. HOJA DESGLOSE FREE SPINS (¡LO QUE PIDE EL CLIENTE!) ---
    ws_fs = workbook.add_worksheet("Desglose Free Spins")
    ws_fs.set_column('A:A', 20)
    ws_fs.set_column('B:E', 15)
    
    headers_fs = ["Escenario (Wild)", "Probabilidad (Peso)", "EV por Giro (%)", "EV Ponderado", "Contribución Final"]
    ws_fs.write_row(0, 0, headers_fs, header)
    
    row = 1
    weighted_sum_ref = []
    
    # Calculamos los valores reales para ponerlos en el Excel
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, weight = feat
        ev = calculate_fs_ev(config.FIXED_STRIPS_FS, config.PAYTABLE, sym_id, mult)
        
        ws_fs.write(row, 0, f"Simbolo {sym_id} (x{mult})", cell)
        ws_fs.write(row, 1, weight/100, percent)
        ws_fs.write(row, 2, ev/100, percent) # Escribimos el % (ej 5.32)
        
        # Fórmula de Excel: Peso * EV
        ws_fs.write_formula(row, 3, f"=B{row+1}*C{row+1}", percent)
        weighted_sum_ref.append(f"D{row+1}")
        row += 1
        
    # Suma de ponderados (EV promedio por giro)
    ws_fs.write(row, 2, "EV PROMEDIO:", bold)
    formula_sum = f"=SUM({':'.join(weighted_sum_ref)})" if len(weighted_sum_ref) > 1 else f"={weighted_sum_ref[0]}"
    ws_fs.write_formula(row, 3, f"=SUM(D2:D5)", percent)
    ev_avg_cell = f"D{row+1}"
    
    row += 2
    # Cálculo Final con Frecuencia
    # Datos fijos tomados de la teoría (aprox)
    prob_trigger = 0.006050 
    avg_spins = 10.24
    
    ws_fs.write(row, 0, "Probabilidad Entrada", cell)
    ws_fs.write(row, 1, prob_trigger, percent)
    prob_cell = f"B{row+1}"
    
    ws_fs.write(row+1, 0, "Giros Promedio", cell)
    ws_fs.write(row+1, 1, avg_spins, num_fmt)
    spins_cell = f"B{row+2}"
    
    ws_fs.write(row+2, 0, "RTP TOTAL FS", bold)
    # Fórmula Maestra: EV_Promedio * Prob * Giros / Apuesta (EV ya está en % de apuesta en theory_check logic, ajustamos)
    # En theory_check: (weighted_rtp * avg_spins * prob_trigger)
    # Aquí weighted_rtp (D6) es % payout (ej 500%).
    # RTP Contribution = D6 * Prob * Spins.
    ws_fs.write_formula(row+2, 1, f"={ev_avg_cell}*{prob_cell}*{spins_cell}", percent)
    
    # Linkeamos la celda E8 (aprox) para el resumen
    ws_fs.write(7, 4, f"={f'B{row+3}'}", percent) # Celda helper para el link

    # --- 3. HOJA MATEMÁTICA BASE ---
    ws_base = workbook.add_worksheet("Matemática Base")
    headers = ["Symbol", "Reel 1", "Reel 2", "Reel 3", "Reel 4", "Reel 5", "Hits 5", "Hits 4", "Hits 3", "Total Pay", "Contrib %"]
    ws_base.write_row(0, 0, headers, header)
    
    strips = config.FIXED_STRIPS_BASE
    lengths = [len(s) for s in strips]
    total_combos = lengths[0]*lengths[1]*lengths[2]*lengths[3]*lengths[4]
    
    row = 1
    names = {1:"L1", 2:"L2", 3:"L3", 4:"L4", 5:"H1", 6:"H2", 7:"H3", 8:"H4", 10:"Scatter", 11:"ScatterJP"}
    
    for sym_id in config.PAYTABLE:
        if sym_id >= 10: continue
        
        counts = [s.count(sym_id) for s in strips]
        pays = config.PAYTABLE[sym_id]
        
        ws_base.write(row, 0, names.get(sym_id, str(sym_id)), cell)
        # Escribimos Counts
        for i in range(5): ws_base.write(row, i+1, counts[i], cell)
        
        # Escribimos Fórmulas de Combinatoria (Lo que pidió el cliente)
        # Hits 5 = R1*R2*R3*R4*R5
        ws_base.write_formula(row, 6, f"=PRODUCT(B{row+1}:F{row+1})", cell)
        
        # Hits 4 = R1*R2*R3*R4*(L5-R5)
        ws_base.write_formula(row, 7, f"=B{row+1}*C{row+1}*D{row+1}*E{row+1}*({lengths[4]}-F{row+1})", cell)
        
        # Hits 3 = R1*R2*R3*(L4-R4)*L5
        ws_base.write_formula(row, 8, f"=B{row+1}*C{row+1}*D{row+1}*({lengths[3]}-E{row+1})*{lengths[4]}", cell)
        
        # Total Pay = (H5*Pay5 + H4*Pay4 + H3*Pay3)
        ws_base.write_formula(row, 9, f"=(G{row+1}*{pays[5]})+(H{row+1}*{pays[4]})+(I{row+1}*{pays[3]})", cell)
        
        # RTP Contribution = (Total Pay / Total Combos) / Bet
        ws_base.write_formula(row, 10, f"=(J{row+1}/{total_combos})/{config.PAYLINES_COUNT}", percent)
        
        row += 1

    print(f"Excel PAR Sheet generado en: {filename}")
    workbook.close()

if __name__ == "__main__":
    generate_excel_parsheet()