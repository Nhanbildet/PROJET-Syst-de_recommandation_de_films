import requests
import streamlit as st
from streamlit_authenticator import Authenticate
import pandas as pd
import plotly_express as px
import seaborn as sns
import matplotlib.pyplot as plt
# Import du module d'écritur
from st_keyup import st_keyup
# Importation du module
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import CountVectorizer
import random
from bs4 import BeautifulSoup
import re
from datetime import datetime, date, timedelta


st.set_page_config(layout="wide",
                   initial_sidebar_state="collapsed" )

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('movie_stats.csv')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10

def accueil():
    st.title("")

def tableau_bord():
    st.title("Tableau de bord")

def selection_acteur():
    st.title("Recherche par acteur/actrice")

def selection_genre():
    st.title("Recherche par genre")

def selection_realisateur():
    st.title("Recherche par réalisateur")

def selection_scenariste():
    st.title("Recherche par scénariste")

def selection_film():
    st.title("Recommandation de films")

with st.sidebar:

    # st.sidebar.markdown(
    # """
    # <style>
    # .sidebar .sidebar-content {
    #     background-color: #f0f0f5;
    #     padding: 10px;
    # }
    # </style>
    # """,
    # unsafe_allow_html=True)

    st.sidebar.image('LOGO.webp')
        
    # st.write('Bienvenue')

    selection = option_menu(menu_title=None,
                            options=["Accueil", "Tableau de bord", "Recherche par genre", "Recherche par actrice/acteur", "Recherche par réalisateur", "Recherche par scénariste", "Recherche par films"],
                            icons=['house', 'kanban', 'book', 'book', 'book', 'book', 'book',],
                            styles={
                            "container": {"background-color": "#262730"},
                            "icon": {"color": "white", "font-size": "15px"}, 
                            "nav-link": {"font-size": "15px", "text-align": "left", "margin":"0px"},
                            "nav-link-selected": {"background-color": "#39445C"}}
                            )


# définition de la fonction d'affichage du top 2 à 4 pour éviter de retaper le code
def fn_top_1(df, max_films =1):

    # initialisation de 6 colonnes
    cols = st.columns(2)

    # variable d'affichage max
    max_films = 1

    # boucle sur le range maxi de la variable d'affichage
    for i in range(max_films):
        # colonne pour info à afficher (titre, réal, année, durée, affiche cliquable)
        with cols[i * 2]:  # définition des colonnes impaires
            # iterrow pour boucler sur les lignes et récupérer les positions de chaque film sélectionné
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'poster_path' in row:
                    # définition de la position souhaitée
                    if pos == i:
                        # affichage des infos du film (titre, réal, année de sortie, durée) selon position définie
                        # double * pour mettre en gras entre les 3 guillemets (balises type html)
                        st.subheader(f'''**{row["title"]}**''')
                        st.markdown(f'''
                            **Réalisateur** : {row["director_name"]}  \n
                            **Année** : {row["startYear"]}  \n
                            **Durée** : {row["runtimeMinutes"]} min
                        ''')
                        # récup image dans le DF via poster_path
                        image_url = f'https://image.tmdb.org/t/p/w500/{row["poster_path"]}?language=fr'
                        # récup lien vers tmdb via l'id du film dans le DF
                        target_url = f'https://www.themoviedb.org/movie/{row["id"]}?language=fr'
                        # affichage de l'image en version cliquable
                        st.markdown(
                            f'<a href="{target_url}" target="_blank">'
                            f'<img src="{image_url}" width="300"></a>',
                            unsafe_allow_html=True
                        )
                        
                        url_video = f"https://api.themoviedb.org/3/movie/{row['id']}/videos"

                        response_video = requests.get(url_video, headers=headers)

                        video_data = response_video.json().get('results', [])

                        trailers = [
                            ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                            ]
                        if trailers:
                            trailer_key = trailers[0]['key']
                            youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                            st.write('Bande-annonce:')
                            st.video(youtube_url)
                            # break pour passer au prochain film de la boucle sur max_films
                            break

        # colonne à droite de la première pour les infos complémentaires du même film (acteurs + synopsis)
        with cols[i * 2 + 1]: # définition des colonnes paires
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'overview' in row:
                    if pos == i:
                        # affichage acteurs
                        st.write(f'**Acteurs** : {row["actor_name"]}')
                        # récupération url via API TMDB en fonction de l'id dans le DF
                        url = f"https://api.themoviedb.org/3/movie/{row['id']}?language=fr"
                        response = requests.get(url, headers=headers)
                        # récupération du synopsis si existant
                        synopsis = response.json().get('overview', 'Aucun synopsis disponible.')
                        # affichage synopsis
                        st.write(f"""
                            <div style="text-align: justify;">
                            {synopsis}
                            </div>
                        """, unsafe_allow_html=True)
                        # break pour passer au prochain film de la boucle sur max_films
                        break

# définition de la fonction d'affichage du top 2 à 4 pour éviter de retaper le code
def fn_top_films(df, max_films =3):

    # initialisation de 6 colonnes
    cols = st.columns(6)

    # variable d'affichage max
    max_films = 3

    # boucle sur le range maxi de la variable d'affichage
    for i in range(max_films):
        # colonne pour info à afficher (titre, réal, année, durée, affiche cliquable)
        with cols[i * 2]:  # définition des colonnes impaires
            # iterrow pour boucler sur les lignes et récupérer les positions de chaque film sélectionné
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'poster_path' in row:
                    # définition de la position souhaitée
                    if pos == i:
                        # affichage des infos du film (titre, réal, année de sortie, durée) selon position définie
                        # double * pour mettre en gras entre les 3 guillemets (balises type html)
                        st.subheader(f'''**{row["title"]}**''')
                        
                        # récup im
                        # récup image dans le DF via poster_path
                        image_url = f'https://image.tmdb.org/t/p/w500/{row["poster_path"]}?language=fr'
                        # récup lien vers tmdb via l'id du film dans le DF
                        target_url = f'https://www.themoviedb.org/movie/{row["id"]}?language=fr'
                        # affichage de l'image en version cliquable
                        st.markdown(
                            f'<a href="{target_url}" target="_blank">'
                            f'<img src="{image_url}" width="200"></a>',
                            unsafe_allow_html=True
                        )
                        
                        url_video = f"https://api.themoviedb.org/3/movie/{row['id']}/videos"

                        response_video = requests.get(url_video, headers=headers)

                        video_data = response_video.json().get('results', [])

                        trailers = [
                            ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                            ]
                        if trailers:
                            trailer_key = trailers[0]['key']
                            youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                            st.write('Bande-annonce:')
                            st.video(youtube_url)
                            # break pour passer au prochain film de la boucle sur max_films
                            break

        # colonne à droite de la première pour les infos complémentaires du même film (acteurs + synopsis)
        with cols[i * 2 + 1]: # définition des colonnes paires
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'overview' in row:
                    if pos == i:
                        # affichage acteurs
                        st.markdown(f'''
                            **Réalisateur** : {row["director_name"]}  \n
                            **Acteur(s)** : {row["actor_name"]} \n
                            **Actrice(s)** : {row["actress_name"]} \n
                            **Année** : {row["startYear"]}  \n
                            **Durée** : {row["runtimeMinutes"]} min \n
                            **Note** : {row["averageRating"]}
                        ''')
                        # st.write(f'\n **Acteurs** : {row["actor_name"]}')
                        # récupération url via API TMDB en fonction de l'id dans le DF
                        url = f"https://api.themoviedb.org/3/movie/{row['id']}?language=fr"
                        response = requests.get(url, headers=headers)
                        # récupération du synopsis si existant
                        synopsis = response.json().get('overview', 'Aucun synopsis disponible.')
                        # affichage synopsis
                        st.write(f"""
                                 **Synopsis**: \n
                            <div style="text-align: justify;">
                            {synopsis}
                            </div>
                        """, unsafe_allow_html=True)
                        # break pour passer au prochain film de la boucle sur max_films
                        break

# Création du menu qui va afficher les choix qui se trouvent dans la variable options
# On indique au programme quoi faire en fonction du choix
if selection == "Accueil":
  
    # créer 3 colonne pour placer l'image à la colonne 2, de manière à la centrer
    col1, col2, col3 = st.columns([1.4,2,1])
    with col1:
        st.write('')
        
    with col2:
        st.image('LOGO.webp', width=600)

    with col3:
        st.write('')
        
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)    

    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.write('')
            
    with col2:
        st.header('Sorties de la semaine')
        
    with col3:
        st.write('')

    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)    

    link = 'https://www.allocine.fr/film/sorties-semaine/'
    html = requests.get(link)
    soup = BeautifulSoup(html.text, 'html.parser')

    # st.divider()

    # conversion de la page en soup
    program = soup.find_all('div', {'class' : 'card entity-card entity-card-list cf'})

    # boucle sur la soup pour trouver les films et séances
    for film in program:

        titres = film.find('a', {'class' : 'meta-title-link'})
        titre_text = titres.text.strip()
        
        col1, col2, col3 = st.columns([1,1,3])

        # affiches
        affiches = film.find_all('img', class_="thumbnail-img")
        
        # print(affiches) # OK infos du films
        
        for affiche in affiches:
            img = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', 
            str(affiche))
            # print(titre_text, img, synopsi)
            st.columns(3)
        
        with col1:
            
            # récupérer id du film
            id = re.findall(r"(?<=cfilm=)\d+(?=\.html)", 
                            str(titres))
            video = 'https://www.allocine.fr/video/player_gen_cmedia=19549962&cfilm=' + id[0] +'.html'

            st.markdown(
            f'<a href="{video}" target="_blank">'
            f'<img src="{img[0]}" width="300"></a>',
            unsafe_allow_html=True
        )
        
        with col2:
            
            # récupérer noms des films
            titres = film.find('a', {'class' : 'meta-title-link'})
            titre_text = titres.text.strip()
            st.header(titre_text)
            

        with col3:
            
            synopsis = film.find('div', {'class' : 'synopsis' })
            synopsi = synopsis.text.strip()     
                
            st.write(f'**{synopsi}**')
    
elif selection == "Tableau de bord":
    
    st.title('Tableau de bord')

    with st.expander("Acteurs/trices - Réalisateurs - Scénaristes"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # tableau des acteurs les plus représentés
            st.subheader('Acteurs les plus présents')
            st.dataframe((film_dataframe['actor_name'][film_dataframe['actor_name'] != 'NC'].apply(lambda x: x.split(','))\
                                                .explode().value_counts().head(10).reset_index())\
                                                .rename(columns={'actor_name' : 'Acteurs', 'count': 'Nombre de films'}),
                                                hide_index=True)

        with col2:
            # tableau des acteurs les plus représentés
            st.subheader('Actrices les plus présentes')
            st.dataframe((film_dataframe['actress_name'][film_dataframe['actress_name'] != 'NC'].apply(lambda x: x.split(','))\
                                                .explode().value_counts().head(10).reset_index())\
                                                .rename(columns={'actress_name' : 'Actrices', 'count': 'Nombre de films'}),
                                                hide_index=True)

        with col3:
            # tableau des réalisateurs les plus représentés
            st.subheader('Réalisateurs les plus présents')
            st.dataframe((film_dataframe['director_name'][film_dataframe['director_name'] != 'NC'].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(10).reset_index())\
                                            .rename(columns={'director_name' : 'Réalisateur', 'count': 'Nombre de films'}),
                                            hide_index=True)
        with col4:
            # tableau des scénaristes les plus représentés
            st.subheader('Scénaristes les plus présents')
            st.dataframe((film_dataframe['writer_name'][film_dataframe['writer_name'] != 'NC'].apply(lambda x: x.split(','))\
                                                .explode().value_counts().head(10).reset_index())\
                                                .rename(columns={'writer_name' : 'Scénariste', 'count': 'Nombre de scénarios'}),
                                                hide_index=True)
            
        # En-tête de l'application
        st.header("Acteurs/actrices dans les films/Séries TV")
        col1, col2  = st.columns(2)
        # Listes pour les sélections
        with col1:
            st.write("Top 20 acteurs/actrices")
            list_actor = ["actor_name", "actress_name"]
            list_classer = ["Films", "Séries TV"]

        # Sélection utilisateur
            actor = st.selectbox("Rechercher un(e) acteur(trice)", list_actor)
            classer = st.selectbox("Classer selon nombre de films ou séries TV", list_classer)

            df_actor = pd.merge(
                left=film_dataframe.loc[film_dataframe['titleType'] == "movie", actor]
                .dropna()
                .apply(lambda x: x.split(","))
                .explode()
                .value_counts()
                .to_frame("Films"),
                right=film_dataframe.loc[film_dataframe['titleType'] == "tvSeries", actor]
                .dropna()
                .apply(lambda x: x.split(","))
                .explode()
                .value_counts()
                .to_frame("Séries TV"),
                left_index= True,
                right_index= True,
                how='inner'
                )

        # Créer les DataFrames pour les acteurs ou actrices
            if actor:
            # Trier et afficher les résultats
                if classer:
                    df_actor = df_actor.iloc[1:,].sort_values(by=classer, ascending=False).head(20)
                    st.table(df_actor)

            else:
                st.write("Veuillez sélectionner un critère pour afficher les données")
        with col2:
            st.write("Recherche par nom")
        #liste de nom d'actor ou d'actress
            list_actress = sorted(film_dataframe['actress_name'].dropna().apply(lambda x: x.split(",")).explode().unique())
            list_actor = sorted(film_dataframe['actor_name'].dropna().apply(lambda x: x.split(",")).explode().unique())

        #creation de selectionbox
            actress = st.checkbox("Rechercher une actrice")
            actor = st.checkbox("Rechercher un acteur")
            if actress:
                actress_name = st.selectbox("Sélectionner une actrice", list_actress,index= None)
                if actress_name:
                    # nb_films = int(film_dataframe.loc[(film_dataframe['titleType'] == "movie") & ( film_dataframe['actress_name'].str.contains(actress_name))]['titleType'].value_counts().sum())
                    # nb_series = int(film_dataframe.loc[(film_dataframe['titleType'] == "tvSeries") & ( film_dataframe['actress_name'].str.contains(actress_name))]['titleType'].value_counts().sum())
                    st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "movie") & (film_dataframe["actor_name"].str.contains(actress_name))]["titleType"].value_counts().sum())} films')
                    st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "tvSeries") & (film_dataframe["actor_name"].str.contains(actress_name))]["titleType"].value_counts().sum())} séries TV')
            
            elif actor:
                actor_name = st.selectbox("Rechercher un acteur ?", list_actor,index= None)
                if actor:
                    # nb_films = int(film_dataframe.loc[(film_dataframe['titleType'] == "movie") & (film_dataframe['actor_name'].str.contains(actor_name))]['titleType'].value_counts().sum())
                    # nb_series = int(film_dataframe.loc[(film_dataframe['titleType'] == "tvSeries") & (film_dataframe['actor_name'].str.contains(actor_name))]['titleType'].value_counts().sum())
                    st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "movie") & (film_dataframe["actor_name"].str.contains(actor_name))]["titleType"].value_counts().sum())} films')
                    st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "tvSeries") & (film_dataframe["actor_name"].str.contains(actor_name))]["titleType"].value_counts().sum())} séries TV')
                    
            else:
                st.write("Veuillez sélectionner un critère pour afficher les données")


    # ---------------------------------------- REPARTITION GENRES ------------------------------------

    with st.expander("Genres"):
        
        df_films = film_dataframe[film_dataframe['titleType'] == "movie"]
        df_films.dropna(subset= ['revenue', 'popularity', 'id', 'budget'],inplace= True) 

        df_genres = pd.read_csv("df_genres.csv")
        def fn_count_genre(var):
            var = str(var)
            var.count(",")
            return (var.count(",") + 1)
        
        df_films['nb_genres'] = df_films['genres'].apply(lambda x: fn_count_genre(x))

        # genre =df_films['genres'].loc[df_films['genres'] != "\\N"]\
        #                 .apply(lambda x: x.split(',')).explode()\
        #                     .value_counts().sort_values(ascending= False).head(10)

        # st.dataframe(df_films['genres'].value_counts())

        # st.dataframe(genre)
        
        #########
        st.header("Les Genres de films ")
        graph_top10 = px.bar(data_frame=df_films['genres'].loc[df_films['genres'] != "\\N"]\
                        .apply(lambda x: x.split(',')).explode()\
                            .value_counts().sort_values(ascending= False).head(10),
                    x='count',
                    text_auto=True,
                    labels={"count" : "Nombre",
                            "genres" : "Genres"},
                    title= f'Top 10 des genres' )
        st.plotly_chart(graph_top10)
        
        # --------------------------------------------------------------
        
        st.write("Sélectionnez le graphique souhaité") 
        
        list_genre = sorted(df_genres['Genres'])
        
        col1, col2 = st.columns(2)
        with col1:
            TopNumber = st.checkbox("Répartition de films selon le nombre de genres")
        with col2:  
            Toprevenue = st.checkbox("Revenu moyen par nombre de genres")
        ##########
        
        col1, col2 = st.columns(2)
        with col1:
        
            if TopNumber:
                graph_pourcentage = px.pie(data_frame= df_films['nb_genres'].value_counts(normalize= True),
                                    names=df_films['nb_genres'].value_counts(normalize= True).reset_index()['nb_genres'],
                                    values= 'proportion',
                                    labels={'1':'1 genre','2':'2 genres','3':'3 genres',
                                            'proportion':'Pourcentage de film'},
                                    title= f'Répartition de films selon nombre de genres')
                st.plotly_chart(graph_pourcentage)

        with col2:

            if Toprevenue:
                tb_revenue_genres = {}
                for i in [1,2,3]:
                    mean_revenue = round(df_films['revenue'].loc[(df_films['nb_genres']== i) & (df_films['revenue'] != 0)].mean(),3)
                    tb_revenue_genres.update({ i : mean_revenue})
                graph_toprevenue = px.bar( x= tb_revenue_genres.keys(),y= tb_revenue_genres.values(),
                                        text_auto=True,
                                        labels= ({"x": "Nombre de genre par film",
                                                    "y" : "Revenu moyen"}),
                                        title= f'Revenu moyen par nombre de genres')
                st.plotly_chart(graph_toprevenue)

            
        genre = st.selectbox("Sélectionner le genre",list_genre, index= None)
        
        ##############
        if genre:
            tb_genre = df_genres.loc[(df_genres['Genres'].str.contains(genre,na= False)) & (df_genres['Revenu moyen (millions)'] != 0)]
            st.write("Caractéristiques du genre sélectionné")
            st.dataframe(tb_genre,hide_index= True)
            data_genre = df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['revenue'] != 0)]
            st.header("Sélectionner une statistique")  
            col1, col2= st.columns(2)
            with col1:
                graph_number= st.checkbox("Total de films par décennie")
                graphique_duree = st.checkbox("Le durée de films par décennie") 
            with col2:
                graphique_revenue = st.checkbox("Revenu & Note")
                graph_buget = st.checkbox("Revenu & Budget")   
            
            if graph_number:
                graph_total = px.histogram(data_genre,
                                        x="decade",
                                        labels=({"decade" : "Décennies",
                                            "count" : "Nombre"}),
                                        text_auto=True)
                st.plotly_chart(graph_total)
                    
            if graphique_duree:
                    st.line_chart(data_genre, y='runtimeMinutes', x='decade', x_label= "Décennie", y_label= "Durée du film")   
            
            if graphique_revenue:
                    st.bar_chart(data_genre, y='revenue', x='averageRating', x_label= "Note", y_label= "Revenu")
            
            if graph_buget:
                    st.line_chart(data_genre, y='revenue', x='budget', x_label= "Budget", y_label= "Revenu")
            st.header("Les meilleurs films du genre sélectionné")
            
            col1, col2= st.columns(2)
            
            with col1: 
                list_trier = ['Note moyenne','Revenu (millions)']
                trier = st.selectbox("Classer par note ou revenu",list_trier, index= None)
            with col2:
                list_decennie = sorted(data_genre['decade'].unique())
                decennie = st.selectbox("Sélection de la décennie",list_decennie, index= None)
            
            df_stat = data_genre[['title','startYear', 'runtimeMinutes','genres', 'averageRating', 'numVotes', 'budget','revenue','popularity','actor_name', 'actress_name','director_name', 'writer_name','decade']]\
                .rename(columns={'title': 'Title','startYear': 'Année de sortie','runtimeMinutes': 'Durée (min)','genres': 'Genres','averageRating': 'Note moyenne','numVotes': 'Nombre de votes','budget': 'Budget (millions)',\
                    'revenue' : 'Revenu (millions)', 'popularity': 'Popularité','actor_name': 'Acteurs','actress_name': 'Actrices','writer_name': 'Scénariste','director_name': 'Réalisateurs'})

            if decennie:
                df_stat = df_stat.loc[df_stat['decade'] == decennie] 
            if trier:
                df_stat = df_stat.sort_values(by=trier,ascending= False) 
            else:
                df_stat = df_stat.sort_values(by='Revenu (millions)', ascending= False).head(5)
            st.dataframe(data= df_stat,hide_index= True)
        ###################
            # st.header("Les meilleurs Acteurs/Actrices dans ce genre")
            tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            if decennie:
                tb_actress = df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['decade'] == decennie)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
                tb_actor =  df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['decade'] == decennie)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            else:
                tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
                tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            
            st.subheader("Acteurs et actrices les plus présents dans la décennie sélectionnée")
            
            col1,col2 = st.columns(2)
            with col1:
                graph_actrices10 = px.bar(x=list(sorted(tb_actress.values())),
                                    y=list(tb_actress.keys()),
                                    text_auto=True,
                                    labels=({"x" : "Nombre",
                                        "y" : "Nom d'actrice"}),
                                    title= f'Top 10 actrices')
                st.plotly_chart(graph_actrices10)
            with col2:
                graph_acteur10 = px.bar(x=list(sorted(tb_actor.values())),
                                    y=list(tb_actor.keys()),
                                    text_auto=True,
                                    labels=({"x" : "Nombre",
                                        "y" : "Nom d'acteur"}),
                                    title= f'Top 10 acteurs')
                st.plotly_chart(graph_acteur10)

    # ---------------------------------------- EVOLUTION DUREE FILMS DECENNIE ------------------------------------

    # création d'un DF sur la durée
    duree = film_dataframe[['tconst', 'runtimeMinutes', 'startYear', 'titleType']]\
            [(film_dataframe['runtimeMinutes'] != 0) & (film_dataframe['runtimeMinutes'] != '\\N') &\
            (film_dataframe['startYear'] != 0) & (film_dataframe['startYear'] != '\\N') &\
            (film_dataframe['titleType'] == 'movie')]\
            .drop_duplicates(subset='tconst')

    # bascule en numérique de toutes les valeurs
    duree['startYear'].apply(lambda x: int(x))
    duree['runtimeMinutes'].apply(lambda x: int(x))
    duree['startYear'] = duree['startYear'].apply(pd.to_numeric)
    duree['runtimeMinutes'] = duree['runtimeMinutes'].apply(pd.to_numeric)

    # création dico vide
    dico_duree = {}
    # boucle sur les années par dizaine
    for annee in range(1900, 2023, 10):
        # print(year)
        dico_duree[annee]=round(duree[(duree['startYear']>=annee)&(duree['startYear']<=annee+10)]['runtimeMinutes'].mean(),2)

    # création d'un DF particulier pour l'affichage
    duree_moy = pd.DataFrame(list(dico_duree.items()), columns=["Décennie", "Durée_moyenne"]) 

    with st.expander("Evolution de la durée des films"):
        # affichage de la stats
        evo_duree = px.line(data_frame=duree_moy,
                            x='Décennie',
                            y='Durée_moyenne',
                            title='Evolution de la durée moyenne des films',
                            labels={'Durée_moyenne' : 'Durée moyenne'}
                            )

        st.plotly_chart(evo_duree, theme=None)

#  --------------------------------------------- SELECTION PAR GENRE --------------------------------------------

elif selection == 'Recherche par genre':

    # affichage du titre de la section
    st.title('Recherche par genre')

    # création liste genres
    liste_genre = sorted(set(film_dataframe['genres'].apply(lambda x: x.split(',')).explode().to_list()))
    liste_genre.append('Veuillez choisir un genre')

    # création liste nationalité des films
    liste_nation = sorted(set(film_dataframe['production_countries'].dropna().apply(lambda x: x.split(',')).explode().to_list()))

    nationalite = {
        "Veuillez choisir un pays de production": "",
        "États-Unis": "US",
        "France": "FR",
        "Autres": "Autres"
    }

    # sélection de la nationalité
    natio_choisie = st.selectbox('Choix de la nationalité', list(nationalite.keys()))

    # affichage des selectbox
    col1, col2 = st.columns(2)

    with col1:
        genre_choisi = st.selectbox('Choix du genre :', liste_genre, index=(len(liste_genre) - 1))

    with col2:
        decennie_choisie = st.selectbox(
            "Choisissez une décennie :",
            options=sorted(film_dataframe['decade'][film_dataframe['decade'] != 0].dropna().unique()),
            index=12
        )

    # condition pour gérer le filtre 'Autres'
    if genre_choisi != 'Veuillez choisir un genre' and natio_choisie != 'Veuillez choisir un pays de production':
        # si sélection nation = autre, on crée un DF qui prend les éléments inverses (~) de FR et US
        if natio_choisie == "Autres":
            # DF selon décennie, natio et genre choisi
            genre_search_decennie = film_dataframe[
                (film_dataframe["genres"].str.contains(genre_choisi)) & 
                (~film_dataframe['production_countries'].str.contains('FR|US', na=False)) &
                (film_dataframe['titleType'] == 'movie') & 
                (film_dataframe['numVotes'] > 5000) &
                (film_dataframe['decade'] == decennie_choisie)]\
                .drop_duplicates(subset="tconst")\
                .sort_values(by='averageRating', ascending=False)\
                .head(10)

            # DF pour affichage les films "hors decennie"
            genre_search = film_dataframe[
                (film_dataframe["genres"].str.contains(genre_choisi)) & 
                (~film_dataframe['production_countries'].str.contains('FR|US', na=False)) &
                (film_dataframe['titleType'] == 'movie') & 
                (film_dataframe['numVotes'] > 5000)]\
                .drop_duplicates(subset="tconst")\
                .sort_values(by='averageRating', ascending=False)\
                .head(10)
        # si sélection nation != autre, on crée un DF qui prend la valeur sélectionnée dans liste_natio
        else:
            # DF selon décennie, natio et genre choisi
            genre_search_decennie = film_dataframe[
                (film_dataframe["genres"].str.contains(genre_choisi)) & 
                (film_dataframe['production_countries'].str.contains(nationalite[natio_choisie], na=False)) &
                (film_dataframe['titleType'] == 'movie') & 
                (film_dataframe['numVotes'] > 5000) &
                (film_dataframe['decade'] == decennie_choisie)]\
                .drop_duplicates(subset="tconst")\
                .sort_values(by='averageRating', ascending=False)\
                .head(10)

            # DF pour affichage les films "hors decennie"
            genre_search = film_dataframe[
                (film_dataframe["genres"].str.contains(genre_choisi)) & 
                (film_dataframe['production_countries'].str.contains(nationalite[natio_choisie], na=False)) &
                (film_dataframe['titleType'] == 'movie') & \
                (film_dataframe['numVotes'] > 5000)]\
                .drop_duplicates(subset="tconst")\
                .sort_values(by='averageRating', ascending=False)\
                .head(10)
            
        st.header(f"Top 10 des films de {genre_choisi} de la décennie {decennie_choisie}")
        genre_top10 = px.bar(
            data_frame=genre_search_decennie.sort_values(by='averageRating', ascending=False).head(10),
            x='averageRating',
            y='title',
            text='averageRating',
            title=f'Top 10 des films du genre {genre_choisi}',
            labels={'averageRating': 'Note moyenne', 'title': 'Titre'}
        )
        genre_top10.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
        genre_top10.update_layout(yaxis=dict(categoryorder='total ascending'), title={'x': 0.5})
        st.plotly_chart(genre_top10)

        # ------------------------------- TOP 2 à 4 GENRE DE LA DECENNIE SELECTIONNEE ---------------------------

        # affichage titre section
        st.subheader(f'Top du genre {genre_choisi} et de la nationalité choisie des années {decennie_choisie}'
                    ,divider='blue')

        # récup fonction affichage top 2 à 4
        fn_top_films(genre_search_decennie, max_films=3)

        # ----------------------------------- TOP 3 TOUTE ANNEES CONFONDUES ------------------------------------------

        # affichage titre section
        st.subheader(f"Top du genre {genre_choisi} et de la nationalité choisie"
                    , divider='blue')

        # récup fonction affichage top 2 à 4 all time
        fn_top_films(genre_search, max_films=3)

        #--------------------------- AFFICHAGE TOUS FILMS ---------------------------
        
        # affichage DF avec tous les films du genre choisi
        with st.expander(f"Cliquer pour afficher tous les films appartenant au genre {genre_choisi}"):
            st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                            [film_dataframe['genres']\
                            .str.contains(genre_choisi)]\
                            .sort_values(by='averageRating', ascending=False)\
                            .rename(columns={'title' : 'Titre',
                                            'averageRating' : 'Note moyenne',
                                            'startYear' : 'Année de Sortie',
                                            'genres' : 'Genre(s)',
                                            'actor_name' : 'Acteur(s)',
                                            'actress_name' : 'Actrice(s)',
                                            'writer_name' : 'Scénariste(s)'}),
                        hide_index=True)

#  --------------------------------------------- SELECTION PAR ACTEUR --------------------------------------------

elif selection == "Recherche par actrice/acteur":


    # créer la liste des acteurs depuis le DF de base, en "explosant" chaque cellule, et ne gardant que les valeurs uniques, par ordre alpha
    liste_actor = sorted((film_dataframe['actor_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())
    liste_actrice = sorted((film_dataframe['actress_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

    # créer une seule liste contenant les acteurs et actrices
    liste_acteur = sorted(set(liste_actor + liste_actrice))

    # ajout valeur par défaut pour affiche
    liste_acteur.append('Veuillez choisir un(e) acteur(trice)')

    st.title('Recherche par actrice/acteur')
    st.write(f"{len(liste_acteur)} actrices/acteurs")

    # cellule de sélection de l'acteur selon la liste définie précédemment
    acteur_choisi = st.selectbox("Choix de l'acteur :",
                                    liste_acteur,
                                    index=(len(liste_acteur) - 1))

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # afficher les éléments seulement si un acteur est sélectionné:
    if acteur_choisi != 'Veuillez choisir un(e) acteur(trice)':

        # afficher le nombre de films dans lesquels a joué l'acteur recherché
        st.subheader(f"{acteur_choisi} a tourné dans {film_dataframe['actor_name'].str.contains(acteur_choisi, na=False).sum()} films") 

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # déclaration de 2 colonnes
        col1, col2 = st.columns(2)

        with col1:

            genres = film_dataframe["genres"].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(5).reset_index()

            # 1er tri pour afficher les infos du DF en fonction du nom choisi par l'utilisateur, en filtrant sur le type 'movie', et en ne prenant que les 10 premiers
            act_search = film_dataframe[(film_dataframe["actor_name"].str.contains(acteur_choisi)) & \
                                        (film_dataframe['titleType'] == 'movie')]\
                                        .drop_duplicates(subset="tconst")\
                                        .sort_values(by='averageRating', ascending=False)\
                                        .head(10)

            # histo Top 10 films de l'acteur recherché
            graph_search = px.bar(data_frame=act_search.sort_values(by='averageRating').head(10),
                                        x='averageRating',
                                        y='title',
                                        text='averageRating',
                                        title=f'Top 10 films de \n{acteur_choisi}',
                                        labels={'averageRating': 'Note moyenne',
                                                'title': ''})
            
            # mettre en gras les données et les positionner à l'extérieur du graph
            graph_search.update_traces(
                        texttemplate='<b>%{text}</b>',
                        textposition='outside'
                        )
            # centrer le titre du graph et mettre en ordre décroissant
            graph_search.update_layout(
                        yaxis=dict(categoryorder='total ascending'),
                        title={'x':0.5}
                        )
            # affichage graph et theme none pour bien distinguer du fond de streamlit
            st.plotly_chart(graph_search)

        with col2:

            # camembert de répartition du Top 5 des genres pour l'acteur recherché
            graph_genre = px.pie(data_frame=act_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                                    values='count',
                                names= act_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])

            # valeurs en gras
            graph_genre.update_traces(textinfo='percent+label',
                                    texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                    )

            # titre en gras et centré
            graph_genre.update_layout(
                title={'text': f'<b>Top 5 des genres des films réalisé par {acteur_choisi}</b>', 'x': 0.2})

            st.plotly_chart(graph_genre)

        # afficher les affiches du top 3 en version cliquable vers TMDB
        st.subheader(f'Top Films de {acteur_choisi}')
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # récupération de la fonction d'affichage du top 2 à 4
        fn_top_films(act_search, max_films=3)

        #--------------------------- AFFICHAGE TOUS FILMS ---------------------------

        # affichage DF avec tous les films de l'acteur/trice choisi
        with st.expander(f"Cliquer pour afficher tous les films avec {acteur_choisi}"):
            st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]
                                [(film_dataframe['actor_name'].str.contains(acteur_choisi, na=False)) |
                                (film_dataframe['actress_name'].str.contains(acteur_choisi, na=False))]
                                .sort_values(by='averageRating', ascending=False)
                                .rename(columns={'title': 'Titre',
                                                'averageRating': 'Note moyenne',
                                                'startYear': 'Année de Sortie',
                                                'genres': 'Genre(s)',
                                                'actor_name': 'Acteur(s)',
                                                'actress_name': 'Actrice(s)',
                                                'writer_name': 'Scénariste(s)'}),
                        hide_index=True)


#  --------------------------------------------- SELECTION PAR REALISATEUR -------------------------------------------

elif selection == "Recherche par réalisateur":

    # création liste réalisateurs
    liste_realisateur = sorted((film_dataframe['director_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

    # ajout valeur par défaut à la liste pour affichage qui se trouvera toujours à la fin de la liste
    liste_realisateur.append('Veuillez choisir un réalisateur')

    # affichage titre section
    st.title('Recherche par réalisateur')
    st.write(f"{len(liste_realisateur)} réalisateurs")

    # création select_box de choix du real en variable pour l'intégrer aux graphs et stats
    realisateur_choisi = st.selectbox("Choix du réalisateur :", 
                                        liste_realisateur,
                                        index=(len(liste_realisateur) - 1)) # pour récupérer la valeur au dernier indice de la liste

    real_search = film_dataframe[(film_dataframe["director_name"].str.contains(realisateur_choisi)) & \
                                (film_dataframe['titleType'] == 'movie')]\
                                .drop_duplicates(subset="tconst")\
                                .sort_values(by='averageRating', ascending=False)\
                                .head(10)

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    if realisateur_choisi != 'Veuillez choisir un réalisateur':

        # afficher le nombre de films réalisé
        st.subheader(f"{realisateur_choisi} a réalisé {film_dataframe['director_name'].str.contains(realisateur_choisi, na=False).sum()} films")

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:

            # Top 10 films du réalisateur
            graph_search = px.bar(data_frame=real_search.sort_values(by='averageRating').head(10),
                                        x='averageRating',
                                        y='title',
                                        text_auto=True,
                                        title=f'Top 10 films de \n{realisateur_choisi}',
                                        labels={'averageRating': 'Note moyenne',
                                                'title': 'Film'})

            # Mettre le titre en gras et centrer
            graph_search.update_layout(title={'text': f'<b>Top 10 films de \n{realisateur_choisi}</b>', 'x': 0.5})

            st.plotly_chart(graph_search)

        with col2:

            # camembert de répartition du Top 5 des genres pour l'acteur recherché
            graph_genre = px.pie(data_frame=real_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                                values="count",
                                names= real_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])

            # valeurs en gras
            graph_genre.update_traces(textinfo='percent+label',
                                    texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                    )

            # titre en gras et centré
            graph_genre.update_layout(
                title={'text': f'<b>Top 5 des genres des films réalisé par {realisateur_choisi}</b>', 'x': 0.2}
                )

            st.plotly_chart(graph_genre)

        # afficher les affiches du top 3 en version cliquable vers TMDB
        st.subheader(f"Top Films de {realisateur_choisi}")
        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

        # ------------------------------------ TOP 2 à 4 FILMS REALISATEUR -----------------------------------

        # récup fonction affichage du top 2 à 4
        fn_top_films(real_search, max_films=3)

        # ------------------------------------ AFFICHAGE DF FILMS REALISATEUR -----------------------------------

        # récup fonction affichage du top 2 à 4
        with st.expander(f"Cliquer pour afficher tous les films de {realisateur_choisi}"):
            st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                            [film_dataframe['director_name']\
                            .str.contains(realisateur_choisi)]\
                            .sort_values(by='averageRating', ascending=False)\
                            .rename(columns={'title' : 'Titre',
                                            'averageRating' : 'Note moyenne',
                                            'startYear' : 'Année de Sortie',
                                            'genres' : 'Genre(s)',
                                            'actor_name' : 'Acteur(s)',
                                            'actress_name' : 'Actrice(s)',
                                            'writer_name' : 'Scénariste(s)'}),
                        hide_index=True)

# ------------------------------------ SELECTION PAR SCENARISTE ------------------------------------

elif selection == "Recherche par scénariste":

    # créer la liste des acteurs depuis le DF de base, en "explosant" chaque cellule, et ne gardant que les valeurs uniques, par ordre alpha
    liste_scenariste = sorted((film_dataframe['writer_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

    # ajout valeur par défaut à la liste pour affichage qui se trouvera toujours à la fin de la liste
    liste_scenariste.append('Veuillez choisir un scénariste')

    st.title('Recherche par scénariste')
    st.write(f"{len(liste_scenariste)} scénaristes")

    # cellule de sélection de l'acteur selon la liste définie précédemment
    scen_choisi = st.selectbox("Choix du scénariste :", 
                                liste_scenariste, 
                                index=(len(liste_scenariste) - 1)) # pour récupérer la valeur au dernier indice de la liste

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    if scen_choisi != 'Veuillez choisir un scénariste':
        
        # afficher le nombre de films dans lesquels a joué l'acteur recherché
        st.subheader(f"{scen_choisi} a participé au scénario de {film_dataframe['writer_name'].str.contains(scen_choisi, na=False).sum()} films")
        
        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)
        
        # déclaration de 2 colonnes
        col1, col2 = st.columns(2)
        with col1:

            genres = film_dataframe["genres"].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(5).reset_index()

            # TOP 10 d'un scénariste choisi

            # 1er tri pour afficher les infos du DF en fonction du nom choisi par l'utilisateur, en filtrant sur le type 'movie', et en ne prenant que les 10 premiers
            scen_search = film_dataframe[(film_dataframe["writer_name"].str.contains(scen_choisi)) & \
                                    (film_dataframe['titleType'] == 'movie')]\
                                    .drop_duplicates(subset="tconst")\
                                    .sort_values(by='averageRating', ascending=False)\
                                    .head(10)

            # histo Top 10 films de l'acteur recherché
            graph_scen_search = px.bar(data_frame=scen_search.sort_values(by='averageRating').head(10),
                                    x='averageRating',
                                    y='title',
                                    text_auto=True,
                                    title=f'Top 10 films de {scen_choisi}',
                                    labels={'averageRating': 'Note moyenne',
                                            'title': 'Film'})

            # titre en gras et centré
            graph_scen_search.update_layout(
                title={'text': f'<b>Top 5 des genres des films réalisé par {scen_choisi}</b>', 'x': 0.2}
                )
            
            st.plotly_chart(graph_scen_search)

        with col2:

            # camembert de répartition du Top 5 des genres pour l'acteur recherché
            graph_genre = px.pie(data_frame=scen_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                                values="count",
                                names= scen_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])
            # valeurs en gras
            graph_genre.update_traces(textinfo='percent+label',
                                    texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                    )

            # titre en gras et centré
            graph_genre.update_layout(
                title={'text': f'<b>Top 5 des genres des films réalisé par {scen_choisi}</b>', 'x': 0.5}
                )
            st.plotly_chart(graph_genre, theme=None)

        # afficher les affiches du top 3 en version cliquable vers TMDB
        st.subheader(f"Top Films de {scen_choisi}")
        st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

        # récup fonction pour top 2 à 4
        fn_top_films(scen_search, max_films=3)

        #--------------------------- AFFICHAGE TOUS FILMS ---------------------------

        # affichage DF avec tous les films de l'acteur/trice choisi
        with st.expander(f"Cliquer pour afficher tous les films écrits par {scen_choisi}"):
            st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                            [film_dataframe['writer_name']\
                            .str.contains(scen_choisi)]\
                            .sort_values(by='averageRating', ascending=False)\
                            .rename(columns={'title' : 'Titre',
                                            'averageRating' : 'Note moyenne',
                                            'startYear' : 'Année de Sortie',
                                            'genres' : 'Genre(s)',
                                            'actor_name' : 'Acteur(s)',
                                            'actress_name' : 'Actrice(s)',
                                            'writer_name' : 'Scénariste(s)'}),
                        hide_index=True)

# -------------------------------- MACHINE LEARNING - RECOMMANDATIONS --------------------------------

elif selection == "Recherche par films":

    # Création du DataFrame

    df = pd.read_csv('movie_reco.csv')

    st.title('Bienvenue sur la page de recommandation de film')

    # st.dataframe(df)

    # création liste films pour pouvoir ajouter le choix par défaut "Veuillez choisir un film"
    liste_film = sorted((df['title'].dropna().astype(str)).unique())
    # ajout du choix par défaut dans la liste
    liste_film.append('Veuillez choisir un film')
    
    text_search = st.selectbox(f'Choix du film : ',
                            liste_film,
                            index=(len(liste_film)-1)
                            )
    if text_search != 'Veuillez choisir un film' :
        
        # Filter the dataframe using masks
        m1 = df["title"].str.contains(text_search, na=False)
        df_search = df[m1]

        # -------------------------- INTEGRATION DU ML VECTORIZER + NEARET NEIGHBORS ------------------------

        # Intégration du modèle de machine learning
        from sklearn.neighbors import NearestNeighbors
        vectorizer = CountVectorizer()

        # entrainement et transformation des données texte pour que le ML puisse les traiter
        X = vectorizer.fit_transform(df['combined_features'])

        # déclaration du modèle de NearestNeighbors
        modelNN = NearestNeighbors(n_neighbors=6,
                                metric='cosine'          
                                )

        # entrainement du modèle sur la colonne de features X
        modelNN.fit(X)

        # boucle

        features_film = X[df[df['title'].str.contains(text_search)].index[0]]

        # Gérez le cas où il y a moins de 2 correspondances
        # faire tourner le modèle ML de kneighbors par rapport aux features du film recherché
        distances, indices = modelNN.kneighbors(features_film, n_neighbors=30)

        # créer le DF qui contiendra les films recommandés en focntion des indices du modèle NN
        films_reco = df.iloc[indices[0]]

        # affichage du film et des éléments souhaités
        print(f"Films recommandés pour {text_search} :")

        print(films_reco.iloc[1:4]['title'])
        print(films_reco.iloc[1:4]['poster_path'])

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # ------------------------------------ RESULTATS DU ML --------------------------------

        # -------------------------------- AFFICHAGE DU FILM RECHERCHE -------------------------

        if text_search is not None:

            id_search = df_search.loc[df['title'] == text_search].iloc[0, 16]

            search_col1, search_col2, search_col3 = st.columns([1,2,2])

            with search_col1:

                df_search.reset_index()
                
                # récup image dans le DF via poster_path
                image_url = f'https://image.tmdb.org/t/p/w500/{df_search.iloc[0,20]}'
                # récup lien vers tmdb via l'id du film dans le DF
                target_url = f'https://www.themoviedb.org/movie/{df_search.iloc[0,16]}'
                # affichage de l'image en version cliquable
                st.markdown(
                    f'<a href="{target_url}" target="_blank">'
                    f'<img src="{image_url}" width="330"></a>',
                    unsafe_allow_html=True
                )
                
            with search_col2:
                st.subheader('Informations sur le film')

                st.write(f'**Réalisateur** : {df_search.iloc[0,29]}')
                st.write(f'**Acteur(s)** : {df_search.iloc[0,27]}')
                st.write(f'**Actrice(s)** : {df_search.iloc[0,28]}')
                st.write(f'**Durée** : {df_search.iloc[0,5]} minutes')
                st.write(f'**Note** : {df_search.iloc[0,7]}/10')

                id_search = df_search.loc[df['title'] == text_search].iloc[0, 16] # Ce code me donne l'id du film cherché par l'user

                url = f"https://api.themoviedb.org/3/movie/{id_search}?language=fr"
                
                st.subheader('Résumé du film')
                response = requests.get(url, headers=headers)

                # Texte justifié avec HTML et CSS
                texte = f"""
                <div style="text-align: justify;">
                    {response.json().get('overview', 'Aucun résumé disponible.')}
                </div>
                """
                # Afficher le texte avec justification
                st.write(texte, unsafe_allow_html=True)

            with search_col3:
                url_video = f"https://api.themoviedb.org/3/movie/{id_search}/videos"

                response_video = requests.get(url_video, headers=headers)

                video_data = response_video.json().get('results', [])

                trailers = [
                    ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                    ]
                if trailers:
                    trailer_key = trailers[0]['key']
                    youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                    st.write('Bande-annonce:')
                    st.video(youtube_url)

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # ---------------------------- AFFICHAGE DES 3 FILMS RECOMMANDES LES PLUS PROCHES -------------------------

        # 3 colonnes pour centrer le titre en colonne 2
        col1, col2, col3 = st.columns(3)

        with col2:
            st.subheader('Films recommandés')

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        reco_col1, reco_col2, reco_col3, reco_col4, reco_col5, reco_col6 = st.columns(6)

        with reco_col1:

            st.subheader(f"**{films_reco.iloc[1,10]}**")
            
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[1,20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[1,16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )
            
            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[1,16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[1,10], 'id'].iloc[0])


        with reco_col2:

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

            response = requests.get(url, headers=headers)

            st.write(f'**Réalisateur :** {films_reco.iloc[1,29]}')
            st.write(f'**Acteur(s):** {films_reco.iloc[1,27]}')
            st.write(f'**Actrice(s):** {films_reco.iloc[1,28]}')
            st.write(f'**Durée:** {films_reco.iloc[1,5]} minutes')
            st.write(f'**Note:** {films_reco.iloc[1,7]}/10')

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        with reco_col3:

            st.subheader(f"**{films_reco.iloc[2,10]}**")
            
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[2,20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[2,16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )
            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[2,16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[2,10], 'id'].iloc[0])

        with reco_col4:

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

            response = requests.get(url, headers=headers)

            st.write(f'**Réalisateur :** {films_reco.iloc[2,29]}')
            st.write(f'**Acteur(s) :** {films_reco.iloc[2,27]}')
            st.write(f'**Actrice(s) :** {films_reco.iloc[2,28]}')
            st.write(f'**Durée :** {films_reco.iloc[2,5]} minutes')
            st.write(f'**Note :** {films_reco.iloc[2,7]}/10')
            
            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        with reco_col5:

            st.subheader(f"**{films_reco.iloc[3,10]}**") 
            
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[3,20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[3,16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )
            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[3,16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[3,10], 'id'].iloc[0])

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        with reco_col6:

            response = requests.get(url, headers=headers)

            st.write(f'**Réalisateur :** {films_reco.iloc[3,29]}')
            st.write(f'**Acteur(s) :** {films_reco.iloc[3,27]}')
            st.write(f'**Actrice(s) :** {films_reco.iloc[3,28]}')
            st.write(f'**Durée :** {films_reco.iloc[3,5]} minutes')
            st.write(f'**Note :** {films_reco.iloc[3,7]}/10')
            
            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # -------------------------------------- AFFICHAGE 3 FILMS "VOUS POURRIEZ AIMER" ---------------------

        # 3 colonnes pour centrer le titre en colonne 2
        col1, col2, col3 = st.columns(3)

        with col2:
            st.header('Vous pourriez aussi aimer')

        # affichage ligne de démarcation
        st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

        # création liste pour ajouter les index de films complémentaires
        liste = []
        
        # tant que la liste n'a pas chiffres/index, continue
        while len(liste) < 3:
            num = random.randint(4, 29)
            if num not in liste:
                liste.append(num)
        
        # vérif longueur liste suite à problème d'index hors list"
        # st.write(len(liste))
        
        reco_col1, reco_col2, reco_col3, reco_col4, reco_col5, reco_col6 = st.columns(6)

        with reco_col1:

            st.subheader(f'{films_reco.iloc[liste[0],10]}')
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[0],20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[0],16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )
            
            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[0],16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[liste[0],10], 'id'].iloc[0])

        with reco_col2:

            st.write(f'**Réalisateur :** {films_reco.iloc[liste[0],29]}')
            st.write(f'**Acteur(s) :** {films_reco.iloc[liste[0],27]}')
            st.write(f'**Actrice(s) :** {films_reco.iloc[liste[0],28]}')
            st.write(f'**Durée :** {films_reco.iloc[liste[0],5]} minutes')
            st.write(f'**Note :** {films_reco.iloc[liste[0],7]}/10')

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

            response = requests.get(url, headers=headers)

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        with reco_col3:
            
            st.subheader(f'{films_reco.iloc[liste[1],10]}')   
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[1],20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[1],16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )

            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[1],16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[liste[1],10], 'id'].iloc[0])

        with reco_col4:

            st.write(f'**Réalisateur :** {films_reco.iloc[liste[1],29]}')
            st.write(f'**Acteur(s) :** {films_reco.iloc[liste[1],27]}')
            st.write(f'**Actrice(s) :** {films_reco.iloc[liste[1],28]}')
            st.write(f'**Durée :** {films_reco.iloc[liste[1],5]} minutes')
            st.write(f'**Note :** {films_reco.iloc[liste[1],7]}/10')

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"
            
            response = requests.get(url, headers=headers)

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        with reco_col5:

            st.subheader(f'{films_reco.iloc[liste[2],10]}')
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[2],20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[2],16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="280"></a>',
                unsafe_allow_html=True
            )
            
            url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[2],16]}/videos"

            response_video = requests.get(url_video, headers=headers)

            video_data = response_video.json().get('results', [])

            trailers = [
                ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                ]
            if trailers:
                trailer_key = trailers[0]['key']
                youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                st.write('Bande-annonce:')
                st.video(youtube_url)

            id_test = int(df.loc[df['title'] == films_reco.iloc[liste[2],10], 'id'].iloc[0])

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        with reco_col6:

            st.write(f'**Réalisateur :** {films_reco.iloc[liste[2],29]}')
            st.write(f'**Acteur(s) :** {films_reco.iloc[liste[2],27]}')
            st.write(f'**Actrice(s) :** {films_reco.iloc[liste[2],28]}')
            st.write(f'**Durée :** {films_reco.iloc[liste[2],5]} minutes')
            st.write(f'**Note :** {films_reco.iloc[liste[2],7]}/10')
            
            response = requests.get(url, headers=headers)

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        # ------------------------- AFFICHER LA COLLECTION SI LE FILM FAIT PARTIE D'UNE COLLECTION -------------------

        id_test = int(df.loc[df['title'] == text_search, 'id'].iloc[0])

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        response = requests.get(url, headers=headers)

        data = response.json()

        # Cette ligne permet de traiter l'erreur dans le cas où le film n'appartient pas à une collection
        if data.get("belongs_to_collection") is not None:

            id_collection = response.json()['belongs_to_collection']['id']

            url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

            response = requests.get(url, headers=headers)

            id_collection = response.json()['belongs_to_collection']['id']

            # Nouvel URL pour la 2nde requête
            url_coll = f"https://api.themoviedb.org/3/collection/{id_collection}?language=fr"

            response_coll = requests.get(url_coll, headers=headers)

            st.divider()

            st.title('Autres films de la même collection')

            print(len(response_coll.json()['parts']))
            list_film_coll = []
            for film in range(len(response_coll.json()['parts'])):

                list_film_coll.append(response_coll.json()['parts'][film]['title'])


            resultats_film_col = [film for film in list_film_coll if film in df["title"].to_list()]

            choix_film_coll = st.selectbox('Liste des films de la même collection que le film recherché initialement : ', resultats_film_col)

            # Refaire une requête à l'API qui se base sur "choix_film_col"

            df_choix_coll = df.loc[df['title'] == choix_film_coll]

            film_coll1, film_coll2 = st.columns(2)

            with film_coll1:

                st.image(f'https://image.tmdb.org/t/p/w500{df_choix_coll.iloc[0,20]}', width = 300)

                id_reco = int((df_choix_coll.iloc[0,16]))

            with film_coll2:

                url = f"https://api.themoviedb.org/3/movie/{id_reco}?language=fr"

                response = requests.get(url, headers=headers)
                st.subheader('Résumé du film')

                # Texte justifié avec HTML et CSS
                texte = f"""
                <div style="text-align: justify;">
                    {response.json().get('overview', 'Aucun résumé disponible.')}
                </div>
                """
                # Afficher le texte avec justification
                st.markdown(texte, unsafe_allow_html=True)
