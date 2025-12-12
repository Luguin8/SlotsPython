import xlsxwriter
import config

def get_counts_for_scenario(strips, sym_id, wild_id=None):
    """Retorna los conteos por riel para un símbolo y el wild (si aplica)."""
    counts_sym = []
    counts_wild = []
    lengths = []
    
    for col in range(5):
        strip = strips[col]
        lengths.append(len(strip))
        
        # Conteo del símbolo objetivo
        c_s = strip.count(sym_id)
        # Conteo del Wild (si existe en este escenario)
        c_w = strip.count(wild_id) if wild_id is not None else 0
        
        # Si el símbolo objetivo ES el que se transforma en Wild, ajustamos
        if sym_id == wild_id:
            # En el riel transformado, el símbolo original YA ES Wild.
            # Así que técnicamente el "símbolo base" desaparece y todo es Wild.
            c_w = c_s 
            c_s = 0 
            
        counts_sym.append(c_s)
        counts_wild.append(c_w)
        
    return counts_sym, counts_wild, lengths

def add_math_sheet(workbook, sheet_name, strips, wild_id=None, multiplier=1):
    ws = workbook.add_worksheet(sheet_name)
    
    # Formatos
    header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#366092', 'border': 1, 'align': 'center'})
    cell = workbook.add_format({'border': 1, 'align': 'center'})
    percent = workbook.add_format({'num_format': '0.000000%', 'border': 1})
    currency = workbook.add_format({'num_format': '0.00', 'border': 1})
    
    # Encabezados
    cols = ["Symbol", "Pay 5", "Pay 4", "Pay 3", 
            "R1 Sym", "R2 Sym", "R3 Sym", "R4 Sym", "R5 Sym", 
            "R1 Wild", "R2 Wild", "R3 Wild", "R4 Wild", "R5 Wild",
            "Prob 5 Hit", "Prob 5 Pure", "EV 5", 
            "Prob 4 Hit", "Prob 4 Pure", "EV 4",
            "Prob 3 Hit", "Prob 3 Pure", "EV 3",
            "TOTAL EV %"]
            
    ws.write_row(0, 0, cols, header)
    
    # Datos de Rieles (Largos) para usar en fórmulas
    lengths = [len(s) for s in strips]
    # Escribimos los largos arriba para referencia (Fila 0, Columnas Z en adelante ocultas o lejos)
    # Mejor los hardcodeamos en las fórmulas para que sea legible o usamos celdas auxiliares
    
    row = 1
    # Nombres para mostrar
    names = {1:"L1", 2:"L2", 3:"L3", 4:"L4", 5:"H1", 6:"H2", 7:"H3", 8:"H4"}
    
    total_ev_ref = []
    
    for sym_id in config.PAYTABLE:
        if sym_id >= 10: continue # Ignoramos scatters aquí para simplificar la vista combinatoria
        if wild_id is not None and sym_id == wild_id: continue # El símbolo que se vuelve wild se trata diferente (es el Wild)

        pays = config.PAYTABLE[sym_id]
        c_sym, c_wild, _ = get_counts_for_scenario(strips, sym_id, wild_id)
        
        # Col A-D: Info Básica
        ws.write(row, 0, names.get(sym_id, str(sym_id)), cell)
        ws.write(row, 1, pays.get(5,0), cell)
        ws.write(row, 2, pays.get(4,0), cell)
        ws.write(row, 3, pays.get(3,0), cell)
        
        # Col E-I: Counts Symbol
        for i in range(5): ws.write(row, 4+i, c_sym[i], cell)
        # Col J-N: Counts Wild
        for i in range(5): ws.write(row, 9+i, c_wild[i], cell)
        
        # --- FÓRMULAS DE PROBABILIDAD (CAJA BLANCA) ---
        # Prob Hit (Sym + Wild) / Len
        # Prob Pure (Sym) / Len
        
        # Helpers para las celdas de Counts y Lengths
        # R1_Sym = E{row+1}, R1_Wild = J{row+1}, Len1 = {lengths[0]}
        
        # Definimos las probabilidades por riel como strings de fórmula
        p_hit = []
        p_pure = []
        
        chars = ['E','F','G','H','I'] # Columnas Sym
        charw = ['J','K','L','M','N'] # Columnas Wild
        
        for i in range(5):
            # (Sym + Wild) / Len
            p_hit.append(f"(({chars[i]}{row+1}+{charw[i]}{row+1})/{lengths[i]})")
            # (Sym) / Len
            p_pure.append(f"({chars[i]}{row+1}/{lengths[i]})")

        # --- 5 OF A KIND ---
        # Prob Total 5 = P1*P2*P3*P4*P5
        f_p5_hit = "=" + "*".join(p_hit)
        ws.write_formula(row, 14, f_p5_hit, percent)
        
        # Prob Pure 5 = P1_pure * ...
        f_p5_pure = "=" + "*".join(p_pure)
        ws.write_formula(row, 15, f_p5_pure, percent)
        
        # EV 5 = (Pure * Pay) + ((Hit - Pure) * Pay * Mult)
        # O15 = Hit, P15 = Pure, B15 = Pay
        f_ev5 = f"=(P{row+1}*B{row+1}) + ((O{row+1}-P{row+1})*B{row+1}*{multiplier})"
        ws.write_formula(row, 16, f_ev5, percent) # EV como %
        
        # --- 4 OF A KIND ---
        # Prob 4 = P1*P2*P3*P4*(1-P5)
        f_p4_hit = "=" + "*".join(p_hit[:4]) + f"*(1-{p_hit[4]})"
        ws.write_formula(row, 17, f_p4_hit, percent)
        
        f_p4_pure = "=" + "*".join(p_pure[:4]) + f"*(1-{p_pure[4]})"
        ws.write_formula(row, 18, f_p4_pure, percent)
        
        # EV 4
        f_ev4 = f"=(S{row+1}*C{row+1}) + ((R{row+1}-S{row+1})*C{row+1}*{multiplier})"
        ws.write_formula(row, 19, f_ev4, percent)

        # --- 3 OF A KIND ---
        # Prob 3 = P1*P2*P3*(1-P4)
        f_p3_hit = "=" + "*".join(p_hit[:3]) + f"*(1-{p_hit[3]})"
        ws.write_formula(row, 20, f_p3_hit, percent)
        
        f_p3_pure = "=" + "*".join(p_pure[:3]) + f"*(1-{p_pure[3]})"
        ws.write_formula(row, 21, f_p3_pure, percent)
        
        # EV 3
        f_ev3 = f"=(V{row+1}*D{row+1}) + ((U{row+1}-V{row+1})*D{row+1}*{multiplier})"
        ws.write_formula(row, 22, f_ev3, percent)
        
        # TOTAL EV LINE
        ws.write_formula(row, 23, f"=Q{row+1}+T{row+1}+W{row+1}", percent)
        total_ev_ref.append(f"X{row+1}")
        
        row += 1
        
    # --- LÍNEA DE 5 WILDS (Solo si hay Wilds) ---
    if wild_id is not None:
        ws.write(row, 0, "ONLY WILDS", cell)
        
        # Counts solo de wilds
        c_sym, c_wild, _ = get_counts_for_scenario(strips, wild_id, wild_id) # Trick to get counts
        for i in range(5): ws.write(row, 9+i, c_wild[i], cell)
        
        # Prob 5 Wilds
        p_wilds = []
        charw = ['J','K','L','M','N']
        for i in range(5): p_wilds.append(f"({charw[i]}{row+1}/{lengths[i]})")
        
        ws.write_formula(row, 14, "="+"*".join(p_wilds), percent)
        
        # Pago (Simbolo original * Mult)
        orig_pay = config.PAYTABLE[wild_id][5]
        ws.write(row, 1, orig_pay, cell)
        
        # EV (Prob * Pay * Mult)
        ws.write_formula(row, 23, f"=O{row+1}*B{row+1}*{multiplier}", percent)
        total_ev_ref.append(f"X{row+1}")
        row += 1

    # SUMA TOTAL DEL ESCENARIO
    ws.write(row, 22, "TOTAL ESCENARIO:", header)
    ws.write_formula(row, 23, f"=SUM({','.join(total_ev_ref)})", percent)
    
    return f"'{sheet_name}'!X{row+1}" # Retornamos la referencia a la celda total

def generate_excel_parsheet():
    filename = "../01_Excels_Rieles_Pagos/Slot_Parsheet_Teorico.xlsx"
    workbook = xlsxwriter.Workbook(filename)
    
    # Hoja Resumen
    ws_summ = workbook.add_worksheet("Resumen RTP")
    header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#366092', 'border': 1})
    percent = workbook.add_format({'num_format': '0.00%', 'border': 1})
    
    # 1. Generar Hojas de Detalle
    ref_base = add_math_sheet(workbook, "Base Game", config.FIXED_STRIPS_BASE)
    
    refs_fs = []
    weights_fs = []
    
    for feat in config.FEATURE_WEIGHTS:
        sym_id, mult, weight = feat
        sheet_name = f"FS_Wild{sym_id}_x{mult}"
        ref = add_math_sheet(workbook, sheet_name, config.FIXED_STRIPS_FS, wild_id=sym_id, multiplier=mult)
        refs_fs.append(ref)
        weights_fs.append(weight/100.0)

    # 2. Llenar Resumen con Fórmulas Vinculadas
    ws_summ.set_column('A:B', 30)
    ws_summ.write(0, 0, "COMPONENTE", header)
    ws_summ.write(0, 1, "RTP %", header)
    
    # RTP Base
    ws_summ.write(1, 0, "RTP Juego Base")
    ws_summ.write_formula(1, 1, f"={ref_base}", percent)
    
    # RTP FS (Ponderado)
    # Fórmula: (EV1*W1 + EV2*W2...) * ProbTrigger * AvgSpins / Bet
    # Nota: Los EVs de las hojas ya son % sobre la apuesta unitaria si asumimos 1 linea, 
    # pero aquí el EV calculado es SUM(Prob*Pay). 
    # Si Pay es creditos y Prob es absoluta, EV es creditos promedio ganados por giro.
    # Para RTP hay que dividir por Apuesta Total.
    # En add_math_sheet, EV3 = Prob * Pay. Si Pay = 100 creditos. EV = 0.01 * 100 = 1 credito.
    # Entonces el TOTAL ESCENARIO es Creditos Promedio por Giro.
    
    # Corrección rápida: En add_math_sheet usé "percent" para visualizar, pero el valor numérico es créditos ganados.
    # Para convertir a RTP hay que dividir por config.PAYLINES_COUNT
    
    # Vamos a hacerlo explícito en el Resumen
    row = 5
    ws_summ.write(row, 0, "CÁLCULO FREE SPINS", header)
    
    weighted_sum_parts = []
    for i, ref in enumerate(refs_fs):
        ws_summ.write(row+1+i, 0, f"EV Escenario {i+1} (Peso {weights_fs[i]:.2%})")
        # Traemos el valor de la hoja
        ws_summ.write_formula(row+1+i, 1, f"={ref}", workbook.add_format({'num_format': '0.00'})) # Creditos
        weighted_sum_parts.append(f"B{row+2+i}*{weights_fs[i]}")
        
    row += 5
    ws_summ.write(row, 0, "EV Promedio por Giro FS")
    ws_summ.write_formula(row, 1, f"={'+'.join(weighted_sum_parts)}", workbook.add_format({'num_format': '0.00'}))
    cell_ev_avg = f"B{row+1}"
    
    ws_summ.write(row+1, 0, "Probabilidad Entrada")
    ws_summ.write(row+1, 1, 0.006050, workbook.add_format({'num_format': '0.000000'}))
    cell_prob = f"B{row+2}"
    
    ws_summ.write(row+2, 0, "Giros Promedio")
    ws_summ.write(row+2, 1, 10.24, workbook.add_format({'num_format': '0.00'}))
    cell_spins = f"B{row+3}"
    
    ws_summ.write(row+3, 0, "Apuesta Total")
    ws_summ.write(row+3, 1, config.PAYLINES_COUNT)
    cell_bet = f"B{row+4}"
    
    # RTP FINAL FS
    ws_summ.write(2, 0, "RTP Free Spins")
    # (EV_Avg * Prob * Spins) / Bet
    ws_summ.write_formula(2, 1, f"=({cell_ev_avg}*{cell_prob}*{cell_spins})/{cell_bet}", percent)
    
    # RTP Jackpot
    ws_summ.write(3, 0, "RTP Jackpot")
    ws_summ.write(3, 1, 0.06, percent)
    
    # RTP TOTAL
    ws_summ.write(4, 0, "RTP TOTAL TEÓRICO", header)
    # Suma de Base (ajustado por apuesta) + FS + JP
    # Ojo: ref_base trae créditos, hay que dividir por apuesta
    ws_summ.write_formula(4, 1, f"=(B2/{cell_bet}) + B3 + B4", percent)

    workbook.close()
    print(f"[OK] Excel Detallado generado: {filename}")

if __name__ == "__main__":
    generate_excel_parsheet()