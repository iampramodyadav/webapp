import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import numpy as np
import json

def triangle_area(p1, p2, p3):
    """Calculate the area of a triangle in 2D space."""
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    return abs(np.cross(v1, v2)) / 2

def get_centroid(points):
    """Calculate the centroid of points."""
    return np.mean(points, axis=0)

def get_angle(point, centroid):
    """Calculate angle between point and positive x-axis relative to centroid."""
    return np.arctan2(point[1] - centroid[1], point[0] - centroid[0])

def order_points(points):
    """Order points in counterclockwise direction to form a proper quadrilateral."""
    points = np.array(points)
    centroid = get_centroid(points)
    angles = [get_angle(point, centroid) for point in points]
    sorted_indices = np.argsort(angles)
    return points[sorted_indices]

def is_convex(points):
    """Check if the quadrilateral is convex using cross product method."""
    n = len(points)
    signs = []
    for i in range(n):
        p1 = points[i]
        p2 = points[(i + 1) % n]
        p3 = points[(i + 2) % n]
        v1 = p2 - p1
        v2 = p3 - p2
        cross_product = np.cross(v1, v2)
        signs.append(np.sign(cross_product))
    return all(sign >= 0 for sign in signs) or all(sign <= 0 for sign in signs)

def find_diagonal_triangulation(points):
    """Split quadrilateral into two triangles using sequential points."""
    points = np.array(points)
    
    if not is_convex(points):
        points = order_points(points)
    
    area1_split1 = triangle_area(points[0][:2], points[1][:2], points[2][:2])
    area2_split1 = triangle_area(points[2][:2], points[3][:2], points[0][:2])
    total_area1 = area1_split1 + area2_split1
    
    area1_split2 = triangle_area(points[1][:2], points[2][:2], points[3][:2])
    area2_split2 = triangle_area(points[3][:2], points[0][:2], points[1][:2])
    total_area2 = area1_split2 + area2_split2
    
    if total_area1 <= total_area2:
        return (points[[0,1,2]], points[[2,3,0]], "0-2", points)
    else:
        return (points[[1,2,3]], points[[3,0,1]], "1-3", points)

# Initialize the Dash app
app = dash.Dash(__name__)

# Initial points for the quadrilateral
initial_points = np.array([
    [0, 0],    # P0
    [2.1, 0],    # P1
    [2.1, 2.1],    # P2
    [0, 2.1]     # P3
])

# App layout
app.layout = html.Div([
    html.H1("Interactive Quadrilateral Triangulation", 
            style={'textAlign': 'center', 'marginBottom': '20px'}),
    
    # Add manual point input form
    html.Div([
        html.Div([
            html.Label('Enter Points (x, y):', style={'fontWeight': 'bold'}),
            html.Div([
                dcc.Input(id=f'point-{i}-x', type='number', placeholder=f'P{i} X',
                         style={'marginRight': '10px', 'width': '80px'})
                for i in range(4)
            ], style={'marginBottom': '10px'}),
            html.Div([
                dcc.Input(id=f'point-{i}-y', type='number', placeholder=f'P{i} Y',
                         style={'marginRight': '10px', 'width': '80px'})
                for i in range(4)
            ], style={'marginBottom': '10px'}),
            html.Button('Update Points', id='update-points', 
                       style={'marginRight': '10px'}),
            html.Button('Reset View', id='reset-view')
        ], style={'textAlign': 'center', 'marginBottom': '20px'})
    ]),
    
    dcc.Graph(
        id='triangulation-plot',
        style={'height': '800px'},
        config={
            'displayModeBar': True,
            'editable': True,
            'scrollZoom': True
        }
    ),
    
    html.Div([
        html.Div(
            id='area-display',
            style={'textAlign': 'center', 'marginTop': '20px', 'fontSize': '18px'}
        ),
        html.Div(
            id='convex-status',
            style={'textAlign': 'center', 'marginTop': '10px', 'fontSize': '16px'}
        )
    ]),
    
    # Store components for various states
    dcc.Store(id='points-storage', data=initial_points.tolist()),
    dcc.Store(id='view-storage', data={"autosize": True})
])

@app.callback(
    [Output('triangulation-plot', 'figure'),
     Output('area-display', 'children'),
     Output('convex-status', 'children'),
     Output('points-storage', 'data'),
     Output('view-storage', 'data')],
     
    [Input('triangulation-plot', 'relayoutData'),
     Input('update-points', 'n_clicks'),
     Input('reset-view', 'n_clicks')],
     
    [State('points-storage', 'data'),
     State('view-storage', 'data')] +
    [State(f'point-{i}-{coord}', 'value') for i in range(4) for coord in ['x', 'y']]
)

def update_triangulation(relayout_data, update_clicks, reset_clicks, points, view_data, *point_inputs):
    ctx = dash.callback_context
    trigger = ctx.triggered[0]['prop_id'] if ctx.triggered else None
    points = np.array(points)
    
    # Handle manual point updates
    if trigger == 'update-points.n_clicks':
        new_points = []
        for i in range(0, len(point_inputs), 2):
            x = point_inputs[i] if point_inputs[i] is not None else points[i//2][0]
            y = point_inputs[i+1] if point_inputs[i+1] is not None else points[i//2][1]
            new_points.append([float(x), float(y)])
        points = np.array(new_points)
    
    # Handle point dragging
    elif trigger and trigger.startswith('triangulation-plot.relayoutData'):
        if relayout_data and any(key.startswith('shapes') for key in relayout_data.keys()):
            for key, value in relayout_data.items():
                if 'x0' in key:
                    point_idx = int(key.split('[')[1].split(']')[0])
                    points[point_idx][0] = value
                elif 'y0' in key:
                    point_idx = int(key.split('[')[1].split(']')[0])
                    points[point_idx][1] = value
        
        # Update view data but preserve points
        if relayout_data and any(key in relayout_data for key in ['xaxis.range[0]', 'yaxis.range[0]']):
            view_data.update(relayout_data)
    
    # Reset view if requested
    if trigger == 'reset-view.n_clicks':
        view_data = {"autosize": True}
    
    # Find triangulation
    triangle1, triangle2, diagonal, ordered_points = find_diagonal_triangulation(points)
    
    # Calculate total area
    total_area = (triangle_area(triangle1[0][:2], triangle1[1][:2], triangle1[2][:2]) +
                  triangle_area(triangle2[0][:2], triangle2[1][:2], triangle2[2][:2]))
    
    # Create the figure
    fig = go.Figure()
    
    # Add triangles and other traces
    
    # Add triangles
    fig.add_trace(go.Scatter(
        x=np.append(triangle1[:,0], triangle1[0,0]),
        y=np.append(triangle1[:,1], triangle1[0,1]),
        fill='toself',
        fillcolor='rgba(173, 216, 230, 0.5)',
        line=dict(color='blue'),
        name='Triangle 1'
    ))
    
    fig.add_trace(go.Scatter(
        x=np.append(triangle2[:,0], triangle2[0,0]),
        y=np.append(triangle2[:,1], triangle2[0,1]),
        fill='toself',
        fillcolor='rgba(144, 238, 144, 0.5)',
        line=dict(color='green'),
        name='Triangle 2'
    ))
    
    # Add diagonal
    if diagonal == "0-2":
        diag_start, diag_end = 0, 2
    else:
        diag_start, diag_end = 1, 3
        
    fig.add_trace(go.Scatter(
        x=[ordered_points[diag_start,0], ordered_points[diag_end,0]],
        y=[ordered_points[diag_start,1], ordered_points[diag_end,1]],
        mode='lines',
        line=dict(color='red', dash='dash'),
        name='Diagonal'
    ))
    
    # Add sequential connections
    fig.add_trace(go.Scatter(
        x=np.append(ordered_points[:,0], ordered_points[0,0]),
        y=np.append(ordered_points[:,1], ordered_points[0,1]),
        mode='lines',
        line=dict(color='black'),
        name='Edges'
    ))
    
    # Add draggable points
    shapes = []
    annotations = []
    for i, (x, y) in enumerate(ordered_points):
        shapes.append({
            'type': 'circle',
            'x0': x - 0.1,
            'y0': y - 0.1,
            'x1': x + 0.1,
            'y1': y + 0.1,
            'fillcolor': 'black',
            'line_color': 'black',
            'editable': True,
            # 'draggable': True
        })
        
        annotations.append({
            'x': x,
            'y': y,
            'xref': 'x',
            'yref': 'y',
            'text': f'P{i}',
            'showarrow': False,
            'font': {'size': 14},
            'yshift': 20
        })
    
    # Update layout while preserving view state
    layout_updates = {
        'shapes': shapes,
        'annotations': annotations,
        'showlegend': True,
        'title': 'Drag the points to modify the quadrilateral',
        'hovermode': 'closest'
    }
    
    # Only use autosize if no view state is saved
    if view_data.get("autosize", True):
        layout_updates.update({
            'xaxis': dict(
                scaleanchor='y',
                scaleratio=1,
                range=[min(ordered_points[:,0])-1, max(ordered_points[:,0])+1]
            ),
            'yaxis': dict(
                range=[min(ordered_points[:,1])-1, max(ordered_points[:,1])+1]
            )
        })
    else:
        # pass
        # Preserve zoom and pan state
        for key, value in view_data.items():
            if key.startswith(('xaxis', 'yaxis')):
                layout_updates[key] = value
    
    fig.update_layout(layout_updates)
    
    area_text = f"Total Area: {total_area:.2f} square units"
    convex_status = f"Status: {ordered_points} Points ordered counter-clockwise to maintain convex quadrilateral"
    
    return fig, area_text, convex_status, ordered_points.tolist(), view_data

if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(host="0.0.0.0", port=8051)
