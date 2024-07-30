import numpy as np
import streamlit as st
import pandas as pd
from random import sample
from st_files_connection import FilesConnection
from google.cloud import storage
import datetime


################################
######## Usefull Functions #####
################################

def randomize_row() :
    st.session_state.rdm_row = st.session_state.catalogue.sample()
    st.session_state.tags = st.session_state.rdm_row["list_tags"].values[0].split(" ; ")
    st.session_state.answers = {tag : -1 for tag in st.session_state.tags}
    st.session_state.answer_general = -1
    st.session_state.answer_info = -1

def send_answers() :
    answer = {
        "video_id" : int(st.session_state.rdm_row["video_id"].values[0]),
        "general_answer" : st.session_state.answer_general,
        "additional_info_answer" : st.session_state.answer_info,
        "tag_answers" : st.session_state.answers
        }

    conn = st.connection("gcs", type=FilesConnection)

    filename = str(int(st.session_state.rdm_row["video_id"].values[0]))+str(datetime.datetime.now())
    with conn.open(f"gs://streamlit-ftv-tags/{filename}.txt", "wt") as f:
        f.write(str(answer))

    randomize_row()



################################
######## Initialisation ########
################################

if 'catalogue' not in st.session_state:
    st.session_state.catalogue = pd.read_csv("catalog.csv")
if 'rdm_row' not in st.session_state:
    randomize_row()



#################################
######## Display content ########
#################################

st.markdown("# Evaluation des tags")

container = st.empty()

with container.container() :

    st.markdown("## Description :")

    #print(rdm_row["Description"])
    st.markdown("**" + st.session_state.rdm_row["description_cleaned"].values[0] + "**")

    st.markdown("## Evaluation des tags :")

    st.markdown("Noter la cohérence de chaque tag : Est-il en rapport avec le sujet ?")
    options = [
                "0 : Contradictoire",
                "1 : Aucun rapport",
                "2 : Dans le thème",
                "3 : Cohérent",
                "4 : Très pertinent, subtile"
            ]
    
    my_cols = st.columns(len(st.session_state.tags))
    answers = []

    for i in range(len(st.session_state.tags)) :
        col = my_cols[i]

        with col :
            st.markdown(f"### {st.session_state.tags[i]}")

            st.session_state.answers[st.session_state.tags[i]] = options.index(st.radio(" ", options, 
                key=str(st.session_state.rdm_row["video_id"].values[0])+st.session_state.tags[i], 
                index=0))
            

    st.markdown("## Evaluation globale :")

    st.markdown("Noter la Pertinence global des 3 tags : Le résumé est-il bien caractérisé par les 3 tags ?")
    options_globales = [
        "0 : Contradictoire",
        "1 : Peu informatif",
        "2 : Dans le thème mais pas assez varié",
        "3 : Pertinent",
        "4 : Très pertinent, on retrouve chaque idée clé"
    ]

    st.session_state.answer_general = options_globales.index(st.radio(" ", options_globales, 
            key=str(st.session_state.rdm_row["video_id"].values[0])+"general", 
            index=0))
    
    st.markdown("## Besoin d'informations supplémentaires :")
    
    st.markdown(f'Est-ce l\'ajout du programme *"{st.session_state.rdm_row["program"].values[0]}"* et du titre *"{st.session_state.rdm_row["title"].values[0]}"* aurait aidé à la classification de la vidéo ?')
    options_information = [
        "0 : Au contraire, ces informations induisent en erreur",
        "1 : Pas du tout, la description contient toute l'information nécessaire",
        "2 : Un peu, cela aurait pu ajouter une précision",
        "3 : Beaucoup, on y trouve une information clé absente de la description",
        "4 : Cet ajout est nécessaire pour classifier la vidéo"
    ]

    st.session_state.answer_info = options_information.index(st.radio(" ", options_information, 
            key=str(st.session_state.rdm_row["video_id"].values[0])+"infos", 
            index=0))
    
    st.button(label="Envoyer les réponses", on_click = send_answers)

