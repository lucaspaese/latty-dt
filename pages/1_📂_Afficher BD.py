import streamlit as st
import pandas as pd
import os

st.set_page_config(layout='wide',page_icon=':coffee:', page_title='DT Produits Latty')


dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bd = os.path.join(dossier_actuel, 'bd.xlsx')

df = pd.read_excel(chemin_bd, index_col=0)

st.dataframe(df, height=800)

print("hello")