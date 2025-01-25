import streamlit as st
import math
import pandas as pd


intputData = {
    'PileD': None,
    'PileL': None,
    'Fc':    None,
    'Ht':    None,
    'kh' :   None
    }

intputData['PileD'] = st.sidebar.number_input('樁徑(cm)',value=100, min_value =0)
intputData['PileL'] = st.sidebar.number_input('樁長(m)',value=20,min_value =0)
intputData['Ht'] = st.sidebar.number_input('樁頂距地面高(cm)',value=0, min_value =0)
intputData['Fc'] = st.sidebar.number_input('混凝土強度(kgf/cm^2)',value=245)
intputData['kh'] = st.sidebar.number_input('水平地盤反力係數(kgf/cm3)',format="%0.3f")
intputData['ForceP'] = st.sidebar.number_input('樁頂垂直力(tf)')
intputData['ForceH'] = st.sidebar.number_input('樁頂水平力(tf)')



st.markdown('## 基樁側向分析')
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.markdown('### 基樁資料')
    st.write("樁徑 D =",intputData["PileD"],"cm",)
    st.write("樁長 L =",intputData["PileL"],"m",)
    st.write("樁頂距地面高 Ht =",intputData["Ht"],"cm",)
    st.write("混凝土強度 fc' =",intputData["Fc"],"kgf/cm2")
    st.write("水平地盤反力係數",intputData['kh'],"kgf/cm3")

with col2:
    st.markdown('### 外力資料')
    st.write("樁頂垂直力 P =",intputData['ForceP'],"tf",)
    st.write("樁頂水平力 P =",intputData['ForceH'],"tf",)

st.divider()
Ap = 1/4 * math.pi * intputData['PileD']**2
Ip = 1/64 * math.pi * intputData['PileD']**4
Ep = 15100 * intputData['Fc']**0.5
beta = ((intputData['kh']*intputData['PileD'])/(4*Ep*Ip))**0.25

st.markdown('## 輸出資料')
st.write("斷面積 =" ,round(Ap,1) ,"cm2")
st.write("慣性矩 =" ,round(Ip,1) ,"cm4")
st.write("彈性係數 =" ,round(Ep,1),"kgf/cm2")
st.write("β =" ,round(beta*100,3) ,"1/m")
st.write("βL =" ,round(beta*intputData["PileL"]*100,3) ,"m")

