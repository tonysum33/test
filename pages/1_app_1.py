import streamlit as st
import math
import pandas as pd

def printDataFrame(coordzList, displacementList, momentList, shearList):
    data = {'Depth': coordzList,
            'Moment': momentList,
            'Shear': shearList,
            'Displacement': displacementList,
            }
    pd.options.display.float_format = '{:15.3f}'.format

    df = pd.DataFrame(data)
    df['Depth'] = df['Depth'].map('{:,.2f}'.format)

    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)

    st.write(df)
    st.write("最大彎矩 =", round(df.Moment.abs().max(),3),'tf-m')
    st.write("最大剪力 =", round(df.Shear.abs().max(),3),'tf')
    st.write("最大變位 =", round(df.Displacement.abs().max(),2),'cm')

def cal_main():
    st.markdown('## 基樁側向分析')
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### 基樁資料')
        st.write("樁徑 D =",intputData["PileD"],"cm",)
        st.write("樁長 L =",intputData["PileL"],"cm",)
        st.write("樁頂距地面高 Ht =",intputData["Ht"],"cm",)
        st.write("混凝土強度 fc' =",intputData["Fc"],"kgf/cm$^2$")
        st.write("水平地盤反力係數",intputData['kh'],"kgf/cm$^3$")

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
    st.write("斷面積 =" ,round(Ap) ,"cm$^2$")
    st.write("慣性矩 =" ,round(Ip) ,"cm$^4$")
    st.write("彈性係數 =" ,round(Ep),"kgf/cm$^2$")
    st.write("β =" ,round(beta*100,3) ,"1/m")
    st.write("βL =" ,round(beta*intputData["PileL"],3) ,"m")

    PILEDIVIDE = 50 # cm
    num =  int(intputData['PileL']/PILEDIVIDE)+1

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('### 樁頭拘束')
        coordzList=[]  # m
        momentList=[]  # tf-m
        shearList=[]   # tf
        displacementList=[] # cm
        for i in range(num):
            coordz = i * PILEDIVIDE
            
            if coordz < intputData['Ht']:
                coordz = (coordz - intputData['Ht'])

                displacementList.append(1000*intputData['ForceH']/(12*Ep*Ip*beta**3)*(
                    +2*beta**3*coordz**3
                    -3*(1-beta*intputData['Ht'])*beta**3*coordz**2
                    -6*beta**2*intputData['Ht']*coordz
                    +3*(1+beta*intputData['Ht'])))
                
                momentList.append(intputData['ForceH']/100/(2*beta)*(-2*beta*coordz+(1-beta*intputData['Ht'])))
                shearList.append(-intputData['ForceH'])
                                
            else:
                coordz = (coordz - intputData['Ht'])

                displacementList.append(1000*intputData['ForceH']/(4*Ep*Ip*beta**3)*
                                        math.exp(-beta*coordz)*(
                    (1+beta*intputData['Ht'])*math.cos(beta*coordz)+
                    (1-beta*intputData['Ht'])*math.sin(beta*coordz)))
                
                momentList.append(intputData['ForceH']/100/(2*beta)*math.exp(-beta*coordz)*(
                    (1-beta*intputData['Ht'])*math.cos(beta*coordz)-
                    (1+beta*intputData['Ht'])*math.sin(beta*coordz)))
                shearList.append(-intputData['ForceH']*math.exp(-beta*coordz)*(
                    math.cos(beta*coordz)-(beta*intputData['Ht'])*
                    math.sin(beta*coordz)))
                
            coordzList.append(-coordz/100)

        printDataFrame(coordzList,displacementList,momentList,shearList)
        # plotPile(coordzList,displacementList,shearList,momentList)

        with col2:
            st.markdown('### 樁頭自由')
            coordzList=[]  # m
            momentList=[]  # tf-m
            shearList=[]   # tf
            displacementList=[] # cm
            for i in range(num):
                coordz = i * PILEDIVIDE
                
                if coordz < intputData['Ht']:
                    coordz = (coordz - intputData['Ht'])

                    displacementList.append(1000*intputData['ForceH']/(6*Ep*Ip*beta**3)*(
                        +beta**3*coordz**3
                        +3*beta**3*intputData['Ht']*coordz**2
                        -3*beta*(1+2*beta*intputData['Ht'])*coordz
                        +3*(1+beta*intputData['Ht'])))
                    
                    momentList.append(-intputData['ForceH']/100*(coordz+intputData['Ht']))
                    shearList.append(-intputData['ForceH'])
                                    
                else:
                    coordz = (coordz - intputData['Ht'])

                    displacementList.append(1000*intputData['ForceH']/(2*Ep*Ip*beta**3)*
                                            math.exp(-beta*coordz)*(
                        (1+beta*intputData['Ht'])*math.cos(beta*coordz)-
                        (beta*intputData['Ht'])*math.sin(beta*coordz)))
                    
                    momentList.append(-intputData['ForceH']/100/(beta)*math.exp(-beta*coordz)*(
                        (beta*intputData['Ht'])*math.cos(beta*coordz)+
                        (1+beta*intputData['Ht'])*math.sin(beta*coordz)))
                    shearList.append(-intputData['ForceH']*math.exp(-beta*coordz)*(
                        math.cos(beta*coordz)-(1+2*beta*intputData['Ht'])*
                        math.sin(beta*coordz)))
                    
                coordzList.append(-coordz/100)

            printDataFrame(coordzList,displacementList,momentList,shearList)
            # plotPile(coordzList,displacementList,shearList,momentList)

# with st.sidebar.form(key='form1'):
#     intputData = {
#         'PileD':None,
#         'PileL':None,
#         'Ht':None,
#         'Fc':None,
#         'kh':None,
#         'ForceP':None,
#         'ForceH':None
#     }
#     intputData['PileD'] = st.number_input('樁徑(cm)',value=100, min_value =0)
#     intputData['PileL'] = st.number_input('樁長(cm)',value=2000, min_value =0)
#     intputData['Ht'] = st.number_input('樁頂距地面高(cm)',value=0, min_value =0)
#     intputData['Fc']= st.number_input("混凝土強度(kgf/cm$^2$)",value=245)
#     intputData['kh'] = st.number_input('水平地盤反力係數(kgf/cm$^3$)',value=0.5,format="%0.3f")
#     intputData['ForceP'] = st.number_input('樁頂垂直力(tf)')
#     intputData['ForceH'] = st.number_input('樁頂水平力(tf)',value=30.00)

#     form_submit = st.form_submit_button(label='執行',on_click=cal_main)

intputData = {
    'PileD':None,
    'PileL':None,
    'Ht':None,
    'Fc':None,
    'kh':None,
    'ForceP':None,
    'ForceH':None
}
intputData['PileD'] = st.sidebar.number_input('樁徑(cm)',value=100, min_value =0)
intputData['PileL'] = st.sidebar.number_input('樁長(cm)',value=2000, min_value =0)
intputData['Ht'] = st.sidebar.number_input('樁頂距地面高(cm)',value=0, min_value =0)
intputData['Fc']= st.sidebar.number_input("混凝土強度(kgf/cm$^2$)",value=245)
intputData['kh'] = st.sidebar.number_input('水平地盤反力係數(kgf/cm$^3$)',value=0.5,format="%0.3f")
intputData['ForceP'] = st.sidebar.number_input('樁頂垂直力(tf)')
intputData['ForceH'] = st.sidebar.number_input('樁頂水平力(tf)',value=30.00)
cal_main()

# def plotPile(coordzList,displacementList,shearList,momentList):
#     plt.style.use('_mpl-gallery')
#     plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
#     plt.rcParams['axes.unicode_minus'] = False
#     plt.figure(figsize=(20,10))
#     plt.yticks(fontsize=12)
#     plt.xticks(fontsize=12)

#     #plot 1:
#     plt.subplot(1, 3, 1)
#     plt.title("displacement (cm)")
#     plt.ylabel("depth (m)",fontsize=12)
#     lines= plt.plot(displacementList,coordzList)
#     plt.setp(lines,c='red',linestyle='--') 

#     #plot 2:
#     plt.subplot(1, 3, 2)
#     plt.title("shear (tf)")
#     plt.ylabel("depth (m)",fontsize=12)
#     lines= plt.plot(shearList,coordzList)
#     plt.setp(lines,c='red',linestyle='--') 

#     #plot 3:
#     plt.subplot(1, 3, 3)
#     plt.title("moment (tf-m)")
#     plt.ylabel("depth (m)",fontsize=12)
#     lines= plt.plot(momentList,coordzList)
#     plt.setp(lines,c='red',linestyle='--') 

#     plt.subplots_adjust(left=0.125,
#                         bottom=0.1, 
#                         right=0.9, 
#                         top=0.9, 
#                         wspace=0.5, 
#                         hspace=0.35)

#     st.pyplot(plt)


