import time
from collections import deque

from nucleo import Nodo, es_meta, expandir, reconstruir_camino


def amplitud(estado_inicial, mundo, info):
    inicio = time.perf_counter()

    raiz = Nodo(estado_inicial)
    frontera = deque([raiz])        # cola FIFO
    visitados = {estado_inicial}    # estados ya generados
    expandidos = 0
    profundidad_max = 0

    while frontera:
        nodo = frontera.popleft()

        if es_meta(nodo.estado):
            operadores, estados = reconstruir_camino(nodo)
            return {
                "operadores": operadores,
                "estados": estados,
                "expandidos": expandidos,
                "profundidad": profundidad_max,
                "costo": nodo.costo,
                "tiempo": time.perf_counter() - inicio,
            }

        expandidos += 1
        for hijo in expandir(nodo, mundo, info):
            if hijo.estado not in visitados:
                visitados.add(hijo.estado)
                profundidad_max = max(profundidad_max, hijo.profundidad)
                frontera.append(hijo)

    return None  # no hay solucion