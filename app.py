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

HEADER_COLOR = '#83c3cd'  # color guide: https://www.color-hex.com/color/07889b

df = load_and_clean_data()
tweet_volume_df = data_prep_calculate_tweet_volume(df)
top10_accounts_by_tweets_df = data_prep_accounts_by_tweet_volume(df)
mentions_df = data_prep_top10_mentions(df)
top10_accounts_faves_df = data_prep_top10_accounts_fave(df)
top10_accounts_retweets_df = data_prep_top10_accounts_retweets(df)
retweet_df = data_prep_retweet_df(df)
favorites_df = data_prep_favorites_df(df)
hashtag_counts_df = data_prep_hashtag_counts_df(df)
average_number_of_tweets_per_hour = data_prep_tweets_by_time(df)
links_df, all_urls = data_prep_links_df(df)
domains_df = data_prep_domains_df(all_urls)
leader_df = data_prep_leader_df(df)
leader_hashtag_counts = data_prep_count_hashtags_by_leader(df)

# Constants from df
MIN_DATE = df['day'].min()
MAX_DATE = df['day'].max()
TOTAL_NUM_TWEETS = df.shape[0]
NUM_TWEETERS = df['username'].nunique()
NUM_HASHTAGS = len(set(df['hashtags'].str.cat(sep=' ').split(' ')))

del(df)

# Dash setup
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # https://codepen.io/chriddyp/pen/bWLwgP
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'The 2019 Canadian Federal Election on Twitter'
server = app.server

# Twitter authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)

# Top header
header = html.Div(children=[
    html.H1(children='The 2019 Canadian Federal Election'),
    html.H3(children='Days Until Election: {}'.format((datetime.date(2019, 10, 21) - datetime.date.today()).days)),
    html.H5(children='Last snapshot: {}'.format('October 1')),  # October 1 data
    html.Label(['Analyzing the Twitter conversation around the Canadian election']),
    html.Label(['Dashboard by ', html.A('@mathemakitten', href='https://twitter.com/mathemakitten', target='_blank')]),
])

# Graph: volume of tweets over time
volume_graph = html.Div(children=[
    dcc.Graph(id='example-graph',
              figure={'data': [{'x': tweet_volume_df.index, 'y': tweet_volume_df['num_tweets'],  'type': 'line',
                                'hover_name': tweet_volume_df.index, 'hovertext': tweet_volume_df['day_of_week'],}
                               ],
                      'layout': {'title': 'Tweets about Canadian Politics from July - October 2019'}
                      })], className="six columns")

# Table: General overview stats
overview_stats = html.Div(children=[
    html.H1(children='Overview'),
    html.P(html.Span(children=[html.B('Date range: '), '{} to {}'.format(MIN_DATE, MAX_DATE)])),
    html.P(html.Span(children=[html.B('Criteria: '), 'tweets in any language containing the official hashtags ',
                               '#cdnpoli, #elxn43, #polcan, #ItsOurVote, #CestNotreVote,', ' or tweets from official party leaders ',
                               html.A('@JustinTrudeau', href='http://www.twitter.com/JustinTrudeau', target='_blank'), ', ',
                               html.A('@AndrewScheer', href='http://www.twitter.com/AndrewScheer', target='_blank'),  ', ',
                               html.A('@ElizabethMay', href='http://www.twitter.com/ElizabethMay', target='_blank'), ', ',
                               html.A('@theJagmeetSingh', href='http://www.twitter.com/theJagmeetSingh', target='_blank'), ', ',
                               # html.A('@MaximeBernier', href='http://www.twitter.com/AndrewScheer', target='_blank'), ', ',
                               html.A('@yfblanchet', href='http://www.twitter.com/yfblanchet', target='_blank'),
                               ])),
    html.P(html.Span(children=[html.B('Total number of tweets: '), TOTAL_NUM_TWEETS])),
    html.P(html.Span(children=[html.B('Number of distinct tweeters: '), NUM_TWEETERS])),
    html.Span(children=[html.B('Number of distinct hashtags: '), NUM_HASHTAGS]),
], className="six columns")


# Graph: Top 10 Accounts by Tweet Volume
top10_accounts_by_tweets = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_tweets',
              figure=go.Figure(data=go.Bar(y=top10_accounts_by_tweets_df.index.tolist(),
                                           x=top10_accounts_by_tweets_df['username'], # this is actually count
                                           orientation='h',
                                           marker_color='#07889B'
                                           ),
                               layout=go.Layout(title='Top 10 Accounts by Number of Tweets',
                                                hovermode='closest',
                                                xaxis={'title': 'number of tweets'}, yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                                )),
              ), html.Span(children=[html.P('Who talks the most?')], style={'text-align': 'center'})],
    className="six columns")

# Graph: Top 10 mentions by Twitter handles
top10_mentions = html.Div(children=[
    dcc.Graph(id='top10_mentions',
              figure=go.Figure(data=go.Bar(y=mentions_df['mentions'], x=mentions_df['count'], orientation='h',
                                           marker_color='#51abb9'
                                           ),
                               layout=go.Layout(title='Top 10 Accounts @Mentioned',
                                                hovermode='closest',
                                                xaxis={'title': 'user', 'tickangle': -60},
                                                yaxis={'title': 'times mentioned', 'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14}
                                                )),
              ), html.Span(children=[html.P('Who do people talk to/about the most?')], style={'text-align': 'center'})
], className="six columns")


#  Graph: Top 10 Accounts by Favorites
top10_accounts_by_faves = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_faves',
              figure=go.Figure(data=go.Bar(
                  y=top10_accounts_faves_df.index.tolist(),
                  x=top10_accounts_faves_df['favorites'],
                  marker_color=HEADER_COLOR,
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
top10_accounts_by_retweets = html.Div(children=[
    dcc.Graph(id='top10_accounts_by_retweets',
              figure=go.Figure(data=go.Bar(
                  y=top10_accounts_retweets_df.index.tolist(),
                  x=top10_accounts_retweets_df['retweets'],
                  marker_color='#b4dbe1',
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
                                                        'font-size': 14
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '50px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

top10_tweets_by_favorites = html.Div([
    html.H5(children='Top 10 tweets by favorites'),
    html.Div(children=[dash_table.DataTable(id='top10_tweets_by_favorites',
                                            columns=[{"name": i, "id": i} for i in favorites_df.columns],
                                            data=favorites_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto',
                                                        'minWidth': '0px', 'Width': '500px',
                                                        'whiteSpace': 'normal',
                                                        'font-family': "Arial", 'font-size': 14
                                                        },
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': HEADER_COLOR,
                                                          'fontWeight': 'bold'})],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             )],
    style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})

# Top 25 hashtags
top25_hashtags = html.Div(children=[
    html.Span(html.H5(children='Top 25 Popular Hashtags'), style={'text-align': 'center'}),
    dcc.Graph(
        id='top25_hashtags',
        figure=go.Figure(data=go.Bar(y=hashtag_counts_df['count'],
                                     x=hashtag_counts_df['hashtag'],
                                     marker_color='#07889b'
                                     ),
                         layout=go.Layout(hovermode='closest',
                                          xaxis={'tickangle': -60}, yaxis={'title': 'number of times tweeted'},
                                          font={'family': 'Arial'}, margin=dict(l=50, r=50, t=20, b=20)
                                          )),
    )], className="six columns", style={'padding-top': '10px', 'padding-right': '50px', 'padding-bottom': '50px', 'padding-left': '50px'})


# Average number of tweets by time of day (EST)

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
top10_links = html.Div([
    html.H5(children='Top 10 External Links'),
    html.Span(children=[html.P('What are people sharing on Twitter?')]),
    html.Div(children=[dash_table.DataTable(id='top10_links',
                                            columns=[{"name": i, "id": i} for i in links_df.columns],
                                            data=links_df.to_dict('records'),
                                            style_table={'overflowX': 'scroll'},
                                            style_cell={'height': 'auto', 'minWidth': '0px', 'Width': '500px', 'whiteSpace': 'normal',
                                                        'font-family': "Arial", 'font-size': 14, 'text-align': 'left'},
                                            style_as_list_view=True,
                                            style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
                                            )],
             style={'overflowX': 'scroll', 'Width': '2000px', 'Height': '400px', 'font-family': 'Open Sans'}
             ),
],  className="six columns",
    style={'padding-top': '0px', 'padding-right': '5px', 'padding-bottom': '50px', 'padding-left': '20px'})


# Top 10 domains linked

top10_domains = html.Div(children=[
    html.Span(html.H5(children='Top 10 External Domains'), style={'text-align': 'center'}),
    dcc.Graph(id='top10_domains',
              figure=go.Figure(data=go.Bar(y=domains_df['domain'], x=domains_df['count'], orientation='h',
                                           marker_color='#07889B'
                                           ),
                               layout=go.Layout(hovermode='closest',
                                                xaxis={'title': 'times linked'}, yaxis={'autorange': 'reversed'},
                                                font={'family': 'Arial', 'size': 14},
                                                margin=dict(l=25, r=50, t=20, b=0), height=350
                                                )),
              ),
    html.Span(children=[html.P('Which websites do people link to the most?')], style={'text-align': 'center'})
], className="six columns", style={'height': '400px'})

header_politician = html.Div(children=[html.H3(children='Breakdown by Political Party Leader')], style={'padding-left': '50px', 'padding-top': '20px', 'padding-bottom': '20px'})

# POLITICAL PARTY LEADERS

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
                    marks={str(day): {'label': str(-day), 'style': {"transform": "rotate(-90deg)", 'fontSize': 10}} for day in sorted([x for x in leader_df['days_until_election'].unique() if x % 5 == 0])},
                    step=None
                    )
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'})


# Header for hashtags by politicians
hashtags_politician_header = html.Div(children=[html.H3(children='Top 10 Hashtags by Political Party Leader')], style={'padding-left': '50px', 'padding-top': '50px', 'padding-bottom': '10px'})


# What are the politicians tweeting about? (hashtags)
hashtag_leader_cards = []
for leader in LEADER_USERNAMES:
    hashtag_leader_cards.append(html.Div([html.P(children=[leader]),
                                          html.Div(children=[dash_table.DataTable(id='top_hashtags_by_leader_{}'.format(leader),
                                                columns=[{"name": i, "id": i} for i in ['hashtag', 'count']],
                                                data=leader_hashtag_counts[leader].to_dict('records'),
                                                style_table={'overflowX': 'scroll'},
                                                style_cell={'height': 'auto', 'minWidth': '0px', 'maxWidth': '90px', #'whiteSpace': 'normal',
                                                            'font-family': "Arial", 'font-size': 14},
                                                style_cell_conditional=[{'if': {'column_id': 'count'}, 'width': '20%'}],
                                                style_as_list_view=True,
                                                style_header={'backgroundColor': color_dict[leader],
                                                              'fontWeight': 'bold', 'font-color': 'white'}
                                                )], style={'overflowX': 'scroll', 'Height': '400px', 'font-family': 'Open Sans', 'maxWidth':'200px'}
                                                   )
                                          ], style={'padding-left': '25px'}, className="two columns",))


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
                                     'font-family': "Arial", 'font-size': 14
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
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
                                     'font-family': "Arial", 'font-size': 14
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
                         ),
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'})


# Table: Named entity detection
entity_df = pickle.load(open('nlp_results/named_entities.pkl', 'rb')).head(20)
top10_named_entities = html.Div([
    html.H5(children='Top 20 Most Common Named Entities'),
    html.P(children='* Entities extracted with natural language methods; performance is variable'),
    dash_table.DataTable(id='common-entities', columns=[{"name": i, "id": i} for i in ['entity', 'count']],
                         data=entity_df.to_dict('records'),
                         style_table={'overflowX': 'scroll'},
                         style_cell={'height': 'auto', 'maxHeight': '300px', 'minWidth': '100px', 'Width': '500px', 'whiteSpace': 'normal',
                                     'font-family': "Arial", 'font-size': 14
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
                         ),
], style={'padding-left': '50px', 'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'}, className="six columns")


# Table: Named entity detection broken down by politician
entity_leader_df = pickle.load(open('nlp_results/df_politician.pkl', 'rb')).head(10)
named_entities_by_leader = html.Div([
    html.H5(children='Most Common Named Entities Mentioned by Leader'),
    html.P(children='* Entities extracted with natural language methods; performance is variable'),
    dcc.Dropdown(id='leader-entities-dd',
                     options=[{'label': i, 'value': i} for i in LEADER_USERNAMES],
                     value=1,
                     ),
    dash_table.DataTable(id='common-entities-leader', columns=[{"name": i, "id": i} for i in ['entity', 'count']],
                         #data=entity_df.to_dict('records'),
                         style_table={'overflowX': 'scroll'},
                         style_cell={'height': 'auto', 'maxHeight': '300px', 'minWidth': '100px', 'Width': '500px', 'whiteSpace': 'normal',
                                     'font-family': "Arial", 'font-size': 14
                                     },
                         style_as_list_view=True,
                         style_header={'backgroundColor': HEADER_COLOR, 'fontWeight': 'bold'}
                         ),
], style={'padding-right': '50px', 'padding-top': '50px', 'padding-bottom': '20px'}, className="six columns")


# Top header
footer = html.Div(children=[
    html.H3(children='Coming soon'),
    html.P(['* Tweet similarity analysis & topic modeling']),
    html.P(['* Reverse-proxying for a domain, perhaps 🙃']),
], style={'padding-left': '50px'})


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
    top10_tweets_by_leader_retweets,
    html.Div(children=[top10_named_entities, named_entities_by_leader], className="row"),
    footer

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


@app.callback(Output('common-entities-leader', 'data'), [Input('leader-entities-dd', 'value')])
def update_leader_retweets(leader):
    filtered_leader_df = entity_leader_df[entity_leader_df['username'] == leader] #.sort_values(by=['retweets'], ascending=False)[['day', 'text', 'retweets']].head(10).sort_values(by=['retweets'], ascending=False)
    # parse out entities
    entity_count = filtered_leader_df['named_entity'].tolist()
    entity_count = [i for j in entity_count for i in j]
    leader_entities_df = pd.DataFrame(Counter(entity_count).most_common(10), columns=['entity', 'count'])
    return leader_entities_df.to_dict('records')


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)
    #app.run_server()
    #app.run_server(debug=True, dev_tools_hot_reload=False)

