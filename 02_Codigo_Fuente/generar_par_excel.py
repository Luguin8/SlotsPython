# generar_par_excel.py
import csv
import config

def generate_par_report():
    print("--- GENERANDO DATOS PARA EXCEL TEÓRICO (PAR SHEET) ---")
    
    # 1. Obtener Rieles Fijos
    strips_base = config.generate_strips(config.REEL_WEIGHTS_BASE)
    reel_lengths = [len(s) for s in strips_base]
    base_cycle = 1
    for l in reel_lengths: base_cycle *= l
    
    # 2. Contar símbolos por riel
    counts = []
    for col in range(5):
        reel_counts = {}
        for sym in strips_base[col]:
            reel_counts[sym] = reel_counts.get(sym, 0) + 1
        counts.append(reel_counts)
        
    # 3. Generar CSV detallado
    filename = "Reporte_PAR_Detallado.csv"
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Encabezados
        writer.writerow(["--- TABLA MATEMÁTICA JUEGO BASE ---"])
        header = [
            "Symbol ID", "Name", 
            "Count R1", "Count R2", "Count R3", "Count R4", "Count R5",
            "Pays (3)", "Pays (4)", "Pays (5)",
            "Hits (3)", "Hits (4)", "Hits (5)",
            "Total Pay (3)", "Total Pay (4)", "Total Pay (5)",
            "Total EV", "RTP Contribution %"
        ]
        writer.writerow(header)
        
        total_rtp_base = 0
        
        # Nombres para referencia
        SYM_NAMES = {
            1: "Low 1", 2: "Low 2", 3: "Low 3", 4: "Low 4",
            5: "High 1", 6: "High 2", 7: "High 3", 8: "High 4",
            10: "SCATTER", 11: "SCATTER JP"
        }

        sorted_ids = sorted(config.PAYTABLE.keys())
        
        for sym_id in sorted_ids:
            if sym_id in [10, 11]: continue # Scatters se calculan aparte
            
            name = SYM_NAMES.get(sym_id, f"Sym {sym_id}")
            pay = config.PAYTABLE[sym_id]
            
            # Conteos por riel
            c = [counts[i].get(sym_id, 0) for i in range(5)]
            others = [reel_lengths[i] - c[i] for i in range(5)]
            
            # Cálculo Combinatorio (Hits en el Ciclo)
            # 5 of a kind: c1*c2*c3*c4*c5
            hits_5 = c[0] * c[1] * c[2] * c[3] * c[4]
            
            # 4 of a kind: c1*c2*c3*c4 * others5
            hits_4 = c[0] * c[1] * c[2] * c[3] * others[4]
            
            # 3 of a kind: c1*c2*c3 * others4 * TotalR5
            hits_3 = c[0] * c[1] * c[2] * others[3] * reel_lengths[4] # Riel 5 cualquiera
            
            # Total Pagado en el Ciclo
            pay_total_5 = hits_5 * pay.get(5, 0)
            pay_total_4 = hits_4 * pay.get(4, 0)
            pay_total_3 = hits_3 * pay.get(3, 0)
            
            total_pay_cycle = pay_total_5 + pay_total_4 + pay_total_3
            
            # RTP Contribución = (Total Pagado * Lineas) / (Ciclo * Apuesta)
            # Simplificado: (Total Pagado / Ciclo) * 100  (Si asumimos 1 linea por apuesta unitaria)
            # Ajuste exacto: EV Symbol = Total Pagado / Ciclo.
            # RTP Symbol = EV Symbol * 100 (Ya que la apuesta se distribuye)
            
            ev_symbol = total_pay_cycle / base_cycle
            rtp_contrib = ev_symbol * 100
            
            total_rtp_base += rtp_contrib
            
            row = [
                sym_id, name,
                c[0], c[1], c[2], c[3], c[4],
                pay.get(3,0), pay.get(4,0), pay.get(5,0),
                hits_3, hits_4, hits_5,
                pay_total_3, pay_total_4, pay_total_5,
                f"{ev_symbol:.6f}", f"{rtp_contrib:.4f}%"
            ]
            writer.writerow(row)
            
        writer.writerow([])
        writer.writerow(["TOTAL RTP BASE", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", f"{total_rtp_base:.4f}%"])

    print(f"[OK] Archivo generado: {filename}")
    print("Entrega este archivo Excel al cliente. Contiene las fórmulas desglosadas.")

if __name__ == "__main__":
    generate_par_report()