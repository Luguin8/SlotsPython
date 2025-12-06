# simulation.py
import time
from main import SlotMachine
import config

def run_simulation(num_spins=100000):
    print(f"--- INICIANDO SIMULACIÓN DE {num_spins} GIROS ---")
    start_time = time.time()
    
    # Instanciamos la máquina
    slot = SlotMachine()
    
    # ACUMULADORES ESTADÍSTICOS
    total_bet = 0
    total_won = 0
    
    base_hits = 0       # Cuántas veces ganamos en el juego base
    feature_hits = 0    # Cuántas veces entramos al Bono
    jackpot_hits = 0    # Cuántos Jackpots salieron
    
    # Costo por giro (Asumimos apuesta 1 por línea)
    bet_per_spin = config.PAYLINES_COUNT * 1 

    for i in range(1, num_spins + 1):
        # Ejecutamos giro
        result = slot.spin_base_game()
        
        # Actualizamos contadores
        total_bet += bet_per_spin
        total_won += result['total_win']
        
        if result['base_win'] > 0:
            base_hits += 1
            
        if result['feature_data']:
            feature_hits += 1
            jackpot_hits += result['feature_data']['jackpots_hit']
            
        # Log de progreso cada 10%
        if i % (num_spins // 10) == 0:
            progress = (i / num_spins) * 100
            current_rtp = (total_won / total_bet) * 100
            print(f"Progreso: {int(progress)}% | RTP Actual: {current_rtp:.2f}% | Bonos: {feature_hits}")

    elapsed_time = time.time() - start_time
    
    # --- REPORTE FINAL ---
    rtp_final = (total_won / total_bet) * 100
    hit_freq = (base_hits / num_spins) * 100
    bonus_freq = num_spins / feature_hits if feature_hits > 0 else 0
    
    print("\n" + "="*40)
    print("      RESULTADOS DE LA SIMULACIÓN      ")
    print("="*40)
    print(f"Giros Totales:    {num_spins}")
    print(f"Tiempo Ejecución: {elapsed_time:.2f} seg")
    print("-" * 40)
    print(f"Total Apostado:   {total_bet:,.0f}")
    print(f"Total Pagado:     {total_won:,.0f}")
    print(f"RTP FINAL:        {rtp_final:.2f}%  <-- ESTE ES EL DATO CRÍTICO")
    print("-" * 40)
    print(f"Hit Frequency:    {hit_freq:.2f}% (Juego Base)")
    print(f"Frecuencia Bono:  1 cada {int(bonus_freq)} giros")
    print(f"Jackpots Totales: {jackpot_hits}")
    print("="*40)

if __name__ == "__main__":
    run_simulation(100000)