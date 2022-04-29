import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from fpdf import FPDF


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

def report(df_post, df_comment):
    derniere_date = df_post.loc[df_post.shape[0]-1, "DATE"]
    
    df_alerte = df_post[(df_post.Sentiments_comment < 0) | (df_post.score_pondere < 0)] 
    df_report = df_alerte[df_alerte.DATE == derniere_date]
    
    cat = df_report.Topics_text.unique().tolist()
    
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.add_page()
    pdf.image("ia_school_report.png", x = 100, w = 250, h = 80)

    pdf.set_font(family='Times', style='B', size=24)
    pdf.cell(w=0, h=45, txt=f"Rapport Smart-City du {str(derniere_date)[:10]}", align='C', ln=1, border = 1)
    
    pdf.set_font(family='Times', style = "B", size = 16)
    pdf.cell(w=300, h=80, txt = "Humeur journalière", ln = 0)
    
    pdf.set_font(family='Times', style = "B", size = 16)
    pdf.cell(w=300, h=80, txt = "Sujets de mécontentement", ln=1)
    
    pdf.set_font(family='Times', style = "B", size = 16)
    pdf.cell(w=0, h=150, txt = "", ln=1)
    
    pdf.image("humeur_journee.png", x = 30, y = 200, w = 150, h=150)
    pdf.image("barplot_report.png", x = 260, y = 200, w = 300, h=150)


    for x in cat:
        pdf.set_font(family='Times', style='B', size=20)
        pdf.cell(w=0, h=50, txt=f"Catégorie {x}", ln=1)

        """ On isole un dataframe pour chaque catégorie """

        df_cat = df_report[df_report.Topics_text == x]
        df_cat = df_cat.reset_index()

        for ind, row in df_cat.iterrows():
            """On isole la date du post et son ID pour joindre les commentaires"""

            date_post = str(row['DATE'])[:10]
            ID_POST = row['ID_POST']

            pdf.set_font(family='Times', style='B', size=14)
            pdf.cell(w=0, h=30, txt=f"Post n°{ind+1}", ln=1)

            pdf.set_font(family='Times', size=12)
            pdf.multi_cell(w=0, h=20, txt=row["post"])

            df_comment_cat = df_comment[df_comment.ID_POST == ID_POST]
            df_comment_cat = df_comment_cat.reset_index()
            for x in range(len(df_comment_cat)):
                """On isole les commentaires du posts en question avec l'ID du post"""

                pdf.set_font(family='Times',style='B', size=12)
                pdf.cell(w=0, h=20, txt=f"Commentaire n°{x+1}", ln=1)

                pdf.set_font(family='Times', size=12)
                pdf.multi_cell(w=0, h=15, txt=df_comment_cat.loc[x, "comment"])

    return pdf.output(f'report_{str(derniere_date)[:10]}.pdf', dest="S")

