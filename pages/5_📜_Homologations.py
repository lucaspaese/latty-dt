import streamlit as st
import pandas as pd
import os

st.set_page_config(layout='wide',page_icon='📜', page_title='DT Produits Latty')

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bd = os.path.join(dossier_actuel, 'bd.xlsx')
df = pd.read_excel(chemin_bd, index_col=0)

def highlight_rows(x):
    styles = pd.DataFrame("", index=x.index, columns=x.columns)
    for i in range(len(x)):
        if i % 2 == 0:
            styles.iloc[i, :] = "background-color: #f0f0f0;"  # even rows
        else:
            styles.iloc[i, :] = "background-color: #ffffff;"  # odd rows
    return styles


st.subheader('Homologations par produit')

df = df.T

df_hmlg = df.filter(like="homologation_")
df_hmlg = df_hmlg.rename(columns=lambda x: x.replace("homologation_", "", 1) if x.startswith("homologation_") else x)

if st.sidebar.checkbox("Afficher seulement produits avec homologation(s)"):
    df_hmlg = df_hmlg.dropna(how='all')
    df_hmlg.fillna("",inplace=True)
    df_hmlg_st = df_hmlg.style.apply(highlight_rows,axis=None)

df_hmlg.fillna("",inplace=True)
df_hmlg_st = df_hmlg.style.apply(highlight_rows,axis=None)
st.dataframe(df_hmlg_st, height=750)