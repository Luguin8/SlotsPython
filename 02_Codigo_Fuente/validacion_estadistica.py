# validacion_estadistica.py
import random
import math
import statistics
from main import SlotMachine
import config
import time

def run_validation_suite(num_simulations=150, spins_per_sim=1000000):
    print(f"--- INICIANDO VALIDACIÓN ESTADÍSTICA CIENTÍFICA ---")
    print(f"Configuración: {num_simulations} simulaciones de {spins_per_sim} giros cada una.")
    print(f"Total Giros: {num_simulations * spins_per_sim:,}")
    print("Objetivo: Validar que el RTP Teórico cae dentro del Intervalo de Confianza 95%.")
    print("-" * 60)
    
    rtp_results = []
    start_time_total = time.time()
    
    for i in range(num_simulations):
        # Semilla variable pero deterministica para cada run (0, 1, 2...)
        random.seed(i) 
        
        slot = SlotMachine()
        total_bet = 0
        total_won = 0
        bet_per_spin = config.PAYLINES_COUNT
        
        # Optimizacion: Loop puro sin prints intermedios
        for _ in range(spins_per_sim):
            res = slot.spin_base_game()
            total_bet += bet_per_spin
            total_won += res['total_win']
            
        sim_rtp = (total_won / total_bet) * 100
        rtp_results.append(sim_rtp)
        
        if (i+1) % 10 == 0:
            elapsed = time.time() - start_time_total
            print(f"Simulacion {i+1}/{num_simulations} | RTP Run: {sim_rtp:.2f}% | Tiempo: {elapsed:.1f}s")

    # --- CÁLCULOS ESTADÍSTICOS FINALES ---
    mean_rtp = statistics.mean(rtp_results)
    stdev = statistics.stdev(rtp_results)
    
    # Error Estandar de la Media (SEM)
    sem = stdev / math.sqrt(num_simulations)
    
    # Margen de Error 95% (Z=1.96)
    margin_error = 1.96 * sem
    
    lower_bound = mean_rtp - margin_error
    upper_bound = mean_rtp + margin_error
    
    print("\n" + "="*60)
    print("      RESULTADOS DE LA VALIDACIÓN ESTADÍSTICA      ")
    print("============================================================")
    print(f"RTP Promedio (Media Muestral): {mean_rtp:.4f}%")
    print(f"Desviación Estándar (Sigma):   {stdev:.4f}")
    print(f"Margen de Error (95% CI):      +/- {margin_error:.4f}%")
    print(f"Intervalo de Confianza:        [{lower_bound:.4f}%, {upper_bound:.4f}%]")
    print("-" * 60)
    print("Para validar, revisa si tu RTP Teórico (theory_check_v2.py)")
    print("cae dentro de este intervalo.")
    print("="*60)

if __name__ == "__main__":
    # Ajusta spins_per_sim si tu PC es lenta, pero 1M es lo ideal para convergencia.
    run_validation_suite(num_simulations=150, spins_per_sim=1000000)