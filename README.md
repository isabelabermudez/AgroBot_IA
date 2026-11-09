# AgroBot_IA

## Aplicación gráfica

En Debian/Ubuntu, crea un entorno virtual para instalar las dependencias sin
modificar el Python administrado por el sistema (PEP 668):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Si `python3 -m venv .venv` indica que falta `ensurepip` o el módulo `venv`,
instala el paquete del sistema `python3-venv` y vuelve a ejecutar el comando.
También puedes usar el entorno sin activarlo con `./.venv/bin/python main.py`.

En Windows, si Python 3.12 ya está instalado, crea el entorno con esa versión
explícitamente:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -m pip install -r requirements.txt
python main.py
```

`python --version` debe mostrar Python 3.12. Usa `py -3.12`, no `py -3`, para
evitar que el lanzador seleccione otra versión instalada. Si ya existe `.venv`
creado con otra versión de Python, elimínalo antes de crearlo de nuevo.

Si Python 3.12 no está instalado, puedes usar `uv` para descargarlo y
administrarlo sin instalarlo globalmente. Instala `uv` con WinGet:

```powershell
winget install --id astral-sh.uv -e
```

Cierra y vuelve a abrir PowerShell para que se actualice el `PATH`. Después,
desde la carpeta del proyecto, descarga Python 3.12, crea el entorno e instala
las dependencias:

```powershell
uv python install 3.12
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.venv\Scripts\python.exe main.py
```

`uv` administra esa versión de Python por separado; no hace falta instalarla
globalmente ni activar el entorno. Un entorno virtual creado con el comando
`python -m venv` por sí solo no descarga ni instala Python: utiliza un
intérprete que ya esté disponible.

La aplicación inicia con `Prueba1.txt`. Para cargar otro mundo, escribe su ruta
en el campo **Archivo del mundo** y pulsa **Cargar archivo**. El archivo debe
contener una cuadrícula de 10x10 con valores de `0` a `5`, un AgroBot (`2`), un
depósito (`4`) y una avioneta (`5`).

En el campo de ruta puedes usar `Ctrl+A` para seleccionar todo, `Ctrl+C` y
`Ctrl+V` para copiar y pegar, y `Ctrl+X` para cortar. También funcionan las
teclas `Inicio`, `Fin`, `Supr` y `Retroceso`. Usa el botón **×** de la esquina
superior derecha para cerrar la interfaz.
Puedes mover la ventana arrastrando la franja superior; su tamaño permanece fijo.

Selecciona el tipo de búsqueda y el algoritmo, y pulsa **Ejecutar búsqueda**.
La ruta encontrada se anima sobre el tablero y, al finalizar la animación, el
panel de reporte muestra los nodos expandidos, la profundidad del árbol y el
tiempo de cómputo. También muestra el costo para Costo uniforme y A*.