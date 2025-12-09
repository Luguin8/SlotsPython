# generar_par_excel_v2.py
import csv
import config

def generate_par_data():
    print("--- GENERANDO DATOS PARA PAR SHEET (BASE + 4 ESCENARIOS) ---")
    
    # Función auxiliar para contar y exportar
    def export_scenario(filename, strips, title):
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow([f"--- DATOS: {title} ---"])
            writer.writerow(["Symbol ID", "Name", "R1", "R2", "R3", "R4", "R5", "Total Hits Cycle"])
            
            counts = []
            for col in range(5):
                c = {}
                for s in strips[col]: c[s] = c.get(s,0)+1
                counts.append(c)
                
            reel_lens = [len(s) for s in strips]
            cycle = 1
            for l in reel_lens: cycle *= l
            
            sorted_ids = sorted(config.PAYTABLE.keys())
            for sym in sorted_ids:
                if sym in [10, 11]: continue # Scatters aparte
                
                c_vals = [counts[i].get(sym, 0) for i in range(5)]
                # Ejemplo Hits 5
                hits5 = c_vals[0]*c_vals[1]*c_vals[2]*c_vals[3]*c_vals[4]
                
                row = [sym, ""] + c_vals + [hits5]
                writer.writerow(row)
        print(f"Generado: {filename}")

    # 1. Base
    export_scenario("PAR_Data_Base.csv", config.FIXED_STRIPS_BASE, "JUEGO BASE")
    
    # 2. Escenarios FG (usamos los mismos strips, la logica cambia en el calculo de pago, pero los conteos son los mismos)
    # El cliente quiere ver las combinaciones. Como los strips son fijos, el conteo fisico es el mismo.
    # Lo que cambia es el "Wild sustituto".
    export_scenario("PAR_Data_FS_Physical.csv", config.FIXED_STRIPS_FS, "FÍSICO GIROS GRATIS")
    
    print("Listo. Entrega estos CSVs al cliente para que alimente su Excel.")

if __name__ == "__main__":
    generate_par_data()