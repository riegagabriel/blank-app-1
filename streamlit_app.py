import streamlit as st
import zipfile
import tempfile
import os
import pandas as pd
from streamlit.components.v1 import html as st_html

st.set_page_config(
    page_title="Bienestar Docente — Extorsión cerca de IIEE",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem; font-weight: 700; }
[data-testid="stMetricLabel"] { font-size: 0.8rem; color: #666; }
.section-title {
    font-size: 1.1rem; font-weight: 700; color: #1a4a7a;
    border-left: 4px solid #1a4a7a; padding-left: 10px; margin: 16px 0 8px 0;
}
.fuente { font-size: 0.72rem; color: #888; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Carga del XLSX (cacheada) ─────────────────────────────────────────────────
_OUT_DIR  = "OUTPUTS_DASHBOARD"
XLSX_FILE = os.path.join(_OUT_DIR, "dashboard_bienestar_docente.xlsx")
ZIP_FILE  = os.path.join(_OUT_DIR, "mapa_iiee_extorsion.zip")

@st.cache_data(show_spinner="Cargando datos del dashboard...")
def load_xlsx(path):
    return pd.read_excel(path, sheet_name=None, engine="openpyxl")

sheets = {}
if os.path.exists(XLSX_FILE):
    sheets = load_xlsx(XLSX_FILE)
else:
    st.warning(f"No se encontró `{XLSX_FILE}`. Ejecuta la Celda 16 del notebook primero.")

def get(sheet, fallback=pd.DataFrame()):
    return sheets.get(sheet, fallback)

kpi = get("Resumen_KPI")
def kv(nombre):
    row = kpi[kpi["Indicador"].str.strip() == nombre]
    return row["Valor"].iloc[0] if not row.empty else "—"

# ── Header ────────────────────────────────────────────────────────────────────
st.title("Cercanía de denuncias de extorsión a instituciones educativas")
st.caption("Lima y Callao · 2025–2026 · Fuentes: MINEDU (Padrón Web) y PNP / SIDPOL-DGIS")

# ── KPIs fila 1: IIEE ─────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Instituciones Educativas (MINEDU — Padrón Web 29/04/2026)</div>',
            unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
c1.metric("IIEE activas en Lima y Callao", f"{int(kv('IIEE activas en Lima y Callao')):,}")
c2.metric("Docentes censados 2025",        f"{int(kv('Docentes censados 2025 (total)')):,}")
c3.metric("Alumnos censados 2025",         f"{int(kv('Alumnos censados 2025 (total)')):,}")

# ── KPIs fila 2: Delitos ──────────────────────────────────────────────────────
st.markdown('<div class="section-title">Denuncias de extorsión (PNP / SIDPOL-DGIS · 26/05/2026)</div>',
            unsafe_allow_html=True)
c4, c5, c6 = st.columns(3)
c4.metric("Total denuncias (Lima y Callao)", f"{int(kv('Denuncias de extorsión (total)')):,}")
c5.metric("Extorsión simple",               f"{int(kv('— Extorsión simple')):,}")
c6.metric("Extorsión agravada",             f"{int(kv('— Extorsión agravada')):,}")

# ── KPIs fila 3: Exposición ───────────────────────────────────────────────────
st.markdown('<div class="section-title">Exposición del sistema educativo (radio ≤ 100 m)</div>',
            unsafe_allow_html=True)
c7, c8, c9, c10 = st.columns(4)
c7.metric("Denuncias cerca de IIEE",  f"{int(kv('Denuncias ≤ 100 m de IIEE')):,}",
          delta=f"{float(kv('% denuncias cerca de IIEE'))}% del total",
          delta_color="inverse")
c8.metric("IIEE afectadas",           f"{int(kv('IIEE con ≥ 1 denuncia en entorno')):,}",
          delta=f"{float(kv('% IIEE afectadas'))}% del total",
          delta_color="inverse")
c9.metric("Docentes expuestos",       f"{int(kv('Docentes en IIEE afectadas')):,}")
c10.metric("Alumnos expuestos",       f"{int(kv('Alumnos en IIEE afectadas')):,}")

st.markdown("---")

# ── Pestañas de análisis + mapa ────────────────────────────────────────────────
tab_mapa, tab_tiempo, tab_distritos, tab_iiee, tab_turno, tab_gestion = st.tabs([
    "🗺️ Mapa interactivo",
    "📅 Línea de tiempo",
    "📍 Distritos",
    "🏫 IIEE más afectadas",
    "🕐 Por turno",
    "🏛️ Por tipo de gestión",
])

# ── Tab 1: Mapa ───────────────────────────────────────────────────────────────
with tab_mapa:
    st.markdown("Clusters de denuncias y marcadores de IIEE. Usa el panel de capas (arriba a la derecha) "
                "para activar o desactivar cada capa.")

    if os.path.exists(ZIP_FILE):
        with tempfile.TemporaryDirectory() as tmp:
            with zipfile.ZipFile(ZIP_FILE, "r") as z:
                z.extractall(tmp)
            html_file = None
            for root, _, files in os.walk(tmp):
                for f in files:
                    if f.endswith(".html"):
                        html_file = os.path.join(root, f)
                        break
            if html_file:
                with open(html_file, "r", encoding="utf-8") as fh:
                    source = fh.read()
                st_html(source, height=680, scrolling=False)
            else:
                st.error("No se encontró un archivo HTML dentro del ZIP.")
    else:
        st.info(f"Sube `{ZIP_FILE}` al repositorio para visualizar el mapa.")
        st.markdown(
            "**Cómo generar el ZIP:**\n"
            "```bash\n"
            "zip mapa_iiee_extorsion.zip mapa_bienestar_cluster.html\n"
            "```"
        )

# ── Tab 2: Línea de tiempo ────────────────────────────────────────────────────
with tab_tiempo:
    df_t = get("Linea_Tiempo")
    if not df_t.empty:
        st.markdown('<div class="section-title">Denuncias de extorsión por mes</div>',
                    unsafe_allow_html=True)
        periodo_col = df_t.columns[0]
        df_plot = df_t.set_index(periodo_col)
        st.bar_chart(df_plot[["EXTORSION", "EXTORSION AGRAVADA"]] if "EXTORSION" in df_plot.columns
                     else df_plot.drop(columns=["Total"], errors="ignore"))
        st.dataframe(df_t, use_container_width=True, hide_index=True)
        st.markdown('<div class="fuente">Fuente: PNP / SIDPOL-DGIS · fecha_hora_hecho convertida desde timestamp Unix (ms)</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Sin datos de línea de tiempo.")

# ── Tab 3: Distritos ──────────────────────────────────────────────────────────
with tab_distritos:
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-title">Top 20 distritos — todas las denuncias</div>',
                    unsafe_allow_html=True)
        df_da = get("Top_Distritos").head(20)
        if not df_da.empty:
            st.bar_chart(df_da.set_index("Distrito")["Total denuncias"])
            st.dataframe(df_da, use_container_width=True, hide_index=True)

    with col_b:
        st.markdown(f'<div class="section-title">Top 20 distritos — denuncias ≤ 100 m de IIEE</div>',
                    unsafe_allow_html=True)
        df_dn = get("Distritos_IIEE").head(20)
        if not df_dn.empty:
            st.bar_chart(df_dn.set_index("Distrito")["Denuncias ≤100m IIEE"])
            st.dataframe(df_dn, use_container_width=True, hide_index=True)

    st.markdown('<div class="fuente">Fuente: PNP / SIDPOL-DGIS + MINEDU · Análisis espacial radio 100 m</div>',
                unsafe_allow_html=True)

# ── Tab 4: Top IIEE ───────────────────────────────────────────────────────────
with tab_iiee:
    st.markdown('<div class="section-title">Instituciones educativas con más denuncias en su entorno inmediato (≤ 100 m)</div>',
                unsafe_allow_html=True)
    df_ti = get("Top_IIEE")
    if not df_ti.empty:
        st.bar_chart(df_ti.head(15).set_index("IIEE")["Denuncias cercanas"])
        st.info(
            "**Lectura:** Cada barra indica cuántas denuncias de extorsión fueron registradas "
            "dentro de un radio de 100 m alrededor de esa institución educativa. "
            "Una misma denuncia puede contabilizarse para más de una IIEE si varias se encuentran "
            "dentro de ese radio. El ranking refleja exposición geográfica directa, no atribución exclusiva."
        )
        st.dataframe(df_ti, use_container_width=True, hide_index=True)
        st.markdown('<div class="fuente">Fuente: MINEDU + PNP / SIDPOL-DGIS · buffer circular 100 m · geopandas.sjoin predicate="within"</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Sin datos.")

# ── Tab 5: Por turno ──────────────────────────────────────────────────────────
with tab_turno:
    st.markdown('<div class="section-title">Denuncias de extorsión según turno del hecho</div>',
                unsafe_allow_html=True)
    df_tu = get("Por_Turno")
    if not df_tu.empty:
        st.bar_chart(df_tu.set_index("Turno del hecho")["Total"])
        st.dataframe(df_tu, use_container_width=True, hide_index=True)
        st.info(
            "**Lectura:** El turno del hecho indica el momento del día en que se registró la denuncia. "
            "Un pico en turno mañana/tarde es relevante porque coincide con el horario escolar, "
            "aumentando el riesgo percibido por docentes y alumnos."
        )
        st.markdown('<div class="fuente">Fuente: PNP / SIDPOL-DGIS · campo turno_hecho</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Sin datos.")

# ── Tab 6: Por tipo de gestión ────────────────────────────────────────────────
with tab_gestion:
    st.markdown('<div class="section-title">Exposición según tipo de gestión de la IIEE</div>',
                unsafe_allow_html=True)
    df_g = get("Por_Gestion")
    if not df_g.empty:
        st.bar_chart(df_g.set_index("Tipo de gestión")[["IIEE afectadas", "Total IIEE"]])
        st.dataframe(df_g, use_container_width=True, hide_index=True)
        st.info(
            "**Lectura:** Compara cuántas IIEE de cada tipo de gestión (pública, privada, etc.) "
            "tienen al menos una denuncia de extorsión registrada a ≤ 100 m. "
            "El % de IIEE afectadas permite comparar la exposición relativa entre tipos."
        )
        st.markdown('<div class="fuente">Fuente: MINEDU + análisis espacial</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Sin datos.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "**Fuentes:** MINEDU — Padrón Web de Instituciones Educativas (actualización 29/04/2026) · "
    "PNP / SIDPOL-DGIS — Registro de delitos policiales 2025–2026 (corte 26/05/2026) · "
    "IGN Perú — Límites político-administrativos. "
    "**Metodología:** Análisis de proximidad espacial con buffer circular de 100 m por IIEE (`geopandas.sjoin`, predicate='within') en proyección UTM-18S. "
    "Una denuncia se contabiliza para todas las IIEE cuyo radio de 100 m la contenga. "
    "Los datos de denuncias no representan la totalidad de los hechos delictivos (cifra negra no contabilizada)."
)
