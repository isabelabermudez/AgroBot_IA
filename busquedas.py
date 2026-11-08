import time
import heapq
from collections import deque
from itertools import count

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

def costo_uniforme(estado_inicial, mundo, info):
    inicio = time.perf_counter()

    contador = count()  # contador para romper empates en la cola de prioridad
    
    raiz = Nodo(estado_inicial)
    cola_prioridad = []

    heapq.heappush(
        cola_prioridad, 
        (raiz.costo,
        next(contador),
        raiz)
        )
    
    mejores_costos = {estado_inicial: raiz.costo}  # diccionario de estados ya generados con su costo mínimo

    expandidos = 0
    profundidad_max = 0
    
    while cola_prioridad:
        costo, _, nodo = heapq.heappop(cola_prioridad)

        if costo > mejores_costos[nodo.estado]:
            continue  # ya se encontró un camino más barato a este estado
        
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

            costo_anterior = mejores_costos.get(hijo.estado)

            if costo_anterior is None or hijo.costo < costo_anterior:
                
                mejores_costos[hijo.estado] = hijo.costo

                profundidad_max = max(profundidad_max, hijo.profundidad) 

                heapq.heappush(cola_prioridad,(hijo.costo,next(contador), hijo))
                
    return None  # no hay solucion


def preferente_por_profundidad(estado_inicial, mundo, info):
    inicio = time.perf_counter()

    contador = count()  # contador para romper empates en la cola de prioridad
        
    raiz = Nodo(estado_inicial)
    cola_profundidad = []
    visitados = set()  # estados ya generados

    heapq.heappush(
        cola_profundidad, 
        (raiz.profundidad,
        next(contador),
        raiz)
        )

    expandidos = 0
    profundidad_max = 0

    while cola_profundidad:
        _, _, nodo = heapq.heappop(cola_profundidad)

        if nodo.estado in visitados:
            continue  # ya se visitó este estado
        visitados.add(nodo.estado)

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
                profundidad_max = max(profundidad_max, hijo.profundidad) 
                heapq.heappush(cola_profundidad,(-hijo.profundidad,next(contador), hijo))

    return None  # no hay solucion


def preferente_por_profundidad_pila(estado_inicial, mundo, info):
    inicio = time.perf_counter()

    raiz = Nodo(estado_inicial)
    frontera = [raiz]  # pila LIFO ultimo en entrar, primero en salir
    visitados = set()  # estados ya generados
    expandidos = 0
    profundidad_max = 0

    while frontera:
        nodo = frontera.pop()

        if nodo.estado in visitados:
                continue  # ya se visitó este estado
        
        visitados.add(nodo.estado)

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
        for hijo in reversed(expandir(nodo, mundo, info)):
            if hijo.estado not in visitados:
                profundidad_max = max(profundidad_max, hijo.profundidad)
                frontera.append(hijo)

    return None  # no hay solucion


