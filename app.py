# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table

import plotly.graph_objects as go
import datetime
import tweepy

from secrets import *
from data_prep import *

# Data
df = load_and_clean_data()

# Dash setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # https://codepen.io/chriddyp/pen/bWLwgP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# TODO try to load from most up-to-date cache to avoid recalculation

# Top header
header = html.Div(children=[
    html.H1(children='The 2019 Canadian Federal Election'),
    html.H3(children='Days Until Election: {}'.format((datetime.date(2019, 10, 21) - datetime.date.today()).days)),
    html.H5(children='Last snapshot: {}'.format('September 25')),
    html.Label(['Analyzing the Twitter conversation around the Canadian election']),
    html.Label(['Dashboard by ', html.A('@mathemakitten', href='https://twitter.com/mathemakitten', target='_blank')]),
])

# Top left chart: tweets by volume over time
tweet_volume_df = data_prep_calculate_tweet_volume(df)

# Graph: volume of tweets over time
volume_graph = html.Div(children=[
    dcc.Graph(id='example-graph',
              figure={'data': [{'x': tweet_volume_df.index, 'y': tweet_volume_df['num_tweets'],'type': 'line',
                                'hover_name': tweet_volume_df.index, 'hovertext': tweet_volume_df['day_of_week']},],
                      'layout': {'title': 'Tweets about Canadian Politics from April - September 2019'}
                      })], className="six columns")

# Table: General overview stats
overview_stats = html.Div(children=[
    html.H1(children='Overview'),
    html.P(html.Span(children=[html.B('Date range: '), '{} to {}'.format(df['day'].min(), df['day'].max())])),
    html.P(html.Span(children=[html.B('Criteria: '), 'tweets in any language containing the official hashtags ',
                               '#cdnpoli, #elxn43, #polcan, #ItsOurVote, #CestNotreVote,', ' or tweets from official party leaders ',
                               html.A('@JustinTrudeau', href='http://www.twitter.com/JustinTrudeau', target='_blank'), ', ',
                               html.A('@AndrewScheer', href='http://www.twitter.com/AndrewScheer', target='_blank'),  ', ',
                               html.A('@ElizabethMay', href='http://www.twitter.com/ElizabethMay', target='_blank'), ', ',
                               html.A('@theJagmeetSingh', href='http://www.twitter.com/theJagmeetSingh', target='_blank'), ', ',
                               # html.A('@MaximeBernier', href='http://www.twitter.com/AndrewScheer', target='_blank'), ', ',
                               html.A('@yfblanchet', href='http://www.twitter.com/yfblanchet', target='_blank'),
                               ])),
    html.P(html.Span(children=[html.B('Total number of tweets: '), df.shape[0]])),
    html.P(html.Span(children=[html.B('Number of distinct tweeters: '), df['username'].nunique()])),
    html.Span(children=[html.B('Number of distinct hashtags: '), len(set(df['hashtags'].str.cat(sep=' ').split(' ')))]),
], className="six columns")

# Graph: Top 10 Accounts by Tweet Volume
top10_accounts_by_tweets = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_tweets',
              figure=go.Figure(data=go.Bar(y=df['username'].value_counts().head(10).index.tolist(),
                                           x=df['username'].value_counts().head(10),
                                           orientation='h'),
                               layout=go.Layout(title='Top 10 Accounts by Number of Tweets',
                                                hovermode='closest',
                                                xaxis={'title': 'number of tweets'}, yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                                )),
              ), html.Span(children=[html.P('Who talks the most?')], style={'text-align': 'center'})],
    className="six columns")

# Graph: Top 10 mentions by Twitter handles
mentions_df = data_prep_top10_mentions(df)
top10_mentions = html.Div(children=[
    dcc.Graph(id='top10_mentions',
              figure=go.Figure(data=go.Bar(y=mentions_df['mentions'], x=mentions_df['count'], orientation='h'),
                               layout=go.Layout(title='Top 10 Accounts @Mentioned',
                                                hovermode='closest',
                                                xaxis={'title': 'user', 'tickangle': -60},
                                                yaxis={'title': 'times mentioned', 'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                                )),
              ), html.Span(children=[html.P('Who do people talk to/about the most?')], style={'text-align': 'center'})
], className="six columns")


#  Graph: Top 10 Accounts by Favorites
top10_accounts_faves_df = data_prep_top10_accounts_fave(df)
top10_accounts_by_faves = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_faves',
              figure=go.Figure(data=go.Bar(
                  y=top10_accounts_faves_df.index.tolist(),
                  x=top10_accounts_faves_df['favorites'],
                  orientation='h'),
                  layout=go.Layout(title='Top 10 Accounts by Favourites',
                                   hovermode='closest',
                                   xaxis={'title': 'times tweets favourited by others'},
                                   yaxis={'autorange': 'reversed'},
                                   font={'family': 'Arial', 'size': 14}
                                   )),
              ),
    html.Span(children=[html.P('This graph aims to capture tweeters who tweet highly-faved Canadian political content.')],
              style={'text-align': 'center'})
], className="six columns")

# Graph: Top 10 Accounts by Retweets
top10_accounts_retweets_df = data_prep_top10_accounts_retweets(df)
top10_accounts_by_retweets = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_retweets',
              figure=go.Figure(data=go.Bar(
                  y=top10_accounts_retweets_df.index.tolist(),
                  x=top10_accounts_retweets_df['retweets'],
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

# Graph: Top 10 Accounts by Retweets
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
    )], className="six columns", style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})


# Average number of tweets by time of day (EST)
average_number_of_tweets_per_hour = data_prep_tweets_by_time(df)

tweet_volume_hourly = html.Div(children=[
    dcc.Graph(
        id='tweet_volume_by_hour',
        figure={'data': [{'x': [hour_dict[x] for x in average_number_of_tweets_per_hour.index.tolist()],
                          'y': [int(item) for item in average_number_of_tweets_per_hour.values],
                          'type': 'line', 'hovertext': 'tweets'},
                         ],
                'layout': {'title': 'Average Tweet Volume by Time of Day (Eastern Standard Time)', 'xaxis': {'tickangle': -60}}
                }),
    html.Span(children=[html.P('When does the conversation happen across Canada?')], style={'text-align': 'center'}),
], className="six columns", style={'padding-bottom': '50px'})

# Top external links
links_df, all_urls = data_prep_links_df(df)
top10_links = html.Div([
    html.H5(children='Top 10 External Links'),
    html.Span(children=[html.P('What are people sharing on Twitter?')]),
    html.Div(children=[dash_table.DataTable(id='top10_links',
                                            columns=[{"name": i, "id": i} for i in links_df.columns],
                                            data=links_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto', 'minWidth': '0px', 'Width': '500px', 'whiteSpace': 'normal',
                                                        'font-family': "Arial", 'font-size': 12, 'text-align': 'left'},
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             ),
],  className="six columns",
    style={'padding-top': '0px', 'padding-right': '5px', 'padding-bottom': '50px', 'padding-left': '20px'})


# Top 10 domains linked
domains_df = data_prep_domains_df(all_urls)

top10_domains = html.Div(children=[
    html.Span(html.H5(children='Top 10 External Domains'), style={'text-align': 'center'}),
    dcc.Graph(id='top10_domains',
              figure=go.Figure(data=go.Bar(y=domains_df['domain'], x=domains_df['count'], orientation='h'),
                               layout=go.Layout(hovermode='closest',
                                                xaxis={'title': 'times linked'}, yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 12},
                                                margin=dict(l=25, r=50, t=20, b=0), height=350
                                                )),
              ),
    html.Span(children=[html.P('Which websites do people link to the most?')], style={'text-align': 'center'})
], className="six columns", style={'height': '400px'})

header_politician = html.Div(children=[html.H3(children='Breakdown by Political Party Leader')], style={'padding-top': '20px', 'padding-bottom': '20px'})

# POLITICAL PARTY LEADERS
leader_df = data_prep_leader_df(df)

leader_id_cards = []
leader_profile = {}

for leader in LEADER_USERNAMES:
    user = api.get_user(leader)
    leader_profile[leader] = user
    leader_id_cards.append(html.Div([
        html.P([html.B([user.name])]),
        html.Img(src=user.profile_image_url.replace('_normal', ''), style={'max-width': '50%'}),
        html.P("Location: {}".format(user.location)),
        html.P("Followers: {}".format(user.followers_count)),
        html.P("Tweets: {}".format(user.statuses_count)),
    ], className="two columns", style={'padding-left': '50px', 'font-family': 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, "Helvetica Neue", sans-serif;'}))


# Graph: Tweet volume by political party leader over time
leader_tweet_volume = html.Div([
    dcc.Graph(id='graph-with-slider'),
    dcc.RangeSlider(id='day-slider',
                    min=leader_df['days_until_election'].min(), max=leader_df['days_until_election'].max(),
                    value=[leader_df['days_until_election'].min(), leader_df['days_until_election'].max()],
                    marks={str(day): {'label': str(-day), 'style': {"transform": "rotate(-90deg)", 'fontSize': 8}} for day in sorted([x for x in leader_df['days_until_election'].unique() if x % 5 == 0])},
                    step=None
                    )
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'})


# Header for hashtags by politicians
hashtags_politician_header = html.Div(children=[html.H3(children='Top 10 Hashtags by Political Party Leader')], style={'padding-top': '50px', 'padding-bottom': '10px'})


# What are the politicians tweeting about? (hashtags)
leader_hashtag_counts = data_prep_count_hashtags_by_leader(df)
hashtag_leader_cards = []
for leader in LEADER_USERNAMES:
    hashtag_leader_cards.append(html.Div([html.P(children=[leader]),
                                          html.Div(children=[dash_table.DataTable(id='top_hashtags_by_leader_{}'.format(leader),
                                                columns=[{"name": i, "id": i} for i in ['hashtag', 'count']],
                                                data=leader_hashtag_counts[leader].to_dict('records'),
                                                style_table={'overflowX': 'scroll'},
                                                style_cell={'height': 'auto', 'minWidth': '0px', 'maxWidth': '115px', 'whiteSpace': 'normal',
                                                            'font-family': "Arial", 'font-size': 12},
                                                style_as_list_view=True,
                                                style_header={'backgroundColor': color_dict[leader],
                                                              'fontWeight': 'bold', 'font-color': 'white'}
                                                )], style={'overflowX': 'scroll', 'Height': '400px', 'font-family': 'Open Sans'}
                                                   )
                                          ], className="two columns",))


# Table: Top 10 tweets by leader by likes
top10_tweets_by_leader_likes = html.Div([
    html.H5(children='Top 10 tweets by Leader, by Favorites'),
    dcc.Dropdown(id='leader-likes-dd',
                 options=[{'label': i, 'value': i} for i in LEADER_USERNAMES],
                 value=1,
                 ),
    dash_table.DataTable(id='leader-likes-graph', columns=[{"name": i, "id": i} for i in ['day', 'text', 'favorites']],
                         style_table={'overflowX': 'scroll'},
                         style_cell={'height': 'auto',
                                     'minWidth': '100px', 'Width': '500px', 'whiteSpace': 'normal',
                                     'font-family': "Arial", 'font-size': 12
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                         ),
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'})

# Table: Top 10 tweets by leader by retweets
top10_tweets_by_leader_retweets = html.Div([
    html.H5(children='Top 10 tweets by Leader, by Retweets'),
    dcc.Dropdown(id='leader-retweets-dd',
                 options=[{'label': i, 'value': i} for i in LEADER_USERNAMES],
                 value=1,
                 ),
    dash_table.DataTable(id='leader-retweets-graph', columns=[{"name": i, "id": i} for i in ['day', 'text', 'retweets']],
                         style_table={'overflowX': 'scroll'},
                         style_cell={'height': 'auto', 'minWidth': '100px', 'Width': '500px', 'whiteSpace': 'normal',
                                     'font-family': "Arial", 'font-size': 12
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'}
                         ),
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'})


# Main container
app.layout = html.Div([
    header,
    html.Div(children=[volume_graph, overview_stats], className="row"),
    html.Div(children=[top10_accounts_by_tweets, top10_mentions], className="row"),
    html.Div(children=[top10_accounts_by_faves, top10_accounts_by_retweets], className="row"),
    top10_tweets_by_retweets,
    top10_tweets_by_favorites,
    html.Div(children=[top25_hashtags, tweet_volume_hourly], className="row"),
    html.Div(children=[top10_links, top10_domains], className="row"),
    header_politician,
    html.Div(children=leader_id_cards, className="row"),
    leader_tweet_volume,
    hashtags_politician_header,
    html.Div(children=hashtag_leader_cards, className="row"),
    top10_tweets_by_leader_likes,
    top10_tweets_by_leader_retweets
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '50px'})


# CALLBACKS
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
            marker={'size': 7, 'line': {'width': 0.5, 'color': 'white'}, 'color': color_dict[i]},
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            title='How much does each party leader tweet leading up to the election?',
            xaxis={'title': 'days until election'},
            yaxis={'title': 'number of tweets'},
            margin={'l': 40, 'b': 40, 't': 30, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest',
        )
    }


@app.callback(Output('leader-likes-graph', 'data'), [Input('leader-likes-dd', 'value')])
def update_leader_likes(leader):
    filtered_leader_df = leader_df[(leader_df['username'] == leader)].sort_values(by=['favorites'], ascending=False)[['day', 'text', 'favorites']].head(10).sort_values(by=['favorites'], ascending=False)
    return filtered_leader_df.to_dict('records')


@app.callback(Output('leader-retweets-graph', 'data'), [Input('leader-retweets-dd', 'value')])
def update_leader_retweets(leader):
    filtered_leader_df = leader_df[(leader_df['username'] == leader)].sort_values(by=['retweets'], ascending=False)[['day', 'text', 'retweets']].head(10).sort_values(by=['retweets'], ascending=False)
    return filtered_leader_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)


# TODO PROBLEM SOLVE
'''
Option 1 
- schedule a nightly rescrape of everything
- this means the dashboard is always 1 day behind
- (assuming that the scrape doesn't fail) 
- is it possible to catch HTTPS errors and restart recursively? ugh

Option 2 
- Just put a big "true as of THIS DATE" disclaimer and forget about it

CACHE THE THINGS!!!
'''

# TODO deploy to Google App Engine