"""
@Author:    Pramod Kumar Yadav
@email:     pramod.kumar@siemensgamesa.com
@Date:      April, 2023
@Credit:    Paramjeet (paramjeet.gill@siemensgamesa.com)
@status:    development
@PythonVersion: python3

"""

# *********** importing all the required library***********
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output


# *********** Function for coordinate transform ***********
def orderMult(order, Tr, Rx, Ry, Rz, typ):
    """[summary]

    Args:
        order ([typ]): [description]
        Tr ([typ]): [description]
        Rx ([typ]): [description]
        Ry ([typ]): [description]
        Rz ([typ]): [description]
        typ ([typ]): [description]

    Returns:
        [typ]: [description]
    """
    MatDict = {char: ord(char) for char in order}
    MatDict['T'] = Tr
    MatDict['X'] = Rx
    MatDict['Y'] = Ry
    MatDict['Z'] = Rz
    keys = list(MatDict.keys())
    val1 = MatDict[keys[0]]
    val2 = MatDict[keys[1]]
    val3 = MatDict[keys[2]]
    val4 = MatDict[keys[3]]

    if typ == 1:
        RotMat = val4 @ val3 @ val2 @ val1
        # RotMat=np.matmul(np.matmul(val4, val3), np.matmul(val2, val1))
        # RotMat=np.matmul(val2, val3)
    elif typ == 2:
        RotMat = val1 @ val2 @ val3 @ val4
        # RotMat=np.matmul(np.matmul(val1, val2), np.matmul(val3, val4))
    return RotMat


def coordinateTransform(order='TXYZ', Tra=[0, 0, 0], a_x=0, a_y=0, a_z=0, point=[0, 0, 0], typ=1):
    """[summary]

    Args:
        order (str, optional): [order of transformation and rotation]. Defaults to 'TXYZ'.
        Tra (list, optional): [Translation of a coordinate or point]. Defaults to [0,0,0].
        a_x (int, optional): [anti-clockwise rotation along the x-axis]. Defaults to 0.
        a_y (int, optional): [anti-clockwise rotation along the y-axis]. Defaults to 0.
        a_z (int, optional): [anti-clockwise rotation along the z-axis]. Defaults to 0.
        point (list, optional): [point to be transformed]. Defaults to [0,0,0].
        typ (int, optional): [1 & 2 (1: for coordinate transformation, 2: for point transformation with fix coordinate)]. Defaults to 1.

    Returns:
        [List]: [point coordinate after transformation]
    """

    Xc = np.matrix([[point[0]], [point[1]], [point[2]], [1]])
    theta_x = np.deg2rad(a_x)
    theta_y = np.deg2rad(a_y)
    theta_z = np.deg2rad(a_z)

    if typ == 2:
        tx = Tra[0]
        ty = Tra[1]
        tz = Tra[2]
    elif typ == 1:
        tx = Tra[0] * -1
        ty = Tra[1] * -1
        tz = Tra[2] * -1
        theta_x = np.deg2rad(a_x) * -1
        theta_y = np.deg2rad(a_y) * -1
        theta_z = np.deg2rad(a_z) * -1
    else:
        print("Enter typ=1: for coordinate transformation & typ=2: for point transformation")

    Tr = np.matrix([[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]])
    Rx = np.matrix([[1, 0, 0, 0], [0, np.cos(theta_x), -np.sin(theta_x), 0], [0, np.sin(theta_x), np.cos(theta_x), 0],
                    [0, 0, 0, 1]])
    Ry = np.matrix([[np.cos(theta_y), 0, np.sin(theta_y), 0], [0, 1, 0, 0], [-np.sin(theta_y), 0, np.cos(theta_y), 0],
                    [0, 0, 0, 1]])
    Rz = np.matrix([[np.cos(theta_z), -np.sin(theta_z), 0, 0], [np.sin(theta_z), np.cos(theta_z), 0, 0], [0, 0, 1, 0],
                    [0, 0, 0, 1]])

    RotMat = orderMult(order, Tr, Rx, Ry, Rz, typ)
    Xf = RotMat @ Xc

    Xf = Xf[0:3].tolist()
    return [Xf[0][0], Xf[1][0], Xf[2][0]]


def coordinatePlot(order='TXYZ', Tra=[0, 0, 0], a_x=0, a_y=0, a_z=0, point=[1, 1, 1], typ=1, l=5):
    """[summary]

    Args:
        order (str, optional): [description]. Defaults to 'TXYZ'.
        Tra (list, optional): [description]. Defaults to [0,0,0].
        a_x (int, optional): [description]. Defaults to 0.
        a_y (int, optional): [description]. Defaults to 0.
        a_z (int, optional): [description]. Defaults to 0.
        point (list, optional): [description]. Defaults to [0,0,0].
        typ (int, optional): [description]. Defaults to 1.
        l (int, optional): [description]. Defaults to 5.
    """
    Xf = coordinateTransform(order, Tra, a_x, a_y, a_z, point, typ)

    Xa = [0, 0, 0]
    Xb = [l, 0, 0]
    Ya = [0, 0, 0]
    Yb = [0, l, 0]
    Za = [0, 0, 0]
    Zb = [0, 0, l]
    Xat = coordinateTransform(order, Tra, a_x, a_y, a_z, Xa, 2)
    Xbt = coordinateTransform(order, Tra, a_x, a_y, a_z, Xb, 2)
    Yat = coordinateTransform(order, Tra, a_x, a_y, a_z, Ya, 2)
    Ybt = coordinateTransform(order, Tra, a_x, a_y, a_z, Yb, 2)
    Zat = coordinateTransform(order, Tra, a_x, a_y, a_z, Za, 2)
    Zbt = coordinateTransform(order, Tra, a_x, a_y, a_z, Zb, 2)
    p = point
    if typ == 1:

        Line = ["$X_0$", "$X_0$", "$Y_0$", "$Y_0$", "$Z_0$", "$Z_0$", "$X_1$", "$X_1$", "$Y_1$", "$Y_1$", "$Z_1$",
                "$Z_1$"]
        x = np.array([Xa[0], Xb[0], Ya[0], Yb[0], Za[0], Zb[0], Xat[0], Xbt[0], Yat[0], Ybt[0], Zat[0], Zbt[0]])
        y = np.array([Xa[1], Xb[1], Ya[1], Yb[1], Za[1], Zb[1], Xat[1], Xbt[1], Yat[1], Ybt[1], Zat[1], Zbt[1]])
        z = np.array([Xa[2], Xb[2], Ya[2], Yb[2], Za[2], Zb[2], Xat[2], Xbt[2], Yat[2], Ybt[2], Zat[2], Zbt[2]])
        df1 = pd.DataFrame({"Line": Line, "x": x, "y": y, "z": z})
        # display(df1)
        fig1 = px.line_3d(df1, x="x", y="y", z="z", color='Line', markers=True)
        fig1.update_traces(marker=dict(size=5), line=dict(width=6))

        df2 = pd.DataFrame({"Point": ["$p_0$"], "x": [p[0]], "y": [p[1]], "z": [p[2]]})
        # display(df2)
        fig2 = px.scatter_3d(df2, x="x", y="y", z="z", color='Point', text=[Xf])
        fig3 = go.Figure(data=fig1.data + fig2.data)
        fig3.update_layout(height=550, plot_bgcolor='rgba(0, 0, 0, 1)', paper_bgcolor='rgba(135, 206, 235, 1)',
                           margin=dict(l=0, r=0, b=0, t=20), scene=dict(aspectmode='data'))

        return fig3

    elif typ == 2:
        Line = ["$X_0$", "$X_0$", "$Y_0$", "$Y_0$", "$Z_0$", "$Z_0$"]
        x = np.array([Xa[0], Xb[0], Ya[0], Yb[0], Za[0], Zb[0]])
        y = np.array([Xa[1], Xb[1], Ya[1], Yb[1], Za[1], Zb[1]])
        z = np.array([Xa[2], Xb[2], Ya[2], Yb[2], Za[2], Zb[2]])
        df1 = pd.DataFrame({"Line": Line, "x": x, "y": y, "z": z})
        # display(df1)
        fig1 = px.line_3d(df1, x="x", y="y", z="z", color='Line', markers=True)
        fig1.update_traces(marker=dict(size=5), line=dict(width=6))
        df2 = pd.DataFrame({"Point": ["$p_0$", "$p_1$"], "x": [p[0], Xf[0]], "y": [p[1], Xf[1]], "z": [p[2], Xf[2]]})
        # display(df2)
        fig2 = px.scatter_3d(df2, x="x", y="y", z="z", color='Point', text=[p, Xf])
        fig3 = go.Figure(data=fig1.data + fig2.data)
        fig3.update_layout(height=550, plot_bgcolor='rgba(0, 0, 2, 0)', paper_bgcolor='rgba(200, 200, 250, 1)',
                           margin=dict(l=0, r=0, b=0, t=20), scene=dict(aspectmode='data'))

        return fig3

    else:
        print("Enter typ=1: for coordinate transformation & typ=2: for point transformation")

    # **************** Building Dash-board ****************


df4 = pd.DataFrame({"Order": ['TXYZ', 'TXZY', 'TYXZ', 'TYZX',
                              'TZXY', 'TZYX', 'XTYZ', 'XTZY', 'XYTZ',
                              'XYZT', 'XZTY', 'XZYT', 'YTXZ', 'YTZX',
                              'YXTZ', 'YXZT', 'YZTX', 'YZXT', 'ZTXY',
                              'ZTYX', 'ZXTY', 'ZXYT', 'ZYTX', 'ZYXT']})

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Footer('pramod.kumar@siemensgamesa.com'),
        html.H2(children='Coordinate Transformation', style={'textAlign': 'center', 'color': 'rgba(0, 0, 235, 1)'}),
        html.Div([
            html.Br(),
            html.B('Translation & Rotation Order'),
            # dcc.Markdown('''***Translation & Rotation Order***'''),
            dcc.Dropdown(
                df4['Order'].unique(),
                'TXYZ', id='ord'
            ),
            html.Br(),
            html.B('Translation in x, y z direction'),
            # dcc.Markdown('''**Translation in x, y, z Direction**'''),          
            html.Div([
                html.Br(),
                html.Label('dx: '),
                dcc.Input(id='t1', type='number', value=1),
                html.Br(),
                html.Label('dy: '),
                dcc.Input(id='t2', type='number', value=1),
                html.Br(),
                html.Label('dz: '),
                dcc.Input(id='t3', type='number', value=1),

            ], style={'padding': 5, 'flex': 1}),

            html.Br(),
            html.B('Rotation about x, y, z (deg)'),
            # dcc.Markdown('''**Rotation about x, y, z (deg)**'''),             
            html.Div([
                html.Br(),
                html.Label('Rx: '),
                dcc.Input(id='rx', type='number', value=0),
                html.Br(),
                html.Label('Ry:  '),
                dcc.Input(id='ry', type='number', value=0),
                html.Br(),
                html.Label('Rz:  '),
                dcc.Input(id='rz', type='number', value=45),

            ], style={'padding': 5, 'flex': 1}),

            html.Br(),
            html.I('1:Coordinate Transformation'),
            html.Br(),
            html.I('2:Point Transformation'),
            # dcc.Markdown('''*1:Coordinate Transformation 2:Point Transformation*'''),
            dcc.RadioItems([1, 2], 1, id='typ', inline=False),

            html.Br(),
            html.I('Triad Zoom'),
            dcc.Slider(min=1, max=500, id='l',
                       marks={i: f'Zoom {i}' if i == 1 else str(i) for i in range(0, 501, 100)},
                       value=5,
                       ),

        ], style={'width': '15%', 'padding': 5, 'display': 'inline-block'}),

        html.Div([
            html.Br(),
            # html.Label('Coordinate and point plot'),   
            dcc.Graph(id='indicator-graphic'),
            html.Br(),
            html.I([html.B('Coordinate after Transformation')]),
            html.Table([
                html.Tr([html.Td(['X', html.Sub(1), ': ']), html.Td(id='Xout')]),
                html.Tr([html.Td(['Y', html.Sub(1), ': ']), html.Td(id='Yout')]),
                html.Tr([html.Td(['Z', html.Sub(1), ': ']), html.Td(id='Zout')]),
            ]),

        ], style={'width': '80%', 'height': '100%', 'float': 'right', 'display': 'inline-block'})

    ]),
    html.Br(),
    html.B('Enter Initial Coordinate of Point'),
    html.Div([
        html.Br(),
        html.Label(['X', html.Sub(0), ': ']),
        dcc.Input(id='p_x', type='number', value=1),
        html.Br(),
        html.Label(['Y', html.Sub(0), ': ']),
        dcc.Input(id='p_y', type='number', value=2),
        html.Br(),
        # html.Label('Z0: '),
        html.Label(['Z', html.Sub(0), ': ']),
        dcc.Input(id='p_z', type='number', value=3),

    ], style={'width': '15%', 'padding': 5, 'display': 'inline-block'}),

])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Output('Xout', 'children'),
    Output('Yout', 'children'),
    Output('Zout', 'children'),
    Input('ord', 'value'),
    Input('typ', 'value'),
    Input('t1', 'value'),
    Input('t2', 'value'),
    Input('t3', 'value'),
    Input('rx', 'value'),
    Input('ry', 'value'),
    Input('rz', 'value'),
    Input('l', 'value'),
    Input('p_x', 'value'),
    Input('p_y', 'value'),
    Input('p_z', 'value'),
)
def update_graph(ord, typ, t1, t2, t3, rx, ry, rz, l, p_x, p_y, p_z):
    Tr = [t1, t2, t3]
    pnt = [p_x, p_y, p_z]
    # fig= coordinatePlot(ord, Tr, rx, ry, rz, pnt,typ,l)
    fig = coordinatePlot(order=ord, Tra=Tr, a_x=rx, a_y=ry, a_z=rz, point=pnt, typ=typ, l=l)
    Pout = coordinateTransform(order=ord, Tra=Tr, a_x=rx, a_y=ry, a_z=rz, point=pnt, typ=typ)

    return fig, Pout[0], Pout[1], Pout[2]


if __name__ == '__main__':
    app.run_server(debug=True)
