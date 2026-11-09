"""Presentación en consola de las métricas de una búsqueda de AgroBot."""


ALGORITMOS_CON_COSTO = {"Costo uniforme", "A*"}


def generar_reporte(nombre_algoritmo, resultado):
    """Construye el reporte solicitado para una búsqueda con solución."""
    lineas = [
        f"Reporte de búsqueda: {nombre_algoritmo}",
        f"Nodos expandidos: {resultado['expandidos']}",
        f"Profundidad del árbol: {resultado['profundidad']}",
        f"Tiempo de cómputo: {resultado['tiempo']:.6f} segundos",
    ]
    if nombre_algoritmo in ALGORITMOS_CON_COSTO:
        lineas.append(f"Costo de la solución: {resultado['costo']:g}")
    return "\n".join(lineas)


def mostrar_reporte(nombre_algoritmo, resultado):
    """Muestra el reporte en la terminal, independiente de la ventana Pygame."""
    reporte = generar_reporte(nombre_algoritmo, resultado)
    print(f"\n{reporte}\n")
    return reporte
