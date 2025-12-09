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
    
    # --- VARIABLES ACUMULADORAS ---
    total_bet = 0
    total_won = 0
    
    # Desglose de RTP (CORRECCIÓN AQUI)
    total_base_won = 0      
    total_feature_won = 0   

    base_hits = 0       
    feature_hits = 0    
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    
    # Usamos PAYLINES_COUNT para el calculo, asumiendo apuesta de 1 credito por linea
    bet_per_spin = config.PAYLINES_COUNT * 1 

    # Para cálculo de Varianza/Desviación
    sum_x = 0.0      # Suma de premios
    sum_x_sq = 0.0   # Suma de premios al cuadrado

    for i in range(1, num_spins + 1):
        result = slot.spin_base_game()
        
        win = result['total_win']
        base_win = result.get('base_win', 0) # Usamos .get por seguridad
        feature_win = win - base_win         # El resto es ganancia de bonos/jackpots
        
        total_bet += bet_per_spin
        total_won += win
        
        # Acumular desglose
        total_base_won += base_win
        total_feature_won += feature_win
        
        # Estadística al vuelo
        sum_x += win
        sum_x_sq += (win * win)
        
        if base_win > 0:
            base_hits += 1
            
        if result['feature_data']:
            feature_hits += 1
            feats = result['feature_data'].get('jackpots_hit', {})
            for k in jp_hits:
                if k in feats:
                    jp_hits[k] += feats[k]
            
        # Progreso cada 10%
        if i % (num_spins // 10) == 0:
            progress = (i / num_spins) * 100
            current_rtp = (total_won / total_bet) * 100
            elapsed = time.time() - start_time
            print(f"{int(progress)}% | RTP Global: {current_rtp:.2f}% | Bonos: {feature_hits} | Tiempo: {elapsed:.1f}s")

    elapsed_time = time.time() - start_time
    
    # --- CÁLCULOS ESTADÍSTICOS FINALES ---
    mean_win = sum_x / num_spins
    # Varianza = (Mean of squares) - (Square of mean)
    mean_sq = sum_x_sq / num_spins
    variance = mean_sq - (mean_win * mean_win)
    std_dev = math.sqrt(variance) if variance > 0 else 0
    
    # Intervalo de Confianza 95% (Z = 1.96)
    margin_error_abs = 1.96 * (std_dev / math.sqrt(num_spins))
    
    # Convertir a % sobre la apuesta
    rtp_final = (total_won / total_bet) * 100
    rtp_base = (total_base_won / total_bet) * 100
    rtp_feature = (total_feature_won / total_bet) * 100
    
    margin_error_rtp = (margin_error_abs / bet_per_spin) * 100
    
    print("\n" + "="*60)
    print("      RESULTADOS DE SIMULACIÓN CIENTÍFICA      ")
    print("============================================================")
    print(f"Semilla Utilizada: {SEED_VALUE}")
    print("-" * 60)
    print(f"RTP FINAL:        {rtp_final:.2f}%")
    print(f"  > RTP Base:     {rtp_base:.2f}%")
    print(f"  > RTP Bonos:    {rtp_feature:.2f}%")
    print(f"Intervalo 95%:    [{rtp_final - margin_error_rtp:.2f}%, {rtp_final + margin_error_rtp:.2f}%]")
    print("-" * 60)
    print(f"Volatilidad (SD): {std_dev:.2f}")
    print(f"Varianza:         {variance:.2f}")
    print("-" * 60)
    print(f"Hit Frequency:    {(base_hits / num_spins) * 100:.2f}%")
    print(f"Frecuencia Bono:  1 cada {num_spins // feature_hits if feature_hits else 0} giros")
    print(f"Jackpots:         {jp_hits}")
    print("="*60)

if __name__ == "__main__":
    # Puedes cambiar a 5000000 aquí si quieres una prueba más larga
    run_simulation(1000000)