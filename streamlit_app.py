import streamlit as st

page={
 "工具程式": [
    st.Page("apps/app1.py", title="1.耐震設計"),
    st.Page("apps/app2.py", title="2.基樁側向分析"),
    st.Page("apps/app3.py", title="3.混凝土分析"),
    st.Page("apps/app4.py", title="4.OpenSee"),
    st.Page("apps/app5.py", title="5.混凝土圓柱"),],
}
 
pg = st.navigation(page)

pg.run()