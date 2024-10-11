import pygame
import random
import time

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (192, 192, 192)
DARK_GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Configuración del juego
FILAS = 5
COLUMNAS = 5
MINAS = 5
TAMANO_CELDA = 80

pygame.init()

ANCHO = COLUMNAS * TAMANO_CELDA
ALTO = FILAS * TAMANO_CELDA + 100
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Buscaminas")

# Fuente para los textos (ajustada para pantalla más grande)
fuente = pygame.font.Font(None, 72)
fuente_menu = pygame.font.Font(None, 48)
fuente_pequena = pygame.font.Font(None, 36)

# Estados del juego
MENU = "menu"
JUGANDO = "jugando"
GANADO = "ganado"
PERDIDO = "perdido"


# Función para crear el tablero y colocar minas
def crear_tablero(filas, columnas, minas):
    tablero = [[' ' for _ in range(columnas)] for _ in range(filas)]
    minas_pos = set()

    # Colocar minas aleatoriamente
    while len(minas_pos) < minas:
        fila = random.randint(0, filas - 1)
        columna = random.randint(0, columnas - 1)
        if (fila, columna) not in minas_pos:
            minas_pos.add((fila, columna))

    # Asignar las minas al tablero
    for (fila, columna) in minas_pos:
        tablero[fila][columna] = 'M'

    # Contar las minas adyacentes
    for i in range(filas):
        for j in range(columnas):
            if tablero[i][j] != 'M':
                contador = contar_minas_adyacentes(tablero, i, j)
                if contador > 0:
                    tablero[i][j] = str(contador)

    return tablero, minas_pos


# contar las minas adyacentes
def contar_minas_adyacentes(tablero, fila, columna):
    filas = len(tablero)
    columnas = len(tablero[0])
    minas_cercanas = 0

    for i in range(max(0, fila - 1), min(fila + 2, filas)):
        for j in range(max(0, columna - 1), min(columna + 2, columnas)):
            if tablero[i][j] == 'M':
                minas_cercanas += 1
    return minas_cercanas


# tablero visible para la IA
def crear_tablero_visible(filas, columnas):
    return [['-' for _ in range(columnas)] for _ in range(filas)]


# Dibujar el tablero
def dibujar_tablero(tablero_visible, perdido=False, mina_explotada=None, resultado=None):
    pantalla.fill(WHITE)
    for fila in range(FILAS):
        for columna in range(COLUMNAS):
            rect = pygame.Rect(columna * TAMANO_CELDA, fila * TAMANO_CELDA, TAMANO_CELDA, TAMANO_CELDA)
            pygame.draw.rect(pantalla, GRAY if tablero_visible[fila][columna] == '-' else DARK_GRAY, rect)
            pygame.draw.rect(pantalla, BLACK, rect, 2)

            celda = tablero_visible[fila][columna]
            if celda == 'F':
                pygame.draw.circle(pantalla, RED, rect.center, 25)
            elif celda.isdigit():
                texto = fuente_pequena.render(celda, True, BLACK)
                pantalla.blit(texto, texto.get_rect(center=rect.center))
            elif perdido and mina_explotada == (fila, columna):
                pygame.draw.circle(pantalla, BLACK, rect.center, 25)

    if resultado == GANADO:
        mostrar_texto("¡Victoria!", GREEN)
    elif resultado == PERDIDO:
        mostrar_texto("¡Derrota!", RED)

    pygame.display.update()


# obtener celdas adyacentes
def obtener_celdas_adyacentes(tablero, fila, columna):
    filas = len(tablero)
    columnas = len(tablero[0])
    adyacentes = []

    for i in range(max(0, fila - 1), min(fila + 2, filas)):
        for j in range(max(0, columna - 1), min(columna + 2, columnas)):
            if (i, j) != (fila, columna):
                adyacentes.append((i, j))
    return adyacentes


def jugar_busca_minas_ia(tablero, filas, columnas):
    tablero_visible = crear_tablero_visible(filas, columnas)
    celdas_restantes = filas * columnas
    minas_marcadas = set()

    # celda aleatoria al comienzo
    fila, columna = random.randint(0, filas - 1), random.randint(0, columnas - 1)

    while celdas_restantes > 0:
        # lose
        if tablero[fila][columna] == 'M':
            tablero_visible[fila][columna] = 'M'
            dibujar_tablero(tablero_visible, perdido=True, mina_explotada=(fila, columna), resultado=PERDIDO)
            return PERDIDO, (fila, columna)

        # Revelar la celda
        if tablero_visible[fila][columna] == '-':
            tablero_visible[fila][columna] = tablero[fila][columna]
            celdas_restantes -= 1

        # verificar y marcar minas si es necesario
        if tablero[fila][columna] != ' ':
            numero = int(tablero[fila][columna])
            celdas_adyacentes = obtener_celdas_adyacentes(tablero, fila, columna)
            celdas_no_reveladas = [(f, c) for (f, c) in celdas_adyacentes if tablero_visible[f][c] == '-']
            if len(celdas_no_reveladas) == numero:
                # Marcar las minas adyacentes
                for f, c in celdas_no_reveladas:
                    tablero_visible[f][c] = 'F'
                    minas_marcadas.add((f, c))
                    celdas_restantes -= 1

        # Dibujar el progreso del juego
        dibujar_tablero(tablero_visible)
        time.sleep(0.5)

        # Escoger una nueva celda
        fila, columna = random.choice(obtener_celdas_adyacentes(tablero, fila, columna))

    return GANADO if celdas_restantes == 0 else JUGANDO, None


# texto la pantalla
def mostrar_texto(texto, color=BLACK):
    texto_render = fuente.render(texto, True, color)
    rect_texto = texto_render.get_rect(
        center=(ANCHO // 2, ALTO - 50))  # Ajustado para que se vea bien al final del tablero
    pantalla.blit(texto_render, rect_texto)
    pygame.display.update()


# manejar el menú
def menu():
    pantalla.fill(WHITE)
    mostrar_texto_menu("ENTER para comenzar", "ESC para salir")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                if event.key == pygame.K_ESCAPE:
                    return False


# texto del menú
def mostrar_texto_menu(linea1, linea2, color=BLACK):
    pantalla.fill(WHITE)
    texto_render1 = fuente_menu.render(linea1, True, color)
    rect_texto1 = texto_render1.get_rect(center=(ANCHO // 2, ALTO // 2 - 40))
    pantalla.blit(texto_render1, rect_texto1)

    texto_render2 = fuente_menu.render(linea2, True, color)
    rect_texto2 = texto_render2.get_rect(center=(ANCHO // 2, ALTO // 2 + 40))
    pantalla.blit(texto_render2, rect_texto2)

    pygame.display.update()


# Función principal del juego
def main():
    estado = MENU
    tablero, minas_pos = None, None

    while True:
        if estado == MENU:
            if not menu():
                break
            tablero, minas_pos = crear_tablero(FILAS, COLUMNAS, MINAS)
            estado = JUGANDO

        elif estado == JUGANDO:
            resultado, pos = jugar_busca_minas_ia(tablero, FILAS, COLUMNAS)

            if resultado == GANADO:
                mostrar_texto("¡Victoria!", GREEN)
                time.sleep(3)
                estado = MENU

            elif resultado == PERDIDO:
                mostrar_texto("¡Derrota!", RED)
                time.sleep(3)
                estado = MENU

        # eventos del juego
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return


main()
pygame.quit()
