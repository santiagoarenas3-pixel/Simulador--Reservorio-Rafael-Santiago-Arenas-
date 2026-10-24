
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

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

    ax.set_title(f"Nivel actual: {h:.2f} m")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Altura (m)")

    ax.set_xlim(-R, R * 1.4)
    ax.set_ylim(-R, R)
    ax.set_zlim(0, H * 1.25)
    ax.set_box_aspect((2.4 * R, 2 * R, 1.25 * H))
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


st.caption(
    "Proyecto académico de Cálculo Integral. "
    "Dimensiones del modelo: radio 3 m y altura 2 m."
)
