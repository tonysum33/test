import streamlit as st


st.title("工具應用程式5")

import openseespy.opensees as ops
import opsvis as opsv
import matplotlib.pyplot as plt

ops.wipe()
ops.model('basic', '-ndm', 2, '-ndf', 3)

colL, girL = 4., 6.

Acol, Agir = 2.e-3, 6.e-3
IzCol, IzGir = 1.6e-5, 5.4e-5

E = 200.e9

Ep = {1: [E, Acol, IzCol],
      2: [E, Acol, IzCol],
      3: [E, Agir, IzGir]}

ops.node(1, 0., 0.)
ops.node(2, 0., colL)
ops.node(3, girL, 0.)
ops.node(4, girL, colL)

ops.fix(1, 1, 1, 1)
ops.fix(3, 1, 1, 0)

opsv.plot_model()
plt.title('plot_model before defining elements')