"""Formato del reporte de métricas de una búsqueda de AgroBot."""


ALGORITMOS_CON_COSTO = {"Costo uniforme", "A*"}
EXPONENTE_TIEMPO = -3


def generar_reporte(nombre_algoritmo, resultado):
    """Construye el reporte solicitado para una búsqueda con solución."""
    tiempo_escalado = resultado["tiempo"] / (10**EXPONENTE_TIEMPO)
    lineas = [
        f"Reporte de búsqueda: {nombre_algoritmo}",
        f"Nodos expandidos: {resultado['expandidos']}",
        f"Profundidad del árbol: {resultado['profundidad']}",
        f"Tiempo de cómputo: {tiempo_escalado:.3f} × 10^{EXPONENTE_TIEMPO} s",
    ]
    if nombre_algoritmo in ALGORITMOS_CON_COSTO:
        lineas.append(f"Costo de la solución: {resultado['costo']:g}")
    return "\n".join(lineas)
