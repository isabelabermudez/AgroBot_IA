

def cargar_mundo(ruta):
    matriz = []
    with open(ruta, "r") as f:
        for linea in f:
            if linea.strip():
                matriz.append([int(x) for x in linea.split()])
    
    # Valida que tenga exactamente 10 filas
    if len(matriz) != 10:
        raise ValueError(f"El archivo debe tener 10 filas, pero se encontraron {len(matriz)}.")
    
    # Valida que cada fila tenga exactamente 10 columnas
    for i, fila in enumerate(matriz):
        if len(fila) != 10:
            raise ValueError(f"La fila {i + 1} debe tener 10 elementos, pero tiene {len(fila)}.")
            
    return matriz


def imprimir_mundo(matriz):
    for fila in matriz:
        for valor in fila:
            print(f"{valor}\t", end="")
        print("")


def extraer_info(matriz):
    inicio_robot = ()
    pos_deposito = ()
    pos_avioneta = ()
    cultivos = []
    for i, fila in enumerate(matriz):
        for j, valor in enumerate(fila):
            if valor == 1:
                continue
            elif valor == 2:
                inicio_robot = (i, j)
            elif valor == 3:
                cultivos.append((i, j))
            elif valor == 4:
                pos_deposito = (i, j)
            elif valor == 5:
                pos_avioneta = (i, j)

    return (inicio_robot,pos_deposito,pos_avioneta,cultivos)
    






