import pandas as pd
import format_nombre

def convert_unit(unite):
    superscripts = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{unite.translate(superscripts)}"  

def get_dict(df_prod,cle):
    for idx, val in df_prod.items():
        if idx.startswith(cle):
            compositions = {}
            parts = idx.split("_")
            nom = parts[1]
            borne = parts[2]  # 'min' ou 'max'
            if nom not in compositions:
                compositions[nom] = {"min": None, "max": None}
            compositions[nom][borne] = val
    return compositions
