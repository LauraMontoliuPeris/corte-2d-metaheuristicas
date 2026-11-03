# -*- coding: utf-8 -*-
"""
Created on Sun Jun  7 17:58:41 2026

@author: Aya Limouri y Laura Montoliu  
"""

# -*- coding: utf-8 -*-
# Problema de corte 2D en dos etapas (caso inexacto)
# Metaheuristico: ALGORITMO GENETICO 



import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# 1. DATOS: piezas [ancho, alto, area, cantidad]

problema1 = {
    "lamina": (40, 70),
    "piezas": [
        [21, 22, 582, 1], [31, 13, 403, 1], [9, 35, 315, 3],
        [9, 24, 216, 3], [30, 7, 210, 2], [11, 13, 143, 3],
        [10, 14, 140, 1], [14, 8, 110, 3], [12, 8, 94, 3],
        [13, 7, 90, 3],
    ],
}

problema2 = {
    "lamina": (50, 60),
    "piezas": [
        [31, 43, 1333, 4], [30, 41, 1230, 2], [29, 39, 1131, 4],
        [28, 38, 1064, 4], [27, 37, 999, 3], [26, 36, 936, 4],
        [25, 35, 875, 3], [24, 34, 816, 4], [33, 23, 759, 4],
        [22, 32, 704, 3], [31, 21, 651, 3], [29, 18, 522, 3],
        [17, 27, 459, 2], [15, 24, 360, 2], [16, 25, 400, 4],
        [15, 24, 360, 1], [23, 14, 322, 4], [21, 12, 252, 3],
        [19, 11, 209, 4], [9, 17, 153, 1],
    ],
}

problema3 = {
    "lamina": (132, 100),
    "piezas": [
        [18, 39, 702, 4], [13, 49, 637, 2], [27, 51, 1377, 1],
        [65, 31, 2015, 3], [45, 27, 1215, 2], [69, 21, 1449, 4],
        [21, 63, 1323, 2], [54, 41, 2214, 2], [41, 31, 1271, 1],
        [37, 22, 814, 1], [29, 54, 1566, 1], [47, 31, 1457, 2],
        [18, 31, 558, 3], [21, 17, 357, 1], [19, 53, 1007, 1],
        [13, 41, 533, 4], [37, 12, 444, 5], [19, 29, 551, 2],
        [67, 17, 1139, 1], [49, 31, 1519, 3], [31, 43, 1333, 1],
        [30, 41, 1230, 2], [29, 39, 1131, 1], [28, 38, 1064, 2],
        [27, 37, 999, 3], [26, 36, 936, 2], [25, 35, 875, 1],
        [24, 34, 816, 1], [33, 23, 759, 2], [22, 32, 704, 3],
    ],
}



# 2.DECODIFICAR: convertir un orden en una solucion factible

def decodificar(orden, lamina, piezas):
    W, H = lamina
    franjas = []            
    alto_usado = 0    
    
    # recorremos las piezas en el orden que nos dio el genetico
    for idx in orden:
        w, h, area, _ = piezas[idx]
        colocada = False

        #  INTENTO 1: meterla en una franja que YA existe 
        for franja in franjas:
            if franja["ancho_libre"] >= w and h <= franja["alto"]:  #permite meter piezas mas bajas que la franja (método inexacto)
                franja["piezas"].append(idx) 
                franja["ancho_libre"] -= w    
                colocada = True
                break      

        #  INTENTO 2: si no cupo, abrir una franja nueva si aún hay hueco
        if not colocada and alto_usado + h <= H:
            franjas.append({
                "alto": h,            
                "ancho_libre": W - w, 
                "piezas": [idx],      
            })
            alto_usado += h             
       
        # si no se colocó ni cabe en franja nueva, la pieza se descarta 

    return franjas   # devolvemos todas las franjas con sus piezas colocadas


# 3. FITNESS (te da el % de aprovechamiento)

def fitness(orden, lamina, piezas):
    W, H = lamina
    # convertimos el orden en franjas (usamos la funcion decodificar)
    franjas = decodificar(orden, lamina, piezas)
    area = 0
    # recorremos todas las franjas que se crearon
    for franja in franjas:
        
        # dentro de cada franja, recorremos sus piezas colocadas
        for idx in franja["piezas"]:
            area += piezas[idx][2]
            
    return 100 * area / (W * H)



# 4. CREAR UN INDIVIDUO: un orden aleatorio de piezas

def crear_individuo(piezas):
    genes = []                          

    # recorremos cada tipo de pieza 
    for i in range(len(piezas)):
        
        for _ in range(piezas[i][3]):
            genes.append(i)             

    random.shuffle(genes)   # orden aleatorio
    return genes                      



# 5. SELECCION

def seleccion(poblacion, lamina, piezas, k=3):
    '''
    torneo (elige el mejor de k al azar):
       Elige un padre para reproducirse: coge k individuos
       al azar y se queda con el mejor de ellos.

    '''
    competidores = random.sample(poblacion, k)

    # ordenamos esos k competidores por su fitness, de mayor a menor
    competidores.sort(key=lambda ind: fitness(ind, lamina, piezas),reverse=True)

    return competidores[0]



# 6. CRUCE: 
    
def cruce(padre1, padre2):
    '''
    order crossover (OX) - mezcla dos individuos
        Crea un Hijo combinando un trozo del padre 1 con el
        resto en el orden del padre2. Respeta cuantas veces
        aparece cada pieza.
        Hereda un trozo aleatorio del padre1 y rellena lo que falta siguiendo
        el orden del padre2, sin repetir piezas de más.

    '''

    n = len(padre1)

    a, b = sorted(random.sample(range(n), 2))  # 2 posicionas aleatorias

    hijo = [None] * n

    # Copiamos el segmento del padre1 en el hijo en las mismas posiciones
    hijo[a:b] = padre1[a:b] 

    pos = b % n #por si llega al final, empezar en 0

    #recorrido circular en el padre2 (empezamos en posicion b)
    for gen in padre2[b:] + padre2[:b]:

        # Cuántas veces debería aparecer esta pieza
        maximo = padre1.count(gen)

        # Cuántas veces ya está en el hijo
        actual = hijo.count(gen)

        if actual < maximo:
            
            # si posicion ocupada avanzamos, si no colocamos el gen en el hueco libre
            while hijo[pos] is not None:
                pos = (pos + 1) % n  # %n para dar la vuelta 

            hijo[pos] = gen
            
            # Avanzamos a la siguiente posición para la próxima inserción
            pos = (pos + 1) % n

    return hijo


# 7. MUTACION

def mutacion(individuo, prob=0.2):
    '''
    Intercambia dos posiciones al azar
        De vez en cuando cambia 2 piezas de sitio en el orden.
    '''
  
    if random.random() < prob:
        
        # elegimos 2 posiciones distintas al azar
        i, j = random.sample(range(len(individuo)), 2)

        # intercambiamos las piezas de esas 2 posiciones 
        individuo[i], individuo[j] = individuo[j], individuo[i]

    return individuo   

# 8. ALGORITMO GENETICO principal

def genetico(problema, n_poblacion=100, generaciones=200, prob_mutacion=0.2, elitismo=2):
    
    # sacamos los datos del problema
    lamina = problema["lamina"]            
    piezas = problema["piezas"]           

    #  Poblacion inicial: n individuos 
    poblacion = [crear_individuo(piezas) for _ in range(n_poblacion)]

    mejor_individuo = None                 
    mejor_fitness = -1                      
    historial = []                          

    # BUCLE PRINCIPAL
    for gen in range(generaciones):

        # ordenamos la poblacion por fitness, de mejor a peor
        poblacion.sort(key=lambda ind: fitness(ind, lamina, piezas), reverse=True)

        # miramos el fitness del mejor de esta generacion
        f = fitness(poblacion[0], lamina, piezas)

        # si es mejor que el record historico, lo guardamos
        if f > mejor_fitness:
            mejor_fitness = f
            mejor_individuo = poblacion[0][:]  

        # guardamos el mejor fitness hasta ahora 
        historial.append(mejor_fitness)

        # CREAR LA NUEVA GENERACION 
        nueva = poblacion[:elitismo]        # elitismo

        # rellenamos el resto de la poblacion con hijos nuevos
        while len(nueva) < n_poblacion:
            padre1 = seleccion(poblacion, lamina, piezas)   
            padre2 = seleccion(poblacion, lamina, piezas)  
            hijo = cruce(padre1, padre2)                    
            hijo = mutacion(hijo, prob_mutacion)          
            nueva.append(hijo)                             

        # la nueva generacion reemplaza a la anterior
        poblacion = nueva

    # devolvemos el mejor orden, su fitness y el historial completo
    return mejor_individuo, mejor_fitness, historial



# 9. DIBUJAR el patron de corte (CÓDIGO GENERADO COMPLETAMENTE CON IA)

def dibujar(nombre, orden, problema, fit, archivo):
    W, H = problema["lamina"]
    piezas = problema["piezas"]
    franjas = decodificar(orden, problema["lamina"], piezas)

    fig, ax = plt.subplots(figsize=(6, 7))
    ax.add_patch(patches.Rectangle((0, 0), W, H,
                 edgecolor="black", facecolor="#dddddd"))

    colores = plt.cm.tab20.colors
    y = 0
    for franja in franjas:
        x = 0
        for idx in franja["piezas"]:
            w, h, ar, _ = piezas[idx]
            ax.add_patch(patches.Rectangle((x, y), w, h,
                         edgecolor="black", facecolor=colores[idx % 20]))
            ax.text(x + w/2, y + h/2, str(idx),
                    ha="center", va="center", fontsize=8)
            x += w
        y += franja["alto"]

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.set_title("{} - Genetico: {:.2f}%".format(nombre, fit))
    plt.tight_layout()
    plt.savefig(archivo, dpi=120)
    plt.close()
    print("Imagen guardada:", archivo)


# 10. GRAFICA DE EVOLUCION (CÓDIGO GENERADO COMPLETAMENTE CON IA)

def dibujar_evolucion(historiales, nombres):
    plt.figure(figsize=(9, 5))
    for hist, nombre in zip(historiales, nombres):
        plt.plot(hist, linewidth=2, label=nombre)
    plt.xlabel("Generacion")
    plt.ylabel("Mejor aprovechamiento (%)")
    plt.title("Evolucion del Algoritmo Genetico")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("evolucion_genetico.png", dpi=120)
    plt.show()
    print("Grafica guardada: evolucion_genetico.png")


# 11. PROGRAMA PRINCIPAL: los 3 problemas

if __name__ == "__main__":
    random.seed(777)

    problemas = [problema1, problema2, problema3]
    nombres = ["Problema 1", "Problema 2", "Problema 3"]
    archivos = ["genetico1.png", "genetico2.png", "genetico3.png"]

    historiales = []

    for problema, nombre, archivo in zip(problemas, nombres, archivos):
        mejor, fit, hist = genetico(problema,
                                    n_poblacion=100,#200
                                    generaciones=50,#500 700
                                    prob_mutacion=0.4,#0.4
                                    elitismo=1)#4 1
        print("=" * 45)
        print("{} -> Aprovechamiento: {:.2f}%".format(nombre, fit))
        print("=" * 45)

        dibujar(nombre, mejor, problema, fit, archivo)
        historiales.append(hist)

    # grafica de evolucion de los 3 juntos
    dibujar_evolucion(historiales, nombres)