# export.py
import csv
import config

def export_project():
    print("--- GENERANDO ENTREGABLES FINALES ---")
    
    # 1. Generamos los strips usando la configuración V19 aprobada
    strips_base = config.generate_strips(config.REEL_WEIGHTS_BASE)
    strips_fs = config.generate_strips(config.REEL_WEIGHTS_FS)
    
    # Mapa de nombres para que el cliente entienda fácil
    SYM_NAMES = {
        1: "Low 1", 2: "Low 2", 3: "Low 3", 4: "Low 4",
        5: "High 1", 6: "High 2", 7: "High 3", 8: "High 4",
        10: "SCATTER (Base)", 11: "SCATTER JP (FS)",
        12: "Wild x1", 13: "Wild x2", 14: "Wild x3"
    }

    # Función auxiliar para escribir CSVs
    def write_strips_csv(filename, strips, title):
        max_len = max(len(s) for s in strips)
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            
            writer.writerow([f"--- {title} ---"])
            writer.writerow(["Position", "Reel 1", "Reel 2", "Reel 3", "Reel 4", "Reel 5"])
            
            for i in range(max_len):
                row_data = [i]
                for col in range(5):
                    if i < len(strips[col]):
                        sym_id = strips[col][i]
                        name = SYM_NAMES.get(sym_id, "Unknown")
                        row_data.append(f"{sym_id} - {name}")
                    else:
                        row_data.append("")
                writer.writerow(row_data)
        print(f"[OK] Archivo generado: {filename}")

    # --- EXPORTAR RIELES ---
    # Agregamos "../01_Excels_Rieles_Pagos/" antes del nombre
    write_strips_csv("../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_BASE.csv", strips_base, "JUEGO BASE (Sin Wilds, con Scatter)")
    write_strips_csv("../01_Excels_Rieles_Pagos/Entregable_Reel_Strips_FS.csv", strips_fs, "GIROS GRATIS (Sin Wilds, con Scatter JP)")

    # --- EXPORTAR TABLA DE PAGOS ---
    filename_pay = "../01_Excels_Rieles_Pagos/Entregable_Paytable.csv"

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
            
    print(f"[OK] Archivo generado: {filename_pay}")
    print("\n¡LISTO! Ya tienes los archivos para enviar al cliente.")

if __name__ == "__main__":
    export_project()