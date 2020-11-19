# import datetime
# import time
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model
import numpy as np
import matplotlib.pyplot as plt
from ..Exploracion import *
from .some import *

dataset = list_principal("", "")
montoset = [float(elemento) for elemento in dataset["amount_list"]]
demandaset = [float(elemento) for elemento in dataset["demand_list"]]
dataset_normalizada_tipicada = get_valores_tipicos(demandaset, montoset)


# tiemposet = []

# for i in range(len(dataset["year_list"])):
#     tiemposet.append(
#         time.mktime(datetime.datetime.strptime("{0}/{1}/{2}".format(dataset["year_list"][i], dataset["month_list"][i], dataset["day_list"][i]), "%Y/%m/%d").timetuple()))


def regresion_polinomica(dataset_normalizada_tipicada):

    # Demanda del servicio como variable independiente
    X = np.reshape(dataset_normalizada_tipicada["X"], (-1, 1))

    # Monto recaudado como variable dependiente
    Y = dataset_normalizada_tipicada["Y"]

    # Separación de datasets en sets de entrenamiento y sets de prueba
    x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
        X, Y, test_size=0.2)

    # Definición del grado del polinomio
    regresion_polinomica = PolynomialFeatures(degree=3)

    # Tranformación de las características existentes en características de mayor grado
    x_entrenamiento_transformado = regresion_polinomica.fit_transform(
        x_entrenamiento)
    x_prueba_transformado = regresion_polinomica.fit_transform(x_prueba)

    # Definición del algoritmo a utilizar
    predictor = linear_model.LinearRegression()

    # Entrenamiento del modelo
    predictor.fit(x_entrenamiento_transformado, y_entrenamiento)

    # Realizo una predicción
    y_prediccion = predictor.predict(x_prueba_transformado)

    # Graficamos los datos junto con el modelo
    # plt.scatter(x_prueba, y_prueba)
    # plt.plot(x_prueba, y_prediccion, color='red', linewidth=1)
    # plt.show()

    # Resultados
    print('Pendiente: {0}'.format(predictor.coef_))
    print('Interseccion: {0}'.format(predictor.intercept_))
    print('Precisión: {0}'.format(predictor.score(
        x_entrenamiento_transformado, y_entrenamiento)))

    return dict(
        X_ENTRENAMIENTO=[X[0] for X in x_entrenamiento],
        X_PRUEBA=[X[0] for X in x_prueba],
        Y_ENTRENAMIENTO=y_entrenamiento,
        Y_PRUEBA=y_prueba,
        Y_PREDICCION=y_prediccion)


# regresion_polinomica(dataset_normalizada_tipicada)
