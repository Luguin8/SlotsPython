# check_rapido.py
import time
from main import SlotMachine
import config

def validacion_flash():
    print("--- DIAGNÓSTICO RÁPIDO DE SALUD DEL MODELO ---")
    print("Objetivo: Verificar que no estamos en 1000% RTP antes de correr la validación larga.")
    
    # 1. Verificar Configuración
    print(f"\n[1] Verificando Rieles...")
    scatters_r1 = config.FIXED_STRIPS_BASE[0].count(10)
    len_r1 = len(config.FIXED_STRIPS_BASE[0])
    prob_teorica = scatters_r1 / len_r1
    print(f"   > Riel 1: {scatters_r1} Scatters en {len_r1} posiciones.")
    print(f"   > Probabilidad de Scatter por celda: {prob_teorica:.4f}")
    
    if scatters_r1 > 15:
        print("   ⚠️ ALERTA CRÍTICA: Demasiados Scatters. Tu config.py es de la versión 'Scatter Injection' vieja.")
        return
    elif scatters_r1 < 8:
        print("   ⚠️ ALERTA: Pocos Scatters. Revisa si copiaste la V30.")
    else:
        print("   ✅ Configuración de Scatters parece correcta (V30).")

    # 2. Mini Simulación (50k giros)
    print(f"\n[2] Corriendo 50,000 giros de prueba...")
    slot = SlotMachine()
    total_bet = 0
    total_won = 0
    bet = config.PAYLINES_COUNT
    
    start = time.time()
    for i in range(1, 50001):
        res = slot.spin_base_game()
        total_bet += bet
        total_won += res['total_win']
        
        if i % 10000 == 0:
            print(f"   > {i} giros... RTP actual: {(total_won/total_bet)*100:.2f}%")
            
    rtp_final = (total_won / total_bet) * 100
    duration = time.time() - start
    
    print(f"\n--- RESULTADO FINAL RÁPIDO ({duration:.2f}s) ---")
    print(f"RTP PROYECTADO: {rtp_final:.2f}%")
    
    if 90 <= rtp_final <= 105:
        print("✅ LUZ VERDE. El modelo está en rango. Puedes correr la validación larga.")
    else:
        print("❌ DETENER. El RTP está fuera de rango. NO corras la validación larga aún.")

if __name__ == "__main__":
    validacion_flash()