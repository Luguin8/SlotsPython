import time
import random
import math
import statistics
import config
from main import SlotMachine

def run_simulation_batch():
    SEED_BASE = 777
    random.seed(SEED_BASE)
    # --- CONFIGURACIÓN ESTADÍSTICA ---
    NUM_SESSIONS = 50        # Cantidad de sesiones independientes
    SPINS_PER_SESSION = 200000 # Giros por sesión (Total = 10M giros)
    # Nota: 50 x 200k = 10 Millones de giros total. Es un buen balance velocidad/precisión.
    
    print(f"--- INICIANDO SIMULACIÓN ESTADÍSTICA POR LOTES ---")
    print(f"Sesiones: {NUM_SESSIONS}")
    print(f"Giros/Sesión: {SPINS_PER_SESSION:,}")
    print(f"Total Giros: {NUM_SESSIONS * SPINS_PER_SESSION:,}")
    print("-" * 60)
    
    session_rtps = []
    start_global = time.time()
    
    # Ejecutamos las sesiones
    for session_idx in range(1, NUM_SESSIONS + 1):
        slot = SlotMachine()
        total_bet = 0
        total_won = 0
        
        # Loop de giros de esta sesión
        for _ in range(SPINS_PER_SESSION):
            res = slot.spin_base_game()
            total_bet += config.PAYLINES_COUNT
            total_won += res['total_win']
        
        # RTP de esta sesión
        session_rtp = (total_won / total_bet) * 100
        session_rtps.append(session_rtp)
        
        # Progreso visual simple
        if session_idx % 5 == 0:
            print(f"Sesión {session_idx}/{NUM_SESSIONS} completada -> RTP: {session_rtp:.2f}%")

    duration = time.time() - start_global
    
    # --- ANÁLISIS ESTADÍSTICO ---
    mean_rtp = statistics.mean(session_rtps)
    stdev_rtp = statistics.stdev(session_rtps)
    
    # Margen de error (95% confianza, Z=1.96)
    # Error estándar de la media = stdev / sqrt(n)
    standard_error = stdev_rtp / math.sqrt(NUM_SESSIONS)
    margin_error = 1.96 * standard_error
    
    ci_lower = mean_rtp - margin_error
    ci_upper = mean_rtp + margin_error
    
    print("\n" + "="*60)
    print("      RESULTADOS DE VALIDACIÓN ESTADÍSTICA      ")
    print("============================================================")
    print(f"Tiempo Total:     {duration:.1f} segundos")
    print("-" * 60)
    print(f"RTP PROMEDIO (Simulado):  {mean_rtp:.4f}%")
    print(f"Desviación Estándar:      {stdev_rtp:.4f}")
    print(f"Intervalo Confianza (95%): [{ci_lower:.4f}%, {ci_upper:.4f}%]")
    print("-" * 60)
    print("CONCLUSIÓN:")
    print("Si el RTP TEÓRICO cae dentro del intervalo anterior,")
    print("el modelo matemático está VALIDADO.")
    print("="*60)

if __name__ == "__main__":
    run_simulation_batch()