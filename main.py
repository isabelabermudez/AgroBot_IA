import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from busquedas import (
    amplitud,
    busqueda_a_estrella,
    busqueda_avara,
    costo_uniforme,
    preferente_por_profundidad_pila,
)
from mundo import cargar_mundo, extraer_info
from nucleo import crear_estado_inicial, crear_info
from reporte import mostrar_reporte


ANCHO = 1080
ALTO = 740
TAM_CASILLA = 56
ORIGEN_TABLERO = (32, 132)
ALGORITMOS = {
    "no_informada": [
        ("amplitud", "Amplitud"),
        ("costo_uniforme", "Costo uniforme"),
        ("profundidad", "Profundidad evitando ciclos"),
    ],
    "informada": [
        ("avara", "Avara"),
        ("a_estrella", "A*"),
    ],
}
FUNCIONES_BUSQUEDA = {
    "amplitud": amplitud,
    "costo_uniforme": costo_uniforme,
    "profundidad": preferente_por_profundidad_pila,
    "avara": busqueda_avara,
    "a_estrella": busqueda_a_estrella,
}
NOMBRES_ALGORITMOS = {
    codigo: nombre
    for opciones in ALGORITMOS.values()
    for codigo, nombre in opciones
}

FONDO = (240, 244, 239)
PANEL = (255, 255, 255)
TEXTO = (35, 48, 41)
SECUNDARIO = (105, 117, 109)
VERDE = (42, 112, 78)
VERDE_CLARO = (221, 239, 223)
BORDE = (210, 219, 211)
OBSTACULO = (68, 77, 70)
CULTIVO_SECO = (235, 187, 91)
CULTIVO_TRATADO = (116, 178, 107)
AZUL = (84, 151, 196)
ROJO = (198, 83, 73)


def validar_mundo(mundo):
    cantidades = {valor: 0 for valor in range(2, 6)}
    for fila in mundo:
        for valor in fila:
            if valor not in range(6):
                raise ValueError(f"El valor {valor} no pertenece a las convenciones del mapa (0-5).")
            if valor in cantidades:
                cantidades[valor] += 1

    nombres = {2: "AgroBot", 4: "depósito", 5: "avioneta"}
    for valor, nombre in nombres.items():
        if cantidades[valor] != 1:
            raise ValueError(f"El mapa debe tener exactamente un {nombre}; se encontraron {cantidades[valor]}.")


class AgroBotApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AgroBot - Búsqueda en terrenos agrícolas")
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("arial", 19)
        self.fuente_pequena = pygame.font.SysFont("arial", 15)
        self.fuente_titulo = pygame.font.SysFont("arial", 27, bold=True)
        self.fuente_casilla = pygame.font.SysFont("arial", 17, bold=True)

        self.ruta = os.path.join(os.path.dirname(__file__), "Prueba1.txt")
        self.campo_activo = False
        self.categoria = "no_informada"
        self.algoritmo = "amplitud"
        self.mundo = None
        self.info = None
        self.estado_inicial = None
        self.estado_actual = None
        self.estados_camino = []
        self.indice_animacion = 0
        self.ultimo_paso = 0
        self.resultado = None
        self.mensaje = "Selecciona un archivo de mundo para comenzar."
        self.error = False

        if os.path.isfile(self.ruta):
            self.cargar_archivo()

    def cargar_archivo(self):
        try:
            mundo = cargar_mundo(self.ruta)
            validar_mundo(mundo)
        except (OSError, UnicodeError, ValueError) as error:
            self.mundo = None
            self.info = None
            self.estado_inicial = None
            self.estado_actual = None
            self.mensaje = f"No se pudo cargar el mundo: {error}"
            self.error = True
            return

        robot, deposito, avioneta, cultivos = extraer_info(mundo)
        self.mundo = mundo
        self.info = crear_info(deposito, avioneta)
        self.estado_inicial = crear_estado_inicial(robot, cultivos)
        self.estado_actual = self.estado_inicial
        self.estados_camino = []
        self.indice_animacion = 0
        self.resultado = None
        self.mensaje = f"Mundo cargado: {len(cultivos)} cultivos secos."
        self.error = False

    def ejecutar_busqueda(self):
        if self.mundo is None or self.estado_inicial is None:
            self.mensaje = "Primero carga un archivo de mundo válido."
            self.error = True
            return

        funcion = FUNCIONES_BUSQUEDA[self.algoritmo]
        self.mensaje = f"Ejecutando {NOMBRES_ALGORITMOS[self.algoritmo]}..."
        self.dibujar()
        pygame.display.flip()

        resultado = funcion(self.estado_inicial, self.mundo, self.info)
        self.resultado = resultado
        self.estado_actual = self.estado_inicial
        self.indice_animacion = 0

        if resultado is None:
            self.estados_camino = []
            self.mensaje = "No se encontró una solución para este mundo."
            self.error = True
            print(f"\n{NOMBRES_ALGORITMOS[self.algoritmo]}: no se encontró solución.")
            return

        self.estados_camino = resultado["estados"]
        self.mensaje = f"Solución encontrada: {len(resultado['operadores'])} movimientos. Animando..."
        self.error = False
        mostrar_reporte(NOMBRES_ALGORITMOS[self.algoritmo], resultado)

    def rectangulo_boton(self, nombre):
        return {
            "cargar": pygame.Rect(922, 66, 126, 40),
            "no_informada": pygame.Rect(674, 173, 180, 42),
            "informada": pygame.Rect(864, 173, 180, 42),
            "ejecutar": pygame.Rect(674, 354, 370, 48),
            "reiniciar": pygame.Rect(674, 414, 178, 40),
            "reanudar": pygame.Rect(866, 414, 178, 40),
        }[nombre]

    def dibujar_boton(self, nombre, etiqueta, activo=False, deshabilitado=False):
        rect = self.rectangulo_boton(nombre)
        color = (223, 229, 224) if deshabilitado else (VERDE if activo else PANEL)
        color_texto = SECUNDARIO if deshabilitado else (PANEL if activo else TEXTO)
        pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
        pygame.draw.rect(self.pantalla, BORDE, rect, 1, border_radius=8)
        self.texto_centrado(etiqueta, color_texto, rect.center)

    def texto(self, contenido, posicion, color=TEXTO, fuente=None):
        superficie = (fuente or self.fuente).render(str(contenido), True, color)
        self.pantalla.blit(superficie, posicion)

    def texto_centrado(self, contenido, color, centro, fuente=None):
        superficie = (fuente or self.fuente).render(str(contenido), True, color)
        self.pantalla.blit(superficie, superficie.get_rect(center=centro))

    def dibujar_tablero(self):
        if self.mundo is None or self.estado_actual is None:
            panel = pygame.Rect(ORIGEN_TABLERO[0], ORIGEN_TABLERO[1], 10 * TAM_CASILLA, 10 * TAM_CASILLA)
            pygame.draw.rect(self.pantalla, PANEL, panel, border_radius=10)
            self.texto_centrado("Carga un archivo para visualizar el mundo", SECUNDARIO, panel.center)
            return

        x0, y0 = ORIGEN_TABLERO
        cultivos_pendientes = self.estado_actual.cultivos
        for fila in range(10):
            for columna in range(10):
                valor = self.mundo[fila][columna]
                rect = pygame.Rect(x0 + columna * TAM_CASILLA, y0 + fila * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA)
                fondo = OBSTACULO if valor == 1 else PANEL
                pygame.draw.rect(self.pantalla, fondo, rect)
                pygame.draw.rect(self.pantalla, BORDE, rect, 1)

                posicion = (fila, columna)
                if valor == 1:
                    self.texto_centrado("X", (220, 224, 220), rect.center, self.fuente_casilla)
                elif valor == 4:
                    self.texto_centrado("D", VERDE, rect.center, self.fuente_casilla)
                elif valor == 5:
                    self.texto_centrado("A", AZUL, rect.center, self.fuente_casilla)
                elif valor == 3:
                    color = CULTIVO_SECO if posicion in cultivos_pendientes else CULTIVO_TRATADO
                    pygame.draw.circle(self.pantalla, color, rect.center, 14)
                    etiqueta = "S" if posicion in cultivos_pendientes else "✓"
                    self.texto_centrado(etiqueta, TEXTO, rect.center, self.fuente_casilla)

        fila, columna = self.estado_actual.pos
        centro = (
            x0 + columna * TAM_CASILLA + TAM_CASILLA // 2,
            y0 + fila * TAM_CASILLA + TAM_CASILLA // 2,
        )
        pygame.draw.circle(self.pantalla, ROJO, centro, 15)
        self.texto_centrado("R", PANEL, centro, self.fuente_casilla)

    def dibujar_panel(self):
        pygame.draw.rect(self.pantalla, PANEL, (650, 32, 398, 680), border_radius=12)
        self.texto("Archivo del mundo", (674, 42), fuente=self.fuente_pequena, color=SECUNDARIO)
        campo = pygame.Rect(674, 64, 238, 42)
        pygame.draw.rect(self.pantalla, PANEL, campo, border_radius=7)
        pygame.draw.rect(self.pantalla, VERDE if self.campo_activo else BORDE, campo, 2, border_radius=7)
        ruta_visible = self.ruta
        while self.fuente_pequena.size(ruta_visible)[0] > campo.width - 16 and ruta_visible:
            ruta_visible = ruta_visible[1:]
        self.texto(ruta_visible, (campo.x + 8, campo.y + 12), fuente=self.fuente_pequena)
        self.dibujar_boton("cargar", "Cargar archivo")

        self.texto("Tipo de búsqueda", (674, 132), fuente=self.fuente_pequena, color=SECUNDARIO)
        self.dibujar_boton("no_informada", "No informada", self.categoria == "no_informada")
        self.dibujar_boton("informada", "Informada", self.categoria == "informada")

        y = 232
        self.texto("Algoritmo", (674, 217), fuente=self.fuente_pequena, color=SECUNDARIO)
        for codigo, nombre in ALGORITMOS[self.categoria]:
            rect = pygame.Rect(674, y, 370, 36)
            activo = self.algoritmo == codigo
            pygame.draw.rect(self.pantalla, VERDE_CLARO if activo else PANEL, rect, border_radius=7)
            pygame.draw.rect(self.pantalla, VERDE if activo else BORDE, rect, 1, border_radius=7)
            pygame.draw.circle(self.pantalla, VERDE if activo else BORDE, (rect.x + 18, rect.centery), 7, 2)
            if activo:
                pygame.draw.circle(self.pantalla, VERDE, (rect.x + 18, rect.centery), 4)
            self.texto(nombre, (rect.x + 36, rect.y + 8), fuente=self.fuente_pequena)
            y += 42

        self.dibujar_boton("ejecutar", "Ejecutar búsqueda", activo=True, deshabilitado=self.mundo is None)
        self.dibujar_boton("reiniciar", "Reiniciar animación", deshabilitado=not self.estados_camino)
        self.dibujar_boton("reanudar", "Ver solución", deshabilitado=not self.estados_camino)

        pygame.draw.line(self.pantalla, BORDE, (674, 474), (1044, 474), 1)
        self.texto("Estado del agente", (674, 490), fuente=self.fuente_pequena, color=SECUNDARIO)
        if self.estado_actual is not None:
            self.texto(f"Fertilizante: {self.estado_actual.fertilizante}/2", (674, 518), fuente=self.fuente_pequena)
            self.texto(f"Combustible: {max(0, self.estado_actual.combustible)}", (674, 543), fuente=self.fuente_pequena)
            self.texto(f"Cultivos pendientes: {len(self.estado_actual.cultivos)}", (674, 568), fuente=self.fuente_pequena)
        color_mensaje = ROJO if self.error else SECUNDARIO
        self.texto("Mensaje", (674, 607), fuente=self.fuente_pequena, color=color_mensaje)
        lineas = self.dividir_texto(self.mensaje, self.fuente_pequena, 360)
        for indice, linea in enumerate(lineas[:3]):
            self.texto(linea, (674, 630 + indice * 20), fuente=self.fuente_pequena, color=color_mensaje)

    def dividir_texto(self, contenido, fuente, ancho):
        palabras = str(contenido).split()
        lineas = []
        linea = ""
        for palabra in palabras:
            candidata = f"{linea} {palabra}".strip()
            if fuente.size(candidata)[0] > ancho and linea:
                lineas.append(linea)
                linea = palabra
            else:
                linea = candidata
        if linea:
            lineas.append(linea)
        return lineas

    def dibujar_leyenda(self):
        y = 710
        elementos = [
            ("X", OBSTACULO, "Obstáculo"),
            ("S", CULTIVO_SECO, "Cultivo seco"),
            ("D", VERDE, "Depósito"),
            ("A", AZUL, "Avioneta"),
            ("R", ROJO, "AgroBot"),
        ]
        x = 34
        for letra, color, etiqueta in elementos:
            pygame.draw.circle(self.pantalla, color, (x + 9, y + 9), 9)
            self.texto_centrado(letra, PANEL if letra == "X" else TEXTO, (x + 9, y + 9), self.fuente_pequena)
            self.texto(etiqueta, (x + 23, y + 1), fuente=self.fuente_pequena, color=SECUNDARIO)
            x += 118

    def dibujar(self):
        self.pantalla.fill(FONDO)
        self.texto("AgroBot", (32, 30), fuente=self.fuente_titulo, color=VERDE)
        self.texto("Planificación de rutas y tratamiento de cultivos", (32, 68), fuente=self.fuente_pequena, color=SECUNDARIO)
        self.dibujar_tablero()
        self.dibujar_panel()
        self.dibujar_leyenda()

    def manejar_clic(self, posicion):
        campo = pygame.Rect(674, 64, 238, 42)
        self.campo_activo = campo.collidepoint(posicion)

        if self.rectangulo_boton("cargar").collidepoint(posicion):
            self.cargar_archivo()
            return

        if self.rectangulo_boton("no_informada").collidepoint(posicion):
            self.categoria = "no_informada"
            self.algoritmo = "amplitud"
            return
        if self.rectangulo_boton("informada").collidepoint(posicion):
            self.categoria = "informada"
            self.algoritmo = "avara"
            return

        y = 232
        for codigo, _ in ALGORITMOS[self.categoria]:
            if pygame.Rect(674, y, 370, 36).collidepoint(posicion):
                self.algoritmo = codigo
                return
            y += 42

        if self.rectangulo_boton("ejecutar").collidepoint(posicion) and self.mundo is not None:
            self.ejecutar_busqueda()
        elif self.rectangulo_boton("reiniciar").collidepoint(posicion) and self.estados_camino:
            self.indice_animacion = 0
            self.estado_actual = self.estados_camino[0]
            self.ultimo_paso = pygame.time.get_ticks()
            self.mensaje = "Reproduciendo la solución desde el inicio."
            self.error = False
        elif self.rectangulo_boton("reanudar").collidepoint(posicion) and self.estados_camino:
            self.indice_animacion = len(self.estados_camino) - 1
            self.estado_actual = self.estados_camino[-1]
            self.mensaje = "Solución completada."
            self.error = False

    def manejar_evento(self, evento):
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            self.manejar_clic(evento.pos)
        elif evento.type == pygame.TEXTINPUT and self.campo_activo:
            self.ruta += evento.text
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.campo_activo = False
            elif self.campo_activo and evento.key == pygame.K_BACKSPACE:
                self.ruta = self.ruta[:-1]
            elif self.campo_activo and evento.key == pygame.K_RETURN:
                self.cargar_archivo()
        return True

    def actualizar_animacion(self):
        if not self.estados_camino or self.indice_animacion >= len(self.estados_camino) - 1:
            return
        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_paso >= 350:
            self.indice_animacion += 1
            self.estado_actual = self.estados_camino[self.indice_animacion]
            self.ultimo_paso = ahora
            if self.indice_animacion == len(self.estados_camino) - 1:
                self.mensaje = "Solución completada."

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                ejecutando = self.manejar_evento(evento) and ejecutando
            self.actualizar_animacion()
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(60)
        pygame.quit()


def main():
    AgroBotApp().ejecutar()


if __name__ == "__main__":
    main()
