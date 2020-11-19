
from mysql.connector import MySQLConnection, Error

from ..Configuracion import get_db_config


def query(func):
    try:
        dbconfig = get_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()
        return func(cursor)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


# Obtener datasets para filtros


def list_distritos(cursor):

    cursor.execute("""SELECT * FROM DISTRITO""")
    rows = cursor.fetchall()

    dictionary = {}

    for row in rows:
        dictionary[row[0]] = row[1]

    return dictionary


def list_modelo_bus(cursor):

    cursor.execute(
        """SELECT DISTINCT B.MODELO FROM BUS B ORDER BY B.MODELO""")
    rows = cursor.fetchall()

    dictionary = {}
    i = 0

    for row in rows:
        dictionary[i] = row[0]
        i += 1

    return dictionary


def list_tipo_bus(cursor):

    cursor.execute(
        """SELECT DISTINCT IF(B.TIPO = 'A', 'alimentador', 'troncal') FROM BUS B ORDER BY B.TIPO""")
    rows = cursor.fetchall()

    dictionary = {}
    i = 0

    for row in rows:
        dictionary[i] = row[0]
        i += 1

    return dictionary


def list_color_bus(cursor):

    cursor.execute(
        """SELECT DISTINCT B.COLOR FROM BUS B ORDER BY B.COLOR""")
    rows = cursor.fetchall()

    dictionary = {}
    i = 0

    for row in rows:
        dictionary[i] = row[0]
        i += 1

    return dictionary


def list_rutas(cursor):

    cursor.execute("""SELECT * FROM RUTA""")
    rows = cursor.fetchall()

    dictionary = {}

    for row in rows:
        dictionary[row[0]] = row[1]

    return dictionary


def list_estaciones(cursor):

    cursor.execute("""SELECT * FROM ESTACION""")
    rows = cursor.fetchall()

    dictionary = {}

    for row in rows:
        dictionary[row[0]] = row[1]

    return dictionary


def list_tipo_estacion(cursor):

    cursor.execute(
        """SELECT DISTINCT E.TIPO FROM ESTACION E ORDER BY E.TIPO""")
    rows = cursor.fetchall()

    dictionary = {}
    i = 0

    for row in rows:
        dictionary[i] = row[0]
        i += 1

    return dictionary


def list_tipo_tarjeta(cursor):

    cursor.execute(
        """SELECT DISTINCT T.TIPO FROM TARJETA T ORDER BY T.TIPO""")
    rows = cursor.fetchall()

    dictionary = {}
    i = 0

    for row in rows:
        dictionary[i] = row[0]
        i += 1

    return dictionary


def list_periodo(cursor):

    cursor.execute(
        """SELECT MIN(T.FECHA), MAX(T.FECHA) FROM TRANSPORTE T""")
    row = cursor.fetchone()

    return {"1": row[0], "2": row[1]}


def list_principal(fecha_inicial, fecha_final):
    try:
        dbconfig = get_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        parameters = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final
        }

        filters = {
            "BY_DATE_RANGE": "AND P.FECHA BETWEEN CAST('{0}' AS DATE) AND CAST('{1}' AS DATE)".format(parameters["fecha_inicial"], parameters["fecha_final"]) if fecha_inicial and fecha_final else ""
        }

        query = """
            SELECT 
                YEAR(P.FECHA) AS ANIO, 
                MONTH(P.FECHA) AS MES, 
                DAY(P.FECHA) AS DIA, 
                SUM(P.TARIFA) AS MONTO, 
                COUNT(T.TRANSPORTE_ID) AS DEMANDA 
            FROM PAGO P, TRANSPORTE T
            WHERE
                YEAR(P.FECHA) = YEAR(T.FECHA)
                AND MONTH(P.FECHA) = MONTH(T.FECHA)
                AND DAY(P.FECHA) = DAY(T.FECHA)
                {0}
            GROUP BY YEAR(P.FECHA), MONTH(P.FECHA), DAY(P.FECHA) 
            ORDER BY YEAR(P.FECHA), MONTH(P.FECHA), DAY(P.FECHA)
            """.format(filters["BY_DATE_RANGE"])

        cursor.execute(query)

        rows = cursor.fetchall()

        year_list = []
        month_list = []
        day_list = []
        amount_list = []
        demand_list = []

        for row in rows:
            year_list.append(row[0])
            month_list.append(row[1])
            day_list.append(row[2])
            amount_list.append(row[3])
            demand_list.append(row[4])

        return dict(year_list=year_list, month_list=month_list, day_list=day_list, amount_list=amount_list, demand_list=demand_list)

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()

# Datasets para gráficas


def list_ganancia_tiempo(fecha_inicial, fecha_final, estaciones_id, tipos_estacion_nombre, tipos_tarjeta_nombre):

    try:
        dbconfig = get_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        parameters = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final,
            'estaciones_id': ', '.join(str(estacion_id) for estacion_id in estaciones_id),
            'tipos_estacion_nombre': ', '.join('"{0}"'.format(tipo_estacion)
                                               for tipo_estacion in tipos_estacion_nombre),
            'tipos_tarjeta_nombre': ', '.join('"{0}"'.format(tipo_tarjeta) for tipo_tarjeta in tipos_tarjeta_nombre)
        }

        filters = {
            "BY_DATE_RANGE": "P.FECHA BETWEEN CAST('{0}' AS DATE) AND CAST('{1}' AS DATE) AND".format(parameters["fecha_inicial"], parameters["fecha_final"]) if fecha_inicial and fecha_final else "",
            "BY_ESTACION_ID": "E.ESTACION_ID IN({0}) AND".format(parameters["estaciones_id"]) if estaciones_id else "",
            "BY_ESTACION_TIPO": "E.TIPO IN({0}) AND".format(parameters["tipos_estacion_nombre"]) if tipos_estacion_nombre else "",
            "BY_TARJETA_TIPO": "T.TIPO IN({0}) AND".format(parameters["tipos_tarjeta_nombre"]) if tipos_tarjeta_nombre else "",
        }

        query = """
            SELECT
                YEAR(P.FECHA) AS "YEAR",
                MONTH(P.FECHA) AS "MONTH",
                SUM(P.TARIFA) AS "PROFIT"
            FROM PAGO P, TARJETA T, RULETA R, ESTACION E
            WHERE
                P.TARJETA_ID = T.TARJETA_ID AND
                P.RULETA_ID = R.RULETA_ID AND
                R.ESTACION_ID = E.ESTACION_ID AND
                {0}
                {1}
                {2}
                {3}
                YEAR(P.FECHA) > 0
            GROUP BY YEAR(P.FECHA), MONTH(P.FECHA)
            ORDER BY YEAR(P.FECHA), MONTH(P.FECHA)
            """.format(filters["BY_DATE_RANGE"], filters["BY_ESTACION_ID"], filters["BY_ESTACION_TIPO"], filters["BY_TARJETA_TIPO"])

        cursor.execute(query)

        rows = cursor.fetchall()

        year_list = []
        month_list = []
        profit_list = []

        for row in rows:
            year_list.append(row[0])
            month_list.append(row[1])
            profit_list.append(row[2])

        return [year_list, month_list, profit_list]

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


def list_demanda_geo(fecha_inicial, fecha_final, distritos, modelo_bus, tipo_bus, color_bus, rutas, estaciones, tipo_estacion, tipo_tarjeta):

    try:
        dbconfig = get_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        parameters = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final,
            'distritos': ', '.join(str(distrito) for distrito in distritos),
            'modelo_bus': ', '.join('"{0}"'.format(modelo) for modelo in modelo_bus),
            'tipo_bus': ', '.join('"{0}"'.format(tipo[0].upper()) for tipo in tipo_bus),
            'color_bus': ', '.join('"{0}"'.format(color) for color in color_bus),
            'rutas': ', '.join(str(ruta) for ruta in rutas),
            'estaciones': ', '.join(str(estacion) for estacion in estaciones),
            'tipo_estacion': ', '.join('"{0}"'.format(tipo) for tipo in tipo_estacion),
            'tipo_tarjeta': ', '.join('"{0}"'.format(tipo) for tipo in tipo_tarjeta)
        }

        filters = {
            "BY_DATE_RANGE": "AND T.FECHA BETWEEN CAST('{0}' AS DATE) AND CAST('{1}' AS DATE)".format(parameters["fecha_inicial"], parameters["fecha_final"]) if fecha_inicial and fecha_final else "",
            "BY_DISTRITO": "AND D.DISTRITO_ID IN({0})".format(parameters["distritos"]) if distritos else "",
            "BY_BUS_MODELO": "AND B.MODELO IN({0})".format(parameters["modelo_bus"]) if modelo_bus else "",
            "BY_BUS_TIPO": "AND B.TIPO IN({0})".format(parameters["tipo_bus"]) if tipo_bus else "",
            "BY_BUS_COLOR": "AND B.COLOR IN({0})".format(parameters["color_bus"]) if color_bus else "",
            "BY_RUTA": "AND R.RUTA_ID IN({0})".format(parameters["rutas"]) if rutas else "",
            "BY_ESTACION": "AND E.ESTACION_ID IN({0})".format(parameters["estaciones"]) if estaciones else "",
            "BY_ESTACION_TIPO": "AND E.TIPO IN({0})".format(parameters["tipo_estacion"]) if tipo_estacion else "",
            "BY_TARJETA_TIPO": "AND TJ.TIPO IN({0})".format(parameters["tipo_tarjeta"]) if tipo_tarjeta else ""
        }

        query = """
            SELECT
                C.LATITUD AS LATITUD,
                C.LONGITUD AS LONGITUD,
                CONCAT(E.NOMBRE, ': ', COUNT(T.TRANSPORTE_ID)) AS ESTACION_DEMANDA
            FROM BUS B, TRANSPORTE T, RUTA R, RUTA_HAS_ESTACION RE, ESTACION E, TARJETA TJ, DISTRITO D, COORDENADA C
            WHERE
                B.BUS_ID = T.BUS_ID
                AND T.RUTA_ID = R.RUTA_ID
                AND R.RUTA_ID = RE.RUTA_ID
                AND RE.ESTACION_ID = E.ESTACION_ID
                AND TJ.ESTACION_ID = E.ESTACION_ID
                AND D.DISTRITO_ID = E.DISTRITO_ID
                AND C.ESTACION_ID = E.ESTACION_ID
                {0}
                {1}
                {2}
                {3}
                {4}
                {5}
                {6}
                {7}
                {8}
            GROUP BY C.LATITUD, C.LONGITUD
            """.format(filters["BY_DATE_RANGE"], filters["BY_DISTRITO"], filters["BY_BUS_MODELO"], filters["BY_BUS_TIPO"], filters["BY_BUS_COLOR"], filters["BY_RUTA"], filters["BY_ESTACION"], filters["BY_ESTACION_TIPO"], filters["BY_TARJETA_TIPO"])

        cursor.execute(query)

        rows = cursor.fetchall()

        latitud_list = []
        longitud_list = []
        estacion_demanda_list = []

        for row in rows:
            latitud_list.append(row[0])
            longitud_list.append(row[1])
            estacion_demanda_list.append(row[2])

        return [latitud_list, longitud_list, estacion_demanda_list]

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


def list_demanda_tiempo(fecha_inicial, fecha_final, distritos, modelo_bus, tipo_bus, color_bus, rutas, estaciones, tipo_estacion, tipo_tarjeta):

    try:
        dbconfig = get_db_config()
        conn = MySQLConnection(**dbconfig)
        cursor = conn.cursor()

        parameters = {
            'fecha_inicial': fecha_inicial,
            'fecha_final': fecha_final,
            'distritos': ', '.join(str(distrito) for distrito in distritos),
            'modelo_bus': ', '.join('"{0}"'.format(modelo) for modelo in modelo_bus),
            'tipo_bus': ', '.join('"{0}"'.format(tipo[0].upper()) for tipo in tipo_bus),
            'color_bus': ', '.join('"{0}"'.format(color) for color in color_bus),
            'rutas': ', '.join(str(ruta) for ruta in rutas),
            'estaciones': ', '.join(str(estacion) for estacion in estaciones),
            'tipo_estacion': ', '.join('"{0}"'.format(tipo) for tipo in tipo_estacion),
            'tipo_tarjeta': ', '.join('"{0}"'.format(tipo) for tipo in tipo_tarjeta)
        }

        filters = {
            "BY_DATE_RANGE": "AND T.FECHA BETWEEN CAST('{0}' AS DATE) AND CAST('{1}' AS DATE)".format(parameters["fecha_inicial"], parameters["fecha_final"]) if fecha_inicial and fecha_final else "",
            "BY_DISTRITO": "AND D.DISTRITO_ID IN({0})".format(parameters["distritos"]) if distritos else "",
            "BY_BUS_MODELO": "AND B.MODELO IN({0})".format(parameters["modelo_bus"]) if modelo_bus else "",
            "BY_BUS_TIPO": "AND B.TIPO IN({0})".format(parameters["tipo_bus"]) if tipo_bus else "",
            "BY_BUS_COLOR": "AND B.COLOR IN({0})".format(parameters["color_bus"]) if color_bus else "",
            "BY_RUTA": "AND R.RUTA_ID IN({0})".format(parameters["rutas"]) if rutas else "",
            "BY_ESTACION": "AND E.ESTACION_ID IN({0})".format(parameters["estaciones"]) if estaciones else "",
            "BY_ESTACION_TIPO": "AND E.TIPO IN({0})".format(parameters["tipo_estacion"]) if tipo_estacion else "",
            "BY_TARJETA_TIPO": "AND TJ.TIPO IN({0})".format(parameters["tipo_tarjeta"]) if tipo_tarjeta else ""
        }

        query = """
            SELECT
                YEAR(T.FECHA),
                MONTH(T.FECHA),
                COUNT(T.TRANSPORTE_ID)AS DEMANDA
            FROM BUS B, TRANSPORTE T, RUTA R, RUTA_HAS_ESTACION RE, ESTACION E, TARJETA TJ, DISTRITO D, COORDENADA C
            WHERE
                B.BUS_ID = T.BUS_ID
                AND T.RUTA_ID = R.RUTA_ID
                AND R.RUTA_ID = RE.RUTA_ID
                AND RE.ESTACION_ID = E.ESTACION_ID
                AND TJ.ESTACION_ID = E.ESTACION_ID
                AND D.DISTRITO_ID = E.DISTRITO_ID
                AND C.ESTACION_ID = E.ESTACION_ID
                {0}
                {1}
                {2}
                {3}
                {4}
                {5}
                {6}
                {7}
                {8}
            GROUP BY YEAR(T.FECHA), MONTH(T.FECHA)
            ORDER BY YEAR(T.FECHA), MONTH(T.FECHA)
            """.format(filters["BY_DATE_RANGE"], filters["BY_DISTRITO"], filters["BY_BUS_MODELO"], filters["BY_BUS_TIPO"], filters["BY_BUS_COLOR"], filters["BY_RUTA"], filters["BY_ESTACION"], filters["BY_ESTACION_TIPO"], filters["BY_TARJETA_TIPO"])

        cursor.execute(query)

        rows = cursor.fetchall()

        year_list = []
        month_list = []
        demanda_list = []

        for row in rows:
            year_list.append(row[0])
            month_list.append(row[1])
            demanda_list.append([row[0], row[1], row[2]])

        year_list = list(dict.fromkeys(year_list))
        month_list = list(dict.fromkeys(month_list))

        demanda2d = []

        for i in range(len(year_list)):
            demanda2d.append([])
            for j in range(len(month_list)):
                for demanda in demanda_list:
                    if demanda[0] == year_list[i] and demanda[1] == month_list[j]:
                        demanda2d[i].append(demanda[2])
                        break

        print(year_list)
        print(month_list)
        print(demanda2d)
        return [year_list, month_list, demanda2d]

    except Error as e:
        print(e)

    finally:
        cursor.close()
        conn.close()


list_demanda_tiempo("", "", [], [], [], [], [], [], [], [])
