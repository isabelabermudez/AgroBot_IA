from dataclasses import dataclass
from collections import namedtuple

# ---------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------
OBSTACULO = 1
FERTILIZANTE_MAX = 2
COMBUSTIBLE_MAX = 30
SIN_SUBIR = -1          # combustible = -1  -> el robot aun no se ha subido a la avioneta

COSTO_NORMAL = 1
COSTO_AVIONETA = 0.5

# operador -> (delta_fila, delta_columna)
OPERADORES = {
    "arriba": (-1, 0),
    "abajo": (1, 0),
    "izquierda": (0, -1),
    "derecha": (0, 1),
}

# Datos fijos del mundo (no cambian durante la busqueda)
Info = namedtuple("Info", ["deposito", "avioneta"])


# ---------------------------------------------------------------
# Estado: inmutable y hashable (sirve para el conjunto de visitados)
# ---------------------------------------------------------------
@dataclass(frozen=True)
class Estado:
    pos: tuple              # (fila, columna)
    fertilizante: int       # 0..2
    cultivos: frozenset     # coordenadas de cultivos secos pendientes
    combustible: int        # -1 sin subir, 30..1 montado con combustible, 0 agotado

    def clave(self):
        """Clave para detectar ciclos: ignora cuánto combustible queda,
        pero distingue si ya se montó en la avioneta."""
        return (self.pos, self.fertilizante, self.cultivos, self.combustible != SIN_SUBIR)


# ---------------------------------------------------------------
# Nodo del arbol de busqueda
# ---------------------------------------------------------------
class Nodo:
    def __init__(self, estado, padre=None, operador=None, profundidad=0, costo=0):
        self.estado = estado
        self.padre = padre
        self.operador = operador
        self.profundidad = profundidad
        self.costo = costo      # g(n): costo acumulado desde la raiz


# ---------------------------------------------------------------
# Construccion del estado inicial
# ---------------------------------------------------------------
def crear_estado_inicial(pos_robot, cultivos):
    """El robot siempre inicia sin fertilizante y sin haberse subido a la avioneta."""
    return Estado(
        pos=pos_robot,
        fertilizante=0,
        cultivos=frozenset(cultivos),
        combustible=SIN_SUBIR,
    )


def crear_info(pos_deposito, pos_avioneta):
    return Info(deposito=pos_deposito, avioneta=pos_avioneta)


# ---------------------------------------------------------------
# Funciones del problema
# ---------------------------------------------------------------
def es_meta(estado):
    """Meta: no queda ningun cultivo seco pendiente."""
    return len(estado.cultivos) == 0


def costo_paso(estado):
    """Costo del movimiento, calculado con el estado ANTES de moverse."""
    if estado.combustible > 0:
        return COSTO_AVIONETA
    return COSTO_NORMAL


def sucesores(estado, mundo, info):
    """Devuelve una lista de (operador, nuevo_estado, costo_paso)."""
    resultado = []
    filas = len(mundo)
    columnas = len(mundo[0])
    f, c = estado.pos

    for operador, (df, dc) in OPERADORES.items():
        nf, nc = f + df, c + dc
        destino = (nf, nc)

        # fuera del tablero u obstaculo
        if not (0 <= nf < filas and 0 <= nc < columnas):
            continue
        if mundo[nf][nc] == OBSTACULO:
            continue

        costo = costo_paso(estado)

        fertilizante = estado.fertilizante
        cultivos = estado.cultivos
        combustible = estado.combustible

        # si iba montado, gasta una unidad de combustible (sin bajar de 0)
        if combustible > 0:
            combustible -= 1

        # efectos automaticos segun la casilla destino
        if destino == info.deposito:
            fertilizante = FERTILIZANTE_MAX
        elif destino == info.avioneta and combustible == SIN_SUBIR:
            combustible = COMBUSTIBLE_MAX
        elif destino in cultivos and fertilizante > 0:
            cultivos = cultivos - {destino}
            fertilizante -= 1

        nuevo = Estado(destino, fertilizante, cultivos, combustible)
        resultado.append((operador, nuevo, costo))

    return resultado


def expandir(nodo, mundo, info):
    """Genera los nodos hijos de un nodo (enlazados a su padre)."""
    hijos = []
    for operador, nuevo_estado, costo in sucesores(nodo.estado, mundo, info):
        hijos.append(
            Nodo(
                estado=nuevo_estado,
                padre=nodo,
                operador=operador,
                profundidad=nodo.profundidad + 1,
                costo=nodo.costo + costo,
            )
        )
    return hijos


def reconstruir_camino(nodo):
    """Sigue los padres hasta la raiz. Devuelve (operadores, estados) en orden desde el inicio."""
    operadores = []
    estados = []
    while nodo is not None:
        estados.append(nodo.estado)
        if nodo.operador is not None:
            operadores.append(nodo.operador)
        nodo = nodo.padre
    operadores.reverse()
    estados.reverse()
    return operadores, estados


def heuristica(estado, info):  

    if not estado.cultivos:
        return 0  # No hay cultivos pendientes, heurística es 0

    if estado.fertilizante == 0:
        # Si no tiene fertilizante, debe ir al depósito primero
        distancia_deposito = distancia_manhattan(estado.pos, info.deposito)
        # Después de recoger el fertilizante, como minimo debera ir al cultivo más lejano
        mas_lejano = max(distancia_manhattan(info.deposito, c) for c in estado.cultivos)

        pasos_totales = distancia_deposito + mas_lejano
    else:
        pasos_totales = max(distancia_manhattan(estado.pos, c) for c in estado.cultivos)

        # Si hay más cultivos que unidades, debe pasar por el depósito
        if len(estado.cultivos) > estado.fertilizante:
            recorrido_total = (distancia_manhattan(estado.pos, info.deposito)
                            + min(distancia_manhattan(info.deposito, c) for c in estado.cultivos))
            pasos_totales = max(pasos_totales, recorrido_total)

    # ...igual que ahora hasta calcular pasos_totales...

    
    
    
    return costo_minimo(pasos_totales, estado.combustible) 


# Calcula el Costo mínimo de 'pasos' o movimientos según el combustible de la avioneta.
def costo_minimo(pasos, combustible):
    if combustible == SIN_SUBIR:
        return pasos * COSTO_AVIONETA          # podría subirse en el camino
    if combustible == 0:
        return pasos * COSTO_NORMAL
    return (COSTO_AVIONETA * min(pasos, combustible)       #calcula el costo de los pasos que puede hacer con la avioneta + el costo de los pasos que le faltan por hacer con el costo normal
            + COSTO_NORMAL * max(pasos - combustible, 0))


def distancia_manhattan(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

