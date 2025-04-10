import pandas as pd
import streamlit as st
import plotly.express as px
####
#""
movie_stats = pd.read_csv('movie_stats.csv.gz')
movie_stats['Décennie'] = (movie_stats['startYear'] // 10) * 10
df_films = movie_stats.loc[(movie_stats['startYear'] < 2025) & (movie_stats['revenue'] > 0) & (movie_stats['titleType'] == "movie")& (movie_stats['runtimeMinutes'] > 0)]
df_films.dropna(subset= ['revenue', 'popularity', 'id', 'budget'],inplace= True) 
df_genre = pd.read_csv("df_genre.csv")
def fn_count_genre(var):
    var = str(var)
    var.count(",")
    return  (var.count(",") + 1)

df_films['nb_genres'] = df_films['genres'].apply(lambda x: fn_count_genre(x))

st.header("Projet data 2")
st.write("Créer un système de recommandation de films pour un cinéma dans la Creuse au 10/11/2024 du 8/1/2025 ")
st.write("C'est une partie du projet qui montre les indicateurs permettant au directeur de cinéma d'évaluer et de choisir les films par genre de film")
st.markdown("<hr style='border: 0.3px solid white;'>", unsafe_allow_html=True)
st.header("Les Genres de films")
graph_top10 = px.bar(data_frame=df_films['genres'].loc[df_films['genres'] != "\\N"]\
                   .apply(lambda x: x.split(',')).explode()\
                    .value_counts().sort_values(ascending= False).head(5),
            x='count',
            text_auto=True,
            labels={"count" : "Nombre",
                     "genres" : "Genres"},
            title= f'Top 5 des genres' )
st.plotly_chart(graph_top10)
st.write("Sélectionnez le graphique souhaité:") 
list_genre = sorted(df_genre['Genres'])
col1, col2 = st.columns(2)
with col1:
         TopNumber = st.checkbox("Répartition de films par nombre de genres")
with col2:  
        Toprevenue = st.checkbox("Revenue moyenne par nombre de genres")
##########

if TopNumber:
        graph_pourcentage = px.pie(data_frame= df_films['nb_genres'].value_counts(normalize= True),
                        names=df_films['nb_genres'].value_counts(normalize= True).reset_index()['nb_genres'],
                        values= 'proportion',
                        labels={'1':'1 genre','2':'2 genre','3':'3 genre',
                                'proportion':'pourcentage de film'},
                        title= f'Répartition de films par nombre de genres')
        st.plotly_chart(graph_pourcentage)

if Toprevenue:
        tb_revenue_genres = {}
        for i in [1,2,3]:
            mean_revenue = round(df_films['revenue'].loc[df_films['nb_genres']== i].mean(),3)
            tb_revenue_genres.update({ i : mean_revenue})
        graph_toprevenue = px.bar( x= tb_revenue_genres.keys(),y= tb_revenue_genres.values(),
                              text_auto=True,
                              labels= ({"x": "Nombre de genre par film",
                                         "y" : "Revenu moyen"}),
                              title= f'Revenu moyen par nombre de genres par film')
        st.plotly_chart(graph_toprevenue)

genre = st.selectbox("Choisir le genre du films? ",list_genre, index= None)
 
##############
if genre:
        tb_genre = df_genre.loc[df_genre['Genres'].str.contains(genre,na= False)].drop(columns=['Unnamed: 0'])
        st.write("Caractéristiques du genre sélectionné")
        st.dataframe(tb_genre,hide_index= True)
        data_genre = df_films.loc[df_films['genres'].str.contains(genre)]
        st.header("Sélectionnez le graphique souhaité:")  
        col1, col2= st.columns(2)
        with col1:
            graph_number= st.checkbox("Total de films par décennie")
            graphique_duree = st.checkbox("Le durée de films par décennie") 
        with col2:
            graphique_revenue = st.checkbox("Le revenu et le note de films")
            graph_buget = st.checkbox("Le revenu et le budget de films")   
        if graph_number:
            graph_total = px.histogram(data_genre, x="Décennie" )
            st.plotly_chart(graph_total)
               
        if graphique_duree:
            st.line_chart(data_genre, y='runtimeMinutes', x='Décennie', x_label= "Décennie", y_label= "Le durée de films")   
        if graphique_revenue:
            st.bar_chart(data_genre, y='revenue', x='averageRating', x_label= "Le Notes", y_label= "Le revenue")
        if graph_buget:
            st.line_chart(data_genre, y='revenue', x='budget', x_label= "Le budget", y_label= "Le revenue")
        st.header("Les meilleurs films du genre sélectionné*")
        col1, col2= st.columns(2)
        with col1: 
            list_trier = ['Note moyenne','revenue']
            trier = st.selectbox("Classer par note ou revenu?",list_trier, index= None)
        with col2:
            list_decennie = sorted(data_genre['Décennie'].unique())
            decennie = st.selectbox("Sélection de la décennie ",list_decennie, index= None)
        df_stat = data_genre[['title','startYear', 'runtimeMinutes','genres', 'averageRating', 'numVotes', 'budget','revenue','popularity','actor_name', 'actress_name','director_name', 'writer_name','Décennie']].rename(columns={'title': 'Title','startYear': 'An','runtimeMinutes': 'Durée (min)','genres': 'Genres','averageRating': 'Note moyenne','numVotes': 'Nombre de votes','budget': 'Budget','popularity': 'Popularité','actor_name': 'Acteurs','actress_name': 'Actrices','writer_name': 'Scénariste','director_name': 'Réalisateurs'})

        if decennie:
            df_stat = df_stat.loc[df_stat['Décennie'] == decennie] 
        if trier:
            df_stat = df_stat.sort_values(by=trier,ascending= False) 
        else:
            df_stat = df_stat.sort_values(by='revenue', ascending= False).head(5)
        st.dataframe(data= df_stat,hide_index= True)
###################
        st.header("Acteurs et actrices les plus présents dans la décennie sélectionnée")
        tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        if decennie:
            tb_actress = df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['Décennie'] == decennie)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            tb_actor =  df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['Décennie'] == decennie)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        else:
            tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        st.write("La liste des acteurs et actrices triée par la même décennie que la liste des films.")
    
        col1,col2 = st.columns(2)
        with col1:
            graph_actrices10 = px.bar(x=list(tb_actress.values()),
                               y=list(tb_actress.keys()),
                            text_auto=True,
                    labels=({"x" : "Nombre",
                         "y" : "Nom d'actrice"}),
                     title= f'Top 10 actrices')
            st.plotly_chart(graph_actrices10)
        with col2:
            graph_acteur10 = px.bar(x=list(tb_actor.values()),
                               y=list(tb_actor.keys()),
                            text_auto=True,
                    labels=({"x" : "Nombre",
                         "y" : "Nom d'acteur"}),
                     title= f'Top 10 acteurs')
            st.plotly_chart(graph_acteur10)


   
 

       
