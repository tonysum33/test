import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from concreteproperties.material import Concrete, SteelBar
from concreteproperties.pre import add_bar
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.stress_strain_profile import (
    ConcreteLinear,
    RectangularStressBlock,
    SteelElasticPlastic,
)
from sectionproperties.pre.library.concrete_sections import concrete_circular_section

st.title("工具應用程式6")
# 設定頁面標題
st.title("混凝土斷面圖繪製")



# 單位轉換
GRAVITY = 9.80665 # m/sec2

# 1 MPa = 1 N/mm2
def kgfcm2_to_MPa(kgfcm2):
    return kgfcm2 * GRAVITY/100



# 輸入參數
st.sidebar.header("輸入參數")
diameter = st.sidebar.number_input("直徑 (mm)", value=600, step=100)
fc_kgfcm2 = st.sidebar.number_input("混凝土抗壓強度 (kgf/cm2)", value=280)
fy_kgfcm2 = st.sidebar.number_input("鋼筋降伏強度 _kgfcm2", value=4200)
bar_number = st.sidebar.number_input("鋼筋數量", value=10)
bar_diameter = st.sidebar.number_input("鋼筋直徑 (mm)", value=16)
bar_area = np.pi * (bar_diameter / 2) ** 2
cover = st.sidebar.number_input("保護層厚度 (mm)", value=30)

fc_MPa = kgfcm2_to_MPa(fc_kgfcm2)
fy_MPa = kgfcm2_to_MPa(fy_kgfcm2)

# 創建混凝土材料
concrete = Concrete(
    name="Concrete",
    density=2.4e-6, # kg/mm3
    stress_strain_profile=ConcreteLinear(elastic_modulus=30.1e3),
        ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=fc_MPa,
        alpha=0.802,
        gamma=0.89,
        ultimate_strain=0.003,
    ),
    colour="lightgrey",
    flexural_tensile_strength=3.4, # MPa
)


# 創建鋼筋材料
steel = SteelBar(
    name="Steel",
    density=7.85e-6, # kg/mm3
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=fy_MPa,
        elastic_modulus=200000, # MPa
        fracture_strain=0.05,
    ),
    colour="red",
)


# 創建矩形斷面
geometry = concrete_circular_section(
    d= diameter,
    area_conc= np.pi * diameter * diameter / 4,
    n_conc= 64,
    dia_bar= bar_diameter,
    area_bar= bar_area,
    n_bar=bar_number,
    cover= cover,
    n_circle= 8,
    conc_mat=concrete,
    steel_mat=steel,
)
concrete_section = ConcreteSection(geometry)


# 創建混凝土斷面
st.header("ConcreteSection")
fig, ax = plt.subplots()
concrete_section.plot_section(ax=ax,background= False,)
ax.set_xlabel("diameter (mm)")
ax.set_ylabel("diameter (mm)")
ax.set_aspect("equal")
st.pyplot(fig)

st.write("直徑 =",diameter ,"mm")
st.write("鋼筋數量 =",bar_number)


# 顯示斷面屬性
st.header("Moment Interaction Diagram")
fig, ax = plt.subplots()
mi_res = concrete_section.moment_interaction_diagram(progress_bar=False)
mi_res.plot_diagram(ax=ax,fmt="-r")
ax.set_ylabel('Axial Force (N)')
ax.set_xlabel('Bending Moment (N-m)')
ax.grid(True, linestyle="--", alpha=0.6)
st.pyplot(fig)
