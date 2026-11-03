# -*- coding: utf-8 -*-
# Trabajo: Problema de corte 2D en dos etapas (caso inexacto)
# Metaheuristico: GRASP + TABU SEARCH
#   - Animacion de la MEJOR solucion distinguiendo que coloco GRASP y que Tabu
# Autor: (tu nombre)

import random
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# -------------------------------------------------------------
# 1. DATOS DE LOS PROBLEMAS (del anexo)
#    Cada pieza es: [ancho, alto, area, cantidad_maxima]
# -------------------------------------------------------------

problema1 = {
    "lamina": (40, 70),
    "piezas": [
        [21, 22, 582, 1],
        [31, 13, 403, 1],
        [9, 35, 315, 3],
        [9, 24, 216, 3],
        [30, 7, 210, 2],
        [11, 13, 143, 3],
        [10, 14, 140, 1],
        [14, 8, 110, 3],
        [12, 8, 94, 3],
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


# -------------------------------------------------------------
# 2. FUNCIONES AUXILIARES
# -------------------------------------------------------------

def calcular_area(franjas, piezas):
    # suma el area de todas las piezas colocadas
    total = 0
    for franja in franjas:
        for idx in franja["piezas"]:
            total += piezas[idx][2]
    return total


def contar_usadas(franjas, piezas):
    # cuenta cuantas piezas de cada tipo hemos usado
    usadas = [0] * len(piezas)
    for franja in franjas:
        for idx in franja["piezas"]:
            usadas[idx] += 1
    return usadas



# 3. FASE CONSTRUCTIVA (GRASP) por franjas

def construir_solucion(lamina, piezas, alpha):
    W, H = lamina
    disponibles = [p[3] for p in piezas]

    franjas = []
    alto_usado = 0

    while True:
        # piezas que todavia podemos colocar
        candidatas = []
        for i in range(len(piezas)):
            if disponibles[i] > 0 and piezas[i][1] <= (H - alto_usado):
                candidatas.append(i)

        if len(candidatas) == 0:
            break

        # construimos la RCL usando el area (las grandes primero)
        areas = [piezas[i][2] for i in candidatas]
        area_max = max(areas)
        area_min = min(areas)
        limite = area_max - alpha * (area_max - area_min) # si alpha = 0 solo entra la de area max
        rcl = [i for i in candidatas if piezas[i][2] >= limite]

        # elegimos una al azar de la RCL
        elegida = random.choice(rcl)
        w, h, area, _ = piezas[elegida]

        # intentamos colocarla en una franja existente
        colocada = False
        for franja in franjas:
            if franja["ancho_libre"] >= w and h <= franja["alto"]: #pieza entra
                franja["piezas"].append(elegida)
                franja["ancho_libre"] -= w
                colocada = True
                break #ya colocada no buscar mas franjas

        # si no cabe, abrimos una franja nueva
        if not colocada:
            if alto_usado + h <= H:
                franjas.append({
                    "alto": h,
                    "ancho_libre": W - w,
                    "piezas": [elegida],
                })
                alto_usado += h
            else:
                disponibles[elegida] = 0 #pieza no cabe 
                continue                 #pasar a siguiente

        disponibles[elegida] -= 1 #reducir el número de piezas disponibles de ese tipo

    return franjas



# 4. TABU SEARCH (busqueda local)


def tabu_search(franjas, lamina, piezas, iteraciones=30, duracion_tabu=5):
    usadas = contar_usadas(franjas, piezas)
    lista_tabu = []  # tipos de pieza prohibidos temporalmente

    for _ in range(iteraciones):
        mejor_movimiento = None
        mejor_ganancia = 0

        for f in range(len(franjas)):
            franja = franjas[f]
            for i in range(len(piezas)):
                w, h, area, cant = piezas[i]
                # definición de condiciones para poder añadir pieza a franja
                cabe = franja["ancho_libre"] >= w and h <= franja["alto"]
                hay_stock = usadas[i] < cant
                es_tabu = i in lista_tabu

                # aspiracion: si mejora mucho la soluciom, aunque sea tabu lo permitimos
                if cabe and hay_stock and (not es_tabu or area > mejor_ganancia):
                    if area > mejor_ganancia:
                        mejor_ganancia = area
                        mejor_movimiento = (f, i)
                        
        # si tabu search no ha conseguido mejorar grasp se sale 
        if mejor_movimiento is None:
            break



        f, i = mejor_movimiento
        franjas[f]["piezas"].append(i)             # meter en la franja
        franjas[f]["ancho_libre"] -= piezas[i][0]  # reducir espacio
        usadas[i] += 1                             # actualizar stock

        # actualizar lista tabú
        lista_tabu.append(i)
        if len(lista_tabu) > duracion_tabu:
            lista_tabu.pop(0)

    return franjas



# 5. ALGORITMO CONJUNTO: GRASP + TABU SEARCH


def grasp_tabu(problema, iteraciones=700000, alpha=0.8):
    lamina = problema["lamina"]
    piezas = problema["piezas"]

    mejor_franjas = None
    mejor_area = -1
    mejor_grasp_counts = None  # cuantas piezas de GRASP por franja (la mejor)

    for _ in range(iteraciones):
        # FASE 1: GRASP 
        sol = construir_solucion(lamina, piezas, alpha)
        # Apuntar cuantas piezas hay en cada franja ants de Tabu
        grasp_counts = [len(f["piezas"]) for f in sol]
        # FASE 2: Tabu Search rellena (añade al final de cada franja)
        sol = tabu_search(sol, lamina, piezas)

        area = calcular_area(sol, piezas)
        if area > mejor_area:
            mejor_area = area
            mejor_franjas = sol
            mejor_grasp_counts = grasp_counts

    return mejor_franjas, mejor_area, mejor_grasp_counts



# 6. MOSTRAR RESULTADOS 

def mostrar_resultado(nombre, problema, franjas, area):
    W, H = problema["lamina"]
    area_total = W * H
    aprovechamiento = 100 * area / area_total

    print("=" * 50)
    print("RESULTADO -", nombre)
    print("Lamina:", W, "x", H, "=", area_total)
    print("Area cortada:", area)
    print("Aprovechamiento: {:.2f} %".format(aprovechamiento))
    print("Numero de franjas:", len(franjas))
    print("=" * 50)
    print()



# 7. DIBUJAR EL PATRON DE CORTE (IA)


def dibujar(nombre, problema, franjas, area, archivo):
    W, H = problema["lamina"]
    piezas = problema["piezas"]

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.add_patch(patches.Rectangle((0, 0), W, H,
                 edgecolor="black", facecolor="#dddddd", linewidth=2))

    colores = plt.cm.tab20.colors
    y = 0
    for franja in franjas:
        x = 0
        for idx in franja["piezas"]:
            w, h, ar, _ = piezas[idx]
            ax.add_patch(patches.Rectangle((x, y), w, h,
                         edgecolor="black",
                         facecolor=colores[idx % 20], linewidth=1))
            ax.text(x + w/2, y + h/2, str(idx),
                    ha="center", va="center", fontsize=8, color="black")
            x += w
        y += franja["alto"]

    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    apr = 100 * area / (W * H)
    ax.set_title("{}  ({}x{})  -  Aprovechamiento: {:.2f}%".format(
                 nombre, W, H, apr))
    plt.tight_layout()
    plt.savefig(archivo, dpi=120)
    plt.close()
    print("Imagen guardada:", archivo)



# 9. PROGRAMA PRINCIPAL


if __name__ == "__main__":
    random.seed(777)

    # ---- calculamos las mejores soluciones ----
    f1, a1, g1 = grasp_tabu(problema1, iteraciones=5000, alpha=0.8)
    mostrar_resultado("PROBLEMA 1", problema1, f1, a1)

    f2, a2, g2 = grasp_tabu(problema2, iteraciones=5000, alpha=0.8)
    mostrar_resultado("PROBLEMA 2", problema2, f2, a2)

    f3, a3, g3 = grasp_tabu(problema3, iteraciones=5000, alpha=0.8)
    mostrar_resultado("PROBLEMA 3", problema3, f3, a3)

    # ---- guardamos imagenes estaticas (para la presentacion) ----
    dibujar("PROBLEMA 1", problema1, f1, a1, "corte1.png")
    dibujar("PROBLEMA 2", problema2, f2, a2, "corte2.png")
    dibujar("PROBLEMA 3", problema3, f3, a3, "corte3.png")


