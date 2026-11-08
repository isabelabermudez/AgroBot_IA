from mundo import cargar_mundo, imprimir_mundo, extraer_info
import os
ruta = os.path.join(os.path.dirname(__file__), "Prueba1.txt")
from nucleo import crear_estado_inicial, crear_info, heuristica
from busquedas import amplitud, costo_uniforme, preferente_por_profundidad, preferente_por_profundidad_pila, busqueda_avara

def main():
    mapa = cargar_mundo(ruta)
    imprimir_mundo(mapa)

    robot, deposito, avioneta, cultivos = extraer_info(mapa)
    estado = crear_estado_inicial(robot, cultivos)
    info = crear_info(deposito, avioneta)

    print("Costo estimado desde el estado inicial:", heuristica(estado))

    algoritmo = int(input("Ingrese el algoritmo a utilizar (1: Amplitud, 2: Costo , 3: Preferente por profundidad, 4: Preferente por profundidad (pila)), 5: Búsqueda Avara: "))

    if algoritmo == 1:
        resultado = amplitud(estado, mapa, info)
    elif algoritmo == 2:
        resultado = costo_uniforme(estado, mapa, info)
    elif algoritmo == 3:
        resultado = preferente_por_profundidad(estado, mapa, info)
    elif algoritmo == 4:
        resultado = preferente_por_profundidad_pila(estado, mapa, info)
    elif algoritmo == 5:
        resultado = busqueda_avara(estado, mapa, info)
    else:
        print("Algoritmo no válido")
        return

    if resultado:
        print(resultado["operadores"])
        print(resultado["expandidos"], resultado["profundidad"], resultado["costo"], resultado["tiempo"])
    else:
        print("Sin solución")

if __name__ == "__main__":
  main()

