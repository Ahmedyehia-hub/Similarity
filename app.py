import streamlit as st
import pandas as pd
from rapidfuzz import fuzz

# إعداد الصفحة
st.set_page_config(page_title="Supplier App", layout="wide")

# 🎨 تنسيق CSS مخصص
st.markdown("""
    <style>
    /* الخلفية والخط */
    body, .stApp {
        background-color: #0e1117;
        color: #fafafa;
        font-family: 'Segoe UI', sans-serif;
    }

    /* العناوين */
    h1, h2, h3 {
        color: #ffffff;
        text-align: center;
        margin-bottom: 20px;
    }

    /* الأزرار */
    .stButton > button {
        background-color: #ffffff;
        color: #000000;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #ff4b4b;
        color: white;
    }

    /* إدخالات النص */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border-radius: 8px;
    }

    /* السلايدر */
    .stSlider {
        color: white;
    }

    /* DataFrame */
    .dataframe {
        background: #1e1e1e;
        color: white;
    }

    </style>
""", unsafe_allow_html=True)


# --- عرض اللوجو ---
col1, col2 = st.columns([4,1])
with col2:
    st.image("cleo.jpg", width=220)  # اللوجو على اليمين
with col1:
    st.markdown("")

# --- حالة تسجيل الدخول ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "page" not in st.session_state:
    st.session_state["page"] = "main"   # الافتراضي القائمة الرئيسية

# --- شاشة تسجيل الدخول ---
if not st.session_state["logged_in"]:
    st.title("🔐 تسجيل الدخول للتطبيق")

    username = st.text_input("اسم المستخدم", key="user")
    password = st.text_input("كلمة المرور", type="password", key="pass")

    if st.button("تسجيل الدخول"):
        if username == "admin" and password == "1234":
            st.session_state["logged_in"] = True
            st.success("✅ تم تسجيل الدخول بنجاح 🎉")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة")

# --- القائمة الرئيسية ---
else:
    if st.session_state["page"] == "main":
        st.markdown("<h1>📂 القائمة الرئيسية</h1>", unsafe_allow_html=True)

        st.write("")  # مسافة

        colA, colB, colC = st.columns(3)

        with colA:
            if st.button("📊 الموردين بالسجل التجاري", use_container_width=True):
                st.session_state["page"] = "suppliers_registry"
                st.rerun()

        with colB:
            if st.button("📊 الموردين", use_container_width=True):
                st.session_state["page"] = "suppliers"
                st.rerun()

        with colC:
            if st.button("🏢 الجهات", use_container_width=True):
                st.session_state["page"] = "entities"
                st.rerun()

    # --- شاشة الموردين بالسجل التجاري ---
    elif st.session_state["page"] == "suppliers_registry":
        st.markdown("<h1>📊 الموردين بالسجل التجاري</h1>", unsafe_allow_html=True)

        similarity_range = st.slider("🔢 اختر نسبة التشابه (من - إلى)", 50, 100, (80, 100))

        if st.button("🚀 تطبيق الفلترة", use_container_width=True):
            try:
                df = pd.read_excel("suppliers2.xlsx")
                codes = df['code']
                names = df['merge']

                results = []
                for i in range(len(names)):
                    for j in range(i+1, len(names)):
                        similarity = fuzz.ratio(str(names[i]), str(names[j]))
                        if similarity_range[0] <= similarity <= similarity_range[1]:
                            results.append({
                                "Code_1": codes[i],
                                "Name_1": names[i],
                                "Code_2": codes[j],
                                "Name_2": names[j],
                                "Similarity %": similarity
                            })

                similar_df = pd.DataFrame(results).sort_values("Similarity %", ascending=False)
                st.dataframe(similar_df, use_container_width=True)

                similar_df.to_excel("similar_suppliers2.xlsx", index=False)
                st.success("✅ تم حفظ النتائج في similar_suppliers2.xlsx")

            except Exception as e:
                st.error(f"⚠️ خطأ في تحميل الملف: {e}")

        if st.button("🔙 رجوع", use_container_width=True):
            st.session_state["page"] = "main"
            st.rerun()

    # --- شاشة الموردين ---
    elif st.session_state["page"] == "suppliers":
        st.markdown("<h1>📊 الموردين</h1>", unsafe_allow_html=True)

        similarity_range = st.slider("🔢 اختر نسبة التشابه (من - إلى)", 50, 100, (80, 100))

        if st.button("🚀 تطبيق الفلترة", use_container_width=True):
            try:
                df = pd.read_excel("suppliers.xlsx")
                codes = df['code']
                names = df['designation']

                results = []
                for i in range(len(names)):
                    for j in range(i+1, len(names)):
                        similarity = fuzz.ratio(str(names[i]), str(names[j]))
                        if similarity_range[0] <= similarity <= similarity_range[1]:
                            results.append({
                                "Code_1": codes[i],
                                "Name_1": names[i],
                                "Code_2": codes[j],
                                "Name_2": names[j],
                                "Similarity %": similarity
                            })

                similar_df = pd.DataFrame(results).sort_values("Similarity %", ascending=False)
                st.dataframe(similar_df, use_container_width=True)

                similar_df.to_excel("similar_suppliers.xlsx", index=False)
                st.success("✅ تم حفظ النتائج في similar_suppliers.xlsx")

            except Exception as e:
                st.error(f"⚠️ خطأ في تحميل الملف: {e}")

        if st.button("🔙 رجوع", use_container_width=True):
            st.session_state["page"] = "main"
            st.rerun()

    # --- شاشة الجهات ---
    elif st.session_state["page"] == "entities":
        st.markdown("<h1>📊 شاشة الجهات</h1>", unsafe_allow_html=True)
        try:
            df = pd.read_excel("entities.xlsx")
            st.dataframe(df, use_container_width=True)
        except:
            st.error("⚠️ لم يتم العثور على ملف الجهات")

        if st.button("🔙 رجوع", use_container_width=True):
            st.session_state["page"] = "main"
            st.rerun()
