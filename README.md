# Escoba

Este proyecto contiene dos versiones del juego de la Escoba para 2 jugadores.

## Descripción

El juego de la Escoba es un tradicional juego de cartas en el que dos jugadores compiten para capturar cartas y sumar puntos. La puntuación se obtiene de dos formas:
- **Escobas:** Cada vez que se captura toda la mesa, se suma 1 punto.
- **Categorías:** Fuera de las escobas, se asigna 1 punto a la categoría (velo, sietes, oros y cartas) al jugador que capture más cartas de esa categoría. En caso de empate, ninguno obtiene puntos en esa categoría.
  - *Velo:* Se cuenta la carta (7, 'O').
  - *Sietes:* Se cuentan todas las cartas de valor 7.
  - *Oros:* Se cuentan todas las cartas de oros.
  - *Cartas:* Se cuentan todas las cartas capturadas.
  
_Nótese que el velo cuenta para las 4 categorías; los sietes que no sean el velo cuentan para sietes y cartas; los oros que no sean el velo cuentan para oros y cartas; el resto de cartas solo cuenta para cartas._

El juego termina cuando no quedan cartas en la mano ni en la baraja. Las cartas restantes en la mesa se asignan al último jugador que capturó.

## Archivos

- **escoba.py**  
  Versión estándar en Python (con comentarios) para uso en PC/WSL.  
  **Notación de cartas:**  
  Se introducen las cartas en el formato `10c`, donde:
  - La cifra (del 1 al 10) indica el valor (8 = sota, 9 = caballo, 10 = rey).
  - La letra indica el palo:  
    - **o** = oros  
    - **c** = copas  
    - **e** = espadas  
    - **b** = bastos

- **escoba_numworks.py**  
  Versión adaptada para la calculadora NUMWORKS (MicroPython). Está optimizada para ocupar el menor espacio posible (sin comentarios, sin líneas en blanco, indentación con 1 espacio) y ajusta la salida a 28 caracteres de ancho.  
  **Notación de cartas:**  
  Se utiliza el formato `valor.palo`, donde:
  - `valor` es un número del 1 al 10 (con la misma lógica: 8 = sota, 9 = caballo, 10 = rey).
  - `palo` es un entero entre 1 y 4, donde:  
    - **1** = oros  
    - **2** = copas  
    - **3** = espadas  
    - **4** = bastos

## Instrucciones de Uso

### Versión Estándar (escoba.py)
1. Ejecuta el archivo con Python 3.
2. Sigue las instrucciones en pantalla:
   - Indica si tienes la mano (responde "S" o "N").
   - Introduce las 4 cartas de la mesa (por ejemplo, `7o,5o,6b,5e`).
   - Introduce tus 3 cartas (por ejemplo, `2c,3e,10b`).
   - Durante el juego se mostrarán sugerencias y se te pedirá elegir la jugada.
3. El juego está diseñado para 2 jugadores.

### Versión NUMWORKS (escoba_numworks.py)
1. Transfiere el archivo a tu calculadora NUMWORKS.
2. Abre el archivo en la calculadora y ejecuta la función `escoba()`.
3. Sigue las instrucciones en pantalla:
   - Introduce las cartas usando el formato `valor.palo` (por ejemplo, `10.1` para 10 de oros).
   - La salida se adapta a 28 caracteres de ancho.
4. El juego está diseñado para 2 jugadores.

## Notas Adicionales

- **Validación de Cartas:**  
  Se evita que se introduzcan cartas ya utilizadas, ya que se eliminan de la baraja conforme se juegan. Por ahora ambas versiones sólo permiten jugar como mano aunque la versión estándar pregunta si eres mano o no al principio.

- **Final del Juego:**  
  El juego finaliza cuando ya no quedan cartas en la mano ni en la baraja. Las cartas restantes en la mesa se asignan al último jugador que capturó, y se muestra un mensaje indicando quién gana la última mano.

- **Cómputo de Puntos:**  
  Además de las escobas, en cada categoría (velo, sietes, oros y cartas) el jugador que capture más cartas se lleva 1 punto; en caso de empate, nadie obtiene puntos en esa categoría. Las escobas suman 1 punto cada una.

