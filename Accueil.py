import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Données techniques Latty",
    page_icon="👋",
)

st.write("# Données techniques produits Latty")


st.markdown(
    """
    Cette interface permet de visualiser les informations techniques relatives aux produits Latty. 

    Ces informations sont gerées par l'ERD sous forme d'une base de données. 
    Vous pouvez visualiser cette base de données dans l'onglet "📂 Afficher BD".

    Tous les autres onglets permettent une visualisation claire des données techniques disponibles.

    "👀 Visualisation DT" permet la visualisation tous les donnes d'un certain produit.

    "⚔️ Comparer produits" montre les valeurs numériques des données techniques de plusieurs produits seleccionés.

    "👉 Sélection de produit" cherche des produits disponibles selon certains critères.



"""
)

