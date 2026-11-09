import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame
from pygame._sdl2 import Window

from busquedas import (
    amplitud,
    busqueda_a_estrella,
    busqueda_avara,
    costo_uniforme,
    preferente_por_profundidad_pila,
)
from mundo import cargar_mundo, extraer_info
from nucleo import crear_estado_inicial, crear_info
from reporte import generar_reporte


ANCHO = 1600
ALTO = 1040
ESCALA_VENTANA = 0.94
ANCHO_VENTANA = round(ANCHO * ESCALA_VENTANA)
ALTO_VENTANA = round(ALTO * ESCALA_VENTANA)
TAM_CASILLA = 78
ORIGEN_TABLERO = (48, 180)
PANEL_X = 880
PANEL_Y = 150
PANEL_ANCHO = 672
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

FONDO = (23, 39, 34)
FONDO_PANEL = (34, 55, 46)
TARJETA = (44, 69, 55)
TARJETA_CLARA = (53, 81, 62)
TEXTO = (242, 232, 198)
SECUNDARIO = (180, 195, 159)
VERDE = (127, 190, 105)
VERDE_CLARO = (207, 226, 151)
DORADO = (238, 187, 91)
BORDE = (96, 129, 83)
OBSTACULO = (38, 51, 43)
TIERRA = (107, 133, 83)
ROJO = (220, 111, 73)

ASSETS = {
    "tierra_seca": "Parched_Pixel_Garden_Tile-removebg-preview.png",
    "cultivo_tratado": "Pixel-Art_Garden_Plot-removebg-preview.png",
    "avioneta": "avioneta-removebg-preview.png",
    "fertilizante": "fertilizante.png",
    "robot": "robot_transparente(1).png",
}


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
        pygame.display.set_caption("AgroBot ")
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        self.ventana_sdl = Window.from_display_module()
        self.arrastrando_ventana = False
        self.pantalla = pygame.Surface((ANCHO, ALTO))
        self.reloj = pygame.time.Clock()
        self.fuente = pygame.font.SysFont("dejavusansmono", 20, bold=True)
        self.fuente_pequena = pygame.font.SysFont("dejavusansmono", 16)
        self.fuente_titulo = pygame.font.SysFont("dejavusansmono", 36, bold=True)
        self.fuente_casilla = pygame.font.SysFont("dejavusansmono", 17, bold=True)

        self.sprites = self.cargar_sprites()
        self.ruta = os.path.join(os.path.dirname(__file__), "Prueba1.txt")
        self.campo_activo = False
        self.cursor_ruta = len(self.ruta)
        self.ancla_seleccion = None
        self.portapapeles_inicializado = False
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
        self.reporte = None
        self.mensaje = "Selecciona un archivo de mundo para comenzar."
        self.error = False

        if os.path.isfile(self.ruta):
            self.cargar_archivo()

    def cargar_sprites(self):
        carpeta = os.path.join(os.path.dirname(__file__), "images")
        sprites = {}
        for nombre, archivo in ASSETS.items():
            ruta_sprite = os.path.join(carpeta, archivo)
            if not os.path.isfile(ruta_sprite):
                raise FileNotFoundError(f"No se encontró el recurso gráfico requerido: {ruta_sprite}")
            sprites[nombre] = pygame.image.load(ruta_sprite).convert_alpha()
        return sprites

    def sprite_ajustado(self, nombre, ancho, alto):
        imagen = self.sprites[nombre]
        escala = min(ancho / imagen.get_width(), alto / imagen.get_height())
        tamano = (
            max(1, round(imagen.get_width() * escala)),
            max(1, round(imagen.get_height() * escala)),
        )
        return pygame.transform.scale(imagen, tamano)

    def cargar_archivo(self):
        try:
            mundo = cargar_mundo(self.ruta)
            validar_mundo(mundo)
        except (OSError, UnicodeError, ValueError) as error:
            self.mundo = None
            self.info = None
            self.estado_inicial = None
            self.estado_actual = None
            self.estados_camino = []
            self.resultado = None
            self.reporte = None
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
        self.reporte = None
        self.mensaje = f"Mundo cargado: {len(cultivos)} cultivos secos."
        self.error = False

    def ejecutar_busqueda(self):
        if self.mundo is None or self.estado_inicial is None:
            self.mensaje = "Primero carga un archivo de mundo válido."
            self.error = True
            return

        self.reporte = None
        self.resultado = None
        self.estados_camino = []
        funcion = FUNCIONES_BUSQUEDA[self.algoritmo]
        self.mensaje = f"Ejecutando {NOMBRES_ALGORITMOS[self.algoritmo]}..."
        self.dibujar()
        self.presentar()

        resultado = funcion(self.estado_inicial, self.mundo, self.info)
        self.resultado = resultado
        self.estado_actual = self.estado_inicial
        self.indice_animacion = 0

        if resultado is None:
            self.mensaje = "No se encontró una solución para este mundo."
            self.error = True
            return

        self.estados_camino = resultado["estados"]
        self.mensaje = f"Solución encontrada: {len(resultado['operadores'])} movimientos. Animando..."
        self.error = False
        self.ultimo_paso = pygame.time.get_ticks()
        if len(self.estados_camino) <= 1:
            self.finalizar_animacion()

    def rectangulo_boton(self, nombre):
        rectangulos = {
            "salir": pygame.Rect(ANCHO - 80, 24, 52, 52),
            "cargar": pygame.Rect(PANEL_X + 452, 206, 192, 52),
            "no_informada": pygame.Rect(PANEL_X + 30, 308, 278, 52),
            "informada": pygame.Rect(PANEL_X + 322, 308, 314, 52),
            "ejecutar": pygame.Rect(PANEL_X + 30, 548, 614, 58),
            "reiniciar": pygame.Rect(PANEL_X + 30, 622, 296, 50),
            "reanudar": pygame.Rect(PANEL_X + 344, 622, 300, 50),
        }
        return rectangulos[nombre]

    def dibujar_panel(self, rect):
        pygame.draw.rect(self.pantalla, FONDO_PANEL, rect)
        pygame.draw.rect(self.pantalla, BORDE, rect, 3)
        pygame.draw.rect(self.pantalla, DORADO, rect.inflate(-10, -10), 1)

    def texto(self, contenido, posicion, color=TEXTO, fuente=None):
        superficie = (fuente or self.fuente).render(str(contenido), True, color)
        self.pantalla.blit(superficie, posicion)

    def texto_centrado(self, contenido, color, centro, fuente=None):
        superficie = (fuente or self.fuente).render(str(contenido), True, color)
        self.pantalla.blit(superficie, superficie.get_rect(center=centro))

    def dibujar_boton(self, nombre, etiqueta, activo=False, deshabilitado=False):
        rect = self.rectangulo_boton(nombre)
        if deshabilitado:
            color, color_texto = TARJETA, SECUNDARIO
        elif activo:
            color, color_texto = VERDE, FONDO
        else:
            color, color_texto = TARJETA_CLARA, TEXTO
        pygame.draw.rect(self.pantalla, color, rect)
        pygame.draw.rect(self.pantalla, BORDE if not activo else DORADO, rect, 3)
        self.texto_centrado(etiqueta, color_texto, rect.center, self.fuente_pequena)

    def dibujar_encabezado(self):
        pygame.draw.rect(self.pantalla, FONDO_PANEL, (0, 0, ANCHO, 128))
        pygame.draw.line(self.pantalla, BORDE, (0, 127), (ANCHO, 127), 4)
        self.texto("AGROBOT", (48, 24), VERDE_CLARO, self.fuente_titulo)
        self.texto("", (52, 76), DORADO, self.fuente_pequena)
        self.texto("", (PANEL_X, 54), SECUNDARIO, self.fuente_pequena)
        boton_salir = self.rectangulo_boton("salir")
        pygame.draw.rect(self.pantalla, TARJETA_CLARA, boton_salir)
        pygame.draw.rect(self.pantalla, BORDE, boton_salir, 2)
        margen = 18
        pygame.draw.line(
            self.pantalla,
            TEXTO,
            (boton_salir.x + margen, boton_salir.y + margen),
            (boton_salir.right - margen, boton_salir.bottom - margen),
            3,
        )
        pygame.draw.line(
            self.pantalla,
            TEXTO,
            (boton_salir.right - margen, boton_salir.y + margen),
            (boton_salir.x + margen, boton_salir.bottom - margen),
            3,
        )
        for x in range(795, 847, 12):
            pygame.draw.rect(self.pantalla, DORADO, (x, 43, 6, 6))
            pygame.draw.rect(self.pantalla, VERDE, (x, 57, 6, 6))

    def dibujar_tablero(self):
        x0, y0 = ORIGEN_TABLERO
        tablero = pygame.Rect(x0 - 12, y0 - 12, 10 * TAM_CASILLA + 24, 10 * TAM_CASILLA + 24)
        pygame.draw.rect(self.pantalla, (30, 49, 39), tablero)
        pygame.draw.rect(self.pantalla, BORDE, tablero, 4)
        if self.mundo is None or self.estado_actual is None:
            self.texto_centrado("CARGA UN MAPA PARA INICIAR", SECUNDARIO, tablero.center, self.fuente)
            return

        cultivos_pendientes = self.estado_actual.cultivos
        for fila in range(10):
            for columna in range(10):
                valor = self.mundo[fila][columna]
                rect = pygame.Rect(x0 + columna * TAM_CASILLA, y0 + fila * TAM_CASILLA, TAM_CASILLA, TAM_CASILLA)
                posicion = (fila, columna)
                pygame.draw.rect(self.pantalla, TIERRA if valor != 1 else OBSTACULO, rect)

                if valor == 1:
                    pygame.draw.rect(self.pantalla, (61, 77, 60), rect.inflate(-12, -12))
                    pygame.draw.rect(self.pantalla, BORDE, (rect.x + 14, rect.y + 14, 8, 8))
                    pygame.draw.rect(self.pantalla, BORDE, (rect.right - 23, rect.bottom - 22, 8, 8))
                elif valor == 3:
                    sprite = "tierra_seca" if posicion in cultivos_pendientes else "cultivo_tratado"
                    imagen = self.sprite_ajustado(sprite, TAM_CASILLA - 2, TAM_CASILLA - 2)
                    self.pantalla.blit(imagen, imagen.get_rect(center=rect.center))
                    if posicion in cultivos_pendientes:
                        pygame.draw.rect(self.pantalla, DORADO, rect, 2)
                elif valor == 4:
                    self.dibujar_objeto("fertilizante", rect, TAM_CASILLA - 10)
                    pygame.draw.rect(self.pantalla, VERDE_CLARO, rect, 2)
                elif valor == 5:
                    self.dibujar_objeto("avioneta", rect, TAM_CASILLA - 8)
                    pygame.draw.rect(self.pantalla, DORADO, rect, 2)

                pygame.draw.rect(self.pantalla, (30, 49, 39), rect, 2)

        fila, columna = self.estado_actual.pos
        rect_robot = pygame.Rect(
            x0 + columna * TAM_CASILLA,
            y0 + fila * TAM_CASILLA,
            TAM_CASILLA,
            TAM_CASILLA,
        )
        self.dibujar_objeto("robot", rect_robot, TAM_CASILLA - 8)
        pygame.draw.rect(self.pantalla, ROJO, rect_robot, 3)

    def dibujar_objeto(self, nombre, rect, tamano):
        imagen = self.sprite_ajustado(nombre, tamano, tamano)
        self.pantalla.blit(imagen, imagen.get_rect(center=rect.center))

    def dibujar_panel_archivo(self):
        self.texto("ARCHIVO DEL MUNDO", (PANEL_X + 30, 172), SECUNDARIO, self.fuente_pequena)
        campo = pygame.Rect(PANEL_X + 30, 202, 404, 58)
        pygame.draw.rect(self.pantalla, TARJETA, campo)
        pygame.draw.rect(self.pantalla, DORADO if self.campo_activo else BORDE, campo, 3)
        ancho_texto = campo.width - 24
        inicio = self.cursor_ruta
        while inicio > 0 and self.fuente_pequena.size(self.ruta[inicio - 1:self.cursor_ruta])[0] <= ancho_texto:
            inicio -= 1
        fin = self.cursor_ruta
        while fin < len(self.ruta) and self.fuente_pequena.size(self.ruta[inicio:fin + 1])[0] <= ancho_texto:
            fin += 1

        texto_visible = self.ruta[inicio:fin]
        posicion_texto = (campo.x + 12, campo.y + 19)
        rect_anterior = self.pantalla.get_clip()
        self.pantalla.set_clip(campo)
        self.pantalla.blit(
            self.fuente_pequena.render(texto_visible, True, TEXTO),
            posicion_texto,
        )

        seleccion = self.rango_seleccionado()
        if seleccion is not None:
            inicio_seleccion = max(seleccion[0], inicio)
            fin_seleccion = min(seleccion[1], fin)
            if inicio_seleccion < fin_seleccion:
                prefijo = self.fuente_pequena.size(self.ruta[inicio:inicio_seleccion])[0]
                seleccionado = self.ruta[inicio_seleccion:fin_seleccion]
                ancho_seleccion = self.fuente_pequena.size(seleccionado)[0]
                pygame.draw.rect(
                    self.pantalla,
                    VERDE,
                    (posicion_texto[0] + prefijo, campo.y + 15, ancho_seleccion, 27),
                )
                texto_seleccionado = self.fuente_pequena.render(seleccionado, True, FONDO)
                self.pantalla.blit(
                    texto_seleccionado,
                    (posicion_texto[0] + prefijo, posicion_texto[1]),
                )
        elif self.campo_activo:
            ancho_cursor = self.fuente_pequena.size(self.ruta[inicio:self.cursor_ruta])[0]
            x_cursor = posicion_texto[0] + ancho_cursor
            pygame.draw.line(
                self.pantalla,
                TEXTO,
                (x_cursor, campo.y + 16),
                (x_cursor, campo.bottom - 16),
                2,
            )
        self.pantalla.set_clip(rect_anterior)
        self.dibujar_boton("cargar", "CARGAR MAPA")

    def dibujar_seleccion(self):
        self.texto("TIPO DE BÚSQUEDA", (PANEL_X + 30, 280), SECUNDARIO, self.fuente_pequena)
        self.dibujar_boton("no_informada", "NO INFORMADA", self.categoria == "no_informada")
        self.dibujar_boton("informada", "INFORMADA", self.categoria == "informada")
        self.texto("ALGORITMO", (PANEL_X + 30, 382), SECUNDARIO, self.fuente_pequena)

        y = 410
        for codigo, nombre in ALGORITMOS[self.categoria]:
            rect = pygame.Rect(PANEL_X + 30, y, 614, 42)
            activo = self.algoritmo == codigo
            pygame.draw.rect(self.pantalla, TARJETA_CLARA if activo else TARJETA, rect)
            pygame.draw.rect(self.pantalla, DORADO if activo else BORDE, rect, 2)
            pygame.draw.rect(self.pantalla, VERDE if activo else BORDE, (rect.x + 14, rect.y + 13, 16, 16), 2)
            if activo:
                pygame.draw.rect(self.pantalla, VERDE_CLARO, (rect.x + 18, rect.y + 17, 8, 8))
            self.texto(nombre.upper(), (rect.x + 48, rect.y + 11), TEXTO, self.fuente_pequena)
            y += 46

        self.dibujar_boton("ejecutar", "INICIAR BÚSQUEDA", activo=True, deshabilitado=self.mundo is None)
        self.dibujar_boton("reiniciar", "REINICIAR ANIMACIÓN", deshabilitado=not self.estados_camino)
        self.dibujar_boton("reanudar", "VER SOLUCIÓN", deshabilitado=not self.estados_camino)

    def dibujar_estado(self):
        rect = pygame.Rect(PANEL_X + 30, 692, 614, 104)
        self.dibujar_panel(rect)
        self.texto("TELEMETRÍA", (rect.x + 16, rect.y + 12), DORADO, self.fuente_pequena)
        if self.estado_actual is not None:
            self.dibujar_objeto("fertilizante", pygame.Rect(rect.x + 22, rect.y + 40, 30, 30), 27)
            self.texto(f"{self.estado_actual.fertilizante}/2", (rect.x + 58, rect.y + 45), TEXTO, self.fuente_pequena)
            self.texto(f"COMBUSTIBLE {max(0, self.estado_actual.combustible)}", (rect.x + 150, rect.y + 45), TEXTO, self.fuente_pequena)
            self.texto(f"SEQUÍA {len(self.estado_actual.cultivos)}", (rect.x + 405, rect.y + 45), TEXTO, self.fuente_pequena)
        color_mensaje = ROJO if self.error else SECUNDARIO
        lineas = self.dividir_texto(self.mensaje, self.fuente_pequena, rect.width - 32)
        for indice, linea in enumerate(lineas[:2]):
            self.texto(linea, (rect.x + 16, rect.y + 72 + indice * 19), color_mensaje, self.fuente_pequena)

    def dibujar_reporte(self):
        rect = pygame.Rect(PANEL_X + 30, 808, 614, 210)
        self.dibujar_panel(rect)
        self.texto("REPORTE DE BÚSQUEDA", (rect.x + 16, rect.y + 15), DORADO, self.fuente)
        pygame.draw.line(self.pantalla, BORDE, (rect.x + 16, rect.y + 48), (rect.right - 16, rect.y + 48), 2)
        if self.reporte is None:
            return

        lineas = self.reporte.splitlines()
        for indice, linea in enumerate(lineas):
            self.texto(linea, (rect.x + 18, rect.y + 65 + indice * 30), TEXTO, self.fuente_pequena)

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
        y = 1004
        elementos = [
            ("ROBOT", ROJO),
            ("CULTIVO SECO", DORADO),
            ("CULTIVO TRATADO", VERDE),
            ("DEPÓSITO", VERDE_CLARO),
            ("AVIONETA", (130, 190, 224)),
        ]
        x = 52
        for etiqueta, color in elementos:
            pygame.draw.rect(self.pantalla, color, (x, y + 3, 14, 14))
            self.texto(etiqueta, (x + 24, y), SECUNDARIO, self.fuente_pequena)
            x += 160 if etiqueta != "CULTIVO TRATADO" else 205

    def dibujar(self):
        self.pantalla.fill(FONDO)
        self.dibujar_encabezado()
        self.texto("TERRENO  //  10 × 10", (48, 145), DORADO, self.fuente_pequena)
        self.dibujar_tablero()
        self.dibujar_panel(pygame.Rect(PANEL_X, PANEL_Y, PANEL_ANCHO, 880))
        self.dibujar_panel_archivo()
        self.dibujar_seleccion()
        self.dibujar_estado()
        self.dibujar_reporte()
        self.dibujar_leyenda()

    def presentar(self):
        pygame.transform.scale(self.pantalla, (ANCHO_VENTANA, ALTO_VENTANA), self.ventana)
        pygame.display.flip()

    def manejar_clic(self, posicion):
        campo = pygame.Rect(PANEL_X + 30, 202, 404, 58)
        self.campo_activo = campo.collidepoint(posicion)
        if self.campo_activo:
            self.cursor_ruta = self.cursor_desde_posicion(posicion, campo)
            self.ancla_seleccion = None
            pygame.key.start_text_input()
            pygame.key.set_repeat(400, 40)
        else:
            self.ancla_seleccion = None
            pygame.key.stop_text_input()
            pygame.key.set_repeat()

        if self.rectangulo_boton("cargar").collidepoint(posicion):
            self.cargar_archivo()
            return
        if self.rectangulo_boton("no_informada").collidepoint(posicion):
            self.categoria = "no_informada"
            self.algoritmo = "amplitud"
            self.reporte = None
            return
        if self.rectangulo_boton("informada").collidepoint(posicion):
            self.categoria = "informada"
            self.algoritmo = "avara"
            self.reporte = None
            return

        y = 410
        for codigo, _ in ALGORITMOS[self.categoria]:
            if pygame.Rect(PANEL_X + 30, y, 614, 42).collidepoint(posicion):
                self.algoritmo = codigo
                self.reporte = None
                return
            y += 46

        if self.rectangulo_boton("ejecutar").collidepoint(posicion) and self.mundo is not None:
            self.ejecutar_busqueda()
        elif self.rectangulo_boton("reiniciar").collidepoint(posicion) and self.estados_camino:
            self.indice_animacion = 0
            self.estado_actual = self.estados_camino[0]
            self.ultimo_paso = pygame.time.get_ticks()
            self.reporte = None
            self.mensaje = "Reproduciendo la solución desde el inicio."
            self.error = False
        elif self.rectangulo_boton("reanudar").collidepoint(posicion) and self.estados_camino:
            self.indice_animacion = len(self.estados_camino) - 1
            self.estado_actual = self.estados_camino[-1]
            self.finalizar_animacion()

    def rango_seleccionado(self):
        if self.ancla_seleccion is None or self.ancla_seleccion == self.cursor_ruta:
            return None
        return (
            min(self.ancla_seleccion, self.cursor_ruta),
            max(self.ancla_seleccion, self.cursor_ruta),
        )

    def cursor_desde_posicion(self, posicion, campo):
        ancho_texto = campo.width - 24
        inicio = self.cursor_ruta
        while inicio > 0 and self.fuente_pequena.size(self.ruta[inicio - 1:self.cursor_ruta])[0] <= ancho_texto:
            inicio -= 1
        fin = self.cursor_ruta
        while fin < len(self.ruta) and self.fuente_pequena.size(self.ruta[inicio:fin + 1])[0] <= ancho_texto:
            fin += 1

        x_relativo = max(0, posicion[0] - (campo.x + 12))
        indice = inicio
        while indice < fin:
            ancho_siguiente = self.fuente_pequena.size(self.ruta[inicio:indice + 1])[0]
            ancho_actual = self.fuente_pequena.size(self.ruta[inicio:indice])[0]
            if x_relativo < (ancho_actual + ancho_siguiente) / 2:
                break
            indice += 1
        return indice

    def reemplazar_seleccion(self, texto):
        seleccion = self.rango_seleccionado()
        if seleccion is None:
            inicio = fin = self.cursor_ruta
        else:
            inicio, fin = seleccion
        self.ruta = self.ruta[:inicio] + texto + self.ruta[fin:]
        self.cursor_ruta = inicio + len(texto)
        self.ancla_seleccion = None

    def mover_cursor(self, nueva_posicion, extender=False):
        if extender:
            if self.ancla_seleccion is None:
                self.ancla_seleccion = self.cursor_ruta
        else:
            self.ancla_seleccion = None
        self.cursor_ruta = max(0, min(len(self.ruta), nueva_posicion))

    def inicializar_portapapeles(self):
        if not self.portapapeles_inicializado:
            pygame.scrap.init()
            self.portapapeles_inicializado = True

    def copiar_seleccion(self, eliminar=False):
        seleccion = self.rango_seleccionado()
        if seleccion is None:
            return
        try:
            self.inicializar_portapapeles()
            texto = self.ruta[seleccion[0]:seleccion[1]]
            pygame.scrap.put(pygame.SCRAP_TEXT, texto.encode("utf-8"))
        except pygame.error as error:
            self.mensaje = f"No se pudo acceder al portapapeles: {error}"
            self.error = True
            return
        if eliminar:
            self.reemplazar_seleccion("")

    def pegar_portapapeles(self):
        try:
            self.inicializar_portapapeles()
            contenido = pygame.scrap.get(pygame.SCRAP_TEXT)
        except pygame.error as error:
            self.mensaje = f"No se pudo acceder al portapapeles: {error}"
            self.error = True
            return
        if contenido:
            texto = contenido.decode("utf-8", errors="replace").rstrip("\x00")
            self.reemplazar_seleccion(texto)

    def manejar_evento(self, evento):
        if evento.type == pygame.QUIT:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            posicion_logica = (
                round(evento.pos[0] * ANCHO / ANCHO_VENTANA),
                round(evento.pos[1] * ALTO / ALTO_VENTANA),
            )
            if self.rectangulo_boton("salir").collidepoint(posicion_logica):
                return False
            self.arrastrando_ventana = posicion_logica[1] < 128
            self.manejar_clic(posicion_logica)
        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            self.arrastrando_ventana = False
        elif evento.type == pygame.MOUSEMOTION and self.arrastrando_ventana:
            x, y = self.ventana_sdl.position
            self.ventana_sdl.position = (x + evento.rel[0], y + evento.rel[1])
        elif evento.type == pygame.TEXTINPUT and self.campo_activo:
            self.reemplazar_seleccion(evento.text)
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.campo_activo = False
                self.ancla_seleccion = None
                pygame.key.stop_text_input()
                pygame.key.set_repeat()
            elif self.campo_activo:
                control = evento.mod & pygame.KMOD_CTRL
                shift = evento.mod & pygame.KMOD_SHIFT
                if control and evento.key == pygame.K_a:
                    self.ancla_seleccion = 0
                    self.cursor_ruta = len(self.ruta)
                elif control and evento.key == pygame.K_c:
                    self.copiar_seleccion()
                elif control and evento.key == pygame.K_x:
                    self.copiar_seleccion(eliminar=True)
                elif control and evento.key == pygame.K_v:
                    self.pegar_portapapeles()
                elif evento.key == pygame.K_BACKSPACE:
                    if self.rango_seleccionado() is not None:
                        self.reemplazar_seleccion("")
                    elif self.cursor_ruta > 0:
                        self.ancla_seleccion = self.cursor_ruta - 1
                        self.reemplazar_seleccion("")
                elif evento.key == pygame.K_DELETE:
                    if self.rango_seleccionado() is not None:
                        self.reemplazar_seleccion("")
                    elif self.cursor_ruta < len(self.ruta):
                        self.ancla_seleccion = self.cursor_ruta + 1
                        self.reemplazar_seleccion("")
                elif evento.key == pygame.K_LEFT:
                    seleccion = self.rango_seleccionado()
                    if seleccion is not None and not shift:
                        self.cursor_ruta = seleccion[0]
                        self.ancla_seleccion = None
                    else:
                        self.mover_cursor(self.cursor_ruta - 1, shift)
                elif evento.key == pygame.K_RIGHT:
                    seleccion = self.rango_seleccionado()
                    if seleccion is not None and not shift:
                        self.cursor_ruta = seleccion[1]
                        self.ancla_seleccion = None
                    else:
                        self.mover_cursor(self.cursor_ruta + 1, shift)
                elif evento.key == pygame.K_HOME:
                    self.mover_cursor(0, shift)
                elif evento.key == pygame.K_END:
                    self.mover_cursor(len(self.ruta), shift)
                elif evento.key == pygame.K_RETURN:
                    self.cargar_archivo()
        return True

    def finalizar_animacion(self):
        if self.resultado is not None:
            self.reporte = generar_reporte(NOMBRES_ALGORITMOS[self.algoritmo], self.resultado)
            self.mensaje = "Solución completada."
            self.error = False

    def actualizar_animacion(self):
        if not self.estados_camino:
            return
        if self.indice_animacion >= len(self.estados_camino) - 1:
            if self.reporte is None and self.resultado is not None:
                self.finalizar_animacion()
            return

        ahora = pygame.time.get_ticks()
        if ahora - self.ultimo_paso >= 350:
            self.indice_animacion += 1
            self.estado_actual = self.estados_camino[self.indice_animacion]
            self.ultimo_paso = ahora
            if self.indice_animacion == len(self.estados_camino) - 1:
                self.finalizar_animacion()

    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                ejecutando = self.manejar_evento(evento) and ejecutando
            self.actualizar_animacion()
            self.dibujar()
            self.presentar()
            self.reloj.tick(60)
        pygame.quit()


def main():
    AgroBotApp().ejecutar()


if __name__ == "__main__":
    main()
