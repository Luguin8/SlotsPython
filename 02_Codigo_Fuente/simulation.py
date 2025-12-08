# simulation.py
import time
from main import SlotMachine
import config

def run_simulation(num_spins=1000000): # <--- CAMBIO: 1 Millón por defecto
    print(f"--- INICIANDO SIMULACIÓN MASIVA DE {num_spins:,} GIROS ---")
    print("(Esto tomará unos segundos/minutos dependiendo de tu PC...)")
    start_time = time.time()
    
    # Instanciamos la máquina
    slot = SlotMachine()
    
    # ACUMULADORES
    total_bet = 0
    total_won = 0
    
    base_hits = 0       
    feature_hits = 0    
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    
    bet_per_spin = config.PAYLINES_COUNT * 1 

    for i in range(1, num_spins + 1):
        # Ejecutamos giro
        result = slot.spin_base_game()
        
        total_bet += bet_per_spin
        total_won += result['total_win']
        
        if result['base_win'] > 0:
            base_hits += 1
            
        if result['feature_data']:
            feature_hits += 1
            feats = result['feature_data']['jackpots_hit']
            for k in jp_hits:
                jp_hits[k] += feats[k]
            
        # Log de progreso cada 10%
        if i % (num_spins // 10) == 0:
            progress = (i / num_spins) * 100
            current_rtp = (total_won / total_bet) * 100
            elapsed = time.time() - start_time
            print(f"{int(progress)}% completado | RTP Actual: {current_rtp:.2f}% | Bonos: {feature_hits} | Tiempo: {elapsed:.1f}s")

    elapsed_time = time.time() - start_time
    
    # --- REPORTE FINAL ---
    rtp_final = (total_won / total_bet) * 100
    hit_freq = (base_hits / num_spins) * 100
    bonus_freq = num_spins / feature_hits if feature_hits > 0 else 0
    
    print("\n" + "="*50)
    print("      RESULTADOS FINALES (1 MILLÓN DE GIROS)      ")
    print("="*50)
    print(f"Tiempo Total:     {elapsed_time:.2f} seg")
    print("-" * 50)
    print(f"Total Apostado:   {total_bet:,.0f}")
    print(f"Total Pagado:     {total_won:,.0f}")
    print(f"RTP FINAL:        {rtp_final:.2f}%")
    print("-" * 50)
    print(f"Hit Frequency:    {hit_freq:.2f}% (Juego Base)")
    print(f"Frecuencia Bono:  1 cada {int(bonus_freq)} giros")
    print(f"Jackpots:         {jp_hits}")
    print("="*50)

if __name__ == "__main__":
    run_simulation()