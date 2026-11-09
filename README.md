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

La aplicación inicia con `Prueba1.txt`. Para cargar otro mundo, escribe su ruta
en el campo **Archivo del mundo** y pulsa **Cargar archivo**. El archivo debe
contener una cuadrícula de 10x10 con valores de `0` a `5`, un AgroBot (`2`), un
depósito (`4`) y una avioneta (`5`).

Selecciona el tipo de búsqueda y el algoritmo, y pulsa **Ejecutar búsqueda**.
La ruta encontrada se anima sobre el tablero y, al finalizar la animación, el
panel de reporte muestra los nodos expandidos, la profundidad del árbol y el
tiempo de cómputo. También muestra el costo para Costo uniforme y A*.