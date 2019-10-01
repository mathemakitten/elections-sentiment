# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import plotly.graph_objects as go

from collections import Counter
import datetime

from data_prep import *

# Data
df = load_and_clean_data()

# Dash setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # https://codepen.io/chriddyp/pen/bWLwgP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Subset data

# Create dropdown list of weeks, Monday - Sunday



# Top left chart: tweets by volume over time
tweet_volume_df = pd.DataFrame(data={'num_tweets': df['day'].value_counts().sort_index(),
                                     'day_of_week': pd.to_datetime(
                                         df['day'].value_counts().sort_index().index).dayofweek.map(
                                         day_of_week_mapping)},
                               index=df['day'].value_counts().sort_index().index, )

header = html.Div(children=[
    html.H1(children='The 2019 Canadian Federal Election'),
    html.H3(children='Days Until Election: {}'.format((datetime.date(2019, 10, 21) - datetime.date.today()).days)),
    html.Label(['Analyzing the Twitter conversation around the Canadian election']),
    html.Label(['Dashboard by ', html.A('@mathemakitten', href='https://twitter.com/mathemakitten', target='_blank')]),
])

volume_graph = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [{'x': tweet_volume_df.index, 'y': tweet_volume_df['num_tweets'],
                      'type': 'line',
                      'hover_name': tweet_volume_df.index, 'hovertext': tweet_volume_df['day_of_week']},
                     ],
            'layout': {'title': 'Tweets about Canadian Politics from April - September 2019'}
        }
    )], className="six columns")

overview_stats = html.Div(children=[
    html.H1(children='Overview'),
    html.P(html.Span(children=[html.B('Date range: '), '{} to {}'.format(df['day'].min(), df['day'].max())])),
    html.P(html.Span(children=[html.B('Criteria: '), 'tweets in any language containing the official hashtags ',
                               '#cdnpoli, #elxn43, #polcan, #ItsOurVote, #CestNotreVote,',
                               ' or tweets from official party leaders ',
                               html.A('@JustinTrudeau', href='http://www.twitter.com/JustinTrudeau', target='_blank'),
                               ', ',
                               html.A('@AndrewScheer', href='http://www.twitter.com/AndrewScheer', target='_blank'),
                               ', ',
                               html.A('@ElizabethMay', href='http://www.twitter.com/ElizabethMay', target='_blank'),
                               ', ',
                               html.A('@theJagmeetSingh', href='http://www.twitter.com/theJagmeetSingh',
                                      target='_blank'), ', ',
                               # html.A('@MaximeBernier', href='http://www.twitter.com/AndrewScheer', target='_blank'), ', ',
                               html.A('@yfblanchet', href='http://www.twitter.com/yfblanchet', target='_blank'),
                               ])),
    html.P(html.Span(children=[html.B('Total number of tweets: '), df.shape[0]])),
    html.P(html.Span(children=[html.B('Number of distinct tweeters: '), df['username'].nunique()])),
    html.Span(children=[html.B('Number of distinct hashtags: '), len(set(df['hashtags'].str.cat(sep=' ').split(' ')))]),
], className="six columns")

top10_accounts_by_tweets = html.Div(children=[
    dcc.Graph(
        id='top10_accounts_by_tweets',
        figure=go.Figure(data=go.Bar(y=df['username'].value_counts().head(10).index.tolist(),
                                     x=df['username'].value_counts().head(10),
                                     orientation='h'),
                         layout=go.Layout(title='Top 10 Accounts by Number of Tweets',
                                          hovermode='closest',
                                          xaxis={'title': 'number of tweets'}, yaxis={'autorange': 'reversed'},
                                          font={'family': 'Arial', 'size': 14}
                                          )),
    ),
    html.Span(children=[html.P('Who talks the most?')], style={'text-align': 'center'})],
    className="six columns")

# top 10 mentions by Twitter handles
all_mentions = df['mentions'].str.cat(sep=' ').split(' ')
mentions_df = pd.DataFrame(Counter(all_mentions).most_common(10), columns=['mentions', 'count'])
top10_mentions = html.Div(children=[
    dcc.Graph(
        id='top10_mentions',
        figure=go.Figure(data=go.Bar(y=mentions_df['mentions'],
                                     x=mentions_df['count'],
                                     orientation='h'
                                     ),
                         layout=go.Layout(title='Top 10 Accounts @Mentioned',
                                          hovermode='closest',
                                          xaxis={'title': 'user', 'tickangle': -60},
                                          yaxis={'title': 'times mentioned', 'autorange': 'reversed'},
                                          font={'family': 'Arial', 'size': 14}
                                          )),
    ),
    html.Span(children=[html.P('Who do people talk to/about the most?')], style={'text-align': 'center'})
], className="six columns")

top10_accounts_by_faves = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_faves',
              figure=go.Figure(data=go.Bar(
                  y=df.groupby(['username']).agg({'favorites': sum}).sort_values('favorites', ascending=False).head(
                      10).index.tolist(),
                  x=df.groupby(['username']).agg({'favorites': sum}).sort_values('favorites', ascending=False).head(10)[
                      'favorites'],
                  orientation='h'),
                  layout=go.Layout(title='Top 10 Accounts by Favourites',
                                   hovermode='closest',
                                   xaxis={'title': 'times tweets favourited by others'},
                                   yaxis={'autorange': 'reversed'},
                                   font={'family': 'Arial', 'size': 14}
                                   )),
              ),
    html.Span(
        children=[html.P('This graph aims to capture tweeters who tweet highly-faved Canadian political content.')],
        style={'text-align': 'center'})
], className="six columns")

top10_accounts_by_retweets = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_retweets',
              figure=go.Figure(data=go.Bar(
                  y=df.groupby(['username']).agg({'retweets': sum}).sort_values('retweets', ascending=False).head(
                      10).index.tolist(),
                  x=df.groupby(['username']).agg({'retweets': sum}).sort_values('retweets', ascending=False).head(10)[
                      'retweets'],
                  orientation='h'),
                  layout=go.Layout(title='Top 10 Accounts by Retweets',
                                   hovermode='closest',
                                   xaxis={'title': 'times tweets retweeted by others'},
                                   yaxis={'autorange': 'reversed'},
                                   font={'family': 'Arial', 'size': 14}
                                   )),
              ),
    html.Span(children=[html.P('This graph captures people who tweet highly-retweeted Canadian political content.')],
              style={'text-align': 'center'})
], className="six columns")

# TODO: query Twitter API for verified status & likes/retweets per each user for "activity" measure

retweet_df = data_prep_retweet_df(df)
top10_tweets_by_retweets = html.Div([
    html.H5(children='Top 10 tweets by retweets'),
    html.Div(children=[dash_table.DataTable(id='top10_tweets_by_retweets',
                                            columns=[{"name": i, "id": i} for i in retweet_df.columns],
                                            data=retweet_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'Width': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial",
                                                        'font-size': 12
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '50px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

favorites_df = data_prep_favorites_df(df)
top10_tweets_by_favorites = html.Div([
    html.H5(children='Top 10 tweets by favorites'),
    html.Div(children=[dash_table.DataTable(id='top10_tweets_by_favorites',
                                            columns=[{"name": i, "id": i} for i in favorites_df.columns],
                                            data=favorites_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'Width': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial", 'font-size': 12
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)',
                                                          'fontWeight': 'bold'})],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

# Top 25 hashtags
hashtag_counts_df = data_prep_hashtag_counts_df(df)
top25_hashtags = html.Div(children=[
    html.Span(html.H5(children='Top 25 Popular Hashtags'), style={'text-align': 'center'}),
    dcc.Graph(
        id='top25_hashtags',
        figure=go.Figure(data=go.Bar(y=hashtag_counts_df['count'],
                                     x=hashtag_counts_df['hashtag']),
                         layout=go.Layout(hovermode='closest',
                                          xaxis={'tickangle': -60}, yaxis={'title': 'number of times tweeted'},
                                          font={'family': 'Arial'}, margin=dict(l=50, r=50, t=20, b=20)
                                          )),
    )], style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})





# Top external links
links_df, all_urls = data_prep_links_df(df)
top10_links = html.Div([
    html.H5(children='Top 10 External Links'),
    html.Span(children=[html.P('What are people sharing on Twitter?')]),
    html.Div(children=[dash_table.DataTable(id='top10_links',
                                            columns=[{"name": i, "id": i} for i in links_df.columns],
                                            data=links_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'Width': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial",
                                                        'font-size': 12,
                                                        'text-align': 'left'
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             ),
    ],
    className="six columns",
    style={'padding-top': '0px', 'padding-right': '5px', 'padding-bottom': '50px', 'padding-left': '20px'})

# Top 10 domains linked
domains_df = data_prep_domains_df(all_urls)

top10_domains = html.Div(children=[
    html.Span(html.H5(children='Top 10 External Domains'), style={'text-align': 'center'}),
    dcc.Graph(
        id='top10_domains',
        figure=go.Figure(data=go.Bar(y=domains_df['domain'],
                                     x=domains_df['count'],
                                     orientation='h'
                                     ),
                         layout=go.Layout(  # title='Top 10 External Domains',
                             hovermode='closest',
                             xaxis={'title': 'times linked'},
                             yaxis={'autorange': 'reversed'},
                             font={'family': 'Arial', 'size': 12},
                             margin=dict(l=25, r=50, t=20, b=0)
                         )),
    ),
    html.Span(children=[html.P('Which websites do people link to the most?')], style={'text-align': 'center'})
], className="six columns", style={'height': '400px'})


# Average number of tweets by time of day (EST)
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['date'].dt.strftime('%H')  #:%M')
average_number_of_tweets_per_hour = df.groupby(['hour'])['hour'].count()/df['day'].nunique()
hour_dict = {'00': 'Midnight', '01': '1:00 AM', '02': '2:00 AM', '03': '3:00 AM', '04': '4:00 AM', '05': '5:00 AM', '06': '6:00 AM',
             '07': '7:00 AM', '08': '8:00 AM', '09': '9:00 AM', '10': '10:00 AM', '11': '11:00 AM', '12': '12:00 PM',
             '13': '1:00 PM', '14': '2:00 PM', '15': '3:00 PM', '16': '4:00 PM', '17': '5:00 PM', '18': '6:00 PM',
             '19': '7:00 PM', '20': '8:00 PM', '21': '9:00 PM', '22': '10:00 PM', '23': '11:00 PM'}

tweet_volume_hourly = html.Div(children=[
    dcc.Graph(
        id='tweet_volume_by_hour',
        figure={
            'data': [{'x': [hour_dict[x] for x in average_number_of_tweets_per_hour.index.tolist()],
                      'y': [int(item) for item in average_number_of_tweets_per_hour.values],
                      # 'y': ["%.2f" % item for item in average_number_of_tweets_per_hour.values],
                      'type': 'line',
                      #'hover_name': average_number_of_tweets_per_hour.index,
                      'hovertext': 'tweets'},
                     ],
            'layout': {'title': 'Average Tweet Volume by Time of Day (Eastern Standard Time)', 'xaxis': {'tickangle': -60}}
        }
    ),
    html.Span(children=[html.P('When does the conversation happen across Canada?')], style={'text-align': 'center'}),
], style={'padding-bottom': '50px'})


header_politician = html.Div(children=[html.H3(children='Breakdown by Political Party Leader')], style={'padding-top': '120px', 'padding-bottom': '50px'})

# POLITICAL PARTY LEADERS
LEADER_USERNAMES = ['JustinTrudeau', 'AndrewScheer', 'ElizabethMay', 'theJagmeetSingh', 'yfblanchet']
leader_df = df[df['username'].isin(LEADER_USERNAMES)]  #df[df['A'].isin([3, 6])]
leader_df['days_until_election'] = [(x - datetime.date(2019, 10, 21)).days for x in pd.to_datetime(leader_df['day']).dt.date]

# Tweet volume by political party leader over time
leader_tweet_volume = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.RangeSlider(
        id='day-slider',
        min=leader_df['days_until_election'].min(),
        max=leader_df['days_until_election'].max(),
        value=[leader_df['days_until_election'].min(), leader_df['days_until_election'].max()],
        marks={str(day): str(-day) for day in sorted(leader_df['days_until_election'].unique())},
        # TODO figure out how to rotate tick marks - https://community.plot.ly/t/how-to-rotate-labels-on-rangeslider/6666
        step=None
    )
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '10px', 'padding-bottom': '50px'})





app.layout = html.Div([
    header,  # header
    html.Div(children=[volume_graph, overview_stats], className="row"),  # first row of grid
    html.Div(children=[top10_accounts_by_tweets, top10_mentions], className="row"),  # second row of grid,
    html.Div(children=[top10_accounts_by_faves, top10_accounts_by_retweets], className="row"),  # second row of grid,
    # top10_accounts_by_faves,
    top10_tweets_by_retweets,  # third row of grid
    top10_tweets_by_favorites,  # fourth row of grid,
    top25_hashtags,  # fifth row of the grid
    tweet_volume_hourly,
    html.Div(children=[top10_links, top10_domains], className="row"),
    header_politician,
    leader_tweet_volume
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '50px'})


# CALLBACKS
color_dict = {'AndrewScheer': '#1A4782', 'JustinTrudeau': '#D71920', 'theJagmeetSingh': '#F37021', 'ElizabethMay': '#3D9B35', 'yfblanchet': '#33B2CC'}
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('day-slider', 'value')])
def update_figure(selected_day):
    filtered_leader_df = leader_df[(leader_df.days_until_election >= selected_day[0]) & (leader_df.days_until_election <= selected_day[1])]
    traces = []
    for i in filtered_leader_df.username.unique():
        df_by_leader = filtered_leader_df[filtered_leader_df['username'] == i]
        traces.append(go.Scatter(
            x=df_by_leader.groupby(['day'])['day'].count().index.tolist(),
            y=df_by_leader.groupby(['day'])['day'].count(),
            text=df_by_leader['username'],
            mode='lines+markers',
            opacity=0.7,
            marker={
                 'size': 7,
                 'line': {'width': 0.5, 'color': 'white'},
                'color': color_dict[i]
             },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='How much does each party leader tweet leading up to the election?',
            xaxis={'title': 'days until election'},
            yaxis={'title': 'number of tweets'},#, 'range': [0, 100]},
            margin={'l': 40, 'b': 40, 't': 30, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
        )
    }



if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
