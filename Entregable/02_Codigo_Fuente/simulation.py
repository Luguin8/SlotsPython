# simulation.py
import time
import random
import math  # Para raiz cuadrada
import config
from main import SlotMachine

def run_simulation(num_spins=1000000):
    # --- 1. CONFIGURACIÓN CIENTÍFICA (SEMILLA FIJA) ---
    SEED_VALUE = 777
    random.seed(SEED_VALUE)
    
    print(f"--- INICIANDO SIMULACIÓN CIENTÍFICA ---")
    print(f"Giros: {num_spins:,}")
    print(f"Semilla Fija (Seed): {SEED_VALUE} (Resultados reproducibles)")
    
    start_time = time.time()
    slot = SlotMachine()
    
    total_bet = 0
    total_won = 0
    base_hits = 0       
    feature_hits = 0    
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    bet_per_spin = config.PAYLINES_COUNT * 1 

    # Para cálculo de Varianza/Desviación
    # Guardamos la ganancia neta de cada giro (Win - Bet) o Win puro?
    # Estándar industria: Desviación sobre el Total Won por giro.
    # Optimizacion: Calcular sumas de cuadrados al vuelo para no llenar la RAM con una lista de 1M.
    sum_x = 0.0      # Suma de premios
    sum_x_sq = 0.0   # Suma de premios al cuadrado

    for i in range(1, num_spins + 1):
        result = slot.spin_base_game()
        
        win = result['total_win']
        total_bet += bet_per_spin
        total_won += win
        
        # Estadística al vuelo
        sum_x += win
        sum_x_sq += (win * win)
        
        if result['base_win'] > 0:
            base_hits += 1
            
        if result['feature_data']:
            feature_hits += 1
            feats = result['feature_data']['jackpots_hit']
            for k in jp_hits:
                jp_hits[k] += feats[k]
            
        if i % (num_spins // 10) == 0:
            progress = (i / num_spins) * 100
            current_rtp = (total_won / total_bet) * 100
            elapsed = time.time() - start_time
            print(f"{int(progress)}% | RTP: {current_rtp:.2f}% | Bonos: {feature_hits} | Tiempo: {elapsed:.1f}s")

    elapsed_time = time.time() - start_time
    
    # --- CÁLCULOS ESTADÍSTICOS FINALES ---
    mean_win = sum_x / num_spins
    # Varianza = (Mean of squares) - (Square of mean)
    mean_sq = sum_x_sq / num_spins
    variance = mean_sq - (mean_win * mean_win)
    std_dev = math.sqrt(variance) if variance > 0 else 0
    
    # Intervalo de Confianza 95% (Z = 1.96)
    # Margen error = 1.96 * (StdDev / sqrt(N))
    margin_error_abs = 1.96 * (std_dev / math.sqrt(num_spins))
    
    # Convertir a % sobre la apuesta
    rtp_final = (total_won / total_bet) * 100
    # El margen de error en % de RTP se calcula sobre la apuesta media (bet_per_spin)
    margin_error_rtp = (margin_error_abs / bet_per_spin) * 100
    
    print("\n" + "="*60)
    print("      RESULTADOS DE SIMULACIÓN CIENTÍFICA      ")
    print("============================================================")
    print(f"Semilla Utilizada: {SEED_VALUE}")
    print("-" * 60)
    print(f"RTP FINAL:        {rtp_final:.2f}%")
    print(f"Intervalo 95%:    [{rtp_final - margin_error_rtp:.2f}%, {rtp_final + margin_error_rtp:.2f}%]")
    print("-" * 60)
    print(f"Volatilidad (SD): {std_dev:.2f} (Desviación Estándar de pagos)")
    print(f"Varianza:         {variance:.2f}")
    print("-" * 60)
    print(f"Hit Frequency:    {(base_hits / num_spins) * 100:.2f}%")
    print(f"Frecuencia Bono:  1 cada {num_spins // feature_hits if feature_hits else 0} giros")
    print(f"Jackpots:         {jp_hits}")
    print("="*60)

if __name__ == "__main__":
    run_simulation()