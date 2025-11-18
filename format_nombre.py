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