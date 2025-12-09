# export.py
import csv
import config

def export_project():
    print("--- GENERANDO ENTREGABLES FINALES (FORMATO GLI) ---")
    
    strips_base = config.generate_strips(config.REEL_WEIGHTS_BASE)
    strips_fs = config.generate_strips(config.REEL_WEIGHTS_FS)
    
    SYM_NAMES = {
        1: "Low 1", 2: "Low 2", 3: "Low 3", 4: "Low 4",
        5: "High 1", 6: "High 2", 7: "High 3", 8: "High 4",
        10: "SCATTER", 11: "SCATTER JP",
        12: "Wild x1", 13: "Wild x2", 14: "Wild x3"
    }

    def write_strips_csv(filename, strips, title):
        max_len = max(len(s) for s in strips)
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow([f"--- {title} ---"])
            
            # FORMATO SOLICITADO: ID y NOMBRE separados
            header = []
            for i in range(1, 6):
                header.append(f"R{i} ID")
                header.append(f"R{i} Name")
            
            writer.writerow(["Pos"] + header)
            
            for i in range(max_len):
                row_data = [i]
                for col in range(5):
                    if i < len(strips[col]):
                        sym_id = strips[col][i]
                        name = SYM_NAMES.get(sym_id, "Unknown")
                        row_data.append(sym_id)
                        row_data.append(name)
                    else:
                        row_data.append("")
                        row_data.append("")
                writer.writerow(row_data)
        print(f"[OK] Archivo generado: {filename}")

    write_strips_csv("Entregable_Reel_Strips_BASE.csv", strips_base, "JUEGO BASE")
    write_strips_csv("Entregable_Reel_Strips_FS.csv", strips_fs, "GIROS GRATIS")

    # Tabla de pagos (igual que antes)
    with open("Entregable_Paytable.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(["Symbol ID", "Name", "3x", "4x", "5x"])
        for sym_id in sorted(config.PAYTABLE.keys()):
            p = config.PAYTABLE[sym_id]
            writer.writerow([sym_id, SYM_NAMES.get(sym_id,""), p.get(3,0), p.get(4,0), p.get(5,0)])
            
    print("[OK] Paytable generada.")

if __name__ == "__main__":
    export_project()