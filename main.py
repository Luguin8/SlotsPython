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

    def _get_reel_window(self, reel_index, stop_position, strips_to_use):
        current_strip = strips_to_use[reel_index]
        strip_length = len(current_strip)
        visible_symbols = []
        for i in range(self.rows):
            idx = (stop_position + i) % strip_length
            visible_symbols.append(current_strip[idx])
        return visible_symbols

    def spin(self):
        # 1. Generar Matriz (Igual que antes)
        stops = [random.randint(0, len(strip) - 1) for strip in self.current_strips]
        reel_columns = []
        for i in range(self.cols):
            reel_columns.append(self._get_reel_window(i, stops[i], self.current_strips))

        grid = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                row_data.append(reel_columns[c][r])
            grid.append(row_data)

        # 2. Evaluar Ganancias (NUEVO)
        total_win, win_details = self.evaluate_spin(grid)

        return grid, stops, total_win, win_details

    def evaluate_spin(self, grid):
        """
        Recorre las 25 líneas y calcula la ganancia total.
        """
        total_win = 0
        win_details = [] # Guardaremos info de qué líneas ganaron

        for line_idx, line_coords in enumerate(self.paylines):
            # line_coords es ej: [1, 1, 1, 1, 1] (Fila para cada rodillo)
            
            # 1. Extraer los símbolos de esta línea específica
            line_symbols = []
            for col_idx, row_idx in enumerate(line_coords):
                line_symbols.append(grid[row_idx][col_idx])
            
            # 2. Calcular ganancia de esta línea
            payout, count, symbol_id = self._calculate_line_win(line_symbols)

            if payout > 0:
                total_win += payout
                win_details.append({
                    "line_number": line_idx + 1,
                    "symbol": symbol_id,
                    "count": count,
                    "amount": payout
                })

        return total_win, win_details

    def _calculate_line_win(self, symbols):
        """
        Algoritmo Core de Evaluación (Left-to-Right con Wilds).
        Retorna: (pago, cantidad_simbolos, id_simbolo_ganador)
        """
        first_symbol = symbols[0]
        match_count = 1
        
        # Definimos cuál es el símbolo que estamos buscando ("Active Symbol")
        # Si el primero es Wild, el símbolo activo es "Indefinido" hasta que salga uno normal
        if first_symbol == config.SYM_WILD:
            active_symbol = None 
        else:
            active_symbol = first_symbol

        # Recorremos desde el 2do rodillo (índice 1) hasta el final
        for i in range(1, len(symbols)):
            current_sym = symbols[i]
            
            # CASO A: Es un WILD
            if current_sym == config.SYM_WILD:
                match_count += 1
                # El Wild no cambia el active_symbol (sigue siendo el que traíamos o None)
            
            # CASO B: Es un símbolo normal
            else:
                if active_symbol is None:
                    # Si veníamos de puros Wilds, este símbolo define la línea
                    active_symbol = current_sym
                    match_count += 1
                elif current_sym == active_symbol:
                    # Coincide con el que buscamos
                    match_count += 1
                else:
                    # Se rompió la cadena
                    break

        # --- LÓGICA DE PAGO ---
        if match_count < 3:
            return 0, 0, 0 # Mínimo 3 para pagar (según config)

        # Si active_symbol sigue siendo None, significa que salieron PUROS WILDS
        # Ej: [W, W, W, W, W]. Pagamos como Wild.
        symbol_to_pay = active_symbol if active_symbol is not None else config.SYM_WILD

        # Buscamos en la Paytable
        # Usamos .get() por si el diccionario no tiene entrada para esa cantidad
        if symbol_to_pay in self.paytable:
            payout = self.paytable[symbol_to_pay].get(match_count, 0)
            return payout, match_count, symbol_to_pay
        
        return 0, 0, 0

# --- TESTING ---
if __name__ == "__main__":
    slot = SlotMachine()
    
    print(f"--- TESTING DE EVALUACIÓN ---")
    
    accumulated_win = 0
    # Simulamos giros hasta que salga algún premio para verlo
    spins_count = 0
    
    while spins_count < 10: # Hacemos 10 intentos fijos
        spins_count += 1
        grid, stops, win, details = slot.spin()
        
        if win > 0:
            print(f"\n[Giro #{spins_count}] ¡GANADOR!")
            for row in grid:
                print(row)
            print(f"Ganancia Total: {win}")
            print("Detalle de Líneas:")
            for d in details:
                print(f"  > Línea {d['line_number']}: {d['count']} de Simbolo ID {d['symbol']} = {d['amount']}")
            accumulated_win += win
        else:
            # Opcional: imprimir un punto para saber que está trabajando
            pass 

    print(f"\n--- Fin de sesión. Ganancia acumulada en 10 giros: {accumulated_win} ---")