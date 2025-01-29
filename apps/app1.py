import streamlit as st
import numpy as np
import pandas as pd
import os
import plotly.graph_objects as go

# st.set_page_config(layout="wide")

script_dir = os.path.dirname(__file__)
csv_file = os.path.join(script_dir,"data.csv")
df = pd.read_csv(csv_file)

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
    "T":None,
    "alfa_y":None,
}

unique_categories = df['縣市'].unique()
selected_category = st.sidebar.selectbox("選擇縣市",unique_categories)
filtered_subcategories = df[df['縣市']==selected_category]['鄉鎮市區'].unique()
selected_subcategory = st.sidebar.selectbox("選擇鄉鎮市區",filtered_subcategories)
filtered_data = df[(df['縣市']==selected_category)&(df['鄉鎮市區']==selected_subcategory)]

respond_info["siteType"] = st.sidebar.selectbox(
    "地盤分類",
    ("第一類地盤(堅實地盤)", "第二類地盤(普通地盤)", "第三類地盤(軟弱軟弱地盤)"),
    index=1,
    placeholder="Select contact method...",
    )

respond_info["var_i"] = st.sidebar.selectbox(
    "I 用途係數",
    (1.00, 1.25, 1.50),
    index=1,
    placeholder="Select contact method...",
    )

respond_info["T"]  = st.sidebar.number_input(
    "T 基本振動週期 (sec)",
    value= 0.6,
    min_value=0.0,
    )

respond_info["R"]  = st.sidebar.number_input(
    "R 結構系統韌性容量",
    value= 4.0,
    min_value=0.0,
    )

respond_info["alfa_y"]  = st.sidebar.number_input(
    "αy 起始降伏地震力放大倍數",
    value= 1.0,
    min_value=1.0,
    )

siteType = respond_info["siteType"]
I = respond_info["var_i"]

SD_S = float(filtered_data["SD_S"].values)
SD_1 = float(filtered_data["SD_1"].values)
SM_S = float(filtered_data["SM_S"].values)
SM_1 = float(filtered_data["SM_1"].values)
SDs_S = 0.70 #假設
SDs_1 = 0.40 #假設

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
st.write("工址位於 :",str(filtered_data["縣市"].values),str(filtered_data["鄉鎮市區"].values))
st.write("地盤種類 :",siteType)
st.write("用途係數 I =",respond_info["var_i"])


col1,col2,col3,col4 = st.columns([2.5,1,1,1])

with col1:
    st.write("####  ")
    st.write("震區短週期水平譜加速度係數")
    st.write("震區一秒週期水平譜加速度係數")
    st.write("反應譜等加速度段之工址放大係數")
    st.write("反應譜等速度段之工址放大係數")
    st.write("工址短週期譜加速度係數")
    st.write("工址一秒週期譜加速度係數")
    st.write("工址反應譜短週期與中長週期之分界")

with col2:
    st.write("#### <U>設計</U>", unsafe_allow_html=True)   
    st.write("S<sub>S</sub><sup>D</sup> =",round(SD_S,3), unsafe_allow_html=True)
    st.write("S<sub>1</sub><sup>D</sup> =",round(SD_1,3), unsafe_allow_html=True)
    st.write("F<sub>a</sub> =",Fa(siteType, SD_S), unsafe_allow_html=True)
    st.write("F<sub>v</sub> =",Fa(siteType, SD_1), unsafe_allow_html=True)
    st.write('S<sub>DS</sub> =',round(S_DS,3), unsafe_allow_html=True) 
    st.write('S<sub>D1</sub> =',round(S_D1,3), unsafe_allow_html=True)  
    st.write("T<sub>0</sub><sup>D</sup> =",round(TD_0,3), unsafe_allow_html=True)

with col3:
    st.write("#### <U>中度</U>", unsafe_allow_html=True) 
    st.write("S<sub>S</sub><sup>D</sup> =",round(SDs_S,3), unsafe_allow_html=True)
    st.write("S<sub>1</sub><sup>D</sup> =",round(SDs_1,3), unsafe_allow_html=True)
    st.write("F<sub>a</sub> =",Fa(siteType, SDs_S), unsafe_allow_html=True)
    st.write("F<sub>v</sub> =",Fv(siteType, SDs_1), unsafe_allow_html=True)
    st.write('S<sub>DS</sub> =',round(S_DsS,3), unsafe_allow_html=True) 
    st.write('S<sub>D1</sub> =',round(S_Ds1,3), unsafe_allow_html=True) 
    st.write("T<sub>0</sub><sup>D</sup> =",round(TDs_0,3), unsafe_allow_html=True) 

with col4:
    st.write("#### <U>最大</U>", unsafe_allow_html=True) 
    st.write("S<sub>S</sub><sup>M</sup> =",round(SM_S,3), unsafe_allow_html=True)
    st.write("S<sub>1</sub><sup>M</sup> =",round(SM_1,3), unsafe_allow_html=True)
    st.write("F<sub>a</sub> =",Fa(siteType, SM_S), unsafe_allow_html=True)
    st.write("F<sub>v</sub> =",Fa(siteType, SM_1), unsafe_allow_html=True)
    st.write('S<sub>MS</sub> =',round(S_MS,3), unsafe_allow_html=True) 
    st.write('S<sub>M1</sub> =',round(S_M1,3), unsafe_allow_html=True) 
    st.write("T<sub>0</sub><sup>M</sup> =",round(TM_0,3), unsafe_allow_html=True) 



st.divider()
st.write("起始降伏地震力放大倍數 αy =",alfa_y)
st.write("基本震動週期 T =",T)
st.write("結構系統韌性容量 R =",R)
st.write("結構系統容許韌性容量 Ra =",Ra)
st.write("正規化設計基準地震力係數 V<sub>D</sub> / W = (I/1.4αy)(SaD/Fu)m ", unsafe_allow_html=True)
         

col1,col2,col3,col4 = st.columns([2.5,1,1,1])
with col1:
    st.write("#### ")
    st.write("工址譜加速度係數")
    st.write("地震力折減係數")
    st.write("地震力係數")

with col2:
    st.write("#### <U>設計</U>", unsafe_allow_html=True)   
    st.write("SaD =",round(S_aD,3)) 
    st.write("FuD =",round(F_uD,3)) 
    st.write("V<sub>D</sub> / W =",round(V_D,3), unsafe_allow_html=True) 

with col3:
    st.write("#### <U>中度</U>", unsafe_allow_html=True) 
    st.write("SaS =",round(S_aDs,3)) 
    st.write("FuS =",round(F_uDs,3)) 
    st.write("V<sub>S</sub> / W =",round(V_S,3), unsafe_allow_html=True) 
    
with col4:
    st.write("#### <U>最大</U>", unsafe_allow_html=True)   
    st.write("SaM =",round(S_aM,3))
    st.write("FuM =",round(F_uM,3))
    st.write("V<sub>M</sub> / W =",round(V_M,3), unsafe_allow_html=True) 

st.write('V<sub>design</sub> / W =',round(V_design,3), unsafe_allow_html=True) 
st.divider()


t_ranges = st.slider("週期範圍", 0.0, 5.0, (0.0, 3.0))
t_step = st.number_input("週期間距",min_value=0.01,max_value=0.5,step=0.01,value=0.05)


t = np.arange(t_ranges[0] , t_ranges[1], t_step)
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
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='設計地震'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='最大地震'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y3'], mode='lines', name='中度地震'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='工址水平譜加速度係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='Sa',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[t_ranges[0]-0.1,t_ranges[1]+0.1],
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
fig.add_trace(go.Scatter(x=data['x'], y=data['y1'], mode='lines', name='設計地震'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y2'], mode='lines', name='最大地震'))
fig.add_trace(go.Scatter(x=data['x'], y=data['y3'], mode='lines', name='中度地震'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='結構系統地震力折減係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='Fu',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[t_ranges[0]-0.1,t_ranges[1]+0.1],
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
    '週期': t,
    '設計地震': V_D,
    '最大地震': V_M,
    '中度地震': V_S
})
fig = go.Figure()

# Add traces for each line
fig.add_trace(go.Scatter(x=data['週期'], y=data['設計地震'], mode='lines', name='設計地震'))
fig.add_trace(go.Scatter(x=data['週期'], y=data['最大地震'], mode='lines', name='最大地震'))
fig.add_trace(go.Scatter(x=data['週期'], y=data['中度地震'], mode='lines', name='中度地震'))

# Update layout to add margins and grid lines
fig.update_layout(
    title='設計水平加速度反應譜係數',
    xaxis_title='週期 T (sec)',
    yaxis_title='V/W',
    margin=dict(l=50, r=50, t=50, b=50),  # Adjust the margins as needed
    xaxis=dict(
        range=[t_ranges[0]-0.1,t_ranges[1]+0.1],
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
st.write(data)