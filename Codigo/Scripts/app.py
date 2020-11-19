import pickle
import copy
import pathlib
import dash
import math
import time
import datetime as dt
import pandas as pd
from dash.dependencies import Input, Output, State, ClientsideFunction
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn import datasets, linear_model
import numpy as np
from dateutil.relativedelta import relativedelta

from ..Exploracion import *
from ..Modelo import *

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

server = app.server

# Filters

PERIODO = query(list_periodo)
DISTRITOS = query(list_distritos)
MODELO_BUS = query(list_modelo_bus)
TIPO_BUS = query(list_tipo_bus)
COLOR_BUS = query(list_color_bus)
RUTAS = query(list_rutas)
ESTACIONES = query(list_estaciones)
TIPO_ESTACION = query(list_tipo_estacion)
TIPO_TARJETA = query(list_tipo_tarjeta)

# Adapters

distrito_options = [
    {"label": str(DISTRITOS[distrito]), "value": str(distrito)}
    for distrito in DISTRITOS
]

modelo_bus_options = [
    {"label": str(MODELO_BUS[modelo_bus]),
     "value": str(MODELO_BUS[modelo_bus])}
    for modelo_bus in MODELO_BUS
]

tipo_bus_options = [
    {"label": str(TIPO_BUS[tipo_bus]), "value": str(TIPO_BUS[tipo_bus])}
    for tipo_bus in TIPO_BUS
]

color_bus_options = [
    {"label": str(COLOR_BUS[color_bus]), "value": str(COLOR_BUS[color_bus])}
    for color_bus in COLOR_BUS
]

ruta_options = [
    {"label": str(RUTAS[ruta]), "value": str(ruta)}
    for ruta in RUTAS
]

estacion_options = [
    {"label": str(ESTACIONES[estacion]), "value": str(estacion)}
    for estacion in ESTACIONES
]

tipo_estacion_options = [
    {"label": str(TIPO_ESTACION[tipo_estacion]),
     "value": str(TIPO_ESTACION[tipo_estacion])}
    for tipo_estacion in TIPO_ESTACION
]

tipo_tarjeta_options = [
    {"label": str(TIPO_TARJETA[tipo_tarjeta]),
     "value": str(TIPO_TARJETA[tipo_tarjeta])}
    for tipo_tarjeta in TIPO_TARJETA
]

# Conversiones de fechas para filtro slider

daterange = pd.date_range(start=PERIODO["1"].strftime(
    '%Y/%m/%d'), end=PERIODO["2"].strftime('%Y/%m/%d'), freq='W')


def unix_time_millis(dt):
    ''' Convert datetime to unix timestamp '''
    return int(time.mktime(dt.timetuple()))


def unix_to_datetime(unix):
    ''' Convert unix timestamp to datetime. '''
    return pd.to_datetime(unix, unit='s')


def get_marks(start, end, nth=100):
    ''' Returns the marks for labeling.
        Every Nth value will be used.
    '''

    result = {}
    for i, date in enumerate(daterange):
        if(i % nth == 1):
            result[unix_time_millis(date)] = str(date.strftime('%Y'))

    return result


# Create app layout
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("metropolitano_logo.svg"),
                            id="plotly-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Servicio de Transporte Público",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Metropolitano Lima Perú", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("GitHub", id="learn-more-button"),
                            href="https://github.com/waltercueva/m1-20192-g3",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Periodo",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id='rangeslider_fecha',
                            updatemode='mouseup',
                            min=unix_time_millis(daterange.min()),
                            max=unix_time_millis(daterange.max()),
                            value=[unix_time_millis(daterange.min()),
                                   unix_time_millis(daterange.max())],
                            marks=get_marks(daterange.min(), daterange.max()),
                            tooltip={"always_visible": False,
                                     "placement": "top"},
                            allowCross=False,
                            className="dcc_control",
                        ),
                        html.Hr(style={"margin-bottom": "10px"}),
                        html.P(
                            "Distritos",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_distritos",
                            multi=True,
                            options=distrito_options,
                            # value=list(DISTRITOS.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Modelo del bus",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_modelo_bus",
                            multi=True,
                            options=modelo_bus_options,
                            # value=list(MODELO_BUS.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Tipo del bus",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_tipo_bus",
                            multi=True,
                            options=tipo_bus_options,
                            # value=list(TIPO_BUS.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Color del bus",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_color_bus",
                            multi=True,
                            options=color_bus_options,
                            # value=list(COLOR_BUS.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Rutas",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_rutas",
                            multi=True,
                            options=ruta_options,
                            # value=list(RUTAS.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Estaciones",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_estaciones",
                            multi=True,
                            options=estacion_options,
                            # value=list(ESTACIONES.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Tipo de estación",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_tipo_estacion",
                            multi=True,
                            options=tipo_estacion_options,
                            # value=list(TIPO_ESTACION.keys()),
                            className="dcc_control",
                        ),
                        html.P(
                            "Tarifa",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="dropdown_tipo_tarjeta",
                            multi=True,
                            options=tipo_tarjeta_options,
                            # value=list(TIPO_TARJETA.keys()),
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="scatter3d_ganancias_tiempo")],
                            className="pretty_container"),
                        html.Div(
                            [dcc.Graph(id="scattermapbox_demanda_geo")],
                            className="pretty_container"),
                        html.Div(
                            [dcc.Graph(id="surface_demanda_tiempo")],
                            className="pretty_container"),
                        html.Div(
                            [dcc.Graph(
                                id="scatter_regresion_polinomica_demanda_monto")],
                            className="pretty_container"),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        )
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


@app.callback(
    Output("scatter_regresion_polinomica_demanda_monto", "figure"),
    [
        Input("rangeslider_fecha", "value")
    ]
)
def scatter_regresion_polinomica_demanda_monto(rangeslider_fecha):

    fecha_inicial = unix_to_datetime(rangeslider_fecha[0])
    fecha_final = unix_to_datetime(rangeslider_fecha[1])
    DATASET = list_principal(fecha_inicial, fecha_final)
    montoset = [float(elemento) for elemento in DATASET["amount_list"]]
    demandaset = [float(elemento) for elemento in DATASET["demand_list"]]
    dataset_normalizada_tipicada = get_valores_tipicos(demandaset, montoset)

    result = regresion_polinomica(dataset_normalizada_tipicada)

    figure = go.Figure()

    figure.add_trace(go.Scatter(
        x=result["X_ENTRENAMIENTO"], y=result["Y_ENTRENAMIENTO"], mode='markers', name='Entrenamiento'))
    figure.add_trace(go.Scatter(
        x=result["X_PRUEBA"], y=result["Y_PRUEBA"], mode='markers', name='Prueba'))
    figure.add_trace(go.Scatter(
        x=result["X_PRUEBA"], y=result["Y_PREDICCION"], mode='markers', name='Prediccion', marker_size=10))
    figure.update_layout(
        title="Proyección - Monto recaudado vs Demanda del servicio",
        autosize=True,
        hovermode='closest',
        margin=dict(l=30, r=30, b=40, t=40),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9"
    )

    return figure


@app.callback(
    Output("scatter3d_ganancias_tiempo", "figure"),
    [
        Input("rangeslider_fecha", "value"),
        Input("dropdown_estaciones", "value"),
        Input("dropdown_tipo_estacion", "value"),
        Input("dropdown_tipo_tarjeta", "value"),
    ],
)
def scatter3d_ganancias_timpo(rangeslider_fecha, dropdown_estaciones, dropdown_tipo_estacion, dropdown_tipo_tarjeta):

    fecha_inicial = unix_to_datetime(rangeslider_fecha[0])
    fecha_final = unix_to_datetime(rangeslider_fecha[1])
    estaciones_id = dropdown_estaciones if dropdown_estaciones else []
    tipos_estacion_nombre = dropdown_tipo_estacion if dropdown_tipo_estacion else []
    tipos_tarjeta_nombre = dropdown_tipo_tarjeta if dropdown_tipo_tarjeta else []

    GANANCIA_TIEMPO = list_ganancia_tiempo(
        fecha_inicial, fecha_final, estaciones_id, tipos_estacion_nombre, tipos_tarjeta_nombre)

    figure = go.Figure(
        data=[
            go.Scatter3d(
                x=GANANCIA_TIEMPO[0],
                y=GANANCIA_TIEMPO[1],
                z=GANANCIA_TIEMPO[2],
                mode="markers",  # lines+markers
                marker=dict(
                    size=7,
                    color=GANANCIA_TIEMPO[2],
                    symbol="circle",
                    colorscale='Viridis',
                    opacity=0.8
                )
            )
        ],
        layout=go.Layout(
            title="Ganancias vs. Tiempo",
            autosize=True,
            margin=dict(l=30, r=30, b=40, t=40),
            hovermode="closest",
            plot_bgcolor="#F9F9F9",
            paper_bgcolor="#F9F9F9",
            scene=dict(
                xaxis=dict(
                    title="Año", showgrid=True, zeroline=False, showticklabels=False),
                yaxis=dict(
                    title="Mes", showgrid=True, zeroline=False, showticklabels=False),
                zaxis=dict(title="Ganancia (S/)", showgrid=True, zeroline=False, showticklabels=False))
        )
    )
    return figure


@app.callback(
    Output("scattermapbox_demanda_geo", "figure"),
    [
        Input("rangeslider_fecha", "value"),
        Input("dropdown_distritos", "value"),
        Input("dropdown_modelo_bus", "value"),
        Input("dropdown_tipo_bus", "value"),
        Input("dropdown_color_bus", "value"),
        Input("dropdown_rutas", "value"),
        Input("dropdown_estaciones", "value"),
        Input("dropdown_tipo_estacion", "value"),
        Input("dropdown_tipo_tarjeta", "value"),
    ],
)
def scattermapbox_demanda_geo(
        rangeslider_fecha,
        dropdown_distritos,
        dropdown_modelo_bus,
        dropdown_tipo_bus,
        dropdown_color_bus,
        dropdown_rutas,
        dropdown_estaciones,
        dropdown_tipo_estacion,
        dropdown_tipo_tarjeta):
    fecha_inicial = unix_to_datetime(rangeslider_fecha[0])
    fecha_final = unix_to_datetime(rangeslider_fecha[1])
    distritos = dropdown_distritos if dropdown_distritos else []
    modelo_bus = dropdown_modelo_bus if dropdown_modelo_bus else []
    tipo_bus = dropdown_tipo_bus if dropdown_tipo_bus else []
    color_bus = dropdown_color_bus if dropdown_color_bus else []
    rutas = dropdown_rutas if dropdown_rutas else []
    estaciones = dropdown_estaciones if dropdown_estaciones else []
    tipo_estacion = dropdown_tipo_estacion if dropdown_tipo_estacion else []
    tipo_tarjeta = dropdown_tipo_tarjeta if dropdown_tipo_tarjeta else []

    DEMANDA_GEO = list_demanda_geo(fecha_inicial, fecha_final, distritos, modelo_bus,
                                   tipo_bus, color_bus, rutas, estaciones, tipo_estacion, tipo_tarjeta)

    figure = go.Figure(
        go.Scattermapbox(
            lat=DEMANDA_GEO[0],
            lon=DEMANDA_GEO[1],
            text=DEMANDA_GEO[2],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10
            )
        )
    )

    figure.update_layout(
        title="Demanda del servicio",
        autosize=True,
        hovermode='closest',
        margin=dict(l=30, r=30, b=40, t=40),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F9F9F9",
        mapbox=go.layout.Mapbox(
            accesstoken="pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w",
            pitch=0,
            bearing=0,
            style="light",
            center=go.layout.mapbox.Center(
                lat=-12.044708,
                lon=-77.042387
            ),
            zoom=10
        )
    )

    return figure


@app.callback(
    Output("surface_demanda_tiempo", "figure"),
    [
        Input("rangeslider_fecha", "value"),
        Input("dropdown_distritos", "value"),
        Input("dropdown_modelo_bus", "value"),
        Input("dropdown_tipo_bus", "value"),
        Input("dropdown_color_bus", "value"),
        Input("dropdown_rutas", "value"),
        Input("dropdown_estaciones", "value"),
        Input("dropdown_tipo_estacion", "value"),
        Input("dropdown_tipo_tarjeta", "value"),
    ],
)
def surface_demanda_tiempo(
        rangeslider_fecha,
        dropdown_distritos,
        dropdown_modelo_bus,
        dropdown_tipo_bus,
        dropdown_color_bus,
        dropdown_rutas,
        dropdown_estaciones,
        dropdown_tipo_estacion,
        dropdown_tipo_tarjeta):
    fecha_inicial = unix_to_datetime(rangeslider_fecha[0])
    fecha_final = unix_to_datetime(rangeslider_fecha[1])
    distritos = dropdown_distritos if dropdown_distritos else []
    modelo_bus = dropdown_modelo_bus if dropdown_modelo_bus else []
    tipo_bus = dropdown_tipo_bus if dropdown_tipo_bus else []
    color_bus = dropdown_color_bus if dropdown_color_bus else []
    rutas = dropdown_rutas if dropdown_rutas else []
    estaciones = dropdown_estaciones if dropdown_estaciones else []
    tipo_estacion = dropdown_tipo_estacion if dropdown_tipo_estacion else []
    tipo_tarjeta = dropdown_tipo_tarjeta if dropdown_tipo_tarjeta else []

    DEMANDA_TIEMPO = list_demanda_tiempo(fecha_inicial, fecha_final, distritos, modelo_bus,
                                         tipo_bus, color_bus, rutas, estaciones, tipo_estacion, tipo_tarjeta)

    figure = go.Figure(
        data=[
            go.Surface(
                x=DEMANDA_TIEMPO[0],
                y=DEMANDA_TIEMPO[1],
                z=DEMANDA_TIEMPO[2],
                showscale=True,
                opacity=0.8
            )
        ]
    )

    figure.update_traces(contours_z=dict(show=True, usecolormap=True,
                                         highlightcolor="limegreen", project_z=True))

    figure.update_layout(title='Demanda del Servicio vs Tiempo', autosize=True,
                         margin=dict(l=30, r=30, b=40, t=40), plot_bgcolor="#F9F9F9",
                         paper_bgcolor="#F9F9F9")

    return figure

    rendered = render_template('pdf_template.html', app)


# Main
if __name__ == "__main__":
    app.run_server()
