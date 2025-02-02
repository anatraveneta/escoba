# -*- coding: utf-8 -*-
"""
Programa Escoba
Con validación de jugadas, sugerencia de la mejor jugada contra el oponente
(incluyendo razonamiento a 1 jugada, la respuesta del oponente, la elección interactiva
de captura para el usuario cuando el oponente renuncia a capturar) y desglose final de la puntuación.

Cada carta aporta:
  - 1/21 por carta (hasta 21),
  - 1/3 por carta con valor 7 (hasta 3),
  - 1/6 por carta de oros (hasta 6),
  - y, si es 7 de oros (velo), 1 adicional.
"""

# ===============================
# Funciones de manejo de cartas
# ===============================
def parsear_carta(carta_str):
    """
    Parsea una cadena con formato <valor><palo> y devuelve (valor, palo)
    o None si el formato es erróneo.
    """
    carta_str = carta_str.strip()
    if len(carta_str) < 2:
        return None
    valor_str = carta_str[:-1]
    palo = carta_str[-1].upper()
    if palo not in ('O', 'C', 'E', 'B'):
        return None
    try:
        valor = int(valor_str)
    except:
        return None
    if not (1 <= valor <= 10):
        return None
    return (valor, palo)

def leer_cartas(mensaje, cantidad, allowed=None):
    """
    Solicita al usuario 'cantidad' de cartas separadas por comas y las valida.
    Si se proporciona el parámetro 'allowed', se verificará que cada carta
    ingresada se encuentre en esa lista.
    """
    while True:
        entrada = input(mensaje)
        partes = [p.strip() for p in entrada.split(',')]
        if len(partes) != cantidad:
            print(f"Error: Debes introducir {cantidad} cartas separadas por comas.")
            continue
        cartas = []
        valido = True
        for p in partes:
            carta = parsear_carta(p)
            if carta is None:
                print(f"La carta '{p}' no es válida.")
                valido = False
                break
            if allowed is not None and carta not in allowed:
                print(f"La carta {carta} no está disponible (ya se usó o no está en la baraja).")
                valido = False
                break
            cartas.append(carta)
        if valido:
            return cartas

# ===================================
# Funciones para el juego y el estado
# ===================================
def inicializar_baraja():
    """ Inicializa la baraja española de 40 cartas. """
    return [(valor, palo) for palo in ('O', 'C', 'E', 'B') for valor in range(1, 11)]

def remover_cartas(baraja, cartas_a_remover):
    """ Devuelve una copia de la baraja sin las cartas indicadas. """
    nueva = baraja.copy()
    for c in cartas_a_remover:
        if c in nueva:
            nueva.remove(c)
    return nueva

# ====================================
# Funciones para la evaluación y sugerencia
# ====================================
def puntos_cartas(cartas, escobas=0):
    """
    Calcula el puntaje de las cartas aplicando las reglas de puntuación.
    """
    total_cartas = len(cartas)
    pts_cartas = min(total_cartas, 21) / 21
    pts_velo = sum(1 for c in cartas if c == (7, 'O'))
    pts_sietes = min(sum(1 for c in cartas if c[0] == 7 and c[1] != 'O'), 3) * (1/3)
    pts_oros = min(sum(1 for c in cartas if c[1] == 'O' and c != (7, 'O')), 6) * (1/6)
    return pts_cartas + pts_velo + pts_sietes + pts_oros + escobas

def detalle_puntuacion(cartas, escobas):
    """
    Calcula el desglose de la puntuación.
    """
    return {
        "cartas": min(len(cartas), 21) / 21,
        "velo": sum(1 for c in cartas if c == (7, 'O')),
        "sietes": min(sum(1 for c in cartas if c[0] == 7 and c[1] != 'O'), 3) * (1/3),
        "oros": min(sum(1 for c in cartas if c[1] == 'O' and c != (7, 'O')), 6) * (1/6),
        "escobas": escobas,
        "total": puntos_cartas(cartas, escobas)
    }

def combinaciones_que_suman(cartas, objetivo):
    """
    Retorna una lista de combinaciones (listas) de cartas de 'cartas'
    cuya suma de valores es igual a 'objetivo'.
    """
    resultados = []
    def backtrack(start, current, suma):
        if suma == objetivo:
            resultados.append(current.copy())
        elif suma > objetivo:
            return
        else:
            for i in range(start, len(cartas)):
                current.append(cartas[i])
                backtrack(i+1, current, suma + cartas[i][0])
                current.pop()
    backtrack(0, [], 0)
    return resultados

def evaluar_movida(card, mesa, deck, movida):
    """
    Evalúa una movida para una carta dada.
    'movida' es una tupla (tipo, combinación) donde tipo es "captura" o "no captura".
    Retorna (neto, puntos_jugador, expectativa_oponente, new_mesa)
    
    - En una jugada de captura se asume que se capturan las cartas indicadas y, si la mesa queda vacía,
      se suma la bonificación de escoba.
    - En una jugada de no captura, la carta se coloca sobre la mesa sin obtener puntos inmediatos.
    """
    if movida[0] == "captura":
        combo = movida[1]
        new_mesa = [c for c in mesa if c not in combo]
        puntos_jugador = puntos_cartas(combo + [card], 1 if len(new_mesa) == 0 else 0)
    else:
        new_mesa = mesa + [card]
        puntos_jugador = 0
    total_oponente = 0
    if deck:
        for op_card in deck:
            target = 15 - op_card[0]
            combos = combinaciones_que_suman(new_mesa, target)
            mejor = 0
            for combo in combos:
                new_mesa_op = [c for c in new_mesa if c not in combo]
                pts = puntos_cartas(combo + [op_card], 1 if len(new_mesa_op) == 0 else 0)
                if pts > mejor:
                    mejor = pts
            total_oponente += mejor
        expectativa_oponente = total_oponente / len(deck)
    else:
        expectativa_oponente = 0
    neto = puntos_jugador - expectativa_oponente
    return neto, puntos_jugador, expectativa_oponente, new_mesa

def sugerir_mejor_jugada(estado):
    """
    Sugiere la mejor jugada para el usuario evaluando, para cada carta en mano,
    únicamente las jugadas de captura (si existen) y, en caso de que no exista captura,
    la opción de no capturar.
    
    Se numeran las opciones y se permite elegir la estrategia mediante su número,
    con la opción por defecto (al pulsar Enter) siendo la de mayor valor neto.
    
    Devuelve la jugada elegida y el nuevo estado de la mesa tras ejecutar la jugada.
    La jugada se representa como una tupla (tipo, combinación, carta).
    """
    evaluaciones_totales = []
    for card in estado['mano_usuario']:
        target = 15 - card[0]
        capture_combos = combinaciones_que_suman(estado['mesa'], target)
        if capture_combos:
            moves = [("captura", combo, card) for combo in capture_combos]
        else:
            moves = [("no captura", None, card)]
        for move in moves:
            neto, pts, exp_op, new_mesa = evaluar_movida(card, estado['mesa'], estado['baraja'], (move[0], move[1]))
            evaluaciones_totales.append((move, neto, pts, exp_op, new_mesa))
    if evaluaciones_totales:
        best = max(evaluaciones_totales, key=lambda x: x[1])
        print("\nEvaluación de jugadas posibles:")
        for i, eval_item in enumerate(evaluaciones_totales):
            move, neto, pts, exp_op, new_mesa = eval_item
            escoba_str = " (escoba)" if move[0]=="captura" and not new_mesa else ""
            if move[0] == "captura":
                print(f"{i+1}. Con la carta {move[2]}: Capturar {move[1]}{escoba_str} -> Puntos usuario: {pts:.2f}, Expectativa oponente: {exp_op:.2f}, Valor neto: {neto:.2f}")
            else:
                print(f"{i+1}. Con la carta {move[2]}: No capturar -> Puntos usuario: {pts:.2f}, Expectativa oponente: {exp_op:.2f}, Valor neto: {neto:.2f}")
        default_option = evaluaciones_totales.index(best) + 1
        choice = input(f"Elige la opción (presiona Enter para la opción {default_option}): ")
        if choice.strip() == "":
            chosen = best
        else:
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(evaluaciones_totales):
                    print("Opción no válida, se escoge la opción por defecto.")
                    chosen = best
                else:
                    chosen = evaluaciones_totales[index]
            except:
                print("Entrada no válida, se escoge la opción por defecto.")
                chosen = best
        move, neto, pts, exp_op, new_mesa = chosen
        escoba_str = " (escoba)" if move[0]=="captura" and not new_mesa else ""
        if move[0] == "captura":
            print(f"Sugerencia: Jugar la carta {move[2]} capturando {move[1]}{escoba_str}\n")
        else:
            print(f"Sugerencia: Jugar la carta {move[2]} sin capturar (colocándola en la mesa)\n")
        return move, new_mesa
    else:
        print("No hay jugadas evaluables.")
        return None, estado['mesa']

def sugerir_movida_oponente(op_card, mesa, deck):
    """
    Evalúa las posibles jugadas para el oponente, dada su carta, la mesa y el mazo.
    Se generan todas las opciones de captura (si existen) y se añade la opción "no captura".
    Devuelve una lista de evaluaciones: cada elemento es una tupla
       (move, neto, puntos_oponente, expectativa_usuario, new_mesa)
    donde move es una tupla (tipo, combinación, op_card).
    """
    target = 15 - op_card[0]
    capture_combos = combinaciones_que_suman(mesa, target)
    moves = []
    for combo in capture_combos:
        moves.append(("captura", combo, op_card))
    moves.append(("no captura", None, op_card))
    evaluaciones = []
    for move in moves:
        neto, pts, exp_user, new_mesa = evaluar_movida(op_card, mesa, deck, (move[0], move[1]))
        evaluaciones.append((move, neto, pts, exp_user, new_mesa))
    return evaluaciones

def elegir_captura_usuario(estado):
    """
    Permite al usuario elegir entre las jugadas de captura disponibles con sus cartas,
    cuando el oponente, teniendo posibilidad, renuncia a capturar.
    Se muestran las opciones numeradas; la opción por defecto (al pulsar Enter) será la de mayor valor neto.
    Una vez elegida la opción, se actualiza el estado:
      - Se elimina la carta jugada de la mano.
      - Se retiran de la mesa las cartas capturadas.
      - Se añaden las cartas capturadas al montón del usuario.
      - Se actualiza el contador de escobas si la mesa queda vacía.
      - Se actualiza el último capturador.
    """
    evaluaciones = []
    for card in estado['mano_usuario']:
        target = 15 - card[0]
        combos = combinaciones_que_suman(estado['mesa'], target)
        if combos:
            for combo in combos:
                neto, pts, exp_op, new_mesa = evaluar_movida(card, estado['mesa'], estado['baraja'], ("captura", combo))
                evaluaciones.append((("captura", combo, card), neto, pts, exp_op, new_mesa))
    if not evaluaciones:
        print("No hay posibilidades de captura para el usuario.")
        return
    if len(evaluaciones) == 1:
        chosen = evaluaciones[0]
        move, neto, pts, exp_op, new_mesa = chosen
        escoba_str = " (escoba)" if not new_mesa else ""
        print(f"Captura automática para el usuario: Jugar la carta {move[2]} capturando {move[1]}{escoba_str}")
    else:
        print("\nEvaluación de jugadas de captura disponibles para el usuario:")
        for i, eval_item in enumerate(evaluaciones):
            move, neto, pts, exp_op, new_mesa = eval_item
            escoba_str = " (escoba)" if not new_mesa else ""
            print(f"{i+1}. Con la carta {move[2]}: Capturar {move[1]}{escoba_str} -> Puntos usuario: {pts:.2f}, Valor neto: {neto:.2f}")
        best = max(evaluaciones, key=lambda x: x[1])
        default_option = evaluaciones.index(best) + 1
        choice = input(f"Elige la opción de captura (presiona Enter para la opción {default_option}): ")
        if choice.strip() == "":
            chosen = best
        else:
            try:
                index = int(choice) - 1
                if index < 0 or index >= len(evaluaciones):
                    print("Opción no válida, se escoge la opción por defecto.")
                    chosen = best
                else:
                    chosen = evaluaciones[index]
            except:
                print("Entrada no válida, se escoge la opción por defecto.")
                chosen = best
        move, neto, pts, exp_op, new_mesa = chosen
        escoba_str = " (escoba)" if not new_mesa else ""
        print(f"Captura elegida para el usuario: Jugar la carta {move[2]} capturando {move[1]}{escoba_str}")
    card = move[2]
    captured = [c for c in estado['mesa'] if c not in new_mesa] + [card]
    if card in estado['mano_usuario']:
        estado['mano_usuario'].remove(card)
    estado['capturadas_usuario'].extend(captured)
    if not new_mesa:
        estado['escobas_usuario'] += 1
    estado['mesa'] = new_mesa
    estado['last_capturador'] = "usuario"

# ===============================
# Función principal: escoba()
# ===============================
def escoba():
    """ Función principal del juego. """
    baraja = inicializar_baraja()
    estado = {
        'baraja': baraja,
        'mesa': [],
        'mano_usuario': [],
        'capturadas_usuario': [],
        'capturadas_oponente': [],
        'escobas_usuario': 0,
        'escobas_oponente': 0,
        'last_capturador': None
    }

    user_inicia = input("¿Tienes tú la mano (S/N)? ").strip().upper() == 'S'
    
    # Lectura inicial: se validan las cartas usando la baraja completa.
    estado['mesa'] = leer_cartas("Introduce las 4 cartas de la mesa: ", 4, allowed=estado['baraja'])
    estado['baraja'] = remover_cartas(estado['baraja'], estado['mesa'])
    estado['mano_usuario'] = leer_cartas("Introduce tus 3 cartas: ", 3, allowed=estado['baraja'])
    estado['baraja'] = remover_cartas(estado['baraja'], estado['mano_usuario'])

    while True:
        print("\n--- Nueva jugada ---")
        print(f"Mesa: {estado['mesa']}")
        print(f"Tu mano: {estado['mano_usuario']}")
        
        # Sugerencia y ejecución de la jugada del usuario.
        move_user, new_mesa = sugerir_mejor_jugada(estado)
        if move_user is None:
            print("No hay jugadas evaluables. Pasando turno.")
        else:
            card = move_user[2]
            if move_user[0] == "captura":
                escoba_str = " (escoba)" if not new_mesa else ""
                print(f"Ejecutando jugada: Jugar la carta {card} capturando {move_user[1]}{escoba_str}")
                estado['mano_usuario'].remove(card)
                captured = [c for c in estado['mesa'] if c not in new_mesa] + [card]
                estado['capturadas_usuario'].extend(captured)
                estado['mesa'] = new_mesa
                estado['last_capturador'] = "usuario"
                if not estado['mesa']:
                    estado['escobas_usuario'] += 1
            else:
                print(f"Ejecutando jugada: Jugar la carta {card} sin capturar, dejando la mesa en estado {new_mesa}")
                estado['mano_usuario'].remove(card)
                estado['mesa'] = new_mesa
        
        # Turno del oponente:
        op_carta = leer_cartas("Introduce la carta que juega tu oponente: ", 1, allowed=estado['baraja'])[0]
        estado['baraja'] = remover_cartas(estado['baraja'], [op_carta])
        evaluaciones_op = sugerir_movida_oponente(op_carta, estado['mesa'], estado['baraja'])
        if evaluaciones_op:
            if len(evaluaciones_op) == 1:
                chosen_op = evaluaciones_op[0]
                move, neto, pts, exp_user, new_mesa_op = chosen_op
                target = 15 - op_carta[0]
                print("\nÚnica opción para el oponente, se ejecuta automáticamente:")
                if not combinaciones_que_suman(estado['mesa'], target):
                    print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} sin capturar")
                    print("El oponente no puede capturar.")
                else:
                    if move[0] == "captura":
                        escoba_str = " (escoba)" if not new_mesa_op else ""
                        print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} capturando {move[1]}{escoba_str}")
                    else:
                        print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} sin capturar")
                        print("El oponente renuncia a capturar.")
            else:
                best_op = max(evaluaciones_op, key=lambda x: x[1])
                print("\nEvaluación de jugadas posibles para el oponente:")
                for i, eval_item in enumerate(evaluaciones_op):
                    move, neto, pts, exp_user, _ = eval_item
                    escoba_str = " (escoba)" if move[0]=="captura" and not _ else ""
                    if move[0] == "captura":
                        print(f"{i+1}. Con la carta {move[2]}: Capturar {move[1]}{escoba_str} -> Puntos oponente: {pts:.2f}, Expectativa usuario: {exp_user:.2f}, Valor neto: {neto:.2f}")
                    else:
                        print(f"{i+1}. Con la carta {move[2]}: No capturar -> Puntos oponente: {pts:.2f}, Expectativa usuario: {exp_user:.2f}, Valor neto: {neto:.2f}")
                default_option = evaluaciones_op.index(best_op) + 1
                choice = input(f"Elige la opción que tomó tu oponente (presiona Enter para la opción {default_option}): ")
                if choice.strip() == "":
                    chosen_op = best_op
                else:
                    try:
                        index = int(choice) - 1
                        if index < 0 or index >= len(evaluaciones_op):
                            print("Opción no válida, se escoge la opción por defecto.")
                            chosen_op = best_op
                        else:
                            chosen_op = evaluaciones_op[index]
                    except:
                        print("Entrada no válida, se escoge la opción por defecto.")
                        chosen_op = best_op
            move, neto, pts, exp_user, new_mesa_op = chosen_op
            if move[0] == "captura":
                escoba_str = " (escoba)" if not new_mesa_op else ""
                print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} capturando {move[1]}{escoba_str}")
                capturadas = [c for c in estado['mesa'] if c not in new_mesa_op] + [op_carta]
                estado['capturadas_oponente'].extend(capturadas)
                estado['mesa'] = new_mesa_op
                estado['last_capturador'] = "oponente"
                if not estado['mesa']:
                    estado['escobas_oponente'] += 1
            else:
                target = 15 - op_carta[0]
                if not combinaciones_que_suman(estado['mesa'], target):
                    print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} sin capturar")
                    print("El oponente no puede capturar.")
                else:
                    print(f"El oponente ejecuta la jugada: Jugar la carta {move[2]} sin capturar")
                    print("El oponente renuncia a capturar.")
                estado['mesa'].append(op_carta)
                if combinaciones_que_suman(estado['mesa'], target):
                    elegir_captura_usuario(estado)
        else:
            estado['mesa'].append(op_carta)
        
        # Mostrar siempre el estado actual de la mesa.
        print(f"\nEstado actual de la mesa: {estado['mesa']}")
        
        # Comprobación del final de la partida:
        # Si no quedan cartas en la mano y en la baraja, se asignan las cartas que queden en la mesa
        # al último jugador que capturó y se muestra un mensaje.
        if not estado["mano_usuario"] and not estado["baraja"]:
            if estado["mesa"]:
                if estado["last_capturador"] == "usuario":
                    print(f"\nÚltima mano: Ganas las cartas {estado['mesa']} que quedan en la mesa.")
                    estado["capturadas_usuario"].extend(estado["mesa"])
                elif estado["last_capturador"] == "oponente":
                    print(f"\nÚltima mano: El oponente gana las cartas {estado['mesa']} que quedan en la mesa.")
                    estado["capturadas_oponente"].extend(estado["mesa"])
                else:
                    print("\nÚltima mano: No se asignan cartas, pues no hubo capturador final.")
                estado["mesa"] = []
            break
        
        # Si se han acabado las cartas de la mano, se piden nuevas cartas SOLO si quedan en la baraja.
        if not estado["mano_usuario"]:
            if estado["baraja"]:
                num_cards = 3 if len(estado["baraja"]) >= 3 else len(estado["baraja"])
                nuevas = leer_cartas(f"Introduce tus {num_cards} nuevas cartas: ", num_cards, allowed=estado["baraja"])
                estado["mano_usuario"] = nuevas
                estado["baraja"] = remover_cartas(estado["baraja"], nuevas)
            else:
                # Si no quedan cartas en la baraja, se procede a finalizar la partida.
                if estado["mesa"]:
                    if estado["last_capturador"] == "usuario":
                        print(f"\nÚltima mano: Ganas las cartas {estado['mesa']} que quedan en la mesa.")
                        estado["capturadas_usuario"].extend(estado["mesa"])
                    elif estado["last_capturador"] == "oponente":
                        print(f"\nÚltima mano: El oponente gana las cartas {estado['mesa']} que quedan en la mesa.")
                        estado["capturadas_oponente"].extend(estado["mesa"])
                    else:
                        print("\nÚltima mano: No se asignan cartas, pues no hubo capturador final.")
                    estado["mesa"] = []
                break
    
    # Mostrar la puntuación final y el detalle.
    print("\n--- Puntuación Final ---")
    for jugador in ["usuario", "oponente"]:
        detalle = detalle_puntuacion(estado[f"capturadas_{jugador}"], estado[f"escobas_{jugador}"])
        print(f"{jugador.capitalize()}: {detalle['total']:.2f} puntos (Cartas: {detalle['cartas']:.2f}, Velo: {detalle['velo']:.2f}, Sietes: {detalle['sietes']:.2f}, Oros: {detalle['oros']:.2f}, Escobas: {detalle['escobas']})")

if __name__ == '__main__':
    escoba()
