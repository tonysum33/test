import streamlit as st

a1 = st.Page("apps/app1.py", title="1.耐震設計")
a2 = st.Page("apps/app2.py", title="2.基礎設計")
a3 = st.Page("apps/app3.py", title="3.基樁側向分析")
a4 = st.Page("apps/app4.py", title="4.混凝土分析")

 
pg = st.navigation({"工具程式": [a1, a2, a3, a4]})

pg.run()