# quick_verify.py
from main import SlotMachine
import config
import time

def run_quick_test():
    print("--- INICIANDO TEST RÁPIDO DE ESTABILIDAD (50,000 GIROS) ---")
    slot = SlotMachine()
    
    hits = 0
    fs_hits = 0
    jp_hits = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
    total_bet = 0
    total_won = 0
    
    start = time.time()
    
    # Solo 50k giros para verificar que no explote y que active funciones
    for i in range(50000):
        res = slot.spin_base_game()
        total_bet += config.PAYLINES_COUNT
        total_won += res['total_win']
        
        if res['base_win'] > 0:
            hits += 1
            
        if res['feature_data']:
            fs_hits += 1
            # Verificar si hubo Jackpot
            jps = res['feature_data']['jackpots_hit']
            for k, v in jps.items():
                if v > 0:
                    jp_hits[k] += v
                    
    duration = time.time() - start
    rtp = (total_won / total_bet) * 100
    
    print(f"Tiempo: {duration:.2f} segundos")
    print(f"RTP Instantáneo (No convergerá, solo referencia): {rtp:.2f}%")
    print(f"Giros Base con Premio: {hits}")
    print(f"Entradas a Free Spins: {fs_hits}")
    print(f"Jackpots Ganados: {jp_hits}")
    
    if fs_hits == 0:
        print("[ALERTA] No se activaron Free Spins en 50k giros. Revisa la lógica.")
    else:
        print("[OK] Free Spins activados correctamente.")
        
    print("--- TEST FINALIZADO ---")

if __name__ == "__main__":
    run_quick_test()