import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.title("建築物耐震")

# 一般工址或近斷層工址之工址水平譜加速度係數 S_aD, S_aM
def Sa(T, T_0, S_S, S_1):
    if T <= 0.2 * T_0:
        return S_S *( 0.4 + 3*T/T_0)
    elif T <= T_0:
        return S_S
    elif T <= 2.5 * T_0:
        return S_1/T
    else:
        return 0.4 * S_S
    
# 短週期結構之工址放大係數 Fa
def Fa(siteType,Ss):
    if siteType == "第一類地盤(堅實地盤)":
        value = [1.0, 1.0, 1.0, 1.0, 1.0]
    elif siteType == "第二類地盤(普通地盤)":
        value = [1.1, 1.1, 1.0, 1.0, 1.0]
    elif siteType == "第三類地盤(軟弱軟弱地盤)":
        value = [1.2, 1.2, 1.1, 1.0, 1.0]

    return np.interp(Ss, [0.5, 0.6, 0.7, 0.8, 0.9], value)

# 長週期結構之工址放大係數 Fv
def Fv(siteType,S1):
    if siteType == "第一類地盤(堅實地盤)":
        value = [1.0, 1.0, 1.0, 1.0, 1.0]
    elif siteType == "第二類地盤(普通地盤)":
        value = [1.5, 1.4, 1.3, 1.2, 1.1]
    elif siteType == "第三類地盤(軟弱軟弱地盤)":
        value = [1.8, 1.7, 1.6, 1.5, 1.4]

    return np.interp(S1, [0.3, 0.35, 0.4, 0.45, 0.5], value)    

# 結構系統地震力折減係數 Fu
def Fu(T, T_0, Ra):
    tmp = (2*Ra-1)**0.5
    if T <= 0.2 * T_0:
        return tmp + (tmp-1) * (T - 0.2*T_0)/(0.2*T_0)
    elif T <= 0.6 * T_0:
        return tmp
    elif T <= T_0:
        return tmp + (Ra - tmp) * (T - 0.6*T_0)/(0.4*T_0)
    else:
        return Ra

# 修正 (Sa/Fu)m 
def Sa_Fu_m(S_a, Fu):
    tmp = S_a/Fu
    if tmp <= 0.3:
        return tmp
    elif tmp < 0.8:
        return 0.52*tmp +0.144
    else:
        return 0.7 *tmp


respond_info = {
    "siteType":None,
    "var_i":None,
    "SD_S":None,
    "SD_1":None,
    "SM_S":None,
    "SM_1":None,
    "T":None,
    "alfa_y":None,
}


respond_info["siteType"] = st.sidebar.selectbox(
    "地盤分類",
    ("第一類地盤(堅實地盤)", "第二類地盤(普通地盤)", "第三類地盤(軟弱軟弱地盤)"),
    index=1,
    placeholder="Select contact method...",
    )

respond_info["var_i"] = st.sidebar.selectbox(
    "用途係數 I",
    (1.00, 1.25, 1.50),
    index=1,
    placeholder="Select contact method...",
    )

respond_info["SD_S"]  = st.sidebar.number_input(
    "S$^D_S$ 短周期設計水平譜加速度數係數",
    value= 1.00,
    min_value=0.0,
    max_value=1.0
    )

respond_info["SD_1"]  = st.sidebar.number_input(
    "S$^D_1$ 一秒週期設計水平譜加速度數係數",
    value= 0.70,
    min_value=0.0,
    )

respond_info["SM_S"]  = st.sidebar.number_input(
    "S$^M_S$ 短週期最大考量水平譜加速度數係數",
    value= 1.00,
    min_value=0.0,
    )


respond_info["SM_1"]  = st.sidebar.number_input(
    "S$^M_1$ 一秒週期最大考量水平譜加速度數係數",
    value= 0.55,
    min_value=0.0,
    )

respond_info["T"]  = st.sidebar.number_input(
    "所考慮方向之基本震動週期 T(sec)",
    value= 0.6,
    min_value=0.0,
    )

respond_info["R"]  = st.sidebar.number_input(
    "所考慮方向之結構系統韌性容量 R",
    value= 4.0,
    min_value=0.0,
    )

respond_info["alfa_y"]  = st.sidebar.number_input(
    "起始降伏地震力放大倍數 α$_y$",
    value= 1.0,
    min_value=1.0,
    )

siteType = respond_info["siteType"]
I = respond_info["var_i"]

SD_S = respond_info["SD_S"]
SD_1 = respond_info["SD_1"]
SM_S = respond_info["SM_S"]
SM_1 = respond_info["SM_1"]

T = respond_info["T"]
R = respond_info["R"]
Ra = 1 +(R-1)/1.5
alfa_y = 1.0

# 設計地震
S_DS = Fa(siteType, SD_S) * SD_S
S_D1 = Fv(siteType, SD_1) * SD_1
TD_0 = S_D1 / S_DS
S_aD = Sa(T , TD_0, S_DS, S_D1)
F_uD = Fu(T , TD_0, Ra)
V_D = I/1.4/alfa_y * Sa_Fu_m(S_aD, F_uD) 

# 中度地震
SDs_S = 0.70 #假設
SDs_1 = 0.40 #假設
S_DsS = Fa(siteType, SDs_S) * SDs_S
S_Ds1 = Fv(siteType, SDs_1) * SDs_1
TDs_0 = S_Ds1 / S_DsS
S_aDs = Sa(T , TDs_0, S_DsS, S_Ds1)
F_uDs = Fu(T , TDs_0, Ra)
V_S = I/4.2/alfa_y *F_uDs * Sa_Fu_m(S_aDs, F_uDs) 

# 最大地震
S_MS = Fa(siteType, SM_S) * SM_S
S_M1 = Fv(siteType, SM_1) * SM_1
TM_0 = S_M1 / S_MS
S_aM = Sa(T , TM_0, S_MS, S_M1)
F_uM = Fu(T , TM_0, R)
V_M = I/1.4/alfa_y * Sa_Fu_m(S_aM, F_uM) 

# 設計地震
V_design = max(V_D, V_S,V_M)


st.divider()
st.write("地盤種類 :",respond_info["siteType"])
st.write("用途係數 I =",respond_info["var_i"])
st.write("S$^D_S$ 短周期設計水平譜加速度數係數 :",round(respond_info["SD_S"],2))
st.write("S$^D_1$ 一秒週期設計水平譜加速度數係數 :",round(respond_info["SD_1"],2))
st.write("S$^M_S$ 短週期最大考量水平譜加速度數係數 :",round(respond_info["SM_S"],2))
st.write("S$^M_1$ 一秒週期最大考量水平譜加速度數係數 :",round(respond_info["SM_1"],2))

st.divider()
st.write("起始降伏地震力放大倍數 α$_y$",alfa_y)

st.divider()
st.write('設計地震 V$_{d}$ =',round(V_D,3),"tf")
st.write('中度地震 V$_{s}$ =',round(V_S,3),"tf")
st.write('最大地震 V$_{m}$ =',round(V_M,3),"tf")
st.write('設計地震 V$_{design}$ =',round(V_design,3),"tf")

st.divider()



t = np.arange(0.0 , 5.0, 0.05)
SaD  = [Sa(i, TD_0, S_DS, S_D1) for i in t]
SaM  = [Sa(i, TM_0, S_MS, S_M1) for i in t]
SaDs = [Sa(i, TDs_0, S_DsS, S_Ds1) for i in t]

FuDs = [Fu(i, TDs_0, Ra) for i in t]
FuD = [Fu(i, TD_0, Ra) for i in t]
FuM = [Fu(i, TM_0, R)  for i in t]

data = pd.DataFrame({
    'x': t,
    'y1': SaD,
    'y2': SaM,
    'y3': SaDs
})
fig = go.Figure()

# Add traces for each line
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='設計'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='最大'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y3'], mode='lines', name='中度'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='工址水平譜加速度係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='Sa',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[-0.1, 5.1],
        showgrid=True,  # Show grid lines for the x-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    yaxis=dict(
        showgrid=True,  # Show grid lines for the y-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    height=400  # Adjust the height of the chart
)

st.plotly_chart(fig)




data = pd.DataFrame({
    'x': t,
    'y1': FuD,
    'y2': FuM,
    'y3': FuDs
})
fig = go.Figure()

# Add traces for each line
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='設計'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='最大'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y3'], mode='lines', name='中度'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='結構系統地震力折減係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='Fu',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[-0.1, 5.1],
        showgrid=True,  # Show grid lines for the x-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    yaxis=dict(
        showgrid=True,  # Show grid lines for the y-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    height=400  # Adjust the height of the chart
)

st.plotly_chart(fig)


# 設計地震

scale = I/1.4/alfa_y/S_aD * Sa_Fu_m(S_aD, F_uD)
V_D = [scale * Sa(i, TD_0, S_DS, S_D1) for i in t]

# 最大地震
scale = I/1.4/alfa_y/S_aM * Sa_Fu_m(S_aM, F_uM)
V_M = [scale * Sa(i, TM_0, S_MS, S_M1) for i in t]

# 中小地震
scale = I*F_uDs/4.2/alfa_y/S_aDs * Sa_Fu_m(S_aDs, F_uDs) # 非台北盆地
V_S = [scale * Sa(i, TDs_0, S_DsS, S_Ds1) for i in t]


data = pd.DataFrame({
    'x': t,
    'y1': V_D,
    'y2': V_M,
    'y3': V_S
})
fig = go.Figure()

# Add traces for each line
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='設計'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='最大'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y3'], mode='lines', name='中度'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='設計水平加速度反應譜係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='V/W',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[-0.1, 5.1],
        showgrid=True,  # Show grid lines for the x-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    yaxis=dict(
        showgrid=True,  # Show grid lines for the y-axis
        gridwidth=1,
        gridcolor='LightGray'
    ),
    height=400  # Adjust the height of the chart
)

st.plotly_chart(fig)
