# main.py
import random
import config

class SlotMachine:
    def __init__(self):
        # Cargamos los rodillos (Reel Strips)
        # Nota: Usamos una copia para no modificar la original si hacemos cambios luego
        self.base_strips = config.generate_dummy_strips()
        self.current_strips = self.base_strips # Por defecto usamos los strips base
        self.rows = config.ROWS
        self.cols = config.COLS

    def _get_reel_window(self, reel_index, stop_position, strips_to_use):
        """
        Método Privado (interno).
        Devuelve los 3 símbolos visibles de un rodillo dado una posición de parada.
        """
        current_strip = strips_to_use[reel_index]
        strip_length = len(current_strip)
        visible_symbols = []

        for i in range(self.rows):
            # Lógica Circular: Si estamos al final, volvemos al principio con %
            idx = (stop_position + i) % strip_length
            visible_symbols.append(current_strip[idx])
        
        return visible_symbols

    def spin(self):
        """
        Giro del Juego Base.
        1. Elige posiciones de parada aleatorias.
        2. Construye la matriz visible.
        """
        # Elegir posiciones de parada para cada uno de los 5 rodillos
        stops = [random.randint(0, len(strip) - 1) for strip in self.current_strips]
        
        # Construir la matriz transpuesta (Organizada por FILAS para visualizar)
        # Primero extraemos las columnas verticales
        reel_columns = []
        for i in range(self.cols):
            reel_columns.append(self._get_reel_window(i, stops[i], self.current_strips))

        # Transponer a filas: [[Fila 0], [Fila 1], [Fila 2]]
        grid = []
        for r in range(self.rows):
            row_data = []
            for c in range(self.cols):
                row_data.append(reel_columns[c][r])
            grid.append(row_data)

        return grid, stops

# --- TESTING ---
if __name__ == "__main__":
    # Instanciamos la máquina
    slot = SlotMachine()
    
    print(f"--- SIMULACIÓN INICIADA ({config.PAYLINES_COUNT} líneas) ---")
    
    # Hacemos 5 giros de prueba
    for i in range(5):
        print(f"\n[Giro #{i+1}]")
        grid, stops = slot.spin()
        
        # Mostramos la matriz bonita
        for row in grid:
            print(row)
        
        print(f"Posiciones de parada: {stops}")