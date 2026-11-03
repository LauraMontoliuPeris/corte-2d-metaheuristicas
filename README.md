# Problema de corte 2D por etapas: GRASP + Búsqueda Tabú vs. Algoritmo Genético

Trabajo del Máster en Planificación y Gestión de Procesos Empresariales (Universitat de València).
Autoras: Laura Montoliu Peris y Aya Limouri Hazzaf · Profesor: Ramón Álvarez-Valdés

## El problema
Cortar una lámina rectangular en piezas de distintos tamaños (corte guillotina en dos etapas, caso inexacto)
maximizando el área aprovechada. Es un problema NP-hard, habitual en industrias del vidrio, la madera o el metal.

## Métodos
- **GRASP + Búsqueda Tabú:** construcción aleatorizada con lista restringida de candidatos (α = 0,8) y mejora con lista tabú y criterio de aspiración.
- **Algoritmo Genético:** permutaciones de piezas, selección por torneo, cruce OX adaptado a piezas repetidas, mutación por intercambio y elitismo.

## Resultados (aprovechamiento de la lámina)
| Problema | Lámina | GRASP-TS | Algoritmo Genético |
|---|---|---|---|
| 1 | 40 × 70 | 87,46 % | 90,54 % |
| 2 | 50 × 60 | 98,33 % | 98,33 % |
| 3 | 132 × 100 | 95,80 % | 98,69 % |
| **Media** | | **93,86 %** | **95,85 %** |

![Patrón de corte](img/genetico3.png)

## Cómo ejecutarlo
pip install matplotlib
python grasp_tabu.py
python algoritmo_genetico.py
