import time
import random
import math
import statistics
import json
import sys
import os
import config
from main import SlotMachine

# Configuración de la Simulación
NUM_SESSIONS = 400          # <--- AUMENTADO A 400 PARA REDUCIR MARGEN DE ERROR
SPINS_PER_SESSION = 200000  
LOG_FILE = "../03_Reportes_Validacion/simulation_log.json"

def run_single_session(seed_val, session_id=1):
    random.seed(seed_val)
    slot = SlotMachine()
    total_bet = 0
    total_won = 0
    base_hits = 0
    feature_hits = 0
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    
    for _ in range(SPINS_PER_SESSION):
        res = slot.spin_base_game()
        total_bet += config.PAYLINES_COUNT
        total_won += res['total_win']
        
        if res['base_win'] > 0: base_hits += 1
        if res['feature_data']:
            feature_hits += 1
            jps = res['feature_data']['jackpots_hit']
            for k in jps: jp_hits[k] += jps[k]

    rtp = (total_won / total_bet) * 100
    return {"session_id": session_id, "seed": seed_val, "rtp": rtp, 
            "total_bet": total_bet, "total_won": total_won, 
            "bonuses": feature_hits, "jackpots": jp_hits}

def run_batch_simulation():
    print(f"--- INICIANDO SIMULACIÓN CIENTÍFICA (400 MUESTRAS) ---")
    print(f"Total Giros: {NUM_SESSIONS * SPINS_PER_SESSION:,}")
    print("-" * 60)

    results = []
    rtp_values = []
    start_time = time.time()
    
    for i in range(1, NUM_SESSIONS + 1):
        current_seed = random.randint(1000000000, 9999999999)
        data = run_single_session(current_seed, session_id=i)
        results.append(data)
        rtp_values.append(data["rtp"])
        
        if i % 20 == 0: # Print menos frecuente para no spammear
            print(f"Sesión {i}/{NUM_SESSIONS} | RTP: {data['rtp']:.2f}%")

    duration = time.time() - start_time
    
    mean_rtp = statistics.mean(rtp_values)
    stdev_rtp = statistics.stdev(rtp_values)
    standard_error = stdev_rtp / math.sqrt(NUM_SESSIONS)
    margin_error = 1.96 * standard_error # 95% Confidence
    
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir): os.makedirs(log_dir)
    
    with open(LOG_FILE, 'w') as f:
        json.dump(results, f, indent=4)
        
    print("\n" + "="*60)
    print("      RESULTADOS ESTADÍSTICOS FINALES      ")
    print("============================================================")
    print(f"Tiempo Total:     {duration:.1f} segundos")
    print("-" * 60)
    print(f"RTP PROMEDIO:     {mean_rtp:.4f}%")
    print(f"Desviación Std:   {stdev_rtp:.4f} (Normal para Slots con Multiplicador)")
    print(f"Margen de Error:  {margin_error:.4f}%")
    print(f"Intervalo 95%:    [{mean_rtp - margin_error:.4f}%, {mean_rtp + margin_error:.4f}%]")
    print("============================================================")

def run_verification_mode(seed_input):
    print(f"\n--- MODO VERIFICACIÓN DE SEMILLA ---")
    print(f"Replicando sesión con Seed: {seed_input}")
    start = time.time()
    data = run_single_session(int(seed_input), session_id=999)
    print(f"RTP REPLICADO: {data['rtp']:.4f}%")

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--verify":
        run_verification_mode(sys.argv[2])
    else:
        run_batch_simulation()