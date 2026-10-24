
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import csv
import io

# ==========================================
# SIMULADOR DE RESERVORIO PARABÓLICO
# Ingeniería Civil - Cálculo Integral
# ==========================================

st.set_page_config(
    page_title="Simulador de reservorio parabólico",
    layout="wide"
)

# 1. Parámetros del modelo
R = 3.0
H = 2.0
rho = 1000.0
g = 9.81

# 2. Funciones matemáticas

def radio_superficie(h):
    return R * np.sqrt(h / H)


def volumen_restante(h):
    return np.pi * R**2 * h**2 / (2 * H)


def porcentaje_lleno(h):
    return 100 * (h / H)**2


def trabajo_acumulado(h):
    W = (
        rho * g * np.pi * R**2 / H
        * (H**3 / 6 - H * h**2 / 2 + h**3 / 3)
    )
    return np.maximum(0.0, W)



V_total = np.pi * R**2 * H / 2
W_total = rho * g * np.pi * R**2 * H**2 / 6

# 3. Encabezado de la aplicación

st.title("Simulador de un reservorio parabólico")
st.caption(
    "Aplicación de integrales definidas al volumen "
    "y al trabajo ideal de bombeo."
)

st.markdown(
    "Modifica el nivel del agua para observar cómo cambian "
    "la geometría, el volumen restante y el trabajo acumulado."
)
# 3.5. Controles de animación

if "vaciado_en_marcha" not in st.session_state:
    st.session_state["vaciado_en_marcha"] = False


def iniciar_vaciado():
    if st.session_state["nivel_agua_anim"] <= 0.0:
        st.session_state["nivel_agua_anim"] = float(H)

    st.session_state["vaciado_en_marcha"] = True

def pausar_vaciado():
    st.session_state["vaciado_en_marcha"] = False


def reiniciar_vaciado():
    st.session_state["vaciado_en_marcha"] = False
    st.session_state["nivel_agua_anim"] = float(H)


st.subheader("Controles de vaciado")

col_inicio, col_pausa, col_reinicio = st.columns(3)

with col_inicio:
    st.button(
        "▶ Iniciar",
        on_click=iniciar_vaciado,
        key="btn_iniciar_vaciado"
    )

with col_pausa:
    st.button(
        "⏸ Pausar",
        on_click=pausar_vaciado,
        key="btn_pausar_vaciado"
    )

with col_reinicio:
    st.button(
        "↺ Reiniciar",
        on_click=reiniciar_vaciado,
        key="btn_reiniciar_vaciado"
    )

# Indicador del estado del reservorio

if "nivel_agua_anim" not in st.session_state:
    st.session_state["nivel_agua_anim"] = float(H)
    
nivel_actual = float(st.session_state["nivel_agua_anim"])

if st.session_state["vaciado_en_marcha"]:
    st.info("🔄 Estado: Vaciado en curso")

elif nivel_actual <= 0.0:
    st.warning(
        "Reservorio vacío. Pulsa Iniciar "
        "para comenzar un nuevo ciclo."
    )

else:
    st.caption(
        f"⏸ Estado: Pausado | "
        f"Nivel actual: {nivel_actual:.2f} m"
    )
# 4. Modelo interactivo dentro de un fragmento

if "nivel_agua_anim" not in st.session_state:
    st.session_state["nivel_agua_anim"] = float(H)


run_every = (
    "1s"
    if st.session_state["vaciado_en_marcha"]
    else None
)

@st.fragment(run_every=run_every)
def mostrar_reservorio():

    # Actualización automática del nivel
    if st.session_state["vaciado_en_marcha"]:
        nuevo_nivel = max(
            0.0,
            float(st.session_state["nivel_agua_anim"])
            - float(H) / 35
        )

        st.session_state["nivel_agua_anim"] = nuevo_nivel

        # Detener al llegar al nivel cero
        if nuevo_nivel <= 0.0:
            st.session_state["vaciado_en_marcha"] = False
            st.rerun()

    # Control del nivel de agua
    st.sidebar.header("Control del reservorio")

    h = st.sidebar.slider(
        "Nivel actual del agua (m)",
        min_value=0.0,
        max_value=float(H),
        step=0.05,
        key="nivel_agua_anim"
    )

    # Cálculos
    r_agua = radio_superficie(h)
    V = volumen_restante(h)
    llenado = porcentaje_lleno(h)
    extraido = 100 - llenado
    V_extraido = max(0.0, V_total - V)
    W = trabajo_acumulado(h)

    # Indicadores numéricos
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Nivel del agua", f"{h:.2f} m")
    c2.metric("Radio de la superficie", f"{r_agua:.2f} m")
    c3.metric("Volumen restante", f"{V:.2f} m³")
    c4.metric("Trabajo acumulado", f"{W / 1000:.2f} kJ")

    st.progress(float(np.clip(extraido / 100, 0, 1)))

    st.caption(
        f"Vaciado: {extraido:.1f}% | "
        f"Volumen extraído: {V_extraido:.2f} m³ | "
        f"Volumen restante: {V:.2f} m³ | "
        f"Llenado: {llenado:.1f}%"
    )

    # Modelo tridimensional
    st.subheader("Geometría 3D del reservorio")

    theta = np.linspace(0, 2 * np.pi, 90)
    radios = np.linspace(0, R, 40)
    T, S = np.meshgrid(theta, radios)

    X = S * np.cos(T)
    Y = S * np.sin(T)
    Z = (H / R**2) * S**2

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(111, projection="3d")

    ax.plot_surface(
        X, Y, Z,
        color="#A7ADB4",
        alpha=0.30,
        linewidth=0.25,
        edgecolor="gray"
    )

    if h > 0:
        radios_h = np.linspace(0, r_agua, 32)
        Th, Sh = np.meshgrid(theta, radios_h)

        Xh = Sh * np.cos(Th)
        Yh = Sh * np.sin(Th)
        Zh = (H / R**2) * Sh**2

        ax.plot_surface(
            Xh, Yh, Zh,
            color="#5B9BD5",
            alpha=0.48,
            linewidth=0
        )

        Tw, Sw = np.meshgrid(theta, radios_h)
        Xw = Sw * np.cos(Tw)
        Yw = Sw * np.sin(Tw)
        Zw = np.full_like(Xw, h)

        ax.plot_surface(
            Xw, Yw, Zw,
            color="#5B9BD5",
            alpha=0.70,
            linewidth=0
        )

        ax.plot(
            r_agua * np.cos(theta),
            r_agua * np.sin(theta),
            np.full_like(theta, h),
            color="#1F5D91",
            linewidth=2
        )

    # Borde superior
    ax.plot(
        R * np.cos(theta),
        R * np.sin(theta),
        np.full_like(theta, H),
        color="black",
        linewidth=2
    )

    # Referencia vertical
    x_ref = R * 1.12

    ax.plot(
        [x_ref, x_ref], [0, 0], [0, H],
        color="black",
        linewidth=1.5
    )

    ax.scatter(
        [x_ref], [0], [h],
        color="#1F5D91",
        s=40
    )

    # Estilo visual del modelo 3D
    fig.patch.set_facecolor("#F7FAFC")
    ax.set_facecolor("#F7FAFC")

    ax.set_title(
        f"Reservorio parabólico — nivel: {h:.2f} m",
        pad=16,
        fontsize=13,
        fontweight="bold"
    )

    ax.set_xlabel("X (m)", labelpad=8)
    ax.set_ylabel("Y (m)", labelpad=8)
    ax.set_zlabel("Altura (m)", labelpad=8)

    # Planos suaves y bordes discretos
    for pane in (ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane):
        pane.set_facecolor((0.91, 0.95, 0.98, 0.35))
        pane.set_edgecolor("#CBD5E1")

    # Cuadrícula y etiquetas
    ax.grid(
        True,
        linestyle=":",
        linewidth=0.6,
        alpha=0.35
    )
    ax.tick_params(axis="both", labelsize=8, pad=0)

    # Proporciones y perspectiva
    ax.set_xlim(-R, R * 1.4)
    ax.set_ylim(-R, R)
    ax.set_zlim(0, H * 1.25)
    ax.set_box_aspect((2.4 * R, 2 * R, 1.25 * H))
    ax.set_proj_type("ortho")
    ax.view_init(elev=25, azim=-55)

    st.pyplot(fig, width="stretch")
    plt.close(fig)

    # Gráficas de comportamiento
    st.subheader("Relaciones entre el nivel y los resultados")

    niveles = np.linspace(0, H, 250)
    volumenes = volumen_restante(niveles)
    trabajos = trabajo_acumulado(niveles) / 1000

    col_v, col_w = st.columns(2)

    with col_v:
        fig_v, ax_v = plt.subplots(figsize=(6, 4))

        ax_v.plot(niveles, volumenes)
        ax_v.scatter([h], [V], color="red", zorder=3)

        ax_v.set_title("Volumen restante")
        ax_v.set_xlabel("Nivel del agua h (m)")
        ax_v.set_ylabel("Volumen (m³)")
        ax_v.grid(True, alpha=0.3)

        st.pyplot(fig_v, width="stretch")
        plt.close(fig_v)

    with col_w:
        fig_w, ax_w = plt.subplots(figsize=(6, 4))

        ax_w.plot(niveles, trabajos)
        ax_w.scatter([h], [W / 1000], color="red", zorder=3)

        ax_w.set_title("Trabajo acumulado")
        ax_w.set_xlabel("Nivel actual h (m)")
        ax_w.set_ylabel("Trabajo (kJ)")
        ax_w.grid(True, alpha=0.3)

        st.pyplot(fig_w, width="stretch")
        plt.close(fig_w)
        
    # 7.1. Análisis matemático del estado actual

    st.subheader("Análisis matemático del estado actual")

    fraccion_altura = h / H
    fraccion_volumen = V / V_total
    fraccion_extraido = V_extraido / V_total

    with st.expander(
        "Interpretar los resultados matemáticamente",
        expanded=True
    ):
        st.markdown("### 1. Relación entre altura y volumen")

        st.latex(
            r"\frac{V(h)}{V_{\text{total}}}"
            r"=\left(\frac{h}{H}\right)^2"
        )

        st.write(
            f"El agua está al {100 * fraccion_altura:.1f}% "
            f"de la altura total."
        )

        st.write(
            f"Permanece el {100 * fraccion_volumen:.1f}% "
            f"del volumen original, equivalente a "
            f"{V:.2f} m³."
        )

        st.write(
            f"Se ha extraído el {100 * fraccion_extraido:.1f}% "
            f"del volumen, equivalente a "
            f"{V_extraido:.2f} m³."
        )

        st.markdown("### 2. Trabajo ideal de bombeo")

        st.latex(
            r"W(h)=\frac{\rho g\pi R^2}{H}"
            r"\left(\frac{H^3}{6}"
            r"-\frac{Hh^2}{2}+\frac{h^3}{3}\right)"
        )

        st.write(
            f"El trabajo ideal acumulado hasta el nivel actual "
            f"es de {W / 1000:.2f} kJ."
        )

        st.write(
            "A medida que baja el nivel, aumenta el trabajo "
            "acumulado porque se ha extraído una mayor cantidad "
            "de agua y se la ha elevado hasta el borde del "
            "reservorio."
        )

        st.markdown("### 3. Interpretación física")

        st.write(
            "El modelo supone densidad constante del agua, "
            "geometría parabólica ideal y ausencia de pérdidas "
            "hidráulicas y eléctricas. El trabajo calculado es "
            "energía mecánica ideal, no el consumo eléctrico "
            "real de una bomba."
        )

mostrar_reservorio()
# 8. Modelo y supuestos

with st.expander("Consultar el modelo matemático"):
    st.markdown("**Radio de la superficie del agua**")
    st.latex(r"r(h)=R\sqrt{\frac{h}{H}}")

    st.markdown("**Volumen restante**")
    st.latex(r"V(h)=\frac{\pi R^2 h^2}{2H}")

    st.markdown("**Trabajo acumulado**")
    st.latex(
        r"W(h)=\frac{\rho g\pi R^2}{H}"
        r"\left(\frac{H^3}{6}"
        r"-\frac{Hh^2}{2}+\frac{h^3}{3}\right)"
    )

    st.markdown(
        "Se supone una geometría parabólica ideal, densidad "
        "constante del agua y bombeo sin pérdidas hidráulicas. "
        "El trabajo es mecánico ideal; no representa el consumo "
        "eléctrico de una bomba real."
    )

st.caption(
    "Proyecto académico de Cálculo Integral. "
    "Dimensiones del modelo: radio 3 m y altura 2 m."
)

# ==========================================
# 9. DESCARGA DE RESULTADOS EN CSV
# ==========================================

def generar_csv_resultados():
    # 41 niveles entre 0 y H, separados por 0.05 m
    alturas = np.linspace(0.0, H, 41)

    salida = io.StringIO(newline="")
    escritor = csv.writer(salida, delimiter=";")

    # Encabezados de la tabla
    escritor.writerow([
        "Altura del agua h (m)",
        "Radio de la superficie (m)",
        "Volumen restante (m3)",
        "Llenado (%)",
        "Volumen extraido (m3)",
        "Trabajo acumulado (kJ)"
    ])

    # Calcular resultados para cada altura
    for altura in alturas:
        radio = float(radio_superficie(altura))
        volumen = float(volumen_restante(altura))
        llenado = float(porcentaje_lleno(altura))
        trabajo = float(trabajo_acumulado(altura))
        volumen_extraido = max(0.0, V_total - volumen)

        escritor.writerow([
            f"{altura:.2f}",
            f"{radio:.4f}",
            f"{volumen:.4f}",
            f"{llenado:.2f}",
            f"{volumen_extraido:.4f}",
            f"{trabajo / 1000:.4f}"
        ])

    # Facilitar la lectura de caracteres españoles en Excel
    return "\ufeff" + salida.getvalue()


st.subheader("Datos y exportación")

st.markdown(
    "Descarga los resultados matemáticos del reservorio "
    "para analizarlos en Excel o utilizarlos en el informe."
)

st.download_button(
    label="⬇ Descargar resultados en CSV",
    data=generar_csv_resultados(),
    file_name="resultados_reservorio_parabolico.csv",
    mime="text/csv",
    key="descargar_resultados_csv"
)
st.caption(
    "Proyecto académico de Cálculo Integral. "
    "Dimensiones del modelo: radio 3 m y altura 2 m."
)
