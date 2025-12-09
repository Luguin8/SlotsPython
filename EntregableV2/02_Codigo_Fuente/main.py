import random
import config

class SlotMachine:
    def __init__(self):
        # Generamos dos sets de rodillos
        self.base_strips = config.generate_strips(config.REEL_WEIGHTS_BASE)
        self.fs_strips = config.generate_strips(config.REEL_WEIGHTS_FS)
        
        self.rows = config.ROWS
        self.cols = config.COLS
        self.paylines = config.PAYLINES
        self.paytable = config.PAYTABLE
        
        # 3 POZOS INDEPENDIENTES
        self.jackpots = {
            "MINI": config.JP_SEEDS["MINI"],
            "MINOR": config.JP_SEEDS["MINOR"],
            "MAJOR": config.JP_SEEDS["MAJOR"]
        }

    def _get_reel_window(self, reel_index, stop_position, strips_to_use):
        current_strip = strips_to_use[reel_index]
        strip_length = len(current_strip)
        visible_symbols = []
        for i in range(self.rows):
            idx = (stop_position + i) % strip_length
            sym = current_strip[idx]
            visible_symbols.append(sym)
        return visible_symbols

    def _pick_special_symbol(self):
        choices = []
        weights = []
        for item in config.FEATURE_WEIGHTS:
            choices.append(item)
            weights.append(item[2])
        selection = random.choices(choices, weights=weights, k=1)[0]
        # selection es (ID_ORIGINAL, MULTIPLIER, PROBABILITY)
        
        original_id = selection[0]
        multiplier = selection[1]
        
        # Mapear al Wild ID correcto
        wild_id = config.SYM_WILD_X1
        if multiplier == 2: wild_id = config.SYM_WILD_X2
        if multiplier == 3: wild_id = config.SYM_WILD_X3
        
        return original_id, wild_id, multiplier

    def spin_base_game(self):
        # 1. Aumentar Jackpots (Todos crecen igual)
        for key in self.jackpots:
            self.jackpots[key] += config.JP_CONTRIBUTION

        # 2. Giro con Rieles Base
        grid, stops = self._generate_grid(self.base_strips)
        
        # 3. Evaluar líneas
        line_win, details = self.evaluate_lines(grid)
        
        # 4. Buscar Scatters (ID 10)
        scatter_count = sum(row.count(config.SYM_SCATTER) for row in grid)
        
        feature_log = None
        total_round_win = line_win

        if scatter_count >= 3:
            spins_qty = config.FREE_SPINS_AWARDED.get(scatter_count, 10)
            feature_win, feature_report = self.play_free_spins(spins_qty)
            total_round_win += feature_win
            feature_log = feature_report

        return {
            "grid": grid,
            "base_win": line_win,
            "scatters": scatter_count,
            "feature_data": feature_log,
            "total_win": total_round_win,
            "jackpot_values": self.jackpots.copy() # Para debug
        }

    def play_free_spins(self, qty):
        # 1. Elegir símbolo especial
        orig_sym, wild_sym, mult = self._pick_special_symbol()
        
        # 2. Transformar Rieles de FS
        # Reemplazamos TODAS las instancias de orig_sym por wild_sym
        transformed_strips = []
        for strip in self.fs_strips:
            new_strip = [wild_sym if s == orig_sym else s for s in strip]
            transformed_strips.append(new_strip)

        fs_total_win = 0
        jp_wins_log = {"MINI": 0, "MINOR": 0, "MAJOR": 0}
        
        for _ in range(qty):
            grid, _ = self._generate_grid(transformed_strips)
            
            # Evaluar líneas (Wilds ya están en la grilla)
            spin_win, _ = self.evaluate_lines(grid)
            fs_total_win += spin_win
            
            # Chequear Jackpot (Scatter JP ID 11)
            jp_scatters = sum(row.count(config.SYM_SCATTER_JP) for row in grid)
            
            if jp_scatters >= 3:
                jp_type = "MINI"
                if jp_scatters == 4: jp_type = "MINOR"
                if jp_scatters >= 5: jp_type = "MAJOR"
                
                # Pagar y Resetear solo ESE pozo
                amount = self.jackpots[jp_type]
                fs_total_win += amount
                jp_wins_log[jp_type] += 1
                self.jackpots[jp_type] = config.JP_SEEDS[jp_type]

        return fs_total_win, {
            "special_symbol": orig_sym,
            "wild_type": wild_sym,
            "multiplier": mult,
            "spins_played": qty,
            "jackpots_hit": jp_wins_log
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
        first_symbol = symbols[0]
        
        # Detectar si es Wild (Solo existen en FS tras transformación)
        is_first_wild = first_symbol in [config.SYM_WILD_X1, config.SYM_WILD_X2, config.SYM_WILD_X3]
        
        active_symbol = None if is_first_wild else first_symbol
        match_count = 1
        max_multiplier_found = 1

        if is_first_wild:
            max_multiplier_found = max(max_multiplier_found, config.WILD_MULTIPLIERS.get(first_symbol, 1))

        for i in range(1, len(symbols)):
            curr = symbols[i]
            is_curr_wild = curr in [config.SYM_WILD_X1, config.SYM_WILD_X2, config.SYM_WILD_X3]
            
            if is_curr_wild:
                match_count += 1
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

        # LOGICA 5 WILDS: Paga como el símbolo original mayor
        if active_symbol is None:
            # Línea de puros Wilds
            # Recuperamos el símbolo original que paga más (referencia)
            # Como todos los wilds en el rodillo son del mismo tipo en una tirada,
            # usamos el first_symbol para mapear.
            original_ref = config.WILD_PAYMENT_REF.get(first_symbol, config.SYM_H1)
            # Obtenemos pago de 5 del original
            base_pay = self.paytable.get(original_ref, {}).get(match_count, 0)
        else:
            base_pay = self.paytable.get(active_symbol, {}).get(match_count, 0)

        return base_pay, match_count, active_symbol, max_multiplier_found