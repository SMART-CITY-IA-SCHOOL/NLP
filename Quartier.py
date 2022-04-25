import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

def humeur(df_temp):

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = np.mean(df_temp["score_pondere"]),
        gauge = {'axis': {'range': [-1, 1]},
                'bar': {'color': "darkgray"},
                'steps' : [{'range': [-1, -0.2], 'color': "firebrick"},
                            {'range': [-0.2, 0.2], 'color': "lightblue"},
                            {'range': [0.2, 1], 'color': "forestgreen"}] }))

    fig.update_layout( autosize=False,
        width=300,
        height=300,margin=dict(
            l=0,
            r=0,
            b=0,
            t=0))

    return st.plotly_chart(fig)


def evolution(df_temp):
    
    df_temp["MOIS"] = df_temp.DATE.apply(lambda x: str(x)[:7])
    df_temp["SEMAINE"] = df_temp.DATE.apply(lambda x: x.strftime('%Y-semaine-%U'))

    df_aggr_JOUR = df_temp.sort_values("DATE").groupby("DATE").agg({"score_pondere":"mean"})
    df_aggr_SEMAINE = df_temp.sort_values("SEMAINE").groupby("SEMAINE").agg({"score_pondere":"mean"})
    df_aggr_MOIS = df_temp.sort_values("MOIS").groupby("MOIS").agg({"score_pondere":"mean"})

    if len(df_aggr_MOIS)>6:
        df_aggr = df_aggr_MOIS

    elif len(df_aggr_JOUR) < 30:
        df_aggr = df_aggr_JOUR

    else :
        df_aggr = df_aggr_SEMAINE
    
    fig = px.line(df_aggr, x = df_aggr.index, y = "score_pondere", range_y = (-1,1))
    fig.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
    fig.update_layout(autosize=False, width=700, height = 350)
    fig.update_yaxes(title='', visible=True, showticklabels=True)

    return st.plotly_chart(fig)

def categorie(df_temp):
    barplot = df_temp.groupby("Topics_text").agg({"post":"count", "score_pondere":"mean"}).reset_index()
    barplot.columns = ["Topics_text", "count", "score_pondere"]
    barplot.score_pondere = round(barplot.score_pondere,2)
    barplot = barplot.sort_values("count", ascending=True).tail(10)

    fig = px.bar(barplot, x="count", y="Topics_text", orientation='h', color = "score_pondere",
            color_continuous_scale='rdylgn', range_color=(-0.6, 0.6), title='Top catégories')

    fig.update_yaxes(title="", visible=True, showticklabels=True)
    fig.update_layout(autosize=False, width=1000)

    return st.plotly_chart(fig)