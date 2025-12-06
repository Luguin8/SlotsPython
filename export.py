# export.py
import csv
import config

def export_project():
    print("--- GENERANDO ARCHIVOS PARA EL CLIENTE (Formato Latino) ---")
    
    # 1. GENERAR RODILLOS DEFINITIVOS
    strips = config.generate_dummy_strips()
    
    max_len = max(len(s) for s in strips)
    
    SYM_NAMES = {
        1: "Low 1", 2: "Low 2", 3: "Low 3", 4: "Low 4",
        5: "High 1 (Wild x1)", 6: "High 2 (Wild x2)", 
        7: "High 3 (Wild x2)", 8: "High 4 (Wild x3)",
        9: "WILD BASE", 10: "SCATTER", 11: "SCATTER JP"
    }

    # --- ARCHIVO 1: REEL STRIPS ---
    filename_strips = "Entregable_Reel_Strips.csv"
    # CAMBIO AQUÍ: Agregamos delimiter=';'
    with open(filename_strips, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';') 
        
        # Encabezados
        writer.writerow(["Position", "Reel 1", "Reel 2", "Reel 3", "Reel 4", "Reel 5"])
        
        for i in range(max_len):
            row_data = [i]
            for col in range(5):
                if i < len(strips[col]):
                    sym_id = strips[col][i]
                    row_data.append(f"{sym_id} - {SYM_NAMES.get(sym_id, 'Unknown')}")
                else:
                    row_data.append("")
            writer.writerow(row_data)
            
    print(f"[OK] Rodillos exportados a: {filename_strips}")

    # --- ARCHIVO 2: PAYTABLE ---
    filename_pay = "Entregable_Paytable.csv"
    # CAMBIO AQUÍ: Agregamos delimiter=';'
    with open(filename_pay, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        
        writer.writerow(["Symbol ID", "Name", "3 of a Kind", "4 of a Kind", "5 of a Kind"])
        
        sorted_ids = sorted(config.PAYTABLE.keys())
        
        for sym_id in sorted_ids:
            payouts = config.PAYTABLE[sym_id]
            name = SYM_NAMES.get(sym_id, "Unknown")
            
            p3 = payouts.get(3, 0)
            p4 = payouts.get(4, 0)
            p5 = payouts.get(5, 0)
            
            writer.writerow([sym_id, name, p3, p4, p5])
            
    print(f"[OK] Tabla de pagos exportada a: {filename_pay}")
    print("\nLISTO. Ahora sí Excel debería abrirlo en columnas separadas.")

if __name__ == "__main__":
    export_project()