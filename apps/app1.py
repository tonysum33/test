import streamlit as st
st.title("工具應用程式1")

st.sidebar.number_input('用途係數',value=1.2)

option = st.sidebar.selectbox(
    "地盤種類",
    ("第一類(堅實)地盤", "第二類(普通)地盤", "第三類(普通)地盤"),
)

st.write("You selected:", option)
st.sidebar.divider()
st.sidebar.number_input('S$^D_S$ 震區短週期設計水平譜加速度係數',value=0.60)
st.sidebar.number_input('S$^D_1$ 震區一秒週期設計水平譜加速度係數',value=0.35)
st.sidebar.number_input('S$^M_S$ 震區短週期最大水平譜加速度係數',value=0.80)
st.sidebar.number_input('S$^M_1$ 震區一秒週期最大水平譜加速度係數',value=0.50)
st.sidebar.divider()