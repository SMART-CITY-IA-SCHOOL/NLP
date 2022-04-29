from markdown import markdown
import pandas as pd
import json
import matplotlib.pyplot as plt
import streamlit as st
import streamlit.components.v1 as stc
import plotly.express as px
import seaborn as sns
from streamlit_option_menu import option_menu
import streamlit.components.v1 as components
import plotly.graph_objects as go
import numpy as np
from Quartier import humeur, evolution, categorie, report
from datetime import timedelta
import time
import base64

timestr = time.strftime("%Y%m%d-%H%M%S")

logo = "logoSC.png"
image = "smart_city.png"
ia_scool_logo = "ia_school_logo.png"
st.set_page_config(page_icon = logo, page_title ="Smart City !", layout = "wide")


def load_data(df):
    df = pd.read_csv(df)
    return df

df_post = load_data("df_post.csv")
df_post.DATE = pd.to_datetime(df_post.DATE).dt.date

df_comment = load_data("df_comment.csv")

def home():
    st.title(":hibiscus: Projet Smart City")
    st.subheader("Détecter les causes de mécontentement des résidents")
    st.markdown("**Cet webApp a été codée dans le cadre du projet IA proposé par l'IA School sur le thème de\
        Smart-City. Elle permet à l'utilisateur de pouvoir détecter rapidement les sources de mécontentement des\
    résidents des quartiers Smart-City. Elle se décompose en plusieurs onglets :**")

    st.markdown("##### :rage: Alerte")
    st.write("La page alerte se veut être un rapport des post et commentaires négatifs des derniers jours.\
        De plus l'utilisateur pourra télécharger un pdf du rapport quotidien avec les posts et commentaires jugés négatifs\
            par catégorie.")

    st.markdown("##### :speech_balloon: Quartier ####")
    st.write("L'onglet quartier permet de définir un intervalle de temps et afficher les KPI de cet intervalle.\
        On peut ainsi analyser les tendances à l'échelle d'une année et détecter quels ont été les sujets de \
            mécontentement des usagers. Les graphiques affichés permettent de voir en un coup d'oeil quelles actions\
                 devraient être menées en priorité.")

    st.markdown("##### :hammer: Maintenance ####")
    st.write("La page maintenance est une analyse des tickets de maintenance. Elle permet de voir rapidement si\
        les tickets sont pris en compte en temps et en heure et quels sont les problèmes majoritaires vécus par les \
            résidents.")
    

    


    



def page_quartier():
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        col1.selectbox("Choisir le quartier", options = ["Quartier 1", "Quartier 2"])

        premiere_date = df_post.loc[0, "DATE"]
        derniere_date = df_post.loc[df_post.shape[0]-1, "DATE"]

        date_min = col2.date_input("Choisir la date min", value = premiere_date, min_value=premiere_date, max_value=derniere_date, )
        date_max = col3.date_input("Choisir la date max", value = derniere_date, min_value=premiere_date, max_value=derniere_date)
        
        
    df_temp = df_post[(df_post.DATE > date_min) & (df_post.DATE < date_max)]

    expander_kpi = st.expander(label='AFFICHER KPI', expanded=False)

    with expander_kpi:

        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre de Posts", len(df_temp))
        col2.metric("Nombre de Likes", sum(df_temp.nb_like))
        col3.metric("Nombre de commentaires", sum(df_temp.nb_comment))
             

    expander_plot = st.expander(label='SENTIMENTS', expanded=False)

    with expander_plot:
        col1, col2, col3 = st.columns([3,1,7])
        with col1:
            humeur(df_temp)

        with col3:
            evolution(df_temp)

    expander_categorie = st.expander(label='CATEGORIES', expanded=False)
    with expander_categorie:


        categorie(df_temp)

        barplot = df_temp.groupby("Topics_text").agg({"post":"count", "score_pondere":"mean"}).reset_index()
        barplot.columns = ["Topics_text", "count", "score_pondere"]
        barplot.score_pondere = round(barplot.score_pondere,2)
        barplot = barplot.sort_values("count", ascending=True).tail(10)

        with st.container():
            col1, col2, col3 = st.columns([6,3,6])

            with col2:
                cat = st.selectbox("Choisir une catégorie", barplot.Topics_text.unique())

        with st.container():
            df_cat_pos = df_temp[(df_temp.Topics_text == cat) & (df_temp.score_pondere > 0)]
            df_cat_neg = df_temp[(df_temp.Topics_text == cat) & (df_temp.score_pondere < 0)]
            
            col1, col2, col3, col4 = st.columns([6,2,2,6])
            with col2:
                
                m = st.markdown("""
                <style>
                div.stButton > button:first-child {
                    background-color: rgb(91, 213, 96);
                }
                </style>""", unsafe_allow_html=True)

                pos = st.button("Posts Positifs")

            with col3:
                n = st.markdown("""
                <style>
                div.stButton > button:first-child {
                    background-color: rgb(233, 120, 46);
                }
                </style>""", unsafe_allow_html=True)

                neg = st.button("Posts négatifs")

        with st.container():
            if neg:
                st.table(df_cat_neg[["DATE", "post", "score_pondere"]].set_index("DATE"))

            if pos:
                st.table(df_cat_pos[["DATE", "post", "score_pondere"]].set_index("DATE"))

            


def alerte():
    derniere_date = df_post.loc[df_post.shape[0]-1, "DATE"]
    date_15j = pd.to_datetime(derniere_date) - timedelta(days=7)

    df_post.DATE = pd.to_datetime(df_post.DATE)
    df_alerte = df_post[df_post.DATE > date_15j]
    df_alerte = df_alerte[(df_alerte.Sentiments_comment < 0) | (df_alerte.score_pondere < 0)]

    if len(df_alerte) == 0:

        st.header("Everything is fine !")
        st.image("data:image/jpeg;base64,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")
    else:
        nombre_alertes = len(df_alerte)
        categorie_detectees = df_alerte.Topics_text.unique().tolist()
        st.error(f"{nombre_alertes} Alertes potentiellement détectées sur les 7 derniers jours")


        moyenne = df_alerte.groupby("Topics_text").agg({"Sentiments_comment":"mean", "score_pondere":"mean", "nb_comment":"count"})
        moyenne = moyenne.reset_index()
        moyenne["sentiment_general"] = moyenne["Sentiments_comment"] + moyenne["score_pondere"]
        moyenne = moyenne.rename(columns = {"nb_comment":"Nombre_Posts"})
        
        with st.container():
            col1, col2, col3 = st.columns(3)
            col2.subheader("Sujets de mécontentement")
        
        
        
        with st.container():
            col1, col2, col3 = st.columns([1.8,1,3])
        
        with col1:
            st.markdown("#")
            st.markdown("#")
            sns.set(rc={'axes.facecolor':'#F3E9D3', 'figure.facecolor':'#F3E9D3'})
            
            fig, ax = plt.subplots(figsize = (1.4,2.6), facecolor= '#F3E9D3' )
            sns.heatmap(moyenne[["Topics_text", "sentiment_general"]].set_index("Topics_text").sort_values("sentiment_general"),\
                 annot=True, cmap = "Reds_r", linewidths = 5, cbar = False, ax=ax)
            plt.ylabel("")
            plt.xticks(ticks = [])

            st.pyplot(fig)

        with col3:
            fig = px.pie(moyenne, names = "Topics_text", values = "Nombre_Posts",
             color_discrete_sequence = px.colors.sequential.RdBu, hole = 0.5, color = "sentiment_general",width=450,
                height=450)

            fig.update_traces(textinfo='value+label')
            fig.update_layout(showlegend=False)

            st.plotly_chart(fig)

        
        with st.container():
            st.markdown("##")
            col1, col2, col3 = st.columns([1,2,1])
            col2.subheader("Afficher les posts et les commentaires")
            cat = col2.selectbox("Choisir une catégorie", categorie_detectees)
            df_cat = df_alerte[df_alerte.Topics_text == cat]
            df_cat = df_cat.reset_index()

        with st.container():

            for i in range(len(df_cat)):
                ID_POST = df_cat.loc[i,"ID_POST"]
                display_post = pd.DataFrame(df_cat.loc[0, ["post", "DATE"]]).T.set_index("DATE")
                display_comment = df_comment[df_comment.ID_POST == ID_POST][["comment"]].reset_index(drop = True)
                st.markdown(f"##### Catégorie {cat} - Post {i+1} ####")
                st.table(display_post)
                st.table(display_comment)
        
        

        with st.container():

            #Je créé le dataset journalier des posts négatifs
            derniere_date = str(df_post.loc[df_post.shape[0]-1, "DATE"])[:10]
            df_post.DATE = pd.to_datetime(df_post.DATE)
            df_alerte = df_post[df_post.DATE == derniere_date]
            df_post_jour = df_alerte[(df_post.Sentiments_comment < 0) | (df_alerte.score_pondere < 0)]  
            

            valeur_humeur = np.mean(df_alerte["score_pondere"])
            if valeur_humeur < -0.2:
                text = "Mauvaise humeur" 
            elif valeur_humeur > 0.2:
                text = "Bonne humeur"
            else :
                text = "Humeur Maussade"


            #1er graphe
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = valeur_humeur,
                title = {'text': text},
                gauge = {'axis': {'range': [-1, 1]},
                         'bar': {'color': "darkgray"},
                         'steps' : [{'range': [-1, -0.2], 'color': "firebrick"},
                                    {'range': [-0.2, 0.2], 'color': "lightblue"},
                                    {'range': [0.2, 1], 'color': "forestgreen"}] }))

            fig.update_layout( autosize=False, width=300, height=300,margin=dict(l=0, r=0, b=0, t=0))
            fig.write_image("humeur_journee.png", engine='kaleido')


            #2eme graphe
            fig = px.bar(df_post_jour, y="Topics_text", x="score_pondere",
                orientation = "h", color = "Sentiment", color_continuous_scale = "reds_r", range_color = (1, -1),width=450,
                height=300)
            fig.update_xaxes(title = "Sentiment")
            fig.update_yaxes(title = "")
            fig.write_image("barplot_report.png")

            
            st.markdown("###### Télécharger le rapport quotidien")

            export_as_pdf = st.button("Export Report")

            def create_download_link(val, filename):
                b64 = base64.b64encode(val)
                return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

            if export_as_pdf:
                rapport_pdf =  report(df_post, df_comment)
                html = create_download_link(rapport_pdf.encode("latin-1"), f"Rapport_du_{derniere_date}")
                st.markdown(html, unsafe_allow_html=True)




def main():

    with st.sidebar:
        st.image(image, width = 300)
        st.markdown("#")
        st.markdown("####")

        choice = option_menu(
            menu_title = "Quartier",
            options = ["Home", "Alerte", "Quartier", "Maintenance"],
            icons=["house", "exclamation-square", "house","hammer"],
            menu_icon="search"
        )
        st.subheader("Par: ")
        st.text(" Maxime Le Tutour\n Dorian Keddar\n Florian Cunit-Ravet")
        st.image(ia_scool_logo, width = 150)
    if choice == "Home":
        home()
    if choice == "Quartier":
        page_quartier()
    elif choice == "Maintenance":
        pass
    elif choice == "Alerte":
        alerte()
    
    
    


if __name__ == '__main__':
	main()
