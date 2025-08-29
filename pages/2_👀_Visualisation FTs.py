import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(layout='wide',page_icon=':coffee:', page_title='DT Produits Latty')

st.markdown("""
    <style>
    /* General font size reduction */
    html, body, .stApp {
        font-size: 1.0rem;
        line-height: 1.0;
    }

    /* General fallback for h2 */
    h2 {
        font-size: 1rem !important;  /* force smaller */
    }

    /* Target specifically Streamlit-markdown headings */
    .stMarkdown h2 {
        font-size: 2rem !important;
    }

    /* Target Streamlit's special heading class (if present) */
    .stMarkdownHeading {
        font-size: 2rem !important;
    }

    /* If Streamlit wraps subheaders in a div with role heading */
    [data-testid="stMarkdownContainer"] h2 {
        font-size: 2rem !important;
    }
    /* Bullet list and paragraph text */
    .stMarkdown p, .stMarkdown li {
        font-size: 0.9rem;
    }

    /* Optional: reduce spacing between bullets */
    .stMarkdown li {
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }

    /* Footer text */
    .footer-container {
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

dossier_actuel = os.path.dirname(os.path.abspath(__file__))
chemin_bd = os.path.join(dossier_actuel, 'bd.xlsx')

df = pd.read_excel(chemin_bd, index_col=0)

def sci_notation(num):
    superscripts = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    s = f"{num:.0e}"        # '1e-05'
    base, exp = s.split("e")
    return f"{base}×10{str(int(exp)).translate(superscripts)}"

def is_scientific(num):
    return "e" in f"{num:.1e}"

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

# a = 5
# b = 5e-4
# c = 5.0

# st.write(format_nombre(b))
# st.write(is_scientific(b))
# st.write(sci_notation(b))


produits = df.columns.tolist()
recherche = st.sidebar.text_input("🔎 Recherche de produit :").strip().lower()
produits_filtres = [p for p in (produits) if recherche.lower() in str(p).lower()]

if produits_filtres:
    produit_selectionne = st.sidebar.selectbox("Produits trouvés :", options=produits_filtres)
else:
    st.warning("Aucun produit trouvé")
    produit_selectionne = None


donnees_produit = df[produit_selectionne].dropna()

st.markdown(f"# :green[{donnees_produit.loc['nom']}]")

raw_date = str(donnees_produit.loc['date_maj'])
try:
    date_obj = pd.to_datetime(raw_date)
    formatted_date = date_obj.strftime("%d/%m/%Y")
except:
    formatted_date = raw_date  # fallback if parsing fails

st.caption(f"Fiche technique: {donnees_produit.loc['version_ft']} (dernière mise à jour : {formatted_date})")
st.markdown(f"**<div style='text-align: justify; font-size: 1.0rem; color: #333; line-height:1.7rem'>{donnees_produit.loc['description']}</div>**", unsafe_allow_html=True)

## COMPOSITIONS

compositions = {}

for idx, val in donnees_produit.items():
    if idx.startswith("comp_"):
        parts = idx.split("_")
        nom = parts[1]
        borne = parts[2]  # 'min' ou 'max'
            
        if nom not in compositions:
            compositions[nom] = {"min": None, "max": None}
        compositions[nom][borne] = val

if compositions:

    col1, col2 = st.columns(2)

    with col1 :
        st.markdown(f"#### :blue[{'🔬 Composition'}]")
        with st.container(border=True):
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
                    affichage = f"&gt; {format_nombre(min_val)} %"
                elif max_val is not None:
                    affichage = f"< {format_nombre(max_val)} %"
                else:
                    affichage = ""

                col11, col12 = st.columns([3, 1])
                with col11:
                    st.markdown(f"**{nom}**", unsafe_allow_html=True)
                with col12:
                    st.markdown(f"{affichage}", unsafe_allow_html=True)

## HALOGENES

halogenes = {}

for idx, val in donnees_produit.items():
    if idx.startswith("concent_"):
        parts = idx.split("_")
        nom = parts[1]
        borne = parts[2]  # 'max' ou 'approx'
        unite = parts[3] # normalement 'ppm'
            
        if nom not in halogenes:
            halogenes[nom] = {"max": None, "approx": None, "unite": None}
        halogenes[nom][borne] = val
        halogenes[nom]['unite'] = unite

if halogenes:
    with col2 :
        st.markdown(f"#### :blue[{'⚠️ Halogènes et soufre'}]")
        with st.container(border=True):
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

                col21, col22 = st.columns([3, 1])
                with col21:
                    st.markdown(f"**{nom}**", unsafe_allow_html=True)
                with col22:
                    st.markdown(f"{affichage}", unsafe_allow_html=True)

## CARACTERISTIQUES

caract_physiques = {}

for idx, val in donnees_produit.items():
    if idx.startswith("caract_"):
        parts = idx.split("_")
        nom = parts[1]
        if nom not in caract_physiques:
            caract_physiques[nom] = {"max": None, "min": None, "unite": None, "norme": None, "obs": None}
        if parts[2] in ('min', 'max'):
            borne = parts[2]  # 'min' ou 'max'
            unite = parts[3]
            unite = convert_unit(unite)
            caract_physiques[nom][borne] = val
        elif parts[2] == 'norme':
            norme = val
            caract_physiques[nom]['norme'] = norme
        elif parts[2] == 'obs':
            obs = val
            caract_physiques[nom]['obs'] = obs
        if unite == "adim":
            caract_physiques[nom]['unite'] = ""
        else:
            caract_physiques[nom]['unite'] = convert_unit(unite)

if caract_physiques:

    st.markdown(f"#### :blue[{'📐 Caractéristiques techniques'}]")
    col1, col2, col3,col4 = st.columns([3,1,1,3])
    col1.caption('Caractéristique')
    col2.caption('Valeur')
    col3.caption('Selon norme')
    col4.caption('Observation(s)')
    with st.container(border=True):
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
                norme = valeurs["norme"] if pd.notna(valeurs["norme"]) else ""
            except ValueError:
                norme = ""
            try:
                obs = valeurs["obs"] if pd.notna(valeurs["obs"]) else ""
            except ValueError:
                obs = ""

            if min_val is not None and max_val is not None:
                if min_val == max_val:
                    affichage = f"{format_nombre(min_val)} {caract_physiques[nom]['unite']}"
                else:
                    affichage = f"{format_nombre(min_val)} – {format_nombre(max_val)} {caract_physiques[nom]['unite']}"
            elif min_val is not None:
                affichage = f"&gt;  {format_nombre(min_val)} {caract_physiques[nom]['unite']}"
            elif max_val is not None:
                affichage = f"< {format_nombre(max_val)} {caract_physiques[nom]['unite']}"
            else:
                affichage = ""
            col1, col2, col3,col4 = st.columns([3,1,1,3])    
            with col1:
                st.markdown(f" **{nom}**", unsafe_allow_html=True)
            with col2:
                st.markdown(f"{affichage}", unsafe_allow_html=True)
            with col3:
                st.markdown(f"{norme}", unsafe_allow_html=True)
            with col4:
                st.markdown(f"{obs}", unsafe_allow_html=True)

## PARAMETRES UTILISATION

param = {}

for idx, val in donnees_produit.items():
    if idx.startswith("param_"):
        parts = idx.split("_")
        nom = parts[1]
        if nom not in param:
            param[nom] = {"max": None, "min": None, "unite": None, "obs": None}
        if parts[2] in ('min', 'max'):
            borne = parts[2]  # 'min' ou 'max'
            unite = parts[3]
            if unite == 'adim':
                unite = ""
            param[nom][borne] = format_nombre(val)
            param[nom]['unite'] = convert_unit(unite)
        else:
        # elif parts[2] == 'obs':
            param[nom]['obs'] = val
        # if unite == "adim":
        #     param[nom]['unite'] = ""
        # else:
        #     param[nom]['unite'] = unite

if param:

    st.markdown(f"#### :blue[{'⚙️ Paramètres de fonctionnement (non associés)'}]")
    col1, col2, col3 = st.columns([1,1,2])
    col1.caption('Paramètre')
    col2.caption('Valeur')
    col3.caption('Observation(s)')
    with st.container(border=True):
        for nom, valeurs in param.items():
            try:
                min_val = float(valeurs["min"]) if pd.notna(valeurs["min"]) else None
                # try:
                #     if is_scientific(min_val):
                #         min_val = sci_notation(min_val)
                #     else :
                #         min_val = format_nombre(min_val)
                # except:
                #     min_val = None
            except ValueError:
                min_val = None

            try:
                max_val = float(valeurs["max"]) if pd.notna(valeurs["max"]) else None
                # try:
                #     if is_scientific(max_val):
                #         max_val = sci_notation(max_val)
                #     else :
                #         max_val = format_nombre(max_val)
                # except TypeError:
                #     max_val = None
            except ValueError:
                max_val = None

            try:
                obs = valeurs["obs"] if pd.notna(valeurs["obs"]) else ""
            except ValueError:
                obs = ""

            # Déterminer le texte à afficher
            if min_val is not None and max_val is not None:
                if min_val == max_val:
                    affichage = f"{format_nombre(min_val)} {param[nom]['unite']}"
                else:
                    affichage = f"{format_nombre(min_val)} – {format_nombre(max_val)} {param[nom]['unite']}"
            elif min_val is not None:
                affichage = f"&gt;  {format_nombre(min_val)} {param[nom]['unite']}"
                moyenne = None  # Ignoré dans le graphique
            elif max_val is not None:
                affichage = f"< {format_nombre(max_val)} {param[nom]['unite']}"
                moyenne = None  # Ignoré dans le graphique
            else:
                affichage = ""
            col1, col2, col3 = st.columns([1,1,2])    
            with col1:
                st.markdown(f" **{nom}**", unsafe_allow_html=True)
            with col2:
                st.markdown(f"{affichage}", unsafe_allow_html=True)
            with col3:
                st.markdown(f"{obs}", unsafe_allow_html=True)

## HOMOLOGATIONS

homologations = []
refs = {}
bam_refs = {}

for idx, val in donnees_produit.items():
    if idx.startswith("homologation_"):
        parts = idx.split("_")
        nom = parts[1]
        homologations.append(nom)
    if idx.startswith("ref_"):
        parts = idx.split("_")
        nom = parts[1]
        refs[nom] = val
    if idx.startswith("Application BAM"):
        nom = idx
        bam_refs[nom] = val

if homologations:
    st.markdown("#### :blue[🛡️ Homologation(s)]")
    with st.container(border=True):
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(f"**{", ".join(homologations)}**")
            for idx,val in refs.items():
                st.markdown(f"Réference {idx}: **{val}**")
        with col2:
            for idx,val in bam_refs.items():
                st.markdown(f"{idx}: **{val}**")

## AUTRES INFOS

observations = {}

for idx, val in donnees_produit.items():
    if idx.startswith("obs_"):
        observations[idx] = val

if observations:

    st.markdown("#### :blue[🗨️ Informations complémentaires]")
    with st.container(border=True):
        for idx,val in observations.items():
            st.markdown(f"- {val}")

dossier_images = os.path.join(dossier_actuel, 'images')

afaq = Image.open(os.path.join(dossier_images, 'afaq.png'))
latty = Image.open(os.path.join(dossier_images, 'latty.jpg'))

with st.container():
    col1, col2, col3 = st.columns([1, 10, 1])

    with col1:
        st.image(afaq, width=60)
    with col2:
        st.markdown("""
            <div style='text-align: center; font-size: 0.75rem; color: #333; line-height:1.1rem'>
                Les recommandations et limites de stockage avant utilisation sont décrites dans le document référencé
                <strong>AQ SPE 009</strong> disponible sur notre site internet.
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; font-size: 0.85rem; color: #333; line-height:1.1rem'>
                LATTY® International – 1 rue Xavier Latty – 28160 BROU – www.latty.com
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.image(latty, width=60)