from dash import dcc, html, dash_table, Dash
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc



# Read the Excel file
df_medication = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='newdata')
df_surgery = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='data_surgery')
df_alternative = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='alternative treatment')
df_percentage = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='percentage')

# Initialize the Dash app
app = Dash(external_stylesheets=[dbc.themes.CERULEAN],suppress_callback_exceptions=True)
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
# https://dash-bootstrap-components.opensource.faculty.ai/docs/
server = app.server

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.Div([
                html.Label('Disease Name', style={'fontWeight': '1000'}),
                dcc.Dropdown(
                    id='search-dropdown',
                    placeholder='Type in disease',
                    style={'width': '100%'}
                )
            ]),
            md=6, lg=6
        ),
        dbc.Col(
            html.Div([
                html.Label('Treatment Type', style={'fontWeight': '1000'}),
                dcc.Dropdown(
                    id='treatment-type-dropdown',
                    options=[
                        {'label': 'Medication', 'value': 'medication'},
                        {'label': 'Surgery', 'value': 'surgery'}
                    ],
                    value='medication',
                    style={'width': '100%'}
                )
            ]),
            md=6, lg=6
        )
    ]),

    # Message below the dropdowns once dashboard starts
    dbc.Row([
        dbc.Col(
            html.Div(
                id='selection-message', 
                children='This is the dashboard for medication comparison. You can start by selecting a disease and treatment type based on your desire.', 
                style={'textAlign': 'center', 'marginTop': '10px', 'color': 'darkblue'}  
            ),
            width=12
        )
    ]),

    # Row for Medication Table and Side Effects Chart
    dbc.Row([
        dbc.Col(
            html.Div([
                dash_table.DataTable(
                    id='medication-table',
                    row_selectable='multi',
                    selected_rows=[],
                    style_table={
                        'height': '450px',
                        'overflowY': 'auto',
                        'overflowX': 'auto',
                        'width': '100%',
                        'border': 'none',  
                        'borderRadius': '10px'
                    },
                    style_cell={
                        'textAlign': 'center',
                        'whiteSpace': 'normal',
                        'height': '30px',
                        'lineHeight': '30px',
                        'overflow': 'hidden',
                        'border-right': '1px solid rgba(0, 0, 0, 0.1)',
                        'border-top': 'none',
                        'border-bottom': 'none',
                        'textOverflow': 'ellipsis'
                    },
                    style_header={
                        'backgroundColor': 'rgba(168, 212, 247)',
                        'fontWeight': '1000'
                    }
     
                ),
                # Add the message below the medication table
                html.Div(id='selection2-message', style={'marginTop': '20px'})  # Message about selecting up to two rows
            ], style={ 'marginTop': '20px'}  
            ),
            md=6, lg=6  
        ),
        dbc.Col(
            html.Div(id='side-effects-chart'),
            md=6, lg=6
        )
    ]),

    # Row for Sources' Demographics, Age Distribution, Race Distribution, and medication info container
    dbc.Row([
        # Column for Sources' Demographics, Age Distribution, and Race Distribution
        dbc.Col(
            html.Div([
                # Sources' Demographics Title
                html.Div(id='demographics-title', className='my-bg-color', style={'textAlign': 'center', 'marginTop': '10px'}),

                # Age and Race Distribution Charts
                dbc.Row([
                    dbc.Col(
                        html.Div(id='age-distribution-chart', style={'textAlign': 'center'}),
                        width=6,  
                        style={'paddingRight': '0px', 'textAlign': 'center', 'marginTop': '-17px'}
                    ),
                    dbc.Col(
                        html.Div(id='race-distribution-chart', style={'textAlign': 'center'}),
                        width=6,  
                        style={'paddingLeft': '0px', 'textAlign': 'center', 'marginTop': '-17px'}
                    )
                ])
            ]),
            md=6  
        ),

# Column for Medication Info Container 
dbc.Col(
    html.Div(
        id='overall-info-container',  
        children=[
            # First Box: Medication Info Container 
            html.Div(
                id='medication-info-container',  
                children=[
                    html.P(
                        html.B("Select the first medication to rank its side effects (descending).\n"
                               "You can then choose a second for comparison."),
                        style={'textAlign': 'center', 'marginTop': '10px', 'whiteSpace': 'pre-wrap'}
                    )
                ],
                className='my-bg-color',
                style={
                    'border': '4px solid rgba(230, 245, 255)',
                    'borderRadius': '10px',
                    'padding': '10px',
                    'marginBottom': '20px'
                }
            ),

            # Second Box: Percentage Info
            html.Div(
                id='percentage-info',
                className='my-bg-color',
                style={
                    'border': '4px solid rgba(230, 245, 255)',
                    'borderRadius': '10px',
                    'padding': '10px',
                    'marginTop': '10px',
                    'textAlign': 'center'
                }
            ),

            # Third Box: Alternative Treatment
            html.Div(
                id='alternative-treatment-section',
                style={
                    'padding': '10px',
                    'marginTop': '20px',
                    'borderRadius': '10px',
                    'border': '4px solid rgba(230, 245, 255)',  
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)',  
                    'display': 'none'  # Initially hidden
                }
            )
        ],
        style={'textAlign': 'center', 'marginTop': '10px', 'display': 'block'}
    ),
    md=6
)

        
    ]),  # End of demographics and medication row

    # Selected Medication Names Row
    dbc.Row([
        dbc.Col(
            html.Div(id='selected-medication-names'),
            md=6, lg=6
        )
    ]),

    # Area for Percentage Display
    dbc.Row([
        dbc.Col(
            html.Div(id='area-for-display-percentage'),
            md=12
        )
    ]),

])


############ STARTING CALLBACKS

# Callback: Display alternative treatment for the selected disease
@app.callback(
    Output('alternative-treatment-section', 'children'),  
    Output('alternative-treatment-section', 'style'),     
    Input('search-dropdown', 'value')                     
)
def update_alternative_treatment(disease_name):
    if disease_name:
        # Fetch the alternative treatment for the selected disease
        treatment_info = df_alternative[df_alternative['disease_name'] == disease_name]['alternative_treatment'].values
        
        if len(treatment_info) > 0 and isinstance(treatment_info[0], str):
            treatments = treatment_info[0].split(',')  # Treatments are comma-separated
            links = [
                html.A(treatment.strip(), href=f"https://www.google.com/search?q={treatment.strip()}", target="_blank") 
                for treatment in treatments
            ]

            # Content to display
            alternative_treatment_content = html.Div(
                children=[
                    html.H5("Alternative Treatment", style={'textAlign': 'left', 'fontWeight': '1000'}),
                    html.P("Click each option to view further details", style={'textAlign': 'left'}),
                    html.Ul([html.Li(link) for link in links], style={'textAlign': 'left'})
                ],
                style={
                    'padding': '10px',
                    'marginTop': '20px',
                    'borderRadius': '10px',
                    'border': '4px solid rgba(230, 245, 255)',  # Border: width, style, and color
                    'boxShadow': '0px 4px 6px rgba(0, 0, 0, 0.1)'  # Add a shadow
                }
            )

            # Return the content and set display to 'block' to show the section
            return alternative_treatment_content, {'display': 'block'}

        else:
            # If no alternative treatment is available, display message and keep the section visible
            return html.P("No alternative treatments available."), {'display': 'block'}
    
    # If no disease is selected, hide the section
    return "", {'display': 'none'}


# Callback: Update search dropdown options based on treatment type
@app.callback( 
    Output('search-dropdown', 'options'),
    Input('treatment-type-dropdown', 'value')
)
def update_search_options(treatment_type):
    if treatment_type == 'medication':
        disease_names = df_medication['disease_name'].unique()
    else:
        disease_names = df_surgery['disease_name'].unique()
    return [{'label': name, 'value': name} for name in disease_names]

# Callback: Update table based on selected disease and treatment type
@app.callback(
    Output('medication-table', 'columns'),
    Output('medication-table', 'data'),
    Output('medication-table', 'row_selectable'),
    Output('medication-table', 'selected_rows'),  
    Input('search-dropdown', 'value'),
    Input('treatment-type-dropdown', 'value')
)
def update_table(disease_name, treatment_type):
    if not disease_name:
        return [], [], 'multi', []  # Reset selected rows when no disease is selected

    if treatment_type == 'medication':
        filtered_df = df_medication[df_medication['disease_name'] == disease_name]
        columns = [
            {'name': 'Medication Name', 'id': 'medication_name'},
            {'name': 'Dosage', 'id': 'dosage'},
            {'name': 'Common Side Effect', 'id': 'common_side_effect'},
            {'name': 'Rare Side Effect', 'id': 'common_side_effect_rare'},
            {'name': 'Drug Interaction', 'id': 'drug_interaction'}
        ]
        
        # Aggregate common and rare side effects
        filtered_df['common_side_effect'] = filtered_df[['side_effect_common_1', 'side_effect_common_2', 
                                                          'side_effect_common_3', 'side_effect_common_4']].apply(
            lambda x: '/'.join(x.dropna().value_counts().nlargest(3).index), axis=1)
        
        rare_side_effects = filtered_df.groupby('medication_name')['side_effect_rare'].apply(
            lambda x: '/'.join(x.dropna().value_counts().nlargest(2).index))
        filtered_df['common_side_effect_rare'] = filtered_df['medication_name'].map(rare_side_effects)

        # Randomly select a dosage for each medication
        filtered_df['dosage'] = filtered_df.groupby('medication_name')['medication_dosage'].transform(
            lambda x: x.sample(1).values[0])

        # Remove duplicates
        filtered_df = filtered_df.drop_duplicates(subset=['disease_name', 'medication_name'])

    else:  # Treatment type: surgery
        filtered_df = df_surgery[df_surgery['disease_name'] == disease_name]
        columns = [
            {'name': 'Surgery Name', 'id': 'medication_name'},
            {'name': 'Common Side Effect', 'id': 'common_side_effect'},
            {'name': 'Common Side Effect (Rare)', 'id': 'common_side_effect_rare'}
        ]
        
        # Similar aggregation for surgery side effects
        filtered_df['common_side_effect'] = filtered_df[['side_effect_common_1', 'side_effect_common_2', 
                                                          'side_effect_common_3', 'side_effect_common_4']].apply(
            lambda x: '/'.join(x.dropna().value_counts().nlargest(3).index), axis=1)

        rare_side_effects = filtered_df.groupby('medication_name')['side_effect_rare'].apply(
            lambda x: '/'.join(x.dropna().value_counts().nlargest(2).index))
        filtered_df['common_side_effect_rare'] = filtered_df['medication_name'].map(rare_side_effects)

        # Remove duplicates
        filtered_df = filtered_df.drop_duplicates(subset=['disease_name', 'medication_name'])

    # Ensure no empty rows are included
    filtered_df = filtered_df.dropna(subset=['medication_name'])

    return columns, filtered_df.to_dict('records'), 'multi' if treatment_type == 'medication' else None, []
    
# Callback: Display side effects, message, and charts
@app.callback(
    Output('selection2-message', 'children'),  
    Output('side-effects-chart', 'children'), 
    Output('age-distribution-chart', 'children'),
    Output('race-distribution-chart', 'children'),
    Output('demographics-title', 'children'),  
    Input('medication-table', 'selected_rows'),
    State('medication-table', 'data'),
    State('treatment-type-dropdown', 'value'),
    State('search-dropdown', 'value')
)
def display_selected_medications(selected_rows, data, treatment_type, disease_name):

    if not data or len(data) == 0:
        # Do not display anything if the table hasn't shown up yet
        return html.Div(""), html.Div(""), html.Div(""), html.Div(""), ""  

    if treatment_type == 'surgery':
        # If treatment type is surgery, 
        return html.Div(""), html.Div(children=[
         html.B("To view the side effects' comparisons bar charts here,"),
                html.Br(),  # Line break
                html.B("select medication as treatment type")], 
        style={'textAlign': 'center', 
                'color': '#4169E1',
                'padding': '10px',
                'borderRadius': '10px' ,
                'marginTop': '40px',
                'textAlign': 'center',
                'whiteSpace': 'pre-wrap'}), html.Div(""), html.Div(""), ""

    # If the number of selected rows is neither 1 nor 2, display the message 
    if len(selected_rows) not in [1, 2]:
        return html.Div([
            html.P([
                html.B("Please select up to two rows to compare medication side effects."),
                html.Br(),  # Line break
                html.B("Your selections will be highlighted in the table")
            ], style={'textAlign': 'center', 'color': 'red', 'marginTop': '10px'})
        ]), html.Div(""), html.Div(""), html.Div(""), ""  

    selected_medications = [data[i]['medication_name'] for i in selected_rows]
    filtered_df = df_medication[df_medication['medication_name'].isin(selected_medications)]

    # Side Effects Chart
    side_effects_data = []
    for med in selected_medications:
        med_side_effects = filtered_df[filtered_df['medication_name'] == med][[
            'side_effect_common_1', 'side_effect_common_2', 'side_effect_common_3', 
            'side_effect_common_4', 'side_effect_rare'
        ]].melt(value_name='side_effect').dropna()
        side_effects_count = med_side_effects['side_effect'].value_counts().reset_index()
        side_effects_count.columns = ['side_effect', 'count']
        side_effects_count['medication_name'] = med
        side_effects_data.append(side_effects_count)

    side_effects_df = pd.concat(side_effects_data)
    side_effect_fig = go.Figure()

    color_palette = ['#377eb8', '#ff7f00']
    for i, med in enumerate(selected_medications):
        med_data = side_effects_df[side_effects_df['medication_name'] == med]
        side_effect_fig.add_trace(go.Bar(
            x=med_data['side_effect'],
            y=med_data['count'],
            name=med,
            marker_color=color_palette[i % len(color_palette)]
        ))

    side_effect_fig.update_layout(
        barmode='group',
        title='Side Effects by Medication',
        xaxis_title='Side Effect',
        yaxis_title='Number of people',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(55, 126, 184)',
        height=450,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        xaxis=dict(
            tickangle=45,  
        )
    )

    # Age Distribution Chart
    age_bins = [0, 20, 40, 60, float('inf')]
    age_labels = ['(0-20]', '(20-40]', '(40-60]', '>60']
    filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels)
    age_distribution = filtered_df.groupby('age_group').size().reset_index(name='count')

    age_fig = go.Figure(data=[go.Bar(
        x=age_distribution['age_group'],
        y=age_distribution['count'],
        marker_color='#377eb8'
    )])
    age_fig.update_layout(
        title='Age Distribution',
        xaxis_title='Age Group',
        yaxis_title='Number of people',
        paper_bgcolor='rgba(0, 0, 0, 0)', #https://community.plotly.com/t/create-plots-with-transparent-background/14658
        plot_bgcolor='rgba(55, 126, 184)',
        width=370,  
        height=400  
    )

    # Race Distribution Chart
    race_distribution = filtered_df['race'].value_counts()
    race_fig = go.Figure(data=[go.Bar(
        x=race_distribution.index,
        y=race_distribution.values,
        marker_color='#377eb8'
    )])
    race_fig.update_layout(
        title='Race Distribution',
        xaxis_title='Race',
        yaxis_title='Number of people',
        paper_bgcolor='rgba(0, 0, 0, 0)', #https://community.plotly.com/t/create-plots-with-transparent-background/14658
        plot_bgcolor='rgba(55, 126, 184)',
        width=370,  
        height=400
    )
    race_fig.update_xaxes(
        ticks="outside",  
        tickangle=45,   
    )

    # Demographics Title
    if len(selected_rows) == 1:
        demographics_title = html.Div([
            html.H5("Sources' Demographics", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Demographic distribution of samples who used {selected_medications[0]}", 
                style={'textAlign': 'center', 'fontSize': '12px'})
        ])
    elif len(selected_rows) == 2:
        demographics_title = html.Div([
            html.H5("Sources' Demographics", style={'textAlign': 'center', 'fontWeight': 'bold', 'marginBottom': '10px'}),
            html.P(f"Demographic distribution of samples who used {selected_medications[0]} and {selected_medications[1]}", 
                style={'textAlign': 'center', 'fontSize': '12px'})
        ])

#add classname here to standardize the format each elements as desired
    return "" , dcc.Graph(figure=side_effect_fig), dcc.Graph(figure=age_fig,className='my-bg-color'), dcc.Graph(figure=race_fig,className='my-bg-color'), demographics_title

# Callback for displaying percentage based on selected rows
@app.callback(
    Output('percentage-info', 'children'),  
    Input('medication-table', 'selected_rows'),
    State('medication-table', 'data'),
    Input('treatment-type-dropdown', 'value')
)
def update_percentage(selected_rows, data, treatment_type):
    if treatment_type == 'surgery':
        return ""  # Do not display anything if surgery is selected

    if not selected_rows:
        return "No medication selected."

    selected_medications = [data[i]['medication_name'] for i in selected_rows]
    filtered_df = df_percentage[df_percentage['medication_name'].isin(selected_medications)]

    # Check the number of selected medications
    num_medications = filtered_df['medication_name'].nunique()

    if num_medications == 1 or num_medications == 2:
        # Format and display percentages for each selected medication
        percentage_info = []
        for _, row in filtered_df.iterrows():
            medication_name = row['medication_name']
            percentage = row['percentage'] * 100 
            percentage_info.append(
                html.Div(
                    [
                       html.P([
                            # To make important text stand out, we apply class (specified details in css) to percentage and medication name using html.Span: https://www.w3schools.com/tags/tag_span.asp
                            html.Span(f"{percentage:.2f}%", className ='text-bold'), 
                            " of patients taking ", 
                            html.Span(medication_name, className ='text-bold'),
                            " report experiencing side effects."
                    ]
                ) ]
            ))
        
        # Return the list of percentage info wrapped in a Div
        return html.Div(percentage_info + ["The bar chart breaks down these side effects,\n"
         "showing the percentage of each type experienced by patients"], 
        style={ 'padding': '10px',
                'borderRadius': '10px' ,
                'marginTop': '20px',
                'textAlign': 'center',
                'whiteSpace': 'pre-wrap'
                })

    else:
        # Return a blank message if the number of selected medications is not 1 or 2
        return html.Div([
            html.P("")
        ])


# Callback: Show/Hide the medication info, percentage info, and medication table only if treatment type is 'medication'
@app.callback(
    [Output('medication-info-container', 'style'), 
     Output('percentage-info', 'style'), 
     Output('medication-table', 'style_table')],    
    [Input('treatment-type-dropdown', 'value'),
     Input('medication-table', 'data'),            # Check when data is available
     Input('medication-table', 'selected_rows')]   # Check selected rows
)
def toggle_medication_info_and_table(treatment_type, data, selected_rows):
    # Handle the style for the medication info container (First Box)
    if treatment_type == 'medication' and data and len(selected_rows) in [1, 2]:
        # Show the container when medication is selected, and there are 1 or 2 selected rows
        medication_info_style = {'textAlign': 'center', 'marginTop': '10px', 'display': 'block'}
        percentage_info_style = {'textAlign': 'center', 'marginTop': '10px', 'display': 'block'}
    else:
        # Hide the containers otherwise
        medication_info_style = {'display': 'none'}
        percentage_info_style = {'display': 'none'}

    # Handle the style for the medication table (border)
    if data:
        # If there's data, apply the border
        table_style = {
            'min-height': 'auto',  
            'max-height': 'auto',
            'overflowY': 'auto',
            'overflowX': 'auto',
            'width': '100%',
            'border': '4px solid rgba(230, 245, 255)',  # Show the border when data is present
            'borderRadius': '10px'
        }
    else:
        # If no data, keep the border hidden
        table_style = {
            'height': '450px',
            'overflowY': 'auto',
            'overflowX': 'auto',
            'width': '100%',
            'border': 'none',  
            'borderRadius': '10px'
        }

    # Return all three 
    return medication_info_style, percentage_info_style, table_style

    # Callback: Hide the message when a disease is selected
@app.callback(
    Output('selection-message', 'style'),  
    Input('search-dropdown', 'value')     
)
def hide_message_on_disease_selection(disease_name):
    if disease_name:
        return {'display': 'none'}
    else:
        return {'textAlign': 'center', 'marginTop': '10px', 'color': 'blue','fontSize':'20px'}

@app.callback(
    Output('medication-table', 'style_data_conditional'),
    Input('medication-table', 'selected_rows'),
)
def update_selected_row_styles(selected_rows):
    # https://dash.plotly.com/datatable/conditional-formatting
    # this part is adapted from learning about conditional formatting in link above + help from chatgpt to edit the code a bit to get alternating color in table
    style_data_conditional = [ # Base styles for odd and even rows
        {'if': {'row_index': 'even'}, 'backgroundColor': 'rgba(230, 245, 255)'},
        {'if': {'row_index': 'odd'}, 'backgroundColor': 'white'}
    ]
    if selected_rows:   # Add highlight style for selected rows
        for i in selected_rows:
            style_data_conditional.append({
                'if': {'row_index': i},
                'backgroundColor': '#FFFFC5'  
            })

    return style_data_conditional

        
if __name__ == "__main__":
    app.run(debug=True)



