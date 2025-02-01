# -*- coding: utf-8 -*-
"""
Programa Escoba
Con validación de jugadas, evaluación del oponente, asignación de la última mano,
y desglose final de la puntuación.

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
    if palo not in ('O','C','E','B'):
        return None
    try:
        valor = int(valor_str)
    except:
        return None
    if not (1 <= valor <= 10):
        return None
    return (valor, palo)

def leer_cartas(mensaje, cantidad):
    """
    Solicita al usuario 'cantidad' de cartas separadas por comas y las valida.
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
            cartas.append(carta)
        if valido:
            return cartas

# ===================================
# Funciones para el juego y el estado
# ===================================

def inicializar_baraja():
    """
    Inicializa la baraja española de 40 cartas.
    """
    baraja = []
    for palo in ('O','C','E','B'):
        for valor in range(1, 11):
            baraja.append((valor, palo))
    return baraja

def remover_cartas(baraja, cartas_a_remover):
    """
    Devuelve una copia de la baraja sin las cartas indicadas.
    """
    nueva_baraja = baraja.copy()
    for c in cartas_a_remover:
        if c in nueva_baraja:
            nueva_baraja.remove(c)
    return nueva_baraja

# ====================================
# Funciones para sugerir jugadas
# ====================================

def suma_escoba(carta, lista_cartas):
    """
    Retorna la suma de la carta y el total de los valores de la lista.
    """
    return carta[0] + sum(c[0] for c in lista_cartas)

def subconjuntos(lista):
    """
    Genera todos los subconjuntos no vacíos de la lista.
    """
    resultado = []
    n = len(lista)
    def rec(i, actual):
        if actual:
            resultado.append(actual)
        for j in range(i, n):
            rec(j+1, actual + [lista[j]])
    rec(0, [])
    return resultado

def jugadas_validas(mano, mesa):
    """
    Para cada carta de la mano, retorna las combinaciones de la mesa que sumen 15.
    Cada jugada se expresa como (carta, combo, es_escoba). Si no hay combinación, se registra
    como descarte.
    """
    jugadas = []
    for carta in mano:
        posibles = []
        for combo in subconjuntos(mesa):
            if suma_escoba(carta, combo) == 15:
                posibles.append(combo)
        if posibles:
            for combo in posibles:
                es_escoba = (len(combo) == len(mesa))
                jugadas.append((carta, combo, es_escoba))
        else:
            jugadas.append((carta, [], False))
    return jugadas

def puntos_cartas(cartas, cont_cartas=0, cont_sietes=0, cont_oros=0):
    """
    Calcula el puntaje de las cartas aplicando:
      - 1/21 por carta (hasta 21),
      - 1/3 por carta con valor 7 (hasta 3),
      - 1/6 por carta de oros (hasta 6),
      - y, si es 7 de oros, 1 adicional.
    Se respetan los límites acumulados.
    """
    pts = 0.0
    for c in cartas:
        if cont_cartas < 21:
            pts += 1.0 / 21
            cont_cartas += 1
        if c[0] == 7 and cont_sietes < 3:
            pts += 1.0 / 3
            cont_sietes += 1
        if c[1] == 'O' and cont_oros < 6:
            pts += 1.0 / 6
            cont_oros += 1
        if c == (7, 'O'):
            pts += 1.0
    return pts

def detalle_puntuacion(cartas, escobas):
    """
    Calcula el desglose de la puntuación obtenido de las cartas y escobas.
    Devuelve un diccionario con: "cartas", "velo", "sietes", "oros", "escobas" y "total".
    """
    total_cartas = len(cartas)
    pts_cartas = min(total_cartas, 21) / 21
    pts_velo = sum(1 for c in cartas if c == (7, 'O'))
    pts_sietes = min(sum(1 for c in cartas if c[0] == 7 and c[1] != 'O'), 3) * (1/3)
    pts_oros = min(sum(1 for c in cartas if c[1] == 'O' and c != (7, 'O')), 6) * (1/6)
    pts_total = pts_cartas + pts_velo + pts_sietes + pts_oros + escobas
    return {"cartas": pts_cartas, "velo": pts_velo, "sietes": pts_sietes, "oros": pts_oros, "escobas": escobas, "total": pts_total}

# --------------------------------------------------------
# Funciones para la estimación probabilística del oponente
# --------------------------------------------------------

def candidatos_oponente(estado):
    """
    Retorna la lista de cartas no vistas (no en mesa, mano o capturadas).
    """
    full = set(inicializar_baraja())
    conocidos = set(estado['mesa'] + estado['mano_usuario'] +
                    estado['capturadas_usuario'] + estado['capturadas_oponente'])
    return list(full - conocidos)

def evaluar_respuesta_oponente(estado):
    """
    Estima el potencial que el oponente podría obtener en su turno,
    asumiendo que su mano se compone de cartas elegidas aleatoriamente de las no vistas.
    """
    candidatos = candidatos_oponente(estado)
    potenciales = []
    for c in candidatos:
        jugadas = jugadas_validas([c], estado['mesa'])
        if jugadas:
            puntajes = [puntos_cartas(j[1]) + (1 if j[2] else 0) for j in jugadas]
            potenciales.append(max(puntajes))
        else:
            potenciales.append(0)
    return sum(potenciales) / len(potenciales) if potenciales else 0

def copiar_estado(estado):
    """
    Retorna una copia superficial del estado.
    """
    return {
        'baraja': estado['baraja'][:],
        'mesa': estado['mesa'][:],
        'mano_usuario': estado['mano_usuario'][:],
        'capturadas_usuario': estado['capturadas_usuario'][:],
        'capturadas_oponente': estado['capturadas_oponente'][:],
        'escobas_usuario': estado.get('escobas_usuario', 0),
        'escobas_oponente': estado.get('escobas_oponente', 0),
        'last_capturador': estado.get('last_capturador', None)
    }

# --------------------------------------------------------
# Funciones para validar jugadas
# --------------------------------------------------------

def validar_jugada(carta, capturadas, mesa):
    """
    Valida la jugada del usuario comprobando que:
      - Todas las cartas capturadas estén en la mesa.
      - La suma (carta + capturadas) sea 15.
    """
    result = {"valid": True}
    for card in capturadas:
        if card not in mesa:
            result["valid"] = False
            result["error"] = f"La carta {card} no está en la mesa."
            return result
    if suma_escoba(carta, capturadas) != 15:
        result["valid"] = False
        result["error"] = f"La suma de la carta {carta} y las capturadas {capturadas} no es 15."
        return result
    return result

def validar_jugada_oponente(carta_op, capturadas_op, mesa):
    """
    Valida la jugada del oponente comprobando:
      - Si se capturó alguna carta, que todas estén en la mesa y la suma sea 15.
      - Si no se capturó ninguna carta, se verifica si la carta permitiría capturar.
        Si es así, se marca error (renuncia incorrecta) y se solicitan las combinaciones.
        Si no permite captura, se acepta sin preguntar.
    """
    result = {"valid": True}
    if capturadas_op:
        for card in capturadas_op:
            if card not in mesa:
                result["valid"] = False
                result["error"] = f"La carta {card} no está en la mesa."
                return result
        if suma_escoba(carta_op, capturadas_op) != 15:
            result["valid"] = False
            result["error"] = f"La suma de la carta {carta_op} y las capturadas {capturadas_op} no es 15."
            return result
    else:
        jugadas = jugadas_validas([carta_op], mesa)
        valid_combos = [j[1] for j in jugadas if j[1]]
        if valid_combos:
            result["valid"] = False
            result["error"] = "Renuncia incorrecta: existen combinaciones válidas."
            result["renuncio"] = True
            result["combinaciones"] = valid_combos
            return result
    return result

# --------------------------------------------------------
# Función de evaluación de jugadas (para sugerencias)
# --------------------------------------------------------

def evaluar_jugada(jugada, estado):
    """
    Evalúa una jugada potencial del usuario combinando:
      - Beneficio inmediato (puntos de las cartas capturadas, +1 si es escoba).
    Retorna el valor esperado neto.
    (La heurística de ajustes en descartes se incluye en la selección de jugada sugerida.)
    """
    carta, cap, es_escoba = jugada
    pts_inmediatos = puntos_cartas(cap)
    if es_escoba:
        pts_inmediatos += 1.0
    estado_temp = copiar_estado(estado)
    actualizar_estado_jugada(estado_temp, jugada, jugador='usuario')
    potencial_oponente = evaluar_respuesta_oponente(estado_temp)
    return pts_inmediatos - potencial_oponente

def sugerir_mejor_jugada(estado):
    """
    Genera las jugadas válidas de la mano del usuario sobre la mesa, las evalúa
    y retorna la de mayor valor.
    """
    jugadas = jugadas_validas(estado['mano_usuario'], estado['mesa'])
    if not jugadas:
        return None
    evaluaciones = [evaluar_jugada(j, estado) for j in jugadas]
    mejor = jugadas[evaluaciones.index(max(evaluaciones))]
    return mejor

# ====================================
# Funciones para actualizar el estado
# ====================================

def actualizar_estado_jugada(estado, jugada, jugador='usuario'):
    """
    Actualiza el estado tras una jugada:
      - Agrega la carta jugada y las capturadas al registro del jugador.
      - Actualiza la mesa (elimina las cartas capturadas o, si es descarte, agrega la carta jugada).
      - Si el jugador es el usuario, elimina la carta jugada de su mano.
      - Si es escoba, incrementa el contador.
      - Actualiza 'last_capturador' si hubo captura.
    """
    carta, cap, es_escoba = jugada
    if cap:
        estado["last_capturador"] = jugador
    estado["capturadas_" + jugador].append(carta)
    if cap:
        estado["capturadas_" + jugador].extend(cap)
    if cap:
        for c in cap:
            if c in estado["mesa"]:
                estado["mesa"].remove(c)
    else:
        estado["mesa"].append(carta)
    if jugador == "usuario":
        if carta in estado["mano_usuario"]:
            estado["mano_usuario"].remove(carta)
    if es_escoba:
        key = "escobas_" + jugador
        estado[key] = estado.get(key, 0) + 1
    return estado

def actualizar_estado_oponente(estado, carta_jugada, cartas_capturadas):
    """
    Actualiza el estado con la jugada del oponente.
    """
    es_escoba = (len(cartas_capturadas) == len(estado["mesa"]))
    jugada = (carta_jugada, cartas_capturadas, es_escoba)
    actualizar_estado_jugada(estado, jugada, jugador="oponente")
    return estado

# ===============================
# Función principal: escoba()
# ===============================

def escoba():
    # Inicialización del estado
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
    
    # Determinar quién inicia
    user_inicia = (input("¿Tienes tú la mano (S/N)? ").strip().upper() == 'S')
    
    # Primera mano: se piden las 4 cartas de la mesa y las 3 cartas del usuario
    estado['mesa'] = leer_cartas("Introduce las 4 cartas de la mesa (separadas por comas): ", 4)
    estado['baraja'] = remover_cartas(estado['baraja'], estado['mesa'])
    estado['mano_usuario'] = leer_cartas("Introduce tus 3 cartas (separadas por comas): ", 3)
    estado['baraja'] = remover_cartas(estado['baraja'], estado['mano_usuario'])
    
    # Bucle principal de la partida
    while True:
        print("\n--- Nueva jugada ---")
        print("Mesa actual:", estado['mesa'])
        print("Tu mano:", estado['mano_usuario'])
        
        # Mostrar situación de puntos
        consolidados_usuario = puntos_cartas(estado['capturadas_usuario']) + estado['escobas_usuario']
        consolidados_oponente = puntos_cartas(estado['capturadas_oponente']) + estado['escobas_oponente']
        jugadas_user = jugadas_validas(estado['mano_usuario'], estado['mesa'])
        potencial_usuario = max([evaluar_jugada(j, estado) for j in jugadas_user]) if jugadas_user else 0
        potencial_oponente = evaluar_respuesta_oponente(estado)
        print("Situación de puntos:")
        print(f"  Consolidados: Tú = {consolidados_usuario:.2f} | Oponente = {consolidados_oponente:.2f}")
        print(f"  Potenciales:  Tú = {potencial_usuario:.2f} | Oponente = {potencial_oponente:.2f}")
        
        if user_inicia:
            # Turno del usuario
            jugada_sugerida = sugerir_mejor_jugada(estado)
            if jugada_sugerida:
                carta_sug, capturadas_sug, es_escoba = jugada_sugerida
                if es_escoba:
                    print(f"Sugerencia: Jugar la carta {carta_sug} para capturar {capturadas_sug} (¡Escoba!)")
                elif capturadas_sug:
                    print(f"Sugerencia: Jugar la carta {carta_sug} para capturar {capturadas_sug}")
                else:
                    print(f"Sugerencia: Descartar la carta {carta_sug}")
            else:
                print("No se encontraron jugadas válidas.")
            respuesta = input("¿Validas esta jugada? (S/n): ").strip()
            if respuesta == "":
                respuesta = "S"
            respuesta = respuesta.upper()
            if respuesta == "S":
                jugada = jugada_sugerida
            else:
                carta_str = input("Introduce la carta que juegas: ")
                carta_jugada = parsear_carta(carta_str)
                if carta_jugada is None or carta_jugada not in estado['mano_usuario']:
                    print("Carta no válida o no en tu mano. Se usará la jugada sugerida.")
                    jugada = jugada_sugerida
                else:
                    # Si la carta no permite captura, se asume descarte sin preguntar capturas
                    jugadas_para_carta = jugadas_validas([carta_jugada], estado['mesa'])
                    if all(j[1] == [] for j in jugadas_para_carta):
                        jugada = (carta_jugada, [], False)
                    elif len([j for j in jugadas_para_carta if j[1]]) == 1:
                        jugada = [j for j in jugadas_para_carta if j[1]][0]
                    else:
                        capturadas = []
                        s = input("Introduce las cartas que capturas (separadas por comas): ").strip()
                        if s:
                            for p in s.split(','):
                                x = parsear_carta(p)
                                if x is None:
                                    print(f"La carta '{p}' es inválida. Se usará la jugada sugerida.")
                                    jugada = jugada_sugerida
                                    break
                                else:
                                    capturadas.append(x)
                        else:
                            capturadas = []
                        validacion = validar_jugada(carta_jugada, capturadas, estado['mesa'])
                        if not validacion["valid"]:
                            print("Error en tu jugada:", validacion["error"])
                            print("Se usará la jugada sugerida.")
                            jugada = jugada_sugerida
                        else:
                            es_escoba = (len(capturadas) == len(estado['mesa']))
                            jugada = (carta_jugada, capturadas, es_escoba)
            actualizar_estado_jugada(estado, jugada, jugador='usuario')
            
            print("\nDespués de tu jugada:")
            print("Mesa actual:", estado['mesa'])
            consolidados_usuario = puntos_cartas(estado['capturadas_usuario']) + estado['escobas_usuario']
            consolidados_oponente = puntos_cartas(estado['capturadas_oponente']) + estado['escobas_oponente']
            jugadas_user = jugadas_validas(estado['mano_usuario'], estado['mesa'])
            potencial_usuario = max([evaluar_jugada(j, estado) for j in jugadas_user]) if jugadas_user else 0
            potencial_oponente = evaluar_respuesta_oponente(estado)
            print("Situación de puntos:")
            print(f"  Consolidados: Tú = {consolidados_usuario:.2f} | Oponente = {consolidados_oponente:.2f}")
            print(f"  Potenciales:  Tú = {potencial_usuario:.2f} | Oponente = {potencial_oponente:.2f}")
            
            # Turno del oponente
            print("\nAhora, es el turno del oponente.")
            while True:
                carta_op_str = input("Introduce la carta que jugó el oponente: ")
                carta_op = parsear_carta(carta_op_str)
                if carta_op is None:
                    print("Carta del oponente no válida. Inténtalo de nuevo.")
                    continue
                s = input("Introduce las cartas que capturó el oponente (separadas por comas; vacío si no capturó): ").strip()
                capturadas_op = []
                if s:
                    error_en_cap = False
                    for p in s.split(','):
                        x = parsear_carta(p)
                        if x is None:
                            print(f"La carta '{p}' es inválida. Inténtalo de nuevo.")
                            error_en_cap = True
                            break
                        else:
                            capturadas_op.append(x)
                    if error_en_cap:
                        continue
                valid_op = validar_jugada_oponente(carta_op, capturadas_op, estado['mesa'])
                if not valid_op["valid"]:
                    print("Error en la jugada del oponente:", valid_op["error"])
                    if valid_op.get("renuncio", False):
                        print("Las combinaciones válidas que podía capturar son:")
                        for i, combo in enumerate(valid_op["combinaciones"], 1):
                            print(f"  {i}: {combo} (suma: {suma_escoba(carta_op, combo)})")
                        try:
                            idx = input("Elige el número de la combinación correcta (1/n): ").strip()
                            if idx == "":
                                idx = "1"
                            idx = int(idx)
                        except:
                            idx = 1
                        if 1 <= idx <= len(valid_op["combinaciones"]):
                            capturadas_op = valid_op["combinaciones"][idx-1]
                            break
                        else:
                            print("Opción inválida. Inténtalo de nuevo.")
                    else:
                        print("Inténtalo de nuevo la jugada del oponente.")
                        continue
                else:
                    break
            actualizar_estado_oponente(estado, carta_op, capturadas_op)
            
        else:
            # Caso en que el oponente inicia
            print("El oponente tiene la mano. Se espera su jugada.")
            while True:
                carta_op_str = input("Introduce la carta que jugó el oponente: ")
                carta_op = parsear_carta(carta_op_str)
                if carta_op is None:
                    print("Carta del oponente no válida. Inténtalo de nuevo.")
                    continue
                s = input("Introduce las cartas que capturó el oponente (separadas por comas; vacío si no capturó): ").strip()
                capturadas_op = []
                if s:
                    error_en_cap = False
                    for p in s.split(','):
                        x = parsear_carta(p)
                        if x is None:
                            print(f"La carta '{p}' es inválida. Inténtalo de nuevo.")
                            error_en_cap = True
                            break
                        else:
                            capturadas_op.append(x)
                    if error_en_cap:
                        continue
                valid_op = validar_jugada_oponente(carta_op, capturadas_op, estado['mesa'])
                if not valid_op["valid"]:
                    print("Error en la jugada del oponente:", valid_op["error"])
                    if valid_op.get("renuncio", False):
                        print("Las combinaciones válidas que podía capturar son:")
                        for i, combo in enumerate(valid_op["combinaciones"], 1):
                            print(f"  {i}: {combo} (suma: {suma_escoba(carta_op, combo)})")
                        try:
                            idx = input("Elige el número de la combinación correcta (1/n): ").strip()
                            if idx == "":
                                idx = "1"
                            idx = int(idx)
                        except:
                            idx = 1
                        if 1 <= idx <= len(valid_op["combinaciones"]):
                            capturadas_op = valid_op["combinaciones"][idx-1]
                            break
                        else:
                            print("Opción inválida. Inténtalo de nuevo.")
                    else:
                        print("Inténtalo de nuevo la jugada del oponente.")
                        continue
                else:
                    break
            actualizar_estado_oponente(estado, carta_op, capturadas_op)
            
            # Turno del usuario
            jugada_sugerida = sugerir_mejor_jugada(estado)
            if jugada_sugerida:
                print("Sugerencia:", jugada_sugerida)
            respuesta = input("¿Validas la jugada? (S/n): ").strip()
            if respuesta == "":
                respuesta = "S"
            respuesta = respuesta.upper()
            if respuesta == "S":
                jugada = jugada_sugerida
            else:
                carta_str = input("Introduce la carta que juegas: ")
                carta_jugada = parsear_carta(carta_str)
                if carta_jugada is None or carta_jugada not in estado["mano_usuario"]:
                    print("Carta no válida o no en tu mano. Se usará la sugerida.")
                    jugada = jugada_sugerida
                else:
                    jugadas_para_carta = jugadas_validas([carta_jugada], estado["mesa"])
                    if all(j[1] == [] for j in jugadas_para_carta):
                        jugada = (carta_jugada, [], False)
                    elif len([j for j in jugadas_para_carta if j[1]]) == 1:
                        jugada = [j for j in jugadas_para_carta if j[1]][0]
                    else:
                        capturadas = []
                        s = input("Introduce las cartas que capturas (separadas por comas): ").strip()
                        if s:
                            for p in s.split(','):
                                x = parsear_carta(p)
                                if x is None:
                                    print(f"La carta '{p}' es inválida. Se usará la jugada sugerida.")
                                    jugada = jugada_sugerida
                                    break
                                else:
                                    capturadas.append(x)
                        else:
                            capturadas = []
                        validacion = validar_jugada(carta_jugada, capturadas, estado["mesa"])
                        if not validacion["valid"]:
                            print("Error en tu jugada:", validacion["error"])
                            print("Se usará la jugada sugerida.")
                            jugada = jugada_sugerida
                        else:
                            jugada = (carta_jugada, capturadas, len(capturadas)==len(estado["mesa"]))
                actualizar_estado_jugada(estado, jugada, jugador="usuario")
        
        # Si no quedan cartas en la mano y la baraja está vacía, se asume última mano
        if not estado["mano_usuario"]:
            if len(estado["baraja"]) == 0:
                if estado["mesa"] and estado.get("last_capturador") is not None:
                    print("\nÚltima mano: Se asignan las cartas de la mesa a", estado["last_capturador"])
                    if estado["last_capturador"] == "usuario":
                        estado["capturadas_usuario"].extend(estado["mesa"])
                    else:
                        estado["capturadas_oponente"].extend(estado["mesa"])
                    estado["mesa"] = []
                print("Fin de la partida.")
                break
            else:
                nuevas = leer_cartas("Introduce tus 3 nuevas cartas: ", 3)
                estado["mano_usuario"] = nuevas
                estado["baraja"] = remover_cartas(estado["baraja"], nuevas)
                print("Tu mano:", estado["mano_usuario"])
        
        # Mostrar la puntuación final de la ronda
        consolidados_usuario = puntos_cartas(estado["capturadas_usuario"]) + estado["escobas_usuario"]
        consolidados_oponente = puntos_cartas(estado["capturadas_oponente"]) + estado["escobas_oponente"]
        print("\nPuntos finales de la ronda:")
        print(f"  Consolidados: Tú = {consolidados_usuario:.2f} | Oponente = {consolidados_oponente:.2f}")
    
    # Al finalizar la partida, mostrar el desglose final de la puntuación
    print("\n--- Puntuación Final ---")
    detalle_usuario = detalle_puntuacion(estado["capturadas_usuario"], estado["escobas_usuario"])
    detalle_oponente = detalle_puntuacion(estado["capturadas_oponente"], estado["escobas_oponente"])
    print("Tú: Total =", round(detalle_usuario["total"], 2),
          " (Cartas =", round(detalle_usuario["cartas"], 2),
          ", Velo =", round(detalle_usuario["velo"], 2),
          ", Sietes =", round(detalle_usuario["sietes"], 2),
          ", Oros =", round(detalle_usuario["oros"], 2),
          ", Escobas =", detalle_usuario["escobas"], ")")
    print("Oponente: Total =", round(detalle_oponente["total"], 2),
          " (Cartas =", round(detalle_oponente["cartas"], 2),
          ", Velo =", round(detalle_oponente["velo"], 2),
          ", Sietes =", round(detalle_oponente["sietes"], 2),
          ", Oros =", round(detalle_oponente["oros"], 2),
          ", Escobas =", detalle_oponente["escobas"], ")")

if __name__ == '__main__':
    escoba()
