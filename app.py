# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import plotly.graph_objects as go

import pandas as pd
import datetime
import glob

# Data
files = glob.glob('tweets/cdnpoli_*.csv')[0:30]
df = pd.read_csv(files[0])

for file in files[1:]:
    df_tmp = pd.read_csv(file)
    df = pd.concat([df, df_tmp])

df['day'] = pd.to_datetime(df['date']).dt.date
day_of_week_mapping = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
df['day_of_week'] = [x.weekday() for x in df['day']] #.get_weekday()
df.replace({'day_of_week': day_of_week_mapping})

# Top left chart: tweets by volume over time
tweet_volume_df = pd.DataFrame(data={'num_tweets': df['day'].value_counts().sort_index(),
                                     'day_of_week': pd.to_datetime(df['day'].value_counts().sort_index().index).dayofweek.map(day_of_week_mapping)},
                               index=df['day'].value_counts().sort_index().index,
                               #columns=['num tweets', 'day of week']
                               )

# Dash setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # https://codepen.io/chriddyp/pen/bWLwgP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

header = html.Div(children=[
    html.H1(children='The 2019 Canadian Federal Election'),
    html.H3(children='Days Until Election: {}'.format((datetime.date(2019, 10, 21) - datetime.date.today()).days)),
    # html.P(children='as told by tweets'),

    html.Label(['The Twitter conversation around the Canadian election']),# | dashboard by ', html.A('@mathemakitten', href='https://twitter.com/mathemakitten', target='_blank')]),
    html.Label(['Dashboard by ', html.A('@mathemakitten', href='https://twitter.com/mathemakitten', target='_blank')]),
])

volume_graph = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': tweet_volume_df.index, #df['day'].value_counts().sort_index().index,
                 'y': tweet_volume_df['num_tweets'], #df['day'].value_counts().sort_index(),
                 'type': 'line',
                 'name': 'SF',
                 'hover_name': tweet_volume_df.index, #df['day'].value_counts().sort_index().index,
                 'hovertext': tweet_volume_df['day_of_week'] #pd.to_datetime(df['day'].value_counts().sort_index().index).dayofweek.map(day_of_week_mapping)
                 },
                #{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                #{'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Tweets about Canadian Politics from April - September 2019'
            }
        }
    )
], className="six columns")


overview_stats = html.Div(children=[
    html.H1(children='Overview'),
    # html.Span(['An ', html.B('important'), ' undertaking']
    html.P(html.Span(children=[html.B('Date range: '), '{} to {}'.format(df['day'].min(), df['day'].max())])),
    html.P(html.Span(children=[html.B('Criteria: '), 'tweets in any language containing the official hashtags ',
                               '#cdnpoli, #elxn43, #polcan, #ItsOurVote, #CestNotreVote,',
                               ' or tweets from official party leaders ',
                               html.A('@JustinTrudeau', href='http://www.twitter.com/JustinTrudeau', target='_blank'), ', ',
                               html.A('@AndrewScheer', href='http://www.twitter.com/AndrewScheer', target='_blank'), ', ',
                               html.A('@ElizabethMay', href='http://www.twitter.com/ElizabethMay', target='_blank'), ', ',
                               html.A('@theJagmeetSingh', href='http://www.twitter.com/theJagmeetSingh', target='_blank'), ', ',
                               #html.A('@MaximeBernier', href='http://www.twitter.com/AndrewScheer', target='_blank'), ', ',
                               html.A('@yfblanchet', href='http://www.twitter.com/yfblanchet', target='_blank'),
                               ])),
    html.P(html.Span(children=[html.B('Total number of tweets: '), df.shape[0]])),
    html.P(html.Span(children=[html.B('Number of distinct tweeters: '), df['username'].nunique()])),
    html.Span(children=[html.B('Number of distinct hashtags: '), len(set(df['hashtags'].str.cat(sep=' ').split(' '))) ]),
], className="six columns")

'''
annotations: [{
    text: "My SubTitle",
      font: {
      size: 13,
      color: 'rgb(116, 101, 130)',
    },
'''

top10_accounts_by_tweets = html.Div(children=[
    dcc.Graph(
        id='top10_accounts_by_tweets',
        figure=go.Figure(data=go.Bar(y=df['username'].value_counts().head(10).index.tolist(),
                                     x=df['username'].value_counts().head(10),
                                     orientation='h'),
                         layout=go.Layout(title='Top 10 Accounts by Tweets',
                                          hovermode='closest',
                                          xaxis={'title': 'number of tweets'},
                                          yaxis={'autorange': 'reversed'},
                                          font={'family': 'Arial', 'size': 14}
                                          )),
    ),
    html.Span(children=[html.P('This graph aims to capture tweeters by tweet volume.')], style={'text-align': 'center'})
], className="six columns")


top10_accounts_by_faves = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_faves',
              figure=go.Figure(data=go.Bar(y=df.groupby(['username']).agg({'favorites':sum}).sort_values('favorites', ascending=False).head(10).index.tolist(),
                                           x=df.groupby(['username']).agg({'favorites':sum}).sort_values('favorites', ascending=False).head(10)['favorites'],
                                           orientation='h'),
                               layout=go.Layout(title='Top 10 Accounts by Favourites',
                                                hovermode='closest',
                                                xaxis={'title': 'times tweets favourited by others'},
                                                yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                          )),
    ),
    html.Span(children=[html.P('This graph aims to capture tweeters who tweet content popular Canadian political content.')], style={'text-align': 'center'})
], className="six columns")


# TODO: query Twitter API for verified status & likes/retweets per each user for "activity" measure


retweet_df = df.sort_values(by=['retweets'], ascending=False)[['username', 'day', 'text', 'retweets']].head(10)
top10_tweets_by_retweets = html.Div([
    html.H5(children='Top 10 tweets by retweets'),
    html.Div(children=[dash_table.DataTable(id='top10_tweets_by_retweets',
                                            columns=[{"name": i, "id": i} for i in retweet_df.columns],
                                            data=retweet_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial"
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'maxWidth': '2000px', 'maxHeight': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

favorites_df = df.sort_values(by=['favorites'], ascending=False)[['username', 'day', 'text', 'favorites']].head(10)
top10_tweets_by_favorites = html.Div([
    html.H5(children='Top 10 tweets by favorites'),
    html.Div(children=[dash_table.DataTable(id='top10_tweets_by_favorites',
                                            columns=[{"name": i, "id": i} for i in favorites_df.columns],
                                            data=favorites_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'maxWidth': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial"
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'maxWidth': '2000px', 'maxHeight': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

app.layout = html.Div([
    header,  # header
    html.Div(children=[volume_graph, overview_stats], className="row"),  # first row of grid
    html.Div(children=[top10_accounts_by_tweets, top10_accounts_by_faves], className="row"),  # second row of grid,
    top10_tweets_by_retweets,  # third row of grid
    top10_tweets_by_favorites,  # fourth row of grid
                       ])

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)

