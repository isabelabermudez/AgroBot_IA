# AgroBot IA

Aplicación de escritorio hecha con Python y Pygame para visualizar un terreno
agrícola, ejecutar algoritmos de búsqueda y animar la ruta del robot.

## Requisitos

- Python 3.12 recomendado. Puedes instalarlo desde [python.org](https://www.python.org/downloads/).
- Git para clonar el repositorio (o descarga el proyecto como ZIP).
- Windows, macOS o Linux con entorno gráfico.

## 1. Descargar el proyecto

Con Git:

```bash
git clone https://github.com/isabelabermudez/AgroBot_IA.git
cd AgroBot_IA
```

También puedes descargar el ZIP desde GitHub y abrir una terminal dentro de la
carpeta `AgroBot_IA`.

## 2. Crear el entorno e instalar dependencias

Usa un entorno virtual para que Pygame se instale solo para este proyecto y no
modifique el Python del sistema.

### Windows (PowerShell)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si el comando `py` no está disponible, sustituye la primera línea por:

```powershell
python -m venv .venv
```

### macOS y Linux

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

En Ubuntu/Debian, si no puedes crear el entorno porque faltan `venv` o
`ensurepip`, instala el paquete del sistema y repite los comandos:

```bash
sudo apt update
sudo apt install python3-full
```

No uses `sudo pip` ni `--break-system-packages`: el entorno virtual evita el
error `externally-managed-environment` de las distribuciones Linux.

## 3. Ejecutar AgroBot

Desde la carpeta del proyecto:

**Windows:**

```powershell
.\.venv\Scripts\python.exe main.py
```

**macOS/Linux:**

```bash
./.venv/bin/python main.py
```

La ventana abre con **Prueba 1**. Selecciona un mapa en el menú **Prueba del
terreno**, pulsa **Cargar prueba**, elige el tipo y el algoritmo de búsqueda y
pulsa **Iniciar búsqueda**. Al terminar la animación se muestran las métricas
del algoritmo; Costo uniforme y A* también muestran el costo de la solución.

Los mapas disponibles están en `pruebas/`. Para añadir uno, coloca un archivo
`.txt` allí con una cuadrícula de 10 filas por 10 columnas y estos valores:

| Valor | Elemento |
|---:|---|
| 0 | Casilla libre |
| 1 | Obstáculo |
| 2 | AgroBot (exactamente uno) |
| 3 | Cultivo seco |
| 4 | Depósito (exactamente uno) |
| 5 | Avioneta (exactamente una) |

## Solución de problemas

- **`No module named pygame`:** se está usando otro Python. Ejecuta la aplicación
  con el intérprete de `.venv` indicado arriba.
- **`externally-managed-environment`:** no instales dependencias en el Python
  del sistema; crea el entorno virtual y ejecuta `pip` a través de él.
- **No se encuentra `Prueba1` u otro mapa:** confirma que los archivos `.txt`
  estén dentro de `pruebas/` y vuelve a iniciar la aplicación.
