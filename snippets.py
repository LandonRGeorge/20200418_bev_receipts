#%%
# #%%

# import plotly.offline as pyo
# import plotly.graph_objs as go
# import plotly as py

# fig = go.Figure()


# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["BeerSum"],
#         name="BeerSum",
#         text=df_data['LocName']
#         )
# )


# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["LiqSum"],
#         name="LiqSum",
#         text=df_data['LocName']
#         )
# )

# fig.add_trace(
#     go.Bar(
#         x=df_data.index+1,
#         y=df_data["WineSum"],
#         name="WineSum",
#         text=df_data['LocName']
#         )
# )

# fig.update_layout(
#     go.Layout(
#         title=dict(
#             text='Total Receipts', y=0.9, x=0.5, xanchor="center", yanchor="top",
#         ),
#         barmode='stack',
#         hovermode="closest",
#         titlefont=dict(size=24, color="black"),
#         xaxis={'categoryorder':'category ascending'},
#         yaxis=dict(title="Total Receipts"),
#         yaxis_tickprefix="$",
#         yaxis_tickformat=",.",
#         template="plotly_white",  # can try plotly, plotly_white, ggplot, ggplot
#     )
# )

# fig.show()