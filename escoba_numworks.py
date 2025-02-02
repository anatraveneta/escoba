def fmt(s): return "\n".join(s[i:i+28] for i in range(0,len(s),28))
def parsear_carta(s):
 s=s.strip()
 if len(s)<2: return None
 if "." not in s: return None
 p=s.split(".")
 if len(p)!=2: return None
 try:
  v=int(p[0]); su=int(p[1])
 except:
  return None
 if not(1<=v<=10 and 1<=su<=4): return None
 return (v,su)
def leer_cartas(mensaje,cantidad,allowed=None):
 while True:
  entrada=input(fmt(mensaje))
  partes=[p.strip() for p in entrada.split(",")]
  if len(partes)!=cantidad:
   print(fmt("Error: Debes introducir "+str(cantidad)+" cartas"))
   continue
  cartas=[]
  ok=True
  for p in partes:
   carta=parsear_carta(p)
   if carta==None:
    print(fmt("La carta '"+p+"' no es válida"))
    ok=False; break
   if allowed!=None and carta not in allowed:
    print(fmt("La carta "+str(carta)+" no está disponible"))
    ok=False; break
   cartas.append(carta)
  if ok: return cartas
def inicializar_baraja():
 return [(v,su) for su in (1,2,3,4) for v in range(1,11)]
def remover_cartas(b,L):
 r=b[:]
 for c in L:
  if c in r: r.remove(c)
 return r
def puntos_cartas_original(cartas,esc=0):
 t=len(cartas)
 pts=min(t,21)/21
 pts_velo=sum(1 for c in cartas if c==(7,1))
 pts_sietes=min(sum(1 for c in cartas if c[0]==7 and c!=(7,1)),3)*(1/3)
 pts_oros=min(sum(1 for c in cartas if c[1]==1 and c!=(7,1)),6)*(1/6)
 return pts+pts_velo+pts_sietes+pts_oros+esc
def combinaciones_que_suman(cartas,obj):
 res=[]
 def backtrack(i,cur,s):
  if s==obj: res.append(cur.copy())
  elif s>obj: return
  else:
   for j in range(i,len(cartas)):
    cur.append(cartas[j])
    backtrack(j+1,cur,s+cartas[j][0])
    cur.pop()
 backtrack(0,[],0)
 return res
def evaluar_movida(card,mesa,deck,movida):
 if movida[0]=="captura":
  combo=movida[1]
  nm=[c for c in mesa if c not in combo]
  pts=puntos_cartas_original(combo+[card],1 if len(nm)==0 else 0)
 else:
  nm=mesa+[card]; pts=0
 tot=0
 if deck:
  for op in deck:
   t=15-op[0]
   comb=combinaciones_que_suman(nm,t)
   mejor=0
   for combo in comb:
    nmop=[c for c in nm if c not in combo]
    p=puntos_cartas_original(combo+[op],1 if len(nmop)==0 else 0)
    if p>mejor: mejor=p
   tot+=mejor
  exp=tot/len(deck)
 else: exp=0
 net=pts-exp
 return net,pts,exp,nm
def sugerir_mejor_jugada(estado):
 evals=[]
 for card in estado['mano_usuario']:
  t=15-card[0]
  cap=combinaciones_que_suman(estado['mesa'],t)
  if cap: moves=[("captura",c,card) for c in cap]
  else: moves=[("no captura",None,card)]
  for move in moves:
   net,pts,exp,nm=evaluar_movida(card,estado['mesa'],estado['baraja'],(move[0],move[1]))
   evals.append((move,net,pts,exp,nm))
 if evals:
  best=max(evals,key=lambda x: x[1])
  print(fmt("Evaluación de jugadas posibles:"))
  for i,ev in enumerate(evals):
   move,net,pts,exp,nm=ev
   esc=" (escoba)" if move[0]=="captura" and not nm else ""
   if move[0]=="captura":
    print(fmt(str(i+1)+". "+str(move[2])+": Capturar "+str(move[1])+esc+" -> Pts: "+str("{0:.2f}".format(pts))+", Exp: "+str("{0:.2f}".format(exp))+", Neto: "+str("{0:.2f}".format(net))))
   else:
    print(fmt(str(i+1)+". "+str(move[2])+": No capturar -> Pts: "+str("{0:.2f}".format(pts))+", Exp: "+str("{0:.2f}".format(exp))+", Neto: "+str("{0:.2f}".format(net))))
  d=evals.index(best)+1
  c=input(fmt("Elige la opción (Enter para "+str(d)+"): "))
  if c.strip()=="":
   chosen=best
  else:
   try:
    idx=int(c)-1
    if idx<0 or idx>=len(evals):
     print(fmt("Opción no válida, se elige predeterminada"))
     chosen=best
    else: chosen=evals[idx]
   except:
    print(fmt("Entrada no válida, se elige predeterminada"))
    chosen=best
  move,net,pts,exp,nm=chosen
  esc=" (escoba)" if move[0]=="captura" and not nm else ""
  if move[0]=="captura":
   print(fmt("Sugerencia: "+str(move[2])+" capturando "+str(move[1])+esc+"\n"))
  else:
   print(fmt("Sugerencia: "+str(move[2])+" sin capturar\n"))
  return move,nm
 else:
  print(fmt("No hay jugadas evaluables."))
  return None,estado['mesa']
def sugerir_movida_oponente(op,mesa,deck):
 t=15-op[0]
 cap=combinaciones_que_suman(mesa,t)
 moves=[]
 for combo in cap: moves.append(("captura",combo,op))
 moves.append(("no captura",None,op))
 evals=[]
 for move in moves:
  net,pts,exp,nm=evaluar_movida(op,mesa,deck,(move[0],move[1]))
  evals.append((move,net,pts,exp,nm))
 return evals
def elegir_captura_usuario(estado):
 evals=[]
 for card in estado['mano_usuario']:
  t=15-card[0]
  combos=combinaciones_que_suman(estado['mesa'],t)
  if combos:
   for combo in combos:
    net,pts,exp,nm=evaluar_movida(card,estado['mesa'],estado['baraja'],("captura",combo))
    evals.append((("captura",combo,card),net,pts,exp,nm))
 if not evals:
  print(fmt("No hay posibilidades de captura para el usuario."))
  return
 if len(evals)==1:
  chosen=evals[0]
  move,net,pts,exp,nm=chosen
  esc=" (escoba)" if not nm else ""
  print(fmt("Captura automática: "+str(move[2])+" capturando "+str(move[1])+esc))
 else:
  print(fmt("Evaluación de capturas disponibles para el usuario:"))
  for i,ev in enumerate(evals):
   move,net,pts,exp,nm=ev
   esc=" (escoba)" if not nm else ""
   print(fmt(str(i+1)+". "+str(move[2])+" capturar "+str(move[1])+esc+" -> Pts: "+str("{0:.2f}".format(pts))+", Neto: "+str("{0:.2f}".format(net))))
  best=max(evals,key=lambda x: x[1])
  d=evals.index(best)+1
  c=input(fmt("Elige captura (Enter para "+str(d)+"): "))
  if c.strip()=="":
   chosen=best
  else:
   try:
    idx=int(c)-1
    if idx<0 or idx>=len(evals):
     print(fmt("Opción no válida, se elige predeterminada"))
     chosen=best
    else: chosen=evals[idx]
   except:
    print(fmt("Entrada no válida, se elige predeterminada"))
    chosen=best
  move,net,pts,exp,nm=chosen
  esc=" (escoba)" if not nm else ""
  print(fmt("Captura elegida: "+str(move[2])+" capturando "+str(move[1])+esc))
 evals=None
 card=move[2]
 cap=[c for c in estado['mesa'] if c not in nm]+[card]
 if card in estado['mano_usuario']:
  estado['mano_usuario'].remove(card)
 estado['capturadas_usuario'].extend(cap)
 if not nm:
  estado['escobas_usuario']+=1
 estado['mesa']=nm
 estado['last_capturador']="usuario"
def calcular_puntuacion_final(estado):
 cats={"velo":1,"sietes":4,"oros":10,"cartas":40}
 pts_final={"usuario":0,"oponente":0}
 desg={"usuario":{},"oponente":{}}
 for cat,N in cats.items():
  if cat=="velo":
   cu=sum(1 for c in estado["capturadas_usuario"] if c==(7,1))
   co=sum(1 for c in estado["capturadas_oponente"] if c==(7,1))
  elif cat=="sietes":
   cu=sum(1 for c in estado["capturadas_usuario"] if c[0]==7)
   co=sum(1 for c in estado["capturadas_oponente"] if c[0]==7)
  elif cat=="oros":
   cu=sum(1 for c in estado["capturadas_usuario"] if c[1]==1)
   co=sum(1 for c in estado["capturadas_oponente"] if c[1]==1)
  elif cat=="cartas":
   cu=len(estado["capturadas_usuario"])
   co=len(estado["capturadas_oponente"])
  if cu>co:
   pts_final["usuario"]+=1; desg["usuario"][cat]=1; desg["oponente"][cat]=0
  elif co>cu:
   pts_final["oponente"]+=1; desg["usuario"][cat]=0; desg["oponente"][cat]=1
  else:
   desg["usuario"][cat]=0; desg["oponente"][cat]=0
 pts_final["usuario"]+=estado["escobas_usuario"]
 pts_final["oponente"]+=estado["escobas_oponente"]
 desg["usuario"]["escobas"]=estado["escobas_usuario"]
 desg["oponente"]["escobas"]=estado["escobas_oponente"]
 return pts_final,desg
def escoba():
 print(fmt("Bienvenido a Escoba"))
 bar=inicializar_baraja()
 estado={'baraja':bar,'mesa':[],'mano_usuario':[],'capturadas_usuario':[],'capturadas_oponente':[],
 'escobas_usuario':0,'escobas_oponente':0,'last_capturador':None}
 estado['mesa']=leer_cartas("Introduce las 4 cartas de la mesa: ",4,allowed=estado['baraja'])
 estado['baraja']=remover_cartas(estado['baraja'],estado['mesa'])
 estado['mano_usuario']=leer_cartas("Introduce tus 3 cartas: ",3,allowed=estado['baraja'])
 estado['baraja']=remover_cartas(estado['baraja'],estado['mano_usuario'])
 while True:
  print(fmt("Nueva jugada:"))
  print(fmt("Mesa: "+str(estado['mesa'])))
  print(fmt("Mano: "+str(estado['mano_usuario'])))
  move_user,new_mesa=sugerir_mejor_jugada(estado)
  if move_user==None:
   print(fmt("Sin jugadas, turno pasado"))
  else:
   card=move_user[2]
   if move_user[0]=="captura":
    escoba_str=" (escoba)" if not new_mesa else ""
    print(fmt("Ejecutando: "+str(card)+" capturando "+str(move_user[1])+escoba_str))
    estado['mano_usuario'].remove(card)
    cap=[c for c in estado['mesa'] if c not in new_mesa]+[card]
    estado['capturadas_usuario'].extend(cap)
    estado['mesa']=new_mesa
    estado['last_capturador']="usuario"
    if not estado['mesa']:
     estado['escobas_usuario']+=1
   else:
    print(fmt("Ejecutando: "+str(card)+" sin capturar, mesa "+str(new_mesa)))
    estado['mano_usuario'].remove(card)
    estado['mesa']=new_mesa
  if estado["baraja"]:
   op_carta=leer_cartas("Carta oponente: ",1,allowed=estado['baraja'])[0]
   estado['baraja']=remover_cartas(estado['baraja'],[op_carta])
  else:
   op_carta=leer_cartas("Carta oponente: ",1)[0]
  eval_op=sugerir_movida_oponente(op_carta,estado['mesa'],estado['baraja'])
  if eval_op:
   if len(eval_op)==1:
    cho=eval_op[0]
    move,net,pts,exp,new_mesa_op=cho
    t=15-op_carta[0]
    print(fmt("Única op. oponente:"))
    if not combinaciones_que_suman(estado['mesa'],t):
     print(fmt("Jugar "+str(move[2])+" sin capturar"))
     print(fmt("No puede capturar"))
    else:
     if move[0]=="captura":
      escoba_str=" (escoba)" if not new_mesa_op else ""
      print(fmt("Jugar "+str(move[2])+" capturando "+str(move[1])+escoba_str))
     else:
      print(fmt("Jugar "+str(move[2])+" sin capturar"))
      print(fmt("Renuncia a capturar"))
   else:
    best_op=max(eval_op,key=lambda x:x[1])
    print(fmt("Op. posibles oponente:"))
    for i,ev in enumerate(eval_op):
     move,net,pts,exp,_=ev
     escoba_str=" (escoba)" if move[0]=="captura" and not _ else ""
     print(fmt(str(i+1)+". "+str(move[2])+": Capturar "+str(move[1])+escoba_str+" -> Pts: "+str("{0:.2f}".format(pts))+", Exp: "+str("{0:.2f}".format(exp))+", Neto: "+str("{0:.2f}".format(net))))
    d=eval_op.index(best_op)+1
    c=input(fmt("Elige op. oponente (Enter para "+str(d)+"): "))
    if c.strip()=="":
     cho=best_op
    else:
     try:
      idx=int(c)-1
      if idx<0 or idx>=len(eval_op):
       print(fmt("Op. no válida, se elige pred."))
       cho=best_op
      else: cho=eval_op[idx]
     except:
      print(fmt("Entrada no válida, se elige pred."))
      cho=best_op
   move,net,pts,exp,new_mesa_op=cho
   if move[0]=="captura":
    escoba_str=" (escoba)" if not new_mesa_op else ""
    print(fmt("Oponente: "+str(move[2])+" capturando "+str(move[1])+escoba_str))
    cap=[c for c in estado['mesa'] if c not in new_mesa_op]+[op_carta]
    estado['capturadas_oponente'].extend(cap)
    estado['mesa']=new_mesa_op
    estado['last_capturador']="oponente"
    if not estado['mesa']:
     estado['escobas_oponente']+=1
   else:
    t=15-op_carta[0]
    if not combinaciones_que_suman(estado['mesa'],t):
     print(fmt("Oponente: "+str(move[2])+" sin capturar"))
     print(fmt("No puede capturar"))
    else:
     print(fmt("Oponente: "+str(move[2])+" sin capturar"))
     print(fmt("Renuncia a capturar"))
    estado['mesa'].append(op_carta)
    if combinaciones_que_suman(estado['mesa'],t):
     elegir_captura_usuario(estado)
  else:
   estado['mesa'].append(op_carta)
  print(fmt("Estado mesa: "+str(estado['mesa'])))
  if not estado["mano_usuario"] and not estado["baraja"]:
   if estado["mesa"]:
    if estado["last_capturador"]=="usuario":
     print(fmt("Última mano: Ganas las cartas "+str(estado['mesa'])+" que quedan en la mesa."))
     estado["capturadas_usuario"].extend(estado["mesa"])
    elif estado["last_capturador"]=="oponente":
     print(fmt("Última mano: El oponente gana las cartas "+str(estado['mesa'])+" que quedan en la mesa."))
     estado["capturadas_oponente"].extend(estado["mesa"])
    else:
     print(fmt("Última mano: No se asignan cartas, no hubo capturador final."))
    estado["mesa"]=[]
   break
  if not estado["mano_usuario"]:
   if estado["baraja"]:
    num=3 if len(estado["baraja"])>=3 else len(estado["baraja"])
    nuevas=leer_cartas("Introduce tus "+str(num)+" nuevas cartas: ",num,allowed=estado["baraja"])
    estado["mano_usuario"]=nuevas
    estado["baraja"]=remover_cartas(estado["baraja"],nuevas)
   else:
    if estado["mesa"]:
     if estado["last_capturador"]=="usuario":
      print(fmt("Última mano: Ganas las cartas "+str(estado['mesa'])+" que quedan en la mesa."))
      estado["capturadas_usuario"].extend(estado["mesa"])
     elif estado["last_capturador"]=="oponente":
      print(fmt("Última mano: El oponente gana las cartas "+str(estado['mesa'])+" que quedan en la mesa."))
      estado["capturadas_oponente"].extend(estado["mesa"])
     else:
      print(fmt("Última mano: No se asignan cartas, no hubo capturador final."))
     estado["mesa"]=[]
    break
 print(fmt("Puntuación Final:"))
 pf,desg=calcular_puntuacion_final(estado)
 print(fmt("Usuario: "+str(pf["usuario"])+" puntos"))
 for cat,p in desg["usuario"].items():
  print(fmt("   "+cat+": "+str("{0:.2f}".format(p))))
 print(fmt("Oponente: "+str(pf["oponente"])+" puntos"))
 for cat,p in desg["oponente"].items():
  print(fmt("   "+cat+": "+str("{0:.2f}".format(p))))
