


import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go

# Read the Excel file
#new comment
df_medication = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='newdata')
df_surgery = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='data_surgery')
df_alternative = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='alternative treatment')
df_percentage = pd.read_excel('QBUS5010 simulation data.xlsx', sheet_name='percentage')

# Initialize the Dash app
app1 = dash.Dash(__name__)

        
#Layout
app1.layout = html.Div([

    html.Div([
   # Part A: Search box 
        html.Div([
            html.Label('Disease Name', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='search-dropdown',
                placeholder='Type in disease',
                style={'width': '105%'}
            )
        ], style={'width': '45%', 'marginRight': '5%'}),
    # Part B: treatment type dropdown
        html.Div([
            html.Label('Treatment Type', style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='treatment-type-dropdown',
                options=[
                    {'label': 'Medication', 'value': 'medication'},
                    {'label': 'Surgery', 'value': 'surgery'}
                ],
                value='medication',
                style={'width': '100%'}
            )
        ], style={'width': '45%'})
    ], style={'width': '100%', 'margin': '10px 0', 'display': 'flex', 'justifyContent': 'space-between'}),

    # Part D: Side effects chart area
    html.Div(id='side-effects-chart', style={'marginTop': '20px'}),  

    # Part C: Table display area
    html.Div([
        dash_table.DataTable(
            id='medication-table',
            row_selectable='multi',
            selected_rows=[],
            style_table={'height': '200px', 'overflowY': 'auto', 'overflowX': 'auto', 'width': '100%'},
            style_cell={
                'textAlign': 'left',
                'whiteSpace': 'normal',
                'height': 'auto',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
        )
    ], style={'width': '50%', 'marginTop': '10px', 'display': 'flex', 'justifyContent': 'center'}),

    # Display selected medication names
    html.Div(id='selected-medication-names', style={'margin': '10px 0'}),

 # 
    html.Div(id='area-for-display-percentage', style={ 
    'padding': '10px', 
    'width': '300px', 
    'position': 'absolute',  # Change to relative or use flex/grid layout
    'marginTop': '300px',     # Keep marginTop for spacing
    'marginLeft': '1000px',    # Add marginLeft for horizontal spacing 
    }),


# Part F: Alternative Treatment Section
    html.Div(id='alternative-treatment-section', style={ 
    'padding': '10px', 
    'width': '300px', 
    'position': 'relative',  
    'marginTop': '360px',     # Adjust marginTop to place it below age and race charts
    'marginLeft': '200px',      # Adjust marginLeft as needed
    })
])

# Callback: Update search dropdown options based on treatment type
@app1.callback(
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
@app1.callback(
    Output('medication-table', 'columns'),
    Output('medication-table', 'data'),
    Output('medication-table', 'row_selectable'),
    Output('medication-table', 'selected_rows'),  # Reset selected rows
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




# Callback: Display selected medication names
@app1.callback(
    Output('selected-medication-names', 'children'),
    Input('medication-table', 'selected_rows'),
    State('medication-table', 'data'),
    Input('treatment-type-dropdown', 'value'),
    Input('search-dropdown', 'value') 
)
def display_selected_medications(selected_rows, data, treatment_type, disease_name):

    if not data or len(data) == 0:
        # Do not display anything if the table hasn't show up yet
        return ""


    if treatment_type == 'surgery':
        # If treatment type is surgery, do not display the message
        return ""

    if len(selected_rows) not in [1, 2]:
        return html.Div([
            html.P([
                html.B("Please select up to two rows to compare medication side effects.")
            ])
        ])


    selected_medications = [data[i]['medication_name'] for i in selected_rows]
    filtered_df = df_medication[df_medication['medication_name'].isin(selected_medications)]



    
    # Gather side effects data
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

    # Combine side effects for all selected medications
    side_effects_df = pd.concat(side_effects_data)

    # Create a grouped bar chart
    side_effect_fig = go.Figure()

 

    # Define color-blind-friendly colors
    color_palette = ['#377eb8', '#ff7f00']  

    for i, med in enumerate(selected_medications):
        med_data = side_effects_df[side_effects_df['medication_name'] == med]
        side_effect_fig.add_trace(go.Bar(
            x=med_data['side_effect'],
            y=med_data['count'],
            name=med,
            marker_color=color_palette[i % len(color_palette)]  # Apply color from palette
        ))

    side_effect_fig.update_layout(
        barmode='group',
        title='Side Effects by Medication',
        xaxis_title='Side Effect',
        yaxis_title='Count',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5)
    )




    # Calculate age distribution
    age_bins = [0, 20, 40, 60, float('inf')]
    age_labels = ['(0-20]', '(20-40]', '(40-60]', '>60']
    filtered_df['age_group'] = pd.cut(filtered_df['age'], bins=age_bins, labels=age_labels)

    # Calculate race distribution
    race_distribution = filtered_df['race'].value_counts()

    
    # Create age distribution plot
    age_distribution = filtered_df.groupby('age_group').size().reset_index(name='count')
    age_fig = go.Figure(data=[go.Bar(
    x=age_distribution['age_group'], 
    y=age_distribution['count'],
    hovertemplate='Age Group: %{x}<br>Count: %{y}<extra></extra>'  # Custom tooltip
    )])
    age_fig.update_layout(title='Age Distribution', xaxis_title='Age Group', yaxis_title='Count'
    , width=400, height=300, paper_bgcolor='rgba(0, 0, 0, 0)')

    # Create race distribution plot
    race_fig = go.Figure(data=[go.Bar(
    x=race_distribution.index, 
    y=race_distribution.values,
    hovertemplate='Race: %{x}<br>Count: %{y}<extra></extra>'  # Custom tooltip
    )])
    race_fig.update_layout(title='Race Distribution', xaxis_title='Race', yaxis_title='Count'
    , width=400, height=300, paper_bgcolor='rgba(0, 0, 0, 0)')



    # Return the plots

    
    return html.Div([
    dcc.Graph(figure=age_fig, style={'width': '400px', 'height': '300px', 'position': 'absolute', 'bottom': '0', 'left': '0'}),
    dcc.Graph(figure=race_fig, style={'width': '400px', 'height': '300px', 'position': 'absolute', 'bottom': '0', 'left': '380px'}),
    dcc.Graph(figure=side_effect_fig, style={'width': '710px', 'height': '500px', 'position': 'absolute', 'top': '60%', 'right': '-30px', 'transform': 'translateY(-70%)'}),
    
    # Adjust text to be positioned below and to the right of the side effect chart
    html.Div(
        html.P(html.B("Select the first medication to rank its side effects (descending).\n You can then choose a second for comparison."),
               style={'textAlign': 'center', 'marginTop': '10px', 'whiteSpace': 'pre-wrap'}),
        style={'position': 'absolute', 'top': '80%', 'right': '60px'}
    ), 
 

    html.Div(
        html.P('Sources\' Demographics',
               style={'textAlign': 'center', 'marginTop': '10px','fontSize': '20px', 'fontWeight': 'bold'}),
        style={'position': 'absolute', 'top': '50%', 'left': '200px'}
        ),
    html.Div(
    html.P(
        'Demographic distribution of samples who used {}'.format(
            '{}'.format(selected_medications[0]) if len(selected_medications) == 1 else
            '{} and {}'.format(selected_medications[0], selected_medications[1]) if len(selected_medications) >= 2 else
            'no medications'
            
        ),
        style={'textAlign': 'center', 'marginTop': '10px'}
    ),
    style={'position': 'absolute', 'top': '55%', 'left': '100px'}
)])

#callback for percentage section
@app1.callback(
    Output('area-for-display-percentage', 'children'),
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
    print(f"Selected Medications: {selected_medications}") 

    filtered_df = df_percentage[df_percentage['medication_name'].isin(selected_medications)]
    print(f"Filtered Percentages: {filtered_df}")  

    
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
                        html.P(
                            f"{percentage:.2f}% of patients taking {medication_name} report experiencing side effects.",
                            style={'textAlign': 'center'}
                        )
                    ]
                )
            )
        
        # Return the list of percentage info wrapped in a Div
        return html.Div(percentage_info + ['The bar chart breaks down these side effects, showing the percentage of each type experienced by patients'], style={'textAlign': 'center'})

    else:
        # Return a blank message if the number of selected medications is not 1 or 2
        return html.Div([
            html.P("")
        ])


# Callback: Display alternative treatment for the selected disease
@app1.callback(
    Output('alternative-treatment-section', 'children'),
    Input('search-dropdown', 'value')
)
def update_alternative_treatment(disease_name):
    if disease_name:
        # Fetch the alternative treatment for the selected disease
        treatment_info = df_alternative[df_alternative['disease_name'] == disease_name]['alternative_treatment'].values
        
        if len(treatment_info) > 0 and isinstance(treatment_info[0], str):
            treatments = treatment_info[0].split(',')  # Assuming treatments are comma-separated
            links = [
                html.A(treatment.strip(), href=f"https://www.google.com/search?q={treatment.strip()}", target="_blank") 
                for treatment in treatments
            ]
            return html.Div(
                style={'border': '1px solid #ccc', 'padding': '10px', 'marginTop': '200px'},
                children=[
                    html.H3("Alternative Treatment", style={'textAlign': 'center'}),
                    html.P("Click each option to view further details", style={'textAlign': 'center'}),
                    html.Ul([html.Li(link) for link in links])
                ]
            )
        else:
            return html.P("No alternative treatments available.")
    return ""

# Run the application
if __name__ == '__main__':
    app1.run_server(debug=True)




