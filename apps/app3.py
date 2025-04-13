import streamlit as st
st.title("工具應用程式3")


import matplotlib.pyplot as plt
from concreteproperties.material import Concrete, SteelBar
from concreteproperties.pre import add_bar
from concreteproperties.concrete_section import ConcreteSection
from concreteproperties.stress_strain_profile import (
    ConcreteLinear,
    RectangularStressBlock,
    SteelElasticPlastic,
)
from sectionproperties.pre.library.concrete_sections import concrete_rectangular_section

# 設定頁面標題
st.title("混凝土斷面圖繪製")

# 輸入參數
st.sidebar.header("輸入參數")
width = st.sidebar.number_input("斷面寬度 (mm)", value=300)
depth = st.sidebar.number_input("斷面高度 (mm)", value=500)
fc = st.sidebar.number_input("混凝土抗壓強度 (MPa)", value=32)
fy = st.sidebar.number_input("鋼筋降伏強度 (MPa)", value=500)
bar_diameter = st.sidebar.number_input("鋼筋直徑 (mm)", value=20)
bar_area = 3.14159 * (bar_diameter / 2) ** 2
cover = st.sidebar.number_input("保護層厚度 (mm)", value=30)

# 創建混凝土材料
concrete = Concrete(
    name="Concrete",
    density=2.4e-6,
    stress_strain_profile=ConcreteLinear(elastic_modulus=30.1e3),
        ultimate_stress_strain_profile=RectangularStressBlock(
        compressive_strength=fc,
        alpha=0.802,
        gamma=0.89,
        ultimate_strain=0.003,
    ),
    colour="lightgrey",
    flexural_tensile_strength=3.4,
)

# 創建鋼筋材料
steel = SteelBar(
    name="Steel",
    density=7.85e-6,
    stress_strain_profile=SteelElasticPlastic(
        yield_strength=fy,
        elastic_modulus=200e3,
        fracture_strain=0.05,
    ),
    colour="red",
)

# 創建矩形斷面
geometry = concrete_rectangular_section(
    b=width,
    d=depth,
    dia_top=bar_diameter,
    area_top=bar_area,
    n_top=3,
    c_top=cover,
    dia_bot=bar_diameter,
    area_bot=bar_area,
    n_bot=4,
    c_bot=cover,
    n_circle=8,
    conc_mat=concrete,
    steel_mat=steel,
)
concrete_section = ConcreteSection(geometry)


# 創建混凝土斷面
st.header("ConcreteSection")
fig, ax = plt.subplots()
concrete_section.plot_section(ax=ax,)
ax.set_xlabel("Width (mm)")
ax.set_ylabel("Height (mm)")
ax.set_aspect("equal")
st.pyplot(fig)



# 顯示斷面屬性
st.header("Moment Interaction Diagram")
fig, ax = plt.subplots(figsize=(8,6))
mi_res = concrete_section.moment_interaction_diagram(progress_bar=False)
mi_res.plot_diagram(ax=ax,fmt="-r")
ax.set_ylabel('Axial Force (N)')
ax.set_xlabel('Bending Moment (N-m)')
ax.grid(True, linestyle="--", alpha=0.6)
st.pyplot(fig)



