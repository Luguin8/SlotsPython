import xlsxwriter
import config

def get_counts_for_scenario(strips, sym_id, wild_id=None):
    counts_sym = []
    counts_wild = []
    lengths = []
    
    for col in range(5):
        strip = strips[col]
        lengths.append(len(strip))
        c_s = strip.count(sym_id)
        # Si es el escenario de Wild, el símbolo transformado cuenta como Wild
        if wild_id is not None and sym_id == wild_id:
            c_w = c_s # El simbolo se transformó
            c_s = 0   # Ya no existe como normal
        else:
            c_w = strip.count(wild_id) if wild_id is not None else 0
            
        counts_sym.append(c_s)
        counts_wild.append(c_w)
        
    return counts_sym, counts_wild, lengths

def add_hit_style_sheet(workbook, sheet_name, strips, wild_id=None, multiplier=1):
    ws = workbook.add_worksheet(sheet_name)
    
    # Formatos (Estilo Clientes GLI/BMM)
    header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#000080', 'border': 1, 'align': 'center'}) # Azul oscuro como su foto
    cell = workbook.add_format({'border': 1, 'align': 'right', 'num_format': '#,##0'})
    cell_pay = workbook.add_format({'border': 1, 'align': 'center'})
    bold_total = workbook.add_format({'bold': True, 'bg_color': '#92D050', 'border': 1, 'num_format': '#,##0'}) # Verde como su foto
    percent = workbook.add_format({'num_format': '0.000%', 'bold': True, 'border': 1})
    
    # Calcular Ciclo
    lengths = [len(s) for s in strips]
    cycle = lengths[0]*lengths[1]*lengths[2]*lengths[3]*lengths[4]
    
    # Encabezados
    headers = ["Combination", "Hits (1 line)", "Hits (25 lines)", "Payment", "Total Payments"]
    ws.write_row(0, 0, headers, header)
    ws.set_column('A:A', 20)
    ws.set_column('B:E', 18)
    
    row = 1
    total_payment_sum_refs = []
    
    # Nombres
    names = {1:"L1", 2:"L2", 3:"L3", 4:"L4", 5:"H1", 6:"H2", 7:"H3", 8:"H4"}
    
    # --- BLOQUE 1: COMBINACIONES SIN WILD (PURE) ---
    ws.write(row, 0, "Combinaciones SIN Wild", workbook.add_format({'bold':True}))
    row += 1
    
    for sym_id in config.PAYTABLE:
        if sym_id >= 10: continue
        if wild_id is not None and sym_id == wild_id: continue # Este se volvió wild completo
        
        pays = config.PAYTABLE[sym_id]
        c_sym, c_wild, _ = get_counts_for_scenario(strips, sym_id, wild_id)
        
        # Hits Puros (Solo simbolo)
        # 5 of a kind: S*S*S*S*S
        h5 = c_sym[0]*c_sym[1]*c_sym[2]*c_sym[3]*c_sym[4]
        # 4 of a kind: S*S*S*S*(Total-S) -> Ojo: Total-S incluye Wilds aqui? 
        # En "Sin Wild", NO debe haber wilds. Entonces es (Len - S - W).
        # Formula cliente: Pure Hits.
        
        # Simplificación robusta para coincidir con su lógica visual:
        # Puros = S * S * S ...
        # Con Wild = (S+W)^5 - S^5
        
        # 5 Hits Pure
        ws.write(row, 0, f"5 {names[sym_id]} (Pure)", cell)
        ws.write(row, 1, h5, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(5,0), cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h5 > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1
        
        # 4 Hits Pure
        h4 = c_sym[0]*c_sym[1]*c_sym[2]*c_sym[3]*(lengths[4]-c_sym[4]-c_wild[4])
        ws.write(row, 0, f"4 {names[sym_id]} (Pure)", cell)
        ws.write(row, 1, h4, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(4,0), cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h4 > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1

        # 3 Hits Pure
        h3 = c_sym[0]*c_sym[1]*c_sym[2]*(lengths[3]-c_sym[3]-c_wild[3])*lengths[4]
        ws.write(row, 0, f"3 {names[sym_id]} (Pure)", cell)
        ws.write(row, 1, h3, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(3,0), cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h3 > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1
        
    # --- BLOQUE 2: COMBINACIONES CON WILD ---
    row += 1
    ws.write(row, 0, "Combinaciones CON Wild", workbook.add_format({'bold':True}))
    row += 1
    
    for sym_id in config.PAYTABLE:
        if sym_id >= 10: continue
        if wild_id is not None and sym_id == wild_id: continue
        
        pays = config.PAYTABLE[sym_id]
        c_sym, c_wild, _ = get_counts_for_scenario(strips, sym_id, wild_id)
        
        # Totales (Sym + Wild)
        t = [c_sym[i] + c_wild[i] for i in range(5)]
        s = c_sym
        
        # 5 Hits (Mix - Pure)
        h5_total = t[0]*t[1]*t[2]*t[3]*t[4]
        h5_pure = s[0]*s[1]*s[2]*s[3]*s[4]
        h5_wild = h5_total - h5_pure
        
        ws.write(row, 0, f"5 {names[sym_id]} (Wild)", cell)
        ws.write(row, 1, h5_wild, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(5,0)*multiplier, cell_pay) # PAGO CON MULTIPLICADOR
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h5_wild > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1
        
        # 4 Hits (Mix - Pure)
        # Prob 4 Mix = T*T*T*T*(L-T)
        h4_total = t[0]*t[1]*t[2]*t[3]*(lengths[4]-t[4])
        # Prob 4 Pure = S*S*S*S*(L-S-W) -> Ya calculado arriba como h4
        h4_pure = s[0]*s[1]*s[2]*s[3]*(lengths[4]-s[4]-c_wild[4])
        h4_wild = h4_total - h4_pure
        
        ws.write(row, 0, f"4 {names[sym_id]} (Wild)", cell)
        ws.write(row, 1, h4_wild, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(4,0)*multiplier, cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h4_wild > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1

        # 3 Hits (Mix - Pure)
        h3_total = t[0]*t[1]*t[2]*(lengths[3]-t[3])*lengths[4]
        h3_pure = s[0]*s[1]*s[2]*(lengths[3]-s[3]-c_wild[3])*lengths[4]
        h3_wild = h3_total - h3_pure
        
        ws.write(row, 0, f"3 {names[sym_id]} (Wild)", cell)
        ws.write(row, 1, h3_wild, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, pays.get(3,0)*multiplier, cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        if h3_wild > 0: total_payment_sum_refs.append(f"E{row+1}")
        row += 1

    # --- BLOQUE 3: 5 WILDS ---
    if wild_id is not None:
        c_sym, c_wild, _ = get_counts_for_scenario(strips, wild_id, wild_id) # Get wild counts
        h5_w = c_wild[0]*c_wild[1]*c_wild[2]*c_wild[3]*c_wild[4]
        orig_pay = config.PAYTABLE[wild_id][5]
        
        ws.write(row, 0, "5 Wilds", cell)
        ws.write(row, 1, h5_w, cell)
        ws.write_formula(row, 2, f"=B{row+1}*{config.PAYLINES_COUNT}", cell)
        ws.write(row, 3, orig_pay*multiplier, cell_pay)
        ws.write_formula(row, 4, f"=C{row+1}*D{row+1}", cell)
        total_payment_sum_refs.append(f"E{row+1}")
        row += 1

    # TOTALES FINALES (ESTILO CLIENTE)
    row += 1
    ws.write(row, 0, "TOTAL", bold_total)
    ws.write_formula(row, 4, f"=SUM({','.join(total_payment_sum_refs)})", bold_total)
    total_pay_cell = f"E{row+1}"
    
    row += 2
    ws.write(row, 3, "CYCLE", header)
    ws.write(row, 4, cycle, bold_total)
    cycle_cell = f"E{row+1}"
    
    row += 1
    ws.write(row, 3, "RTP %", header)
    # RTP = Total Pagado / (Ciclo * Apuesta Lineas * Apuesta por Linea)
    # Su Excel divide por (Ciclo * Apuesta Total).
    # Apuesta Total = 25.
    ws.write_formula(row, 4, f"={total_pay_cell}/({cycle_cell}*{config.PAYLINES_COUNT})", percent)
    
    return f"'{sheet_name}'!E{row+1}"

def generate_excel_parsheet():
    filename = "../01_Excels_Rieles_Pagos/Slot_Parsheet_Teorico.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    
    # 1. Generar Hojas Detalladas (Estilo Cliente)
    # Base Game
    ref_base = add_hit_style_sheet(workbook, "Base_Game_Hits", config.FIXED_STRIPS_BASE)
    
    refs_fs = []
    weights_fs = []
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, weight = feat
        sheet_name = f"FS_Wild{sym_id}_x{mult}"
        ref = add_hit_style_sheet(workbook, sheet_name, config.FIXED_STRIPS_FS, wild_id=sym_id, multiplier=mult)
        refs_fs.append(ref)
        weights_fs.append(weight/100.0)

    # 2. Hoja Resumen Final
    ws_summ = workbook.add_worksheet("Resumen RTP")
    header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#366092', 'border': 1})
    percent = workbook.add_format({'num_format': '0.00%', 'border': 1})
    
    ws_summ.set_column('A:B', 30)
    ws_summ.write(0, 0, "COMPONENTE", header)
    ws_summ.write(0, 1, "RTP %", header)
    
    # Base
    ws_summ.write(1, 0, "RTP Juego Base")
    ws_summ.write_formula(1, 1, f"={ref_base}", percent)
    
    # FS Ponderado
    row = 5
    weighted_parts = []
    for i, ref in enumerate(refs_fs):
        ws_summ.write(row+i, 0, f"RTP Escenario {i+1} (Peso {weights_fs[i]*100}%)")
        ws_summ.write_formula(row+i, 1, f"={ref}", percent)
        weighted_parts.append(f"B{row+i+1}*{weights_fs[i]}")
    
    ws_summ.write(2, 0, "RTP Free Spins (Ponderado)")
    # (RTP_Pond * Prob * Spins) -> OJO: El RTP calculado en hojas YA es retorno sobre apuesta.
    # Solo falta multiplicar por Probabilidad de entrada y cantidad de giros.
    # En el Excel del cliente, "RTP" era 820% (Pay per spin).
    
    prob_trigger = 0.006050
    avg_spins = 10.24
    
    # Formula: (Suma(RTPs Ponderados)) * Prob * Spins
    sum_rtp_fs = "+".join(weighted_parts)
    ws_summ.write_formula(2, 1, f"=({sum_rtp_fs})*{prob_trigger}*{avg_spins}", percent)
    
    # Jackpot
    ws_summ.write(3, 0, "RTP Jackpot")
    ws_summ.write(3, 1, 0.06, percent)
    
    # Total
    ws_summ.write(4, 0, "RTP TOTAL", header)
    ws_summ.write_formula(4, 1, "=B2+B3+B4", percent)
    
    workbook.close()
    print(f"[OK] Excel Formato Cliente generado: {filename}")

if __name__ == "__main__":
    generate_excel_parsheet()