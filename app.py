import streamlit as st
import pandas as pd
from rapidfuzz import fuzz
import xlwt
import io

# --- إعداد الصفحة ---
st.set_page_config(page_title="Supplier App - Cleopatra Hospitals", layout="wide")

# --- CSS مخصص ---
st.markdown("""
<style>
body, .stApp { background-color: #f5f5f5; color: #00274d; font-family: 'Segoe UI', sans-serif; }
h1, h2, h3 { color: #00274d; text-align: left; font-size: 22px; margin-bottom: 15px; }
.stButton > button { background: linear-gradient(90deg, #00274d 0%, #c02a2a 100%); color: white; border-radius: 8px; border: none; padding: 12px 24px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.3s; width: 100%; }
.stButton > button:hover { background: linear-gradient(90deg, #c02a2a 0%, #00274d 100%); }
.stTextInput > div { width: fit-content; min-width: 250px; }
.stTextInput > div > div > input { width: 250px; background-color: #e6f2f8; color: #00274d; border-radius: 8px; padding: 8px; box-sizing: border-box; }
.dataframe { background: #ffffff; color: #00274d; border-radius: 8px; white-space: pre-wrap; }
.dataframe tbody tr:hover { background-color: #ffdada; }
.footer { color: #666666; font-size: 12px; text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- حالة تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

APP_VERSION = "v1.2"

# =========================
# --- دوال واجهة المستخدم ---
# =========================

def login_screen():
    col1, col2, col3 = st.columns([5,3,2])
    with col3:
        st.image("cleo.jpg", width=220)
    st.markdown("<h1>🔐 Login</h1>", unsafe_allow_html=True)
    st.markdown(f"<div style='color:#666; margin-bottom:8px;'>Cleopatra Hospitals — Supplier similarity tool — {APP_VERSION}</div>", unsafe_allow_html=True)
    username = st.text_input("Username", key="user")
    password = st.text_input("Password", type="password", key="pass")
    if st.button("Login"):
        if username=="admin" and password=="1234":
            st.session_state["logged_in"] = True
            st.session_state["page"] = "main"
            st.success("✅ logged in successfully 🎉")
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

def main_menu():
    col1, col2 = st.columns([5,3])
    with col2:
        st.image("cleo.jpg", width=220)
    st.markdown("<h1>📂 Main Menu</h1>", unsafe_allow_html=True)
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    colA, colB = st.columns(2)
    with colA:
        if st.button("📊 Suppliers(By Name & C/R)",width = 250):
            st.session_state["page"]="suppliers_registry"
            st.rerun()
    with colB:
        if st.button("📊 Suppliers(By Name)",width = 250):
            st.session_state["page"]="suppliers"
            st.rerun()

    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")        
    if st.button("🔓 Logout"):
        st.session_state["logged_in"]=False
        st.session_state["page"]="login"
        st.rerun()

# =========================
# --- تلوين النتائج ---
# =========================

def color_similarity(row):
    sim = row['Similarity %']
    if sim>=90: return ['background-color:#00274d;color:white']*len(row)
    elif sim>=80: return ['background-color:#fff59d;color:black']*len(row)
    elif sim>=70: return ['background-color:#98a6eb;color:black']*len(row)
    elif sim>=60: return ['background-color:#ebc098;color:black']*len(row)
    else: return ['background-color:#ffffff;color:black']*len(row)

# =========================
# --- تصدير Excel (xls فقط) ---
# =========================

def export_to_bytes(similar_df):
    buf = io.BytesIO()
    book = xlwt.Workbook()
    sheet = book.add_sheet("Similar Suppliers")
    style_white = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: color black;')
    style_navy = xlwt.easyxf('pattern: pattern solid, fore_colour dark_blue; font: color white;')
    style_yellow = xlwt.easyxf('pattern: pattern solid, fore_colour yellow; font: color black;')
    style_blue = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue; font: color black;')
    style_tan = xlwt.easyxf('pattern: pattern solid, fore_colour brown; font: color black;')

    for col_idx, col_name in enumerate(similar_df.columns):
        sheet.write(0, col_idx, col_name, style_white)

    for row_idx, (_, row) in enumerate(similar_df.iterrows(), start=1):
        sim = row['Similarity %']
        style = style_white
        if sim>=90: style=style_navy
        elif sim>=80: style=style_yellow
        elif sim>=70: style=style_blue
        elif sim>=60: style=style_tan
        for col_idx, value in enumerate(row):
            sheet.write(row_idx, col_idx, str(value), style)
    book.save(buf)
    buf.seek(0)
    return buf

# =========================
# --- Generate similarity ---
# =========================

def generate_similarity_df(df, code_col, name_col, sim_range):
    results=[]
    ref_counter=1
    visited=set()
    for i in range(len(df)):
        if i in visited: continue
        code_i, name_i = df[code_col][i], str(df[name_col][i])
        cluster=[]
        ref=f"Ref{ref_counter:04d}"
        ref_counter+=1
        for j in range(i, len(df)):
            if j in visited: continue
            code_j, name_j = df[code_col][j], str(df[name_col][j])
            sim = fuzz.ratio(name_i, name_j)
            if sim_range[0] <= sim <= sim_range[1]:
                cluster.append((code_j, name_j, sim))
                visited.add(j)
        for code_j, name_j, sim in cluster:
            results.append({
                "Reference": ref,
                "Code1": code_i,
                "Name1": name_i,
                "Code2": code_j,
                "Name2": name_j,
                "Similarity %": int(round(sim))
            })
    if results:
        df_res=pd.DataFrame(results)
        df_res=df_res.sort_values(["Reference","Similarity %"], ascending=[True,False])
        return df_res
    return pd.DataFrame()

# =========================
# --- شاشات الموردين ---
# =========================


def suppliers_registry_screen():
    col1, col2, col3 = st.columns([5, 3, 2])
    with col3:
        st.image("cleo.jpg", width=220)  # logo على اليمين
    st.markdown("<h1>📊 Suppliers (Name & C/R)</h1>", unsafe_allow_html=True)
    sim_range = st.slider("Similarity % (min - max)", 50, 100, (80, 100))
    df_result = pd.DataFrame()
    
    st.markdown("")
    st.markdown("")
    st.markdown("")
    run_button = st.button("🚀 Run")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    back_button = st.button("🔙 Back")
    
    if run_button:
        with st.spinner("⏳ Processing… please wait"):
            try:
                df = pd.read_excel("suppliers2.xlsx")
                df_result = generate_similarity_df(df, "code", "merge", sim_range)
                if not df_result.empty:
                    st.dataframe(df_result.style.apply(color_similarity, axis=1), use_container_width=True)
                    output = export_to_bytes(df_result)
                    st.download_button("💾 Download Excel", data=output.getvalue(),
                                       file_name="similar_suppliers2.xls",
                                       mime="application/vnd.ms-excel")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                
    if back_button:
        st.session_state["page"] = "main"
        st.rerun()


def suppliers_screen():
    col1, col2, col3 = st.columns([5, 3, 2])
    with col3:
        st.image("cleo.jpg", width=220)  # logo على اليمين
    st.markdown("<h1>📊 Suppliers (Name only)</h1>", unsafe_allow_html=True)
    sim_range = st.slider("Similarity % (min - max)", 50, 100, (80, 100))
    df_result = pd.DataFrame()
    st.markdown("")
    st.markdown("")
    st.markdown("")
    run_button = st.button("🚀 Run")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    back_button = st.button("🔙 Back")
    
    if run_button:
        with st.spinner("⏳ Processing… please wait"):
            try:
                df = pd.read_excel("suppliers.xlsx")
                df_result = generate_similarity_df(df, "code", "designation", sim_range)
                if not df_result.empty:
                    st.dataframe(df_result.style.apply(color_similarity, axis=1), use_container_width=True)
                    output = export_to_bytes(df_result)
                    st.download_button("💾 Download Excel", data=output.getvalue(),
                                       file_name="similar_suppliers.xls",
                                       mime="application/vnd.ms-excel")
            except Exception as e:
                st.error(f"⚠️ Error: {e}")
                
    if back_button:
        st.session_state["page"] = "main"
        st.rerun()


# =========================
# --- Footer ---
# =========================

def footer():
    st.markdown(f"<div class='footer'>Cleopatra Hospitals — Supplier similarity tool • {APP_VERSION}</div>", unsafe_allow_html=True)

# =========================
# --- تشغيل التطبيق ---
# =========================

if not st.session_state["logged_in"]:
    login_screen()
else:
    if st.session_state["page"]=="main":
        main_menu()
    elif st.session_state["page"]=="suppliers_registry":
        suppliers_registry_screen()
    elif st.session_state["page"]=="suppliers":
        suppliers_screen()
    elif st.session_state["page"]=="entities":
        entities_screen()

footer()
