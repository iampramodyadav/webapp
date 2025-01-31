import dash
from dash import dcc, html, Input, Output, State, callback, dash_table, ALL
import dash_daq as daq
import plotly.graph_objects as go
import numpy as np
# Calculation functions
def create_rotation_matrix(euler_angles, rotation_order, translation):
    R = np.eye(3)
    for axis in reversed(rotation_order.lower()):
        idx = rotation_order.lower().index(axis)
        angle = euler_angles[idx]
        R = R @ _axis_rotation(axis, angle)
    return R, np.array(translation)

def _axis_rotation(axis, angle):
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    if axis == 'x':
        return np.array([[1, 0, 0], [0, cos_a, -sin_a], [0, sin_a, cos_a]])
    elif axis == 'y':
        return np.array([[cos_a, 0, sin_a], [0, 1, 0], [-sin_a, 0, cos_a]])
    elif axis == 'z':
        return np.array([[cos_a, -sin_a, 0], [sin_a, cos_a, 0], [0, 0, 1]])
    raise ValueError(f"Invalid axis: {axis}")

def rigid_load_transfer(force_local_A, moment_local_A, R_A, point_A_global, R_B, point_B_global):
    force_global = R_A @ force_local_A
    moment_global = R_A @ moment_local_A
    r = point_A_global - point_B_global
    moment_global += np.cross(r, force_global)
    return R_B.T @ force_global, R_B.T @ moment_global
# Initialize Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.H1("Rigid Load Transfer Analysis", style={
        'textAlign': 'center', 
        'color': '#2c3e50', 
        'fontFamily': 'Arial', 
        'marginBottom': '10px'
    }),

    dcc.Store(id='loads-store', data=[]),
    dcc.Store(id='targets-store', data=[]),

    html.Div([
        html.Div([
            html.H3("Input Systems", style={'color': '#2980b9'}),
            html.Button('➕ Add Load System', id='add-load-btn', n_clicks=0, style={
                'width': '100%', 
                'backgroundColor': '#27ae60', 
                'color': 'white',
                'border': 'none',
                'padding': '10px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px'
            }),
            html.Div(id='load-inputs-container', style={'marginTop': '10px'}),
            html.Hr(style={'border': '1px solid #ccc'}),

            html.Button('➕ Add Target System', id='add-target-btn', n_clicks=0, style={
                'width': '100%', 
                'backgroundColor': '#e67e22', 
                'color': 'white',
                'border': 'none',
                'padding': '10px',
                'borderRadius': '5px',
                'cursor': 'pointer',
                'fontSize': '16px'
            }),
            html.Div(id='target-inputs-container', style={'marginTop': '10px'}),
        ], style={
            'width': '25%', 
            'padding': '15px',
            'borderRadius': '10px',
            'backgroundColor': '#ecf0f1',
            'boxShadow': '2px 2px 10px rgba(0,0,0,0.1)',
            'height': '80vh',
            # 'height': '100%',
            'overflowY': 'auto'
        }),

        html.Div([
            dcc.Graph(id='3d-plot', style={
                'height': '80%', 
                'borderRadius': '10px', 
                'boxShadow': '2px 2px 15px rgba(0,0,0,0.2)',
                'backgroundColor': 'white',
                'padding': '10px'
            }),
            html.Div(id='results-container', style={
                'height': '20%',
                'marginTop': '10px', 
                'padding': '10px', 
                'borderRadius': '10px',
                'backgroundColor': '#f9f9f9'
            })
        ], style={'width': '75%', 'height': '80vh',}),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '20px', 'padding': '20px'})
])

# Callbacks for adding systems
@app.callback(
    Output('loads-store', 'data'),
    Input('add-load-btn', 'n_clicks'),
    State('loads-store', 'data'),
    prevent_initial_call=True
)
def add_load_system(n_clicks, data):
    new_load = {
        'force': [0.0, 0.0, 0.0],
        'moment': [0.0, 0.0, 0.0],
        'euler_angles': [0.0, 0.0, 0.0],
        'rotation_order': 'xyz',
        'translation': [0.0, 0.0, 0.0],
        'color': {'hex': f'#{np.random.randint(0, 0xFFFFFF):06x}'}
    }
    return data + [new_load]

@app.callback(
    Output('targets-store', 'data'),
    Input('add-target-btn', 'n_clicks'),
    State('targets-store', 'data'),
    prevent_initial_call=True
)
def add_target_system(n_clicks, data):
    new_target = {
        'euler_angles': [0.0, 0.0, 0.0],
        'rotation_order': 'xyz',
        'translation': [0.0, 0.0, 0.0],
        'color': {'hex': f'#{np.random.randint(0, 0xFFFFFF):06x}'}
    }
    return data + [new_target]

# Input components callback
@app.callback(
    [Output('load-inputs-container', 'children'),
     Output('target-inputs-container', 'children')],
    [Input('loads-store', 'data'),
     Input('targets-store', 'data')]
)
def update_input_components(loads, targets):
    def create_controls(items, input_type):
        controls = []
        for i, item in enumerate(items):
            # Handle legacy color format
            if isinstance(item['color'], str):
                item['color'] = {'hex': item['color']}

            system_color = item['color']['hex']

            controls.append(
                    html.Div([
                    html.H5(f"{input_type.capitalize()} System {i+1}"),
                   #  daq.ColorPicker(
                   #     id={'type': 'color-picker', 'index': i, 'input-type': input_type},
                   #     value=item['color'],
                   #     label='System Color'
                   # ),
                    html.Div([
                        html.Label("Position(X,Y,Z):"),
                        dcc.Input(value=item['translation'][0], type='number',
                                 id={'type': 'tx', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                        dcc.Input(value=item['translation'][1], type='number',
                                 id={'type': 'ty', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                        dcc.Input(value=item['translation'][2], type='number',
                                 id={'type': 'tz', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                    ], className='input-group',style={'display': 'flex', 'alignItems': 'center', 'gap': '5px'}),
                    # html.Hr(),
                    html.Div([
                        # Rotation order with inline label and dropdown
                        html.Div([
                            html.Label("Rotation Order:", style={'minWidth': '100px'}),
                            dcc.Dropdown(
                                options=['xyz', 'xzy', 'yxz', 'yzx', 'zxy', 'zyx'],
                                value=item['rotation_order'],
                                id={'type': 'rot-order', 'index': i, 'input-type': input_type},
                                style={'width': '120px'}
                            )
                        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'})
                    ], className='input-group', style={'flex': '1'}),
                        
                    html.Div([
                        # Rotation degrees with inline label and inputs
                        html.Div([
                            html.Label("Rotation (deg):", style={'minWidth': '100px'}),
                            html.Div([  # Container for inputs
                                dcc.Input(value=np.degrees(item['euler_angles'][0]), type='number',
                                         id={'type': 'rx', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                                dcc.Input(value=np.degrees(item['euler_angles'][1]), type='number',
                                         id={'type': 'ry', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                                dcc.Input(value=np.degrees(item['euler_angles'][2]), type='number',
                                         id={'type': 'rz', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                            ], style={'display': 'flex', 'gap': '5px'})
                        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'})
                    ], className='input-group', style={'flex': '1'}),
                    html.Hr(),
                        
                    html.Div([
                        html.Label("Force (X,Y,Z):"),
                        dcc.Input(value=item.get('force', [0,0,0])[0], type='number',
                                 id={'type': 'fx', 'index': i, 'input-type': input_type}, style={'width': '50px'}),
                        dcc.Input(value=item.get('force', [0,0,0])[1], type='number',
                                 id={'type': 'fy', 'index': i, 'input-type': input_type}, style={'width': '50px'}),
                        dcc.Input(value=item.get('force', [0,0,0])[2], type='number',
                                 id={'type': 'fz', 'index': i, 'input-type': input_type}, style={'width': '50px'}),
                    ], className='input-group', style={'display': 'flex', 'alignItems': 'center', 'gap': '5px'}) if input_type == 'load' else None,
                        
                    html.Div([
                        html.Label("Moment (X,Y,Z):"),
                        dcc.Input(value=item.get('moment', [0,0,0])[0], type='number',
                                 id={'type': 'mx', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                        dcc.Input(value=item.get('moment', [0,0,0])[1], type='number',
                                 id={'type': 'my', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                        dcc.Input(value=item.get('moment', [0,0,0])[2], type='number',
                                 id={'type': 'mz', 'index': i, 'input-type': input_type},style={'width': '50px'}),
                    ], className='input-group', style={'display': 'flex', 'alignItems': 'center', 'gap': '5px'}) if input_type == 'load' else None
                ], style={
                    'border': f'2px solid {system_color}',
                    'borderRadius': '8px',
                    'padding': '8px',
                    'margin': '5px',
                    'boxShadow': '2px 2px 5px rgba(0,0,0,0.1)'
                })
            )
        return controls

    return create_controls(loads, 'load'), create_controls(targets, 'target')
# Input updates callback
@app.callback(
    [Output('loads-store', 'data', allow_duplicate=True),
     Output('targets-store', 'data', allow_duplicate=True)],
    [Input({'type': 'tx', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'ty', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'tz', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'rx', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'ry', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'rz', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'fx', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'fy', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'fz', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'mx', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'my', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'mz', 'index': ALL, 'input-type': ALL}, 'value'),
     Input({'type': 'rot-order', 'index': ALL, 'input-type': ALL}, 'value'),
     # Input({'type': 'color-picker', 'index': ALL, 'input-type': ALL}, 'value')
    ],
    [State('loads-store', 'data'),
     State('targets-store', 'data')],
    prevent_initial_call=True
)
def update_stores(tx, ty, tz, rx, ry, rz, 
                  fx, fy, fz, mx, my, mz, rot_orders, 
                  # colors, 
                  loads, targets):
    ctx = dash.callback_context
    # print("Triggered Context:", ctx.triggered)

    # inputs = {prop['prop_id']: val for prop, val in zip(ctx.triggered, ctx.triggered[0]['value'])} if ctx.triggered else {}
    inputs = {prop['prop_id']: prop['value'] for prop in ctx.triggered} if ctx.triggered else {}


    # Update loads
    for i in range(len(loads)):
        # Translation
        loads[i]['translation'] = [
            next((v for pid, v in zip(ctx.inputs.keys(), tx) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), ty) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), tz) if f'"index":{i}' in pid and 'load' in pid), 0)
        ]
        
        # Rotation
        loads[i]['euler_angles'] = np.radians([
            next((v for pid, v in zip(ctx.inputs.keys(), rx) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), ry) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), rz) if f'"index":{i}' in pid and 'load' in pid), 0)
        ]).tolist()
        
        # Force/Moment
        loads[i]['force'] = [
            next((v for pid, v in zip(ctx.inputs.keys(), fx) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), fy) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), fz) if f'"index":{i}' in pid and 'load' in pid), 0)
        ]
        loads[i]['moment'] = [
            next((v for pid, v in zip(ctx.inputs.keys(), mx) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), my) if f'"index":{i}' in pid and 'load' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), mz) if f'"index":{i}' in pid and 'load' in pid), 0)
        ]
        
        # Other properties
        loads[i]['rotation_order'] = next((v for pid, v in zip(ctx.inputs.keys(), rot_orders) if f'"index":{i}' in pid and 'load' in pid), 'xyz')
        # loads[i]['color'] = next((v for pid, v in zip(ctx.inputs.keys(), colors) if f'"index":{i}' in pid and 'load' in pid), {'hex': '#000000'})

    # Update targets
    for i in range(len(targets)):
        targets[i]['translation'] = [
            next((v for pid, v in zip(ctx.inputs.keys(), tx) if f'"index":{i}' in pid and 'target' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), ty) if f'"index":{i}' in pid and 'target' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), tz) if f'"index":{i}' in pid and 'target' in pid), 0)
        ]
        
        targets[i]['euler_angles'] = np.radians([
            next((v for pid, v in zip(ctx.inputs.keys(), rx) if f'"index":{i}' in pid and 'target' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), ry) if f'"index":{i}' in pid and 'target' in pid), 0),
            next((v for pid, v in zip(ctx.inputs.keys(), rz) if f'"index":{i}' in pid and 'target' in pid), 0)
        ]).tolist()
        
        targets[i]['rotation_order'] = next((v for pid, v in zip(ctx.inputs.keys(), rot_orders) if f'"index":{i}' in pid and 'target' in pid), 'xyz')
        # targets[i]['color'] = next((v for pid, v in zip(ctx.inputs.keys(), colors) if f'"index":{i}' in pid and 'target' in pid), {'hex': '#000000'})

    return loads, targets
# Visualization callback
@app.callback(
    [Output('3d-plot', 'figure'),
     Output('results-container', 'children')],
    [Input('loads-store', 'data'),
     Input('targets-store', 'data')]
)
def update_visualization(loads, targets):
    fig = go.Figure()
    results = []

    # Add global system
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers',
                              marker=dict(size=2, color='black'), name='Global'))

    # Process loads
    for i, load in enumerate(loads):
        try:
            if isinstance(load['color'], str):  # Handle legacy format
                load['color'] = {'hex': load['color']}

            R, pos = create_rotation_matrix(
                # np.radians(load['euler_angles']),
                np.array(load['euler_angles']),
                load['rotation_order'],
                load['translation']
            )
            color = load['color']['hex']

            # Add coordinate system
            fig.add_traces(create_triad(pos, R, color))

            # Add vectors
            if 'force' in load:
                fig.add_trace(create_vector(pos, R @ load['force'], color, f'Load {i+1} Force'))
            if 'moment' in load:
                fig.add_trace(create_vector(pos, R @ load['moment'], color, f'Load {i+1} Moment'))

        except Exception as e:
            print(f"Error processing load {i}: {e}")

    # Process targets
    for i, target in enumerate(targets):
        try:
            if isinstance(target['color'], str):  # Handle legacy format
                target['color'] = {'hex': target['color']}

            R_target, pos_target = create_rotation_matrix(
                # np.radians(target['euler_angles']),
                np.array(target['euler_angles']),
                target['rotation_order'],
                target['translation']
            )
            color = target['color']['hex']

            # Add coordinate system
            fig.add_traces(create_triad(pos_target, R_target, color))

            # Calculate results
            total_F, total_M = np.zeros(3), np.zeros(3)
            for load in loads:
                R_load, pos_load = create_rotation_matrix(
                    # np.radians(load['euler_angles']),
                    np.array(load['euler_angles']),
                    load['rotation_order'],
                    load['translation']
                )
                F, M = rigid_load_transfer(
                    np.array(load['force']),
                    np.array(load['moment']),
                    R_load, pos_load,
                    R_target, pos_target
                )
                total_F += F
                total_M += M

            results.append({
                'System': f'Target {i+1}',
                'Fx': f"{total_F[0]:.2f}", 'Fy': f"{total_F[1]:.2f}", 'Fz': f"{total_F[2]:.2f}",
                'Mx': f"{total_M[0]:.2f}", 'My': f"{total_M[1]:.2f}", 'Mz': f"{total_M[2]:.2f}"
            })

        except Exception as e:
            print(f"Error processing target {i}: {e}")

    # Configure plot
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', backgroundcolor='white'),
            yaxis=dict(title='Y', backgroundcolor='white'),
            zaxis=dict(title='Z', backgroundcolor='white'),
            aspectmode='cube',
            camera=dict(up=dict(x=0, y=0, z=1))
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        showlegend=True
    )

    # Create results table
    table = dash_table.DataTable(
        columns=[{'name': col, 'id': col} for col in ['System', 'Fx', 'Fy', 'Fz', 'Mx', 'My', 'Mz']],
        data=results,
        style_cell={'textAlign': 'center', 'padding': '5px'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }]
    )

    return fig, table

# Visualization helpers
def create_triad(position, R, color):
    scale = 1.0
    return [
        go.Scatter3d(
            x=[position[0], position[0] + R[0,0]*scale],
            y=[position[1], position[1] + R[1,0]*scale],
            z=[position[2], position[2] + R[2,0]*scale],
            mode='lines',
            line=dict(color=color, width=4),
            showlegend=False
        ),
        go.Scatter3d(
            x=[position[0], position[0] + R[0,1]*scale],
            y=[position[1], position[1] + R[1,1]*scale],
            z=[position[2], position[2] + R[2,1]*scale],
            mode='lines',
            line=dict(color=color, width=4),
            showlegend=False
        ),
        go.Scatter3d(
            x=[position[0], position[0] + R[0,2]*scale],
            y=[position[1], position[1] + R[1,2]*scale],
            z=[position[2], position[2] + R[2,2]*scale],
            mode='lines',
            line=dict(color=color, width=4),
            showlegend=False
        )
    ]

def create_vector(position, vector, color, name):
    return go.Scatter3d(
        x=[position[0], position[0] + vector[0]],
        y=[position[1], position[1] + vector[1]],
        z=[position[2], position[2] + vector[2]],
        mode='lines+markers',
        marker=dict(size=3, color=color),
        line=dict(color=color, width=4),
        name=name
    )

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)