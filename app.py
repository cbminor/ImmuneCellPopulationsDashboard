import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output
import plotly.express as px
from db import Database
import numpy as np
from scipy.stats import ttest_ind
import plotly.graph_objs as go

POPULATION_COLUMNS = ["b_cell","cd8_t_cell","cd4_t_cell","nk_cell","monocyte"]
DB_PATH = "cell_counts_db.db"

# Initialize the database and retrieve the data
app = Dash()
db = Database(db_path=DB_PATH)
samples = db.get_all_samples()

# Generate frequency data 
samples["total"] = samples[POPULATION_COLUMNS].sum(axis=1)
for population in POPULATION_COLUMNS:
    col_name = f"{population}_frequency"
    samples[col_name] = samples.apply(lambda row: row[population] / row['total'], axis=1)
    samples[f"{population}_frequency_text"] = samples.apply(lambda row: f"{row[population]} ({np.round(row[col_name] * 100, decimals=2)}%)", axis=1)


def get_filters():
    """ Outlines HTML for the dashboard filters """
    conditions = samples.condition.unique().tolist()
    treatments = samples.treatment.unique().tolist()
    sample_types = samples.sample_type.unique().tolist()
    times_from_start = samples.time_from_treatment_start.unique().tolist()

    return html.Div([
        html.Div([
            html.Div([
                html.Label("Condition"),
                dcc.Dropdown(conditions, conditions, id='condition-dropdown', multi=True),
            ], style={'padding': '10px', 'flex': 1}),
            html.Div([
                html.Label("Treatment"),
                dcc.Dropdown(treatments, treatments, id='treatment-dropdown', multi=True),
            ], style={'padding': '10px', 'flex': 1}),
            html.Div([
                html.Label("Sample Type"),
                dcc.Dropdown(sample_types, sample_types, id="sample-types-dropdown", multi=True),
            ], style={'padding': '10px', 'flex': 1}),
            html.Div([
                html.Label("Time From Treatment Start"),
                dcc.Checklist(times_from_start, times_from_start, id="time-from-start-checklist", inline=True),
            ], style={'padding': '10px', 'flex': 1}),
        ], style={'display': 'flex', 'flexDirection': 'row'}),
    ])

def get_cell_type_frequency(df: pd.DataFrame) -> pd.DataFrame:
    """ Formats a dataframe with the information to be shown in the summary table """
    cols_to_keep = ["sample_id", "total", "b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    data = df[cols_to_keep]
    summary_table = data.melt(id_vars=["sample_id", "total"], var_name="Population", value_name="PopulationCounts")
    summary_table["Frequency"] = summary_table.apply(lambda row: np.round(row.PopulationCounts / row.total * 100, decimals=2), axis=1)
    summary_table.rename(columns={
        "sample_id": "Sample",
        "total": "Total"
    }, inplace=True)
    return summary_table

def generate_summary_table(df: pd.DataFrame) -> html.Div:
    """ Generates a summary table given the dataframe provided 
    
    Args:
        df: A structured dataframe with the information to be shown in the summary table 
        
    Returns:
        An html.Div element containing the code to render the visulization
    """
    return html.Div([
        html.H4("Cell Population Frequencies"),
        dash_table.DataTable(
            id="summary-table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'), # type: ignore
            style_table={'overflowY': 'auto'},
            fixed_rows={'headers': True},
            fixed_columns={'headers': True},
        )
    ], id="summary-table-wrapper")

def get_boxplot_data(df: pd.DataFrame) -> pd.DataFrame:
    """ Reformats the data for use in the boxplot visualization 
    
    Args:
        df: A short form data frame with the population frequency data

    Returns:
        A dataframe in long format with the necessary information to construct the boxplot visualization
    """
    cols_to_keep = ["sample_id", "b_cell_frequency", "cd8_t_cell_frequency", 
                    "cd4_t_cell_frequency", "nk_cell_frequency", "monocyte_frequency", "response"]
    data = df[cols_to_keep]
    return data.melt(id_vars=["sample_id", "response"], 
                     value_vars=["b_cell_frequency", "cd8_t_cell_frequency", "cd4_t_cell_frequency", "nk_cell_frequency", "monocyte_frequency"], 
                     var_name="population_type", 
                     value_name="frequency")

def get_response_t_test_results(df: pd.DataFrame) -> pd.DataFrame:
    """ Runs t-test for each population type to determine if the population frequency is significantly different between 
    subjects who responded to treatment vs non-respondents
    
    Args:
        df: A long-form data frame with frequency data for all cell populations 
        
    Returns:
        A dataframe containing the t-test results for each population type
    """
    pvalues = []
    t_stats = []
    for population in POPULATION_COLUMNS:
        respondents = df[(df["response"] == 'yes') & (df["population_type"] == f"{population}_frequency")]
        non_respondents = df[(df["response"] == 'no') & (df["population_type"] == f"{population}_frequency")]
        t_stat, pval = ttest_ind(respondents.frequency, non_respondents.frequency, equal_var=False)
        pvalues.append(pval)
        t_stats.append(t_stat)
    return pd.DataFrame({"PValue": pvalues, "TestStatistic": t_stats}, index=POPULATION_COLUMNS)

def generate_boxplots(df: pd.DataFrame) ->go.Figure:
    """ Returns the code necessary to render the boxplot visualization 
    
    Args:
        df: The dataframe with the filtered cell population data
        
    Returns:
        The boxplot figure
    """
    df = get_boxplot_data(df)
    stat_results = get_response_t_test_results(df)
    print(df)
    fig = px.box(df, x="response", y="frequency", facet_col="population_type", 
                 title="Comparing Cell Population Frequencies of Responders vs Non-Responders", labels=stat_results.PValue)
    for i, population in enumerate(sorted(POPULATION_COLUMNS)):
        pvalue = stat_results.loc[population, 'PValue']
        num_facets = len(POPULATION_COLUMNS)

        fig.add_annotation(
            x= (i + 0.5) / num_facets,
            y=-0.3,
            xref='paper',
            yref='paper',
            text=f"p = {np.round(pvalue, 4)}", # type: ignore
            showarrow=False,
            font=dict(size=12)
        )
    return fig

def generate_project_viz(df) -> go.Figure:
    """ Returns the project pie chart visualization 
    
    Args:
        df: The dataframe with the filtered cell population data
         
    Returns: 
        The pie chart figure
    """
    data = df.project_id.value_counts()
    fig = px.pie(names=data.index, values=data.values, title="Samples Per Project")
    fig.update_traces(textinfo='value', hoverinfo='label+percent')
    fig.update_layout(height=150, margin=dict(t=25, b=10, l=20, r=20), legend=dict(orientation='h', y=-0.1))
    return fig

def generate_responders_viz(df):
    """ Returns the responders pie chart visualization 
    
    Args:
        df: The dataframe with the filtered cell population data
         
    Returns: 
        The pie chart figure
    """
    data = df.response.value_counts()
    fig = px.pie(names=data.index, values=data.values, title="Responders vs Non-Responders")
    fig.update_traces(textinfo='value', hoverinfo='label+percent')
    fig.update_layout(height=150, margin=dict(t=25, b=10, l=20, r=20), legend=dict(orientation='h', y=-0.1))
    return fig

def generate_gender_viz(df):
    """ Returns the gender pie chart visualization 
    
    Args:
        df: The dataframe with the filtered cell population data
         
    Returns: 
        The pie chart figure
    """
    data = df.sex.value_counts()
    fig = px.pie(names=data.index, values=data.values, title="Male vs Female")
    fig.update_traces(textinfo='value', hoverinfo='label+percent')
    fig.update_layout(height=150, margin=dict(t=25, b=10, l=20, r=20), legend=dict(orientation='h', y=-0.1))
    return fig

# Create the layout for the dashboard
app.layout = html.Div([
    html.H1('Immune Cell Populations Dashboard', style={'textAlign': 'center'}),
    get_filters(),
    html.Div([
        html.Div([
            dcc.Graph(figure=generate_project_viz(samples), id='project-counts'),
            dcc.Graph(figure=generate_responders_viz(samples), id='responders-counts'),
            dcc.Graph(figure=generate_gender_viz(samples), id='gender-counts')
        ], style={'flex': 1, 'display': 'flex', 'flexDirection': 'column', 'gap': '10px'}),
        html.Div([
            generate_summary_table(get_cell_type_frequency(samples)),
        ], style={'flex': 2, 'padding': '0 10px'})
    ], style={'display': 'flex', 'gap': '20px', 'marginBottom': '30px'}),
    html.Div([
        dcc.Graph(figure=generate_boxplots(samples), id='boxplot-figure'),
    ], style={'width': '100%', 'justifyContent': 'center'})
], style={'padding': '20px'})

@app.callback(
    Output('summary-table', 'data'),
    Output('boxplot-figure', 'figure'),
    Output('project-counts', 'figure'),
    Output('responders-counts', 'figure'),
    Output('gender-counts', 'figure'),
    Input('condition-dropdown', 'value'),
    Input('treatment-dropdown', 'value'),
    Input('sample-types-dropdown', 'value'),
    Input('time-from-start-checklist', 'value')
)
def update_figures(conditions, treatments, sample_types, selected_times):
    """ Updates the figures based on the selected filters 
    
    Args:
        conditions: The conditions currently selected
        treatments: The treatments that are currently selected
        sample_types: The sample_types that are selected
        selected_times: The time_from_treatment_start times that should be shown on the dashboard
        
    Returns:
        summary_table: An updated summary table
        boxplot_fig: An updated boxplot visualization
        project_counts: An updated project counts pie chart visualization
        responder_counts: An updated responder counts pie chart visualization
        gender_counts: An updated gender counts pie chart visualization
    """
    filtered_data = samples.copy()

    # Apply the condition filter
    filtered_data = filtered_data[filtered_data['condition'].isin(conditions)]

    # Apply the treatments filter
    filtered_data = filtered_data[filtered_data['treatment'].isin(treatments)]

    # Apply the sample_types filter
    filtered_data = filtered_data[filtered_data['sample_type'].isin(sample_types)]

    # Apply the time from treatment start filter
    filtered_data = filtered_data[filtered_data['time_from_treatment_start'].isin(selected_times)]

    summary_table = get_cell_type_frequency(filtered_data).to_dict('records')
    boxplot_fig = generate_boxplots(filtered_data)
    projects_counts = generate_project_viz(filtered_data)
    responder_counts = generate_responders_viz(filtered_data)
    gender_counts = generate_gender_viz(filtered_data)

    return summary_table, boxplot_fig, projects_counts, responder_counts, gender_counts

if __name__ == '__main__':
    app.run(debug=True)
