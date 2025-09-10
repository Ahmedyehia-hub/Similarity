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
.css-1aumxhk .stSlider > div > div > div > div { background-color: #00274d !important; }
.css-1aumxhk .stSlider > div > div > div > div:hover { background-color: #c02a2a !important; }
.dataframe { background: #ffffff; color: #00274d; border-radius: 8px; }
.dataframe tbody tr:hover { background-color: #ffdada; }
.stImage > img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# --- حالة تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# =========================
# --- دوال لكل شاشة ---
# =========================

def login_screen():
    st.markdown("<h1>🔐 تسجيل الدخول</h1>", unsafe_allow_html=True)
    st.write("")
    username = st.text_input("اسم المستخدم", key="user")
    password = st.text_input("كلمة المرور", type="password", key="pass")
    st.write("")
    if st.button("تسجيل الدخول"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.session_state["page"] = "main"
            st.success("✅ تم تسجيل الدخول بنجاح 🎉")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

def main_menu():
    st.markdown("<h1>📂 القائمة الرئيسية</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    colA, colB, colC = st.columns(3)
    with colA:
        if st.button("📊 الموردين بالسجل التجاري"):
            st.session_state["page"] = "suppliers_registry"
            st.rerun()
    with colB:
        if st.button("📊 الموردين"):
            st.session_state["page"] = "suppliers"
            st.rerun()
    with colC:
        if st.button("🏢 الجهات"):
            st.session_state["page"] = "entities"
            st.rerun()
    
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    if st.button("🔓 تسجيل الخروج"):
        st.session_state["logged_in"] = False
        st.session_state["page"] = "login"
        st.rerun()

# --- دالة تلوين الصفوف ---
def color_similarity(row):
    sim = row['Similarity %']
    if sim >= 90:
        return ['background-color: #ff4b4b; color: white']*len(row)
    elif sim >= 80:
        return ['background-color: #fff59d; color: black']*len(row)
    elif sim >= 70:
        return ['background-color: #98a6eb; color: black']*len(row)
    elif sim >= 60:
        return ['background-color: #ebc098; color: black']*len(row)
    else:
        return ['background-color: #ffffff; color: black']*len(row)

# --- دالة لحفظ النتائج Excel 97-2003 ---
def save_to_excel_97(similar_df, file_or_buffer):
    book = xlwt.Workbook()
    sheet = book.add_sheet("Similar Suppliers")
    style_red = xlwt.easyxf('pattern: pattern solid, fore_colour red; font: color white;')
    style_yellow = xlwt.easyxf('pattern: pattern solid, fore_colour yellow; font: color black;')
    style_blue = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue; font: color black;')
    style_white = xlwt.easyxf('pattern: pattern solid, fore_colour white; font: color black;')

    # كتابة رؤوس الأعمدة
    for col_idx, col_name in enumerate(similar_df.columns):
        sheet.write(0, col_idx, col_name, style_white)

    # كتابة البيانات مع التلوين
    for row_idx, (index, row) in enumerate(similar_df.iterrows(), start=1):
        sim = row['Similarity %']
        if sim >= 90: style = style_red
        elif sim >= 80: style = style_yellow
        elif sim >= 70: style = style_blue
        else: style = style_white
        for col_idx, value in enumerate(row):
            sheet.write(row_idx, col_idx, value, style)

    book.save(file_or_buffer)

# --- شاشات الموردين ---
def suppliers_registry_screen():
    st.markdown("<h1>📊 الموردين بالسجل التجاري</h1>", unsafe_allow_html=True)
    similarity_range = st.slider("🔢 اختر نسبة التشابه (من - إلى)", 50, 100, (80, 100))
    similar_df = pd.DataFrame()
    if st.button("🚀 تطبيق الفلترة"):
        try:
            df = pd.read_excel("suppliers2.xlsx")
            codes = df['code']
            names = df['merge']
            results = []
            for i in range(len(names)):
                for j in range(i+1, len(names)):
                    sim = fuzz.ratio(str(names[i]), str(names[j]))
                    if similarity_range[0] <= sim <= similarity_range[1]:
                        results.append({"Code_1": codes[i],"Name_1": names[i],"Code_2": codes[j],"Name_2": names[j],"Similarity %": sim})
            similar_df = pd.DataFrame(results).sort_values("Similarity %", ascending=False)
            styled_df = similar_df.style.apply(color_similarity, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")

    # زر التحميل يظهر فقط بعد إنشاء DataFrame
    if not similar_df.empty:
        output = io.BytesIO()
        save_to_excel_97(similar_df, output)
        output.seek(0)
        st.download_button(
            label="💾 تحميل Excel",
            data=output,
            file_name="similar_suppliers2.xls",
            mime="application/vnd.ms-excel"
        )

    if st.button("🔙 رجوع"):
        st.session_state["page"] = "main"
        st.rerun()

def suppliers_screen():
    st.markdown("<h1>📊 الموردين</h1>", unsafe_allow_html=True)
    similarity_range = st.slider("🔢 اختر نسبة التشابه (من - إلى)", 50, 100, (80, 100))
    similar_df = pd.DataFrame()
    if st.button("🚀 تطبيق الفلترة"):
        try:
            df = pd.read_excel("suppliers.xlsx")
            codes = df['code']
            names = df['designation']
            results = []
            for i in range(len(names)):
                for j in range(i+1, len(names)):
                    sim = fuzz.ratio(str(names[i]), str(names[j]))
                    if similarity_range[0] <= sim <= similarity_range[1]:
                        results.append({"Code_1": codes[i],"Name_1": names[i],"Code_2": codes[j],"Name_2": names[j],"Similarity %": sim})
            similar_df = pd.DataFrame(results).sort_values("Similarity %", ascending=False)
            styled_df = similar_df.style.apply(color_similarity, axis=1)
            st.dataframe(styled_df, use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")

    if not similar_df.empty:
        output = io.BytesIO()
        save_to_excel_97(similar_df, output)
        output.seek(0)
        st.download_button(
            label="💾 تحميل Excel",
            data=output,
            file_name="similar_suppliers.xls",
            mime="application/vnd.ms-excel"
        )

    if st.button("🔙 رجوع"):
        st.session_state["page"] = "main"
        st.rerun()

def entities_screen():
    st.markdown("<h1>📊 شاشة الجهات</h1>", unsafe_allow_html=True)
    try:
        df = pd.read_excel("entities.xlsx")
        st.dataframe(df, use_container_width=True)
    except:
        st.error("⚠️ لم يتم العثور على ملف الجهات")
    if st.button("🔙 رجوع"):
        st.session_state["page"] = "main"
        st.rerun()

# =========================
# --- التحكم في الشاشات ---
# =========================

if not st.session_state["logged_in"]:
    login_screen()
else:
    if st.session_state["page"] == "main":
        main_menu()
    elif st.session_state["page"] == "suppliers_registry":
        suppliers_registry_screen()
    elif st.session_state["page"] == "suppliers":
        suppliers_screen()
    elif st.session_state["page"] == "entities":
        entities_screen()
