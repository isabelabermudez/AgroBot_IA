from mundo import cargar_mundo, imprimir_mundo, extraer_info
import os
ruta = os.path.join(os.path.dirname(__file__), "Prueba1.txt")
from nucleo import crear_estado_inicial, crear_info, sucesores
from busquedas import amplitud


def main():
    mapa = cargar_mundo("Prueba1.txt")
    imprimir_mundo(mapa)

    robot, deposito, avioneta, cultivos = extraer_info(mapa)
    estado = crear_estado_inicial(robot, cultivos)
    info = crear_info(deposito, avioneta)

    resultado = amplitud(estado, mapa, info)
    if resultado:
        print(resultado["operadores"])
        print(resultado["expandidos"], resultado["profundidad"], resultado["costo"], resultado["tiempo"])
    else:
        print("Sin solución")

if __name__ == "__main__":
  main()

