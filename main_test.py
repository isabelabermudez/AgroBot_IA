"""Ejecutor de consola para probar los algoritmos sobre mapas de pruebas."""

import argparse
from pathlib import Path

from busquedas import (
    amplitud,
    busqueda_a_estrella,
    busqueda_avara,
    costo_uniforme,
    preferente_por_profundidad_pila,
)
from mundo import cargar_mundo, extraer_info
from nucleo import crear_estado_inicial, crear_info, es_meta, sucesores
from reporte import generar_reporte


ALGORITMOS = {
    "1": ("Amplitud", "amplitud", amplitud),
    "2": ("Costo uniforme", "costo_uniforme", costo_uniforme),
    "3": ("Profundidad evitando ciclos", "profundidad", preferente_por_profundidad_pila),
    "4": ("Avara", "avara", busqueda_avara),
    "5": ("A*", "a_estrella", busqueda_a_estrella),
}


def descubrir_pruebas():
    return sorted(
        (archivo for archivo in (Path(__file__).parent / "pruebas").glob("*.txt")),
        key=lambda archivo: archivo.name.casefold(),
    )


def solicitar_opcion(mensaje, opciones, predeterminado="1"):
    while True:
        seleccion = input(f"{mensaje} [{predeterminado}]: ").strip() or predeterminado
        if seleccion in opciones:
            return seleccion
        print(f"Opción inválida. Elige una de: {', '.join(opciones)}.")


def validar_mundo(mundo):
    cantidades = {valor: 0 for valor in range(2, 6)}
    for fila in mundo:
        for valor in fila:
            if valor not in range(6):
                raise ValueError(f"El valor {valor} está fuera del rango permitido (0-5).")
            if valor in cantidades:
                cantidades[valor] += 1

    nombres = {2: "AgroBot", 4: "depósito", 5: "avioneta"}
    for valor, nombre in nombres.items():
        if cantidades[valor] != 1:
            raise ValueError(f"Se requiere exactamente un {nombre}; se encontraron {cantidades[valor]}.")


def validar_solucion(resultado, mundo, info):
    estados = resultado["estados"]
    operadores = resultado["operadores"]
    if len(estados) != len(operadores) + 1 or not es_meta(estados[-1]):
        return False

    for estado, operador, siguiente in zip(estados, operadores, estados[1:]):
        transiciones = sucesores(estado, mundo, info)
        if not any(op == operador and nuevo == siguiente for op, nuevo, _ in transiciones):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Ejecuta un algoritmo de búsqueda sobre un mapa de prueba.")
    parser.add_argument("--prueba", help="Nombre del archivo de prueba, por ejemplo Prueba2.txt.")
    parser.add_argument(
        "--algoritmo",
        choices=tuple(datos[1] for datos in ALGORITMOS.values()),
        help="Código del algoritmo que se desea ejecutar.",
    )
    args = parser.parse_args()

    pruebas = descubrir_pruebas()
    if not pruebas:
        parser.error("No se encontraron mapas .txt en la carpeta pruebas/.")

    por_nombre = {archivo.name.casefold(): archivo for archivo in pruebas}
    if args.prueba:
        archivo_prueba = por_nombre.get(Path(args.prueba).name.casefold())
        if archivo_prueba is None:
            parser.error(f"No existe {args.prueba!r} en la carpeta pruebas/.")
    else:
        print("Mapas disponibles:")
        for indice, archivo in enumerate(pruebas, start=1):
            print(f"  {indice}. {archivo.stem}")
        opcion = solicitar_opcion("Selecciona el mapa", {str(i) for i in range(1, len(pruebas) + 1)})
        archivo_prueba = pruebas[int(opcion) - 1]

    if args.algoritmo:
        codigo_algoritmo = next(codigo for codigo, datos in ALGORITMOS.items() if datos[1] == args.algoritmo)
    else:
        print("\nAlgoritmos disponibles:")
        for codigo, (nombre, _, _) in ALGORITMOS.items():
            print(f"  {codigo}. {nombre}")
        codigo_algoritmo = solicitar_opcion("Selecciona el algoritmo", ALGORITMOS)

    nombre_algoritmo, _, funcion_busqueda = ALGORITMOS[codigo_algoritmo]
    mundo = cargar_mundo(str(archivo_prueba))
    validar_mundo(mundo)
    robot, deposito, avioneta, cultivos = extraer_info(mundo)
    estado_inicial = crear_estado_inicial(robot, cultivos)
    info = crear_info(deposito, avioneta)

    print(f"\nPrueba: {archivo_prueba.stem}")
    print(f"Algoritmo: {nombre_algoritmo}")
    resultado = funcion_busqueda(estado_inicial, mundo, info)
    if resultado is None:
        print("Resultado: no se encontró solución.")
        return 1

    if not validar_solucion(resultado, mundo, info):
        print("Resultado: la búsqueda devolvió una ruta inválida.")
        return 1

    print(generar_reporte(nombre_algoritmo, resultado))
    print(f"Movimientos de la solución: {', '.join(resultado['operadores']) or '(ninguno)'}")
    print("Validación de ruta: correcta; todos los cultivos fueron tratados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
