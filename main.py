import random
import config

class SlotMachine:
    def __init__(self):
        self.base_strips = config.generate_dummy_strips()
        self.current_strips = self.base_strips
        self.rows = config.ROWS
        self.cols = config.COLS
        self.paylines = config.PAYLINES
        self.paytable = config.PAYTABLE
        
        # Estado del Jackpot (Acumulado Dummy para simulación)
        self.jackpot_pool = 1000.0 

    def _get_reel_window(self, reel_index, stop_position, strips_to_use):
        current_strip = strips_to_use[reel_index]
        strip_length = len(current_strip)
        visible_symbols = []
        for i in range(self.rows):
            idx = (stop_position + i) % strip_length
            sym = current_strip[idx]
            visible_symbols.append(sym)
        return visible_symbols

    # --- MÉTODO PARA ELEGIR EL SÍMBOLO ESPECIAL (WEIGHTED CHOICE) ---
    def _pick_special_symbol(self):
        """
        Elige uno de los símbolos altos basándose en las probabilidades definidas.
        Retorna: (ID_Original, ID_Nuevo_Wild, Multiplicador)
        """
        # Desempaquetamos la configuración
        choices = []
        weights = []
        for item in config.FEATURE_WEIGHTS:
            # item es (ID_SYMBOL, MULTIPLIER, PROBABILITY)
            choices.append(item)
            weights.append(item[2])
            
        # Selección aleatoria ponderada (k=1 devuelve una lista de 1 elemento)
        selection = random.choices(choices, weights=weights, k=1)[0]
        
        original_id, multiplier, _ = selection
        
        # Determinamos qué ID de Wild usaremos
        wild_id = config.SYM_WILD_X1
        if multiplier == 2: wild_id = config.SYM_WILD_X2
        if multiplier == 3: wild_id = config.SYM_WILD_X3
        
        return original_id, wild_id, multiplier

    def spin_base_game(self):
        """
        Giro normal. Si salen Scatters, detona los Free Spins.
        """
        # 1. Giro físico
        grid, stops = self._generate_grid(self.base_strips)
        
        # 2. Evaluar líneas
        line_win, details = self.evaluate_lines(grid)
        
        # 3. Buscar Scatters (Trigger)
        scatter_count = sum(row.count(config.SYM_SCATTER) for row in grid)
        
        feature_log = None
        total_round_win = line_win
        
        # Aumentar Jackpot (Regla: Mitad de apuesta actual. Asumimos apuesta 1.0)
        self.jackpot_pool += 0.5

        if scatter_count >= 3:
            # ¡ACTIVAR FREE SPINS!
            spins_qty = config.FREE_SPINS_AWARDED.get(scatter_count, 10)
            feature_win, feature_report = self.play_free_spins(spins_qty)
            
            total_round_win += feature_win
            feature_log = feature_report

        return {
            "grid": grid,
            "stops": stops,
            "base_win": line_win,
            "scatters": scatter_count,
            "feature_data": feature_log,
            "total_win": total_round_win
        }

    def play_free_spins(self, qty):
        """
        Ejecuta la ronda de bonificación.
        """
        # 1. Seleccionar símbolo especial
        orig_sym, wild_sym, mult = self._pick_special_symbol()
        
        # 2. Crear "Rodillos Modificados" (Virtuales)
        # Reemplazamos todas las instancias del símbolo original por el Wild Especial
        feature_strips = []
        for strip in self.base_strips:
            new_strip = [wild_sym if s == orig_sym else s for s in strip]
            
            # AGREGAR EL SCATTER JACKPOT (ID 11) A LOS RODILLOS DE FS
            # (En una implementación real se diseñan rodillos aparte, aquí los inyectamos al azar para probar)
            # Reemplazamos un 5% de simbolos al azar por Scatter Jackpot
            final_strip = []
            for s in new_strip:
                if random.random() < 0.05 and s != wild_sym: # No sobreescribir el wild especial
                    final_strip.append(config.SYM_SCATTER_JP)
                else:
                    final_strip.append(s)
            feature_strips.append(final_strip)

        fs_total_win = 0
        jp_wins = 0
        
        # Ejecutar los giros
        for _ in range(qty):
            grid, _ = self._generate_grid(feature_strips)
            
            # Evaluar líneas (La función detectará el Wild Especial y su multiplicador)
            spin_win, _ = self.evaluate_lines(grid)
            fs_total_win += spin_win
            
            # Chequear Jackpot (3+ Scatters JP)
            jp_scatters = sum(row.count(config.SYM_SCATTER_JP) for row in grid)
            if jp_scatters >= 3:
                # GANÓ UN JACKPOT (Simulado)
                # Reiniciamos pozo y pagamos
                jp_payout = self.jackpot_pool
                fs_total_win += jp_payout
                jp_wins += 1
                self.jackpot_pool = 1000.0 # Reset semilla

        return fs_total_win, {
            "special_symbol": orig_sym,
            "wild_type": wild_sym,
            "multiplier": mult,
            "spins_played": qty,
            "jackpots_hit": jp_wins
        }

    def _generate_grid(self, strips):
        stops = [random.randint(0, len(strip) - 1) for strip in strips]
        reel_columns = [self._get_reel_window(i, stops[i], strips) for i in range(self.cols)]
        grid = []
        for r in range(self.rows):
            row_data = [reel_columns[c][r] for c in range(self.cols)]
            grid.append(row_data)
        return grid, stops

    def evaluate_lines(self, grid):
        total_win = 0
        details = []
        for line_idx, line_coords in enumerate(self.paylines):
            line_symbols = [grid[row][col] for col, row in enumerate(line_coords)]
            
            payout, count, sym_id, multiplier_applied = self._calculate_line_win(line_symbols)
            
            if payout > 0:
                final_pay = payout * multiplier_applied
                total_win += final_pay
                details.append((line_idx, sym_id, count, final_pay))
        return total_win, details

    def _calculate_line_win(self, symbols):
        # Esencialmente la misma lógica, pero detectando Wilds Especiales
        first_symbol = symbols[0]
        
        # Identificar si es algun tipo de Wild (Base o Especial)
        is_first_wild = first_symbol in [config.SYM_WILD, config.SYM_WILD_X1, config.SYM_WILD_X2, config.SYM_WILD_X3]
        
        active_symbol = None if is_first_wild else first_symbol
        match_count = 1
        max_multiplier_found = 1 # Rastrear el multiplicador más alto en la línea

        # Chequear multiplicador del primer simbolo
        if is_first_wild:
            max_multiplier_found = max(max_multiplier_found, config.WILD_MULTIPLIERS.get(first_symbol, 1))

        for i in range(1, len(symbols)):
            curr = symbols[i]
            is_curr_wild = curr in [config.SYM_WILD, config.SYM_WILD_X1, config.SYM_WILD_X2, config.SYM_WILD_X3]
            
            if is_curr_wild:
                match_count += 1
                # Actualizar multiplicador si este wild es mejor
                w_mult = config.WILD_MULTIPLIERS.get(curr, 1)
                max_multiplier_found = max(max_multiplier_found, w_mult)
            else:
                if active_symbol is None:
                    active_symbol = curr
                    match_count += 1
                elif curr == active_symbol:
                    match_count += 1
                else:
                    break
        
        if match_count < 3: return 0, 0, 0, 1

        # REGLA: Si son 5 Wilds puros
        if active_symbol is None:
            # Si son 5 Wilds Especiales (ej 5 Wilds x3), el cliente dijo:
            # "Pagan el valor del símbolo que se transformó"
            # Recuperamos el símbolo original usando el mapa
            original = config.WILD_ORIGIN_MAP.get(first_symbol, config.SYM_WILD) # Si es wild normal, paga como wild normal
            base_pay = self.paytable.get(original, {}).get(match_count, 0)
        else:
            base_pay = self.paytable.get(active_symbol, {}).get(match_count, 0)

        return base_pay, match_count, active_symbol, max_multiplier_found

# --- TESTING ---
if __name__ == "__main__":
    slot = SlotMachine()
    print("--- BUSCANDO FREE SPINS (Esto puede tardar unos segundos) ---")
    
    attempts = 0
    while True:
        attempts += 1
        # Forzamos un poco la suerte para el test:
        # Ejecutamos spin_base_game hasta que salga feature_data
        result = slot.spin_base_game()
        
        if result['feature_data']:
            print(f"\n!!! BONO ACTIVADO EN INTENTO #{attempts} !!!")
            print(f"Scatters: {result['scatters']}")
            print(f"Ganancia Base: {result['base_win']}")
            
            feat = result['feature_data']
            print("\n--- REPORTE DE FREE SPINS ---")
            print(f"Símbolo Elegido: ID {feat['special_symbol']} -> Transforma a Wild ID {feat['wild_type']}")
            print(f"Multiplicador del Wild: x{feat['multiplier']}")
            print(f"Giros Jugados: {feat['spins_played']}")
            print(f"Jackpots Ganados: {feat['jackpots_hit']}")
            print(f"Ganancia Total del Bono: {result['total_win'] - result['base_win']}")
            break
            
        if attempts % 1000 == 0:
            print(f"...", end="", flush=True)