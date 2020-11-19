# Basado en https://relopezbriega.github.io/blog/2015/06/27/probabilidad-y-estadistica-con-python/
# http://www.damienfrancois.be/blog/files/modelperfcheatsheet.pdf

import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from ..Exploracion import *

# Datos de prueba

dataset = list_principal("", "")
montoset = [float(elemento) for elemento in dataset["amount_list"]]
demandaset = [float(elemento) for elemento in dataset["demand_list"]]
# recargaset = query(list_recarga)

# Funciones de Estadistica Descriptiva


def get_valor_maximo(lista):
    return max(lista)


def get_valor_minimo(lista):
    return min(lista)


def get_media_aritmetica(lista):
    return sum(lista) / len(lista)


def get_desviacion_respecto_media(lista):
    media_aritmetica = get_media_aritmetica(lista)
    return [elemento - media_aritmetica for elemento in lista]


def get_varianza(lista):
    desviacion_media = get_desviacion_respecto_media(lista)
    desviacion_media_2 = [
        elemento ** 2 for elemento in desviacion_media]
    return sum(desviacion_media_2) / len(desviacion_media_2)


def get_desviacion_tipica(lista):
    return get_varianza(lista) ** .5


def get_moda(lista):
    return max(lista, key=lista.count)


def get_mediana(lista):
    return sorted(lista)[int(len(lista) / 2)]


def get_correlacion(lista_1, lista_2):
    desviacion_lista_1 = get_desviacion_respecto_media(lista_1)
    desviacion_lista_2 = get_desviacion_respecto_media(lista_2)
    desviacion_lista_1_x_desviacion_lista_2 = [elemento_1 * elemento_2 for elemento_1,
                                               elemento_2 in zip(desviacion_lista_1, desviacion_lista_2)]
    sum_desviacion_lista_1_x_desviacion_lista_2 = sum(
        desviacion_lista_1_x_desviacion_lista_2)

    desviacion_cuadrada_lista_1 = [elemento **
                                   2 for elemento in desviacion_lista_1]
    desviacion_cuadrada_lista_2 = [elemento **
                                   2 for elemento in desviacion_lista_2]
    raiz_suma_desviacion_cuadrada_lista_1 = float(
        sum(desviacion_cuadrada_lista_1)) ** 0.5
    raiz_suma_desviacion_cuadrada_lista_2 = float(
        sum(desviacion_cuadrada_lista_2)) ** 0.5

    return sum_desviacion_lista_1_x_desviacion_lista_2 / (raiz_suma_desviacion_cuadrada_lista_1 * raiz_suma_desviacion_cuadrada_lista_2)


def get_covarianza(lista_1, lista_2):
    desviacion_lista_1 = get_desviacion_respecto_media(lista_1)
    desviacion_lista_2 = get_desviacion_respecto_media(lista_2)
    lista_1_x_lista_2 = [elemento_1 * elemento_2 for elemento_1,
                         elemento_2 in zip(desviacion_lista_1, desviacion_lista_2)]
    return sum(lista_1_x_lista_2) / len(lista_1_x_lista_2)


def get_cuartil(numero_cuartil, lista):
    lista = sorted(lista, key=float)
    tamaño_muestra = len(lista) if len(lista) % 2 == 0 else len(lista) + 1
    categorias = [float(element) for element in list(dict.fromkeys(lista))]
    frecuencias_absolutas = [float(lista.count(element))
                             for element in categorias]
    frecuencias_absolutas_acumuladas = [
        float(sum(frecuencias_absolutas[0: i + 1])) for i in range(0, len(frecuencias_absolutas))]
    cuartil = numero_cuartil * tamaño_muestra / 4

    # print("Tamaño muestra: {0}".format(tamaño_muestra))
    # print("Categorias: {0}".format(categorias))
    # print("Frecuencias absolutas: {0}".format(frecuencias_absolutas))
    # print("Frecuencias absolutas acumuladas: {0}".format(
    #     frecuencias_absolutas_acumuladas))
    # print("Valor de Cuartil: {0}".format(cuartil))

    if cuartil in frecuencias_absolutas_acumuladas:
        return categorias[frecuencias_absolutas_acumuladas.index(cuartil)]
    else:
        posicion_categoria = [i for i in range(1, len(frecuencias_absolutas_acumuladas) - 1) if cuartil >
                              frecuencias_absolutas_acumuladas[i - 1] and cuartil < frecuencias_absolutas_acumuladas[i + 1]]
        limite_inferior = categorias[posicion_categoria[0]]
        limite_superior = categorias[posicion_categoria[0] +
                                     1] if categorias[posicion_categoria[0] + 1] else categorias[posicion_categoria[0]]

        # print("Posicion: {0}".format(posicion_categoria))
        # print("Inferior: {0}".format(limite_inferior))
        # print("Superior: {0}".format(limite_superior))
        return limite_inferior + (limite_superior - limite_inferior) * ((cuartil - frecuencias_absolutas_acumuladas[posicion_categoria[0] - 1]) / (
            frecuencias_absolutas_acumuladas[posicion_categoria[0]] - frecuencias_absolutas_acumuladas[posicion_categoria[0] - 1]))


# Preparacion de datos


def get_valores_atipicos(X, Y):
    cuartil_1 = get_cuartil(1, Y)
    cuartil_3 = get_cuartil(3, Y)
    rango_intercuartil = cuartil_3 - cuartil_1
    limite_superior = cuartil_3 + (1.5 * rango_intercuartil)
    limite_inferior = cuartil_1 - (1.5 * rango_intercuartil)

    nuevo_X = []
    nuevo_Y = []

    for i in range(len(Y)):
        if Y[i] < limite_inferior or Y[i] > limite_superior:
            nuevo_X.append(normalizar(X, X[i]))
            nuevo_Y.append(normalizar(Y, Y[i]))

    return dict(X=nuevo_X, Y=nuevo_Y)


def get_valores_tipicos(X, Y):
    cuartil_1 = get_cuartil(1, Y)
    cuartil_3 = get_cuartil(3, Y)
    rango_intercuartil = cuartil_3 - cuartil_1
    limite_superior = cuartil_3 + (1.5 * rango_intercuartil)
    limite_inferior = cuartil_1 - (1.5 * rango_intercuartil)

    nuevo_X = []
    nuevo_Y = []

    for i in range(len(Y)):
        if Y[i] > limite_inferior and Y[i] < limite_superior:
            nuevo_X.append(normalizar(X, X[i]))
            nuevo_Y.append(normalizar(Y, Y[i]))

    return dict(X=nuevo_X, Y=nuevo_Y)


def normalizar(lista, elemento):
    valor_minimo = get_valor_minimo(lista)
    valor_maximo = get_valor_maximo(lista)
    return (elemento - valor_minimo)/(valor_maximo-valor_minimo)


def get_lista_normalizada(lista):
    valor_minimo = get_valor_minimo(lista)
    valor_maximo = get_valor_maximo(lista)
    return [(elemento - valor_minimo)/(valor_maximo-valor_minimo) for elemento in lista]


def get_lista_estandarizada(lista):
    media_aritmetica = get_media_aritmetica(lista)
    desviacion_tipica = get_desviacion_tipica(lista)
    return [(elemento - media_aritmetica)/desviacion_tipica for elemento in lista]


# Modelo de regresión polinómica

dataset = get_valores_atipicos(demandaset, montoset)
# print(dataset)
for i in range(len(dataset["Y"])):
    print("{0},{1}".format(dataset["X"][i], dataset["Y"][i]))

# print("Maximo: {0}".format(get_valor_maximo(montoset)))
# print("Minimo: {0}".format(get_valor_minimo(montoset)))
# print("Media aritmetica: {0}".format(get_media_aritmetica(montoset)))
# print("Desviacion media: {0}".format(get_desviacion_respecto_media(montoset)))
# print("Varianza: {0}".format(get_varianza(montoset)))
# print("Desviacion tipica: {0}".format(get_desviacion_tipica(montoset)))
# print("Moda: {0}".format(get_moda(montoset)))
# print("Mediana: {0}".format(get_mediana(montoset)))
# print("Correlacion: {0}".format(get_correlacion(montoset, demandaset)))
# print("Covarianza: {0}".format(get_covarianza(montoset, demandaset)))
# print("Primer cuartil: {0}".format(get_cuartil(1, montoset)))
# print("Tercer cuartil: {0}".format(get_cuartil(3, montoset)))
# print("Valores atipicos: {0}".format(get_valores_atipicos(montoset)))
# print("Valores tipicos: {0}".format(get_valores_tipicos(montoset)))
# print("Normalizacion: {0}".format(get_lista_normalizada(montoset)))
# print("Estandarizacion: {0}".format(get_lista_estandarizada(montoset)))
