import streamlit as st
import math


option = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone"),
)


pileData = {'D':  150,
            'L': 4000,
            'Fc': 245,
            'Ht':  10,
            }
kh = 0.992

Ap = 1/4 * math.pi * pileData["D"]**2
Ip = 1/64* math.pi * pileData["D"]**4
Ep = 15100 * pileData["Fc"]**0.5
beta = ((kh*pileData["D"])/(4*Ep*Ip))**0.25


st.markdown('# 計算結果')
st.write('{:10} {:12.1f} {:10}{:5}'.format("D =",pileData["D"]/100,"m","樁徑")) 
st.write('{:10} {:12.1f} {:10}{:5}'.format("L =",pileData["L"]/100,"m","樁長")) 
st.write('{:10} {:12.1f} {:10}{:5}'.format("Ht =",pileData["Ht"],"cm","樁頂距地面高"))
st.write('{:10} {:12.1f} {:10}{:5}'.format("fc' =",pileData["Fc"],"cm2","混凝土強度")) 
st.write('{:10} {:12.1f} {:10}{:5}'.format("Ap =",Ap,"cm2","基樁面積")) 
st.write('{:10} {:12.1f} {:10}{:5}'.format("Ip =",Ip,"cm4","慣性矩"))
st.write('{:10} {:12.1f} {:10}{:5}'.format("Ep =",Ep,"kgf/cm2","彈性係數"))
st.write('{:10} {:12.3f} {:10}{:5}'.format("kh =",kh,"kgf/cm3","水平地盤反力係數"))


st.write("You selected:", option)