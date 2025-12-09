# validacion_estadistica.py
import random
import numpy as np # Si no tienes numpy, avísame y lo hago con math nativo
import math
from main import SlotMachine
import config

def run_validation_suite(num_simulations=150, spins_per_sim=100000):
    print(f"--- INICIANDO VALIDACIÓN ESTADÍSTICA ({num_simulations} x {spins_per_sim} giros) ---")
    print("Esto validará si el Teórico está dentro del Margen de Error.")
    
    rtp_results = []
    
    # Usamos una semilla base pero variable para cada run para garantizar independencia
    base_seed = 12345
    
    for i in range(num_simulations):
        random.seed(base_seed + i) # Semillas distintas pero reproducibles (12345, 12346, etc)
        
        slot = SlotMachine()
        total_bet = 0
        total_won = 0
        bet_per_spin = config.PAYLINES_COUNT
        
        for _ in range(spins_per_sim):
            res = slot.spin_base_game()
            total_bet += bet_per_spin
            total_won += res['total_win']
            
        sim_rtp = (total_won / total_bet) * 100
        rtp_results.append(sim_rtp)
        
        if (i+1) % 10 == 0:
            print(f"Simulación {i+1}/{num_simulations} completada... RTP: {sim_rtp:.2f}%")

    # --- CÁLCULOS ESTADÍSTICOS ---
    mean_rtp = sum(rtp_results) / len(rtp_results)
    
    # Desviación Estándar de la MUESTRA
    variance = sum((x - mean_rtp) ** 2 for x in rtp_results) / (num_simulations - 1)
    std_dev = math.sqrt(variance)
    
    # Error Estándar de la Media (SEM)
    sem = std_dev / math.sqrt(num_simulations)
    
    # Margen de Error (95% confianza => Z=1.96)
    margin_error = 1.96 * sem
    
    lower_bound = mean_rtp - margin_error
    upper_bound = mean_rtp + margin_error
    
    # VALOR TEÓRICO CALCULADO ANTES
    THEORETICAL_RTP = 96.82 
    
    print("\n" + "="*50)
    print("      RESULTADO DE LA VALIDACIÓN ESTADÍSTICA      ")
    print("==================================================")
    print(f"Simulaciones:      {num_simulations}")
    print(f"Giros por Sim:     {spins_per_sim}")
    print(f"Total Giros:       {num_simulations * spins_per_sim:,}")
    print("-" * 50)
    print(f"RTP Promedio (Obs): {mean_rtp:.4f}%")
    print(f"Desviación Std:     {std_dev:.4f}")
    print(f"Margen de Error:    +/- {margin_error:.4f}%")
    print(f"Intervalo 95%:      [{lower_bound:.4f}%, {upper_bound:.4f}%]")
    print("-" * 50)
    print(f"RTP TEÓRICO (Target): {THEORETICAL_RTP:.4f}%")
    
    if lower_bound <= THEORETICAL_RTP <= upper_bound:
        print("\n[ÉXITO] El RTP Teórico ESTÁ DENTRO del intervalo de confianza.")
        print("El modelo está validado estadísticamente.")
    else:
        print("\n[ATENCIÓN] El RTP Teórico está fuera del intervalo.")
        print("Revisar convergencia (se necesitan más giros o revisar volatilidad).")
    print("="*50)

if __name__ == "__main__":
    run_validation_suite()