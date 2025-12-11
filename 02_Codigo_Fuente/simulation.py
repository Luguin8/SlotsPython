import time
import random
import math
import statistics
import json
import sys
import os  # <--- Agregado para manejar carpetas
import config
from main import SlotMachine

# Configuración de la Simulación
NUM_SESSIONS = 150          # Cantidad de sesiones para el promedio
SPINS_PER_SESSION = 200000  # Giros por sesión (Total 30M de giros)
# Usaremos la carpeta estandarizada según el LEEME
LOG_FILE = "../03_Reportes_Validacion/simulation_log.json"

def run_single_session(seed_val, session_id=1):
    """Ejecuta una sesión completa con una semilla específica."""
    random.seed(seed_val)
    slot = SlotMachine()
    
    total_bet = 0
    total_won = 0
    base_hits = 0
    feature_hits = 0
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    
    # Ejecución rápida
    for _ in range(SPINS_PER_SESSION):
        res = slot.spin_base_game()
        total_bet += config.PAYLINES_COUNT
        total_won += res['total_win']
        
        if res['base_win'] > 0:
            base_hits += 1
        
        if res['feature_data']:
            feature_hits += 1
            jps = res['feature_data']['jackpots_hit']
            for k in jps:
                jp_hits[k] += jps[k]

    rtp = (total_won / total_bet) * 100
    return {
        "session_id": session_id,
        "seed": seed_val,
        "rtp": rtp,
        "total_bet": total_bet,
        "total_won": total_won,
        "bonuses": feature_hits,
        "jackpots": jp_hits
    }

def run_batch_simulation():
    print(f"--- INICIANDO SIMULACIÓN DE VARIANZA REAL ---")
    print(f"Sesiones: {NUM_SESSIONS}")
    print(f"Giros por Sesión: {SPINS_PER_SESSION:,}")
    print(f"Total Giros: {NUM_SESSIONS * SPINS_PER_SESSION:,}")
    print("-" * 60)

    results = []
    rtp_values = []
    
    start_time = time.time()
    
    for i in range(1, NUM_SESSIONS + 1):
        # Generamos una semilla aleatoria para cada sesión
        current_seed = random.randint(1000000000, 9999999999)
        
        data = run_single_session(current_seed, session_id=i)
        results.append(data)
        rtp_values.append(data["rtp"])
        
        # Progreso
        if i % 10 == 0 or i == NUM_SESSIONS:
            print(f"Sesión {i}/{NUM_SESSIONS} | Seed: {current_seed} | RTP: {data['rtp']:.2f}%")

    duration = time.time() - start_time
    
    # Análisis Estadístico
    mean_rtp = statistics.mean(rtp_values)
    stdev_rtp = statistics.stdev(rtp_values)
    
    # Intervalo de Confianza 95%
    standard_error = stdev_rtp / math.sqrt(NUM_SESSIONS)
    margin_error = 1.96 * standard_error
    ci_lower = mean_rtp - margin_error
    ci_upper = mean_rtp + margin_error
    
    # --- CORRECCIÓN: Crear carpeta si no existe ---
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        print(f"[INFO] Carpeta creada: {log_dir}")
    
    # Guardar Log JSON para el cliente
    with open(LOG_FILE, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\n" + "="*60)
    print("      RESULTADOS ESTADÍSTICOS (SEMILLA VARIABLE)      ")
    print("============================================================")
    print(f"Tiempo Total:     {duration:.1f} segundos")
    print(f"Log guardado en:  {LOG_FILE}")
    print("-" * 60)
    print(f"RTP PROMEDIO:     {mean_rtp:.4f}%")
    print(f"Desviación Std:   {stdev_rtp:.4f}")
    print(f"Intervalo 95%:    [{ci_lower:.4f}%, {ci_upper:.4f}%]")
    print("-" * 60)
    print("VERIFICACIÓN:")
    print("Para verificar una sesión específica, ejecuta:")
    print(f"python simulation.py --verify [SEED]")
    print("============================================================")

def run_verification_mode(seed_input):
    print(f"\n--- MODO VERIFICACIÓN DE SEMILLA ---")
    print(f"Replicando sesión con Seed: {seed_input}")
    print("-" * 40)
    
    start = time.time()
    data = run_single_session(int(seed_input), session_id=999)
    duration = time.time() - start
    
    print(f"RESULTADO REPLICADO:")
    print(f"RTP:        {data['rtp']:.4f}%")
    print(f"Total Bet:  {data['total_bet']}")
    print(f"Total Won:  {data['total_won']}")
    print(f"Bonos:      {data['bonuses']}")
    print(f"Jackpots:   {data['jackpots']}")
    print(f"Tiempo:     {duration:.2f}s")
    print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--verify":
        seed_arg = sys.argv[2]
        run_verification_mode(seed_arg)
    else:
        run_batch_simulation()