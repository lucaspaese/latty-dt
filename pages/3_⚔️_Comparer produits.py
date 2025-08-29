import streamlit as st
import pandas as pd
import os

st.set_page_config(layout='wide',page_icon='⚔️', page_title='DT Produits Latty')

def sci_notation(num):
    superscripts = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    s = f"{num:.0e}"        # '1e-05'
    base, exp = s.split("e")
    return f"{base}×10{str(int(exp)).translate(superscripts)}"

def is_scientific(num):
    return "e" in f"{num}" or "E" in f"{num}"

def convert_unit(unite):
    superscripts = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{unite.translate(superscripts)}"   

def format_nombre(n):
    if "e" in f"{n}" or "E" in f"{n}":
        superscripts = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
        s = f"{n:.0e}"        # '1e-05'
        base, exp = s.split("e")
        return f"{base}×10{str(int(exp)).translate(superscripts)}"
    else:
        return str(int(n)) if n == int(n) else str(n)

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bd = os.path.join(dossier_actuel, 'bd.xlsx')

df = pd.read_excel(chemin_bd, index_col=0)

# === Interface utilisateur ===
st.sidebar.title("Compararer produits")

if "comparer_prod" not in st.session_state:
    st.session_state.comparer_prod = []

produits = df.columns.tolist()
produits_selectionnes = st.sidebar.multiselect("Sélectionner produits à comparer :", options=produits, placeholder='Aucun produit sélectioné', default='3207G')

if produits_selectionnes not in st.session_state.comparer_prod:
    st.session_state.comparer_prod.append(produits_selectionnes)

df_comparer = df[produits_selectionnes].dropna(how='all')

compositions = {}
df_compositions = pd.DataFrame()
df_compositions_prod = pd.DataFrame(columns=produits_selectionnes)
halogenes = {}
df_halogenes = pd.DataFrame()
df_halogenes_prod = pd.DataFrame(columns=produits_selectionnes)
caract_physiques = {}
df_caract = pd.DataFrame()
df_caract_prod = pd.DataFrame(columns=produits_selectionnes)
param = {}
df_param = pd.DataFrame()
df_param_prod = pd.DataFrame(columns=produits_selectionnes)

# st.write(df[produits_selectionnes[0]].dropna().items())

for prod in produits_selectionnes:
    # st.dataframe(df_comparer[prod])
    for idx, val in df_comparer[prod].items():
        if idx.startswith("comp_"):
            parts = idx.split("_")
            nom = parts[1]
            borne = parts[2]  # 'min' ou 'max'
            # st.write(nom)
            if nom not in compositions:
                compositions[nom] = {"min": None, "max": None}
                # st.write(compositions)
            compositions[nom][borne] = val
        if idx.startswith("concent_"):
            parts = idx.split("_")
            nom = parts[1]
            borne = parts[2]  # 'max' ou 'approx'
            unite = parts[3] # normalement 'ppm'
        
            if nom not in halogenes:
                halogenes[nom] = {"max": None, "approx": None, "unite": None}
            halogenes[nom][borne] = val
            halogenes[nom]['unite'] = convert_unit(unite)
        if idx.startswith("caract_"):
            parts = idx.split("_")
            nom = parts[1]
            if nom not in caract_physiques:
                caract_physiques[nom] = {"max": None, "min": None, "unite": None, "norme": None, "obs": None}
            if parts[2] in ('min', 'max'):
                borne = parts[2]  # 'min' ou 'max'
                unite = parts[3]
                unite = convert_unit(unite)
                caract_physiques[nom]['unite'] = unite
                caract_physiques[nom][borne] = val
            elif parts[2] == 'norme':
                norme = val
                caract_physiques[nom]['norme'] = norme
            elif parts[2] == 'obs':
                obs = val
                caract_physiques[nom]['obs'] = obs
            if unite == "adim":
                caract_physiques[nom]['unite'] = ""

        if idx.startswith("param_"):
            parts = idx.split("_")
            nom = parts[1]
            if nom not in param:
                param[nom] = {"max": None, "min": None, "unite": None, "obs": None}
            if parts[2] in ('min', 'max'):
                borne = parts[2]  # 'min' ou 'max'
                unite = parts[3]
                param[nom][borne] = val
                param[nom]['unite'] = convert_unit(unite)
            if unite == 'adim':
                param[nom]['unite'] = ""
            else:
                param[nom]['obs'] = val

    data = []
    labels = []

    for nom, valeurs in compositions.items():
        try:
            min_val = float(valeurs["min"]) if pd.notna(valeurs["min"]) else None
        except ValueError:
            min_val = None

        try:
            max_val = float(valeurs["max"]) if pd.notna(valeurs["max"]) else None
        except ValueError:
            max_val = None

        # Déterminer le texte à afficher
        if min_val is not None and max_val is not None:
            if min_val == max_val:
                affichage = f"{format_nombre(min_val)} %"
            else:
                affichage = f"{format_nombre(min_val)} – {format_nombre(max_val)} %"
        elif min_val is not None:
            affichage = f"> {format_nombre(min_val)} %"
        elif max_val is not None:
            affichage = f"< {format_nombre(max_val)} %"
        else:
            affichage = ""

        # Ajouter au tableau
        data.append({
            "Component": nom,
            prod: affichage
        })

        df_compositions_prod = pd.DataFrame(data)
        df_compositions_prod.set_index('Component', inplace=True)
    df_compositions = pd.concat([df_compositions, df_compositions_prod[prod]], axis=1)

    data = []
    labels = []

    for nom, valeurs in halogenes.items():
        try:
            approx_val = float(valeurs["approx"]) if pd.notna(valeurs["approx"]) else None
        except ValueError:
            approx_val = None

        try:
            max_val = float(valeurs["max"]) if pd.notna(valeurs["max"]) else None
        except ValueError:
            max_val = None

        # Déterminer le texte à afficher
        if approx_val is not None:
            affichage = f"~{format_nombre(approx_val)} ppm"
        elif max_val is not None:
            affichage = f"< {format_nombre(max_val)} ppm"
        else:
            affichage = ""
            
        # Ajouter au tableau
        data.append({
            "Component": nom,
            prod: affichage
        })
        df_halogenes_prod = pd.DataFrame(data)
        if not df_halogenes_prod.empty:
            df_halogenes_prod.set_index('Component',inplace=True)
    df_halogenes = pd.concat([df_halogenes, df_halogenes_prod[prod]], axis=1)

    data = []
    labels = []

    for nom, valeurs in caract_physiques.items():
        try:
            min_val = float(valeurs["min"]) if pd.notna(valeurs["min"]) else None
        except ValueError:
            min_val = None

        try:
            max_val = float(valeurs["max"]) if pd.notna(valeurs["max"]) else None
        except ValueError:
            max_val = None

        try:
            norme = valeurs["norme"] if pd.notna(valeurs["norme"]) else None
        except ValueError:
            norme = None

        try:
            obs = valeurs["obs"] if pd.notna(valeurs["obs"]) else None
        except ValueError:
            obs = None

        # Déterminer le texte à afficher
        if min_val is not None and max_val is not None:
            if min_val == max_val:
                affichage = f"{format_nombre(min_val)} {caract_physiques[nom]['unite']}"
            else:
                affichage = f"{format_nombre(min_val)} – {format_nombre(max_val)} {caract_physiques[nom]['unite']}"
        elif min_val is not None:
            affichage = f"> {format_nombre(min_val)} {caract_physiques[nom]['unite']}"
            moyenne = None  # Ignoré dans le graphique
        elif max_val is not None:
            affichage = f"< {format_nombre(max_val)} {caract_physiques[nom]['unite']}"
            moyenne = None  # Ignoré dans le graphique
        else:
            affichage = ""
            moyenne = None

        # Ajouter au tableau
        data.append({
            "Component": nom,
            prod: affichage,
        })

        df_caract_prod = pd.DataFrame(data)
        if not df_caract_prod.empty:
            df_caract_prod.set_index('Component',inplace=True)
    df_caract = pd.concat([df_caract, df_caract_prod[prod]], axis=1)

    data = []
    labels = []

    for nom, valeurs in param.items():
        try:
            min_val = float(valeurs["min"]) if pd.notna(valeurs["min"]) else None
        except ValueError:
            min_val = None

        try:
            max_val = float(valeurs["max"]) if pd.notna(valeurs["max"]) else None
        except ValueError:
            max_val = None

        try:
            obs = valeurs["obs"] if pd.notna(valeurs["obs"]) else None
        except ValueError:
            obs = None

        # Déterminer le texte à afficher
        if min_val is not None and max_val is not None:
            if min_val == max_val:
                affichage = f"{format_nombre(min_val)} {param[nom]['unite']}"
            else:
                affichage = f"{format_nombre(min_val)} – {format_nombre(max_val)} {param[nom]['unite']}"
        elif min_val is not None:
            affichage = f"> {format_nombre(min_val)} {param[nom]['unite']}"
            moyenne = None  # Ignoré dans le graphique
        elif max_val is not None:
            affichage = f"< {format_nombre(max_val)} {param[nom]['unite']}"
            moyenne = None  # Ignoré dans le graphique
        elif approx_val is not None:
            affichage = f"~{format_nombre(approx_val)} {param[nom]['unite']}"
        else:
            affichage = ""
            moyenne = None

        # Ajouter au tableau
        data.append({
            "Component": nom,
            prod: affichage,
        })

        df_param_prod = pd.DataFrame(data)
        if not df_param_prod.empty:
            df_param_prod.set_index('Component',inplace=True)
    df_param = pd.concat([df_param, df_param_prod[prod]], axis=1)

st.subheader("Composition")
st.dataframe(df_compositions)
st.subheader("Halogènes/soufre")
st.dataframe(df_halogenes)
st.subheader("Caractéristiques physiques")
st.dataframe(df_caract)
st.subheader("Paramètres d'utilisation")
st.dataframe(df_param)

#     df_compositions[prod] = df_compositions_prod

# st.dataframe(df_compositions)

# df_comparer = df[produits_selectionnes]

# if st.sidebar.checkbox("Afficher uniquement les lignes contenant des données pour tous les produits"):
#     df_comparer = df_comparer.dropna()
# else:
#     df_comparer = df_comparer.dropna(how='all')

# st.dataframe(df_comparer, height = 1000)


