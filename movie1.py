import pandas as pd
import streamlit as st
from streamlit_authenticator import Authenticate
from streamlit_option_menu import option_menu
#######
df_film = pd.read_csv("df_film.csv")
df_film2 = pd.read_csv("df_film2.csv")

########
def accueil():
    st.title('Bienvenue au Cinema dans la Creuse ')
    st.write("FILMS DE LA SEMAINE ")
    st.table(df_film2.drop_duplicates(subset='Title').reset_index().drop(columns= ['index','category','titleType']).head(7))
   
 
with st.sidebar:
    st.write('Bienvenue')
    selection = option_menu(
        menu_title='Menu',
        options=['ACCUEIL', 'Drama', 'Acteurs/Actrices'],
        icons=['house', 'camera', 'emoji-laughing', 'menu-app-fill'],
        menu_icon='cast'
    )  
if selection == "ACCUEIL":
        accueil()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.header("Le Genre")
            list_genre= df_film2['Genre'].apply(lambda x: x.split(',')).explode().unique().tolist()
            genre = st.selectbox("Choisir le genre que vous voulez? ",list_genre, index= None )
        
        with col2:
            st.header("La durée ")
            list_duration = df_film2['Durée'].unique().tolist()
            reponde_durée = st.selectbox("Choisir le durée du films? ",list_duration, index= None)
          
        with col3:
            st.header("L'année")
            list_year = df_film2[ "l'année"].unique().tolist()
            annee= st.selectbox("Choisir l'année de sortie du film: ",list_year, index= None)
        st.header("FILMS VOUS CHERCHEZ")
        filtered_df = df_film2.drop_duplicates(subset='Title').drop(columns= ['category','titleType'])
        if annee:
            filtered_df = filtered_df[filtered_df["l'année"] == annee]
        if reponde_durée:
            filtered_df = filtered_df[filtered_df['Durée'] == reponde_durée]
        if genre:
            filtered_df = filtered_df[filtered_df['Genre'].str.contains(genre, na=False)]
        if not filtered_df.empty:
             st.table(filtered_df)
        else:
            st.write("Aucun film ne correspond aux critères sélectionnés.")
        
elif selection == "Drama":
    st.write("FILMS DE LA SEMAINE - DRAMA")
elif selection == "Acteurs/Actrices":
     st.title("Chercher les acteurs/actrices vous aimez")
     list_actors = df_film['primaryName'].unique().tolist()
     actor = st.selectbox("Quel actress/acteur que vous voulez? ",list_actors, index= None )
     st.title("Top 5 films avec meilleur notes:")
     st.table(df_film.loc[df_film['primaryName'] == actor].sort_values(by='averageRating', ascending= False).head(5))   

     st.title("Top 5 films les plus récents:")
     st.table(df_film.loc[df_film['primaryName'] == actor].sort_values(by='startYear', ascending= False).head(5))  