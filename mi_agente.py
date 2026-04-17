"""
mi_agente.py — Aquí defines tu agente.
╔══════════════════════════════════════════════╗
║  ✏️  EDITA ESTE ARCHIVO                      ║
╚══════════════════════════════════════════════╝

Tu agente debe:
    1. Heredar de la clase Agente
    2. Implementar el método decidir(percepcion)
    3. Retornar: 'arriba', 'abajo', 'izquierda' o 'derecha'

Lo que recibes en 'percepcion':
───────────────────────────────
percepcion = {
    'posicion':       (3, 5),          # Tu fila y columna actual
    'arriba':         'libre',         # Qué hay arriba
    'abajo':          'pared',         # Qué hay abajo
    'izquierda':      'libre',         # Qué hay a la izquierda
    'derecha':        None,            # None = fuera del mapa

    # OPCIONAL — brújula hacia la meta.
    # No es percepción real del entorno, es información global.
    # Usarla hace el ejercicio más fácil. No usarla es más realista.
    'direccion_meta': ('abajo', 'derecha'),
}

Valores posibles de cada dirección:
    'libre'  → puedes moverte ahí
    'pared'  → bloqueado
    'meta'   → ¡la meta! ve hacia allá
    None     → borde del mapa, no puedes ir

Si tu agente retorna un movimiento inválido (hacia pared o
fuera del mapa), simplemente se queda en su lugar.
"""

from entorno import Agente


class MiAgente(Agente):
    """
    Tu agente de navegación.

    Implementa el método decidir() para que el agente
    llegue del punto A al punto B en el grid.
    """

    def __init__(self):
        super().__init__(nombre="Mi Agente")
        # Atributos inicializados para memoria y contadores
        self.visited = set()
        self.pasos = 0
        # Puedes agregar más campos si los necesitas (p. ej. self.memoria = {})

    def al_iniciar(self):
        """Se llama una vez al iniciar la simulación. Opcional."""
        pass

    def decidir(self, percepcion):
        
        """
        Decide la siguiente acción del agente.
        
        Parámetros:
            percepcion – diccionario con lo que el agente puede ver

        Retorna:
            'arriba', 'abajo', 'izquierda' o 'derecha'
        """
        # Inicializar memoria si hace falta
        if not hasattr(self, 'visited'):
            # visited: mapa pos -> último paso visitado (int)
            self.visited = {}
        elif isinstance(self.visited, set):
            # convertir la representación antigua (set) a dict con timestamp 0
            self.visited = {p: 0 for p in self.visited}
        if not hasattr(self, 'pasos'):
            self.pasos = 0
        if not hasattr(self, 'last_pos'):
            self.last_pos = None

        # Helpers
        def siguiente_pos(p, d):
            r, c = p
            if d == 'arriba':
                return (r - 1, c)
            if d == 'abajo':
                return (r + 1, c)
            if d == 'izquierda':
                return (r, c - 1)
            if d == 'derecha':
                return (r, c + 1)
            return p

        acciones = getattr(self, 'ACCIONES', ('arriba', 'abajo', 'izquierda', 'derecha'))

        pos = tuple(percepcion.get('posicion', (None, None)))
        # actualizar contador de pasos y marca esta posición como visitada
        self.pasos += 1
        if pos[0] is not None:
            self.visited[pos] = self.pasos

        prev = self.last_pos

        # 1) Si vemos la meta en alguna dirección, ir hacia ella inmediatamente
        for d in acciones:
            if percepcion.get(d) == 'meta':
                self.last_pos = pos
                return d

        # 2) Intentar seguir la brújula (vertical primero, luego horizontal)
        direccion_meta = percepcion.get('direccion_meta')
        if direccion_meta:
            for d in direccion_meta:
                if not d:
                    continue
                val = percepcion.get(d)
                if val in ('libre', 'meta'):
                    nxt = siguiente_pos(pos, d)
                    # evitar retroceder al paso inmediatamente anterior si hay alternativa
                    if nxt != prev:
                        self.last_pos = pos
                        return d

        # 3) Buscar movimientos libres que lleven a celdas no visitadas (preferidos)
        candidatos_no_visitados = []
        candidatos_visitados = []
        for d in acciones:
            if percepcion.get(d) == 'libre':
                nxt = siguiente_pos(pos, d)
                if nxt == prev:
                    # no priorizamos volver inmediatamente atrás
                    candidatos_visitados.append((d, self.visited.get(nxt, 0)))
                    continue
                if nxt not in self.visited:
                    candidatos_no_visitados.append(d)
                else:
                    candidatos_visitados.append((d, self.visited.get(nxt, 0)))

        if candidatos_no_visitados:
            # elegir la primera no visitada (heurística simple, mantiene orden estable)
            self.last_pos = pos
            return candidatos_no_visitados[0]

        # 4) Si no hay no-visitadas, elegir el movimiento libre que conduzca a la celda
        # con la visita más antigua (menor timestamp) para explorar/retroceder inteligentemente
        if candidatos_visitados:
            candidatos_visitados.sort(key=lambda x: x[1] or 0)
            self.last_pos = pos
            return candidatos_visitados[0][0]

        # 5) Como último recurso, intentar cualquier movimiento libre (incluye retroceder)
        for d in acciones:
            if percepcion.get(d) == 'libre':
                self.last_pos = pos
                return d

        # 6) No hay movimientos libres visibles — fallback predecible
        self.last_pos = pos
        return 'arriba'