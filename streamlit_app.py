import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="UFC Professional Dashboard",
    page_icon="🥊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Styling for Professional Look ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #ff4b4b;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    h2, h3 {
        color: #fafafa;
    }
    .stMetric {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('ufc_cleaned.csv')
        return df
    except FileNotFoundError:
        st.error("Archivo 'ufc_cleaned.csv' no encontrado. Por favor, ejecuta el script 'clean_data.py' primero.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

# --- Sidebar Filters ---
st.sidebar.title("🎛️ Filtros Globales")
st.sidebar.markdown("---")

# Year Filter
years = sorted(df['Year'].unique())
min_year, max_year = st.sidebar.slider("📅 Rango de Años", int(min(years)), int(max(years)), (2010, int(max(years))))
df_filtered = df[(df['Year'] >= min_year) & (df['Year'] <= max_year)]

# Gender Filter
genders = df_filtered['Gender'].unique()
selected_genders = st.sidebar.multiselect("🚻 Género", options=genders, default=genders)
df_filtered = df_filtered[df_filtered['Gender'].isin(selected_genders)]

# Weight Class Filter
weight_classes = sorted(df_filtered['WeightClass'].astype(str).unique())
selected_classes = st.sidebar.multiselect("⚖️ Categoría de Peso", options=weight_classes, default=weight_classes)
df_filtered = df_filtered[df_filtered['WeightClass'].isin(selected_classes)]

st.sidebar.markdown("### 📊 Dataset Info")
st.sidebar.info(f"Mostrando {len(df_filtered)} peleas.")

# --- Main Dashboard ---
st.title("🥊 Análisis de Rendimiento y Mercado UFC")
st.markdown("### Explorando las dimensiones Física, Estratégica y de Mercado de los ganadores.")
st.markdown("---")

# KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Peleas", len(df_filtered))
with col2:
    ko_rate = len(df_filtered[df_filtered['Finish'].str.contains('KO', na=False)]) / len(df_filtered) * 100
    st.metric("% KO/TKO", f"{ko_rate:.1f}%")
with col3:
    sub_rate = len(df_filtered[df_filtered['Finish'].str.contains('SUB', na=False)]) / len(df_filtered) * 100
    st.metric("% Sumisiones", f"{sub_rate:.1f}%")
with col4:
    fav_win_rate = len(df_filtered[df_filtered['BettingResult'] == 'Favorite']) / len(df_filtered[df_filtered['BettingResult'].isin(['Favorite', 'Underdog'])]) * 100
    st.metric("% Victorias Favorito", f"{fav_win_rate:.1f}%")

st.markdown("---")

# Tabs for Dimensions
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📏 Dimensión Física", "🧠 Dimensión Estratégica", "💰 Dimensión Mercado", "🕰️ Factor Edad", "🏁 Momento Finalización"])

# --- Tab 1: Dimensión Física ---
with tab1:
    st.header("1. ¿El tamaño importa?")
    st.markdown("Distribución de atributos físicos de los ganadores por categoría de peso.")
    
    physical_metric = st.radio("Selecciona la métrica:", ["Altura (cm)", "Alcance (cm)"], horizontal=True)
    metric_col = 'WinnerHeight' if physical_metric == "Altura (cm)" else 'WinnerReach'
    
    # Definir el orden lógico de las categorías de peso
    weight_order = [
        "Women's Strawweight", "Women's Flyweight", "Women's Bantamweight", "Women's Featherweight",
        "Flyweight", "Bantamweight", "Featherweight", "Lightweight", "Welterweight", 
        "Middleweight", "Light Heavyweight", "Heavyweight", "Catch Weight"
    ]
    
    # Filtrar solo las categorías presentes y ordenarlas
    available_classes = [w for w in weight_order if w in df_filtered['WeightClass'].unique()]
    
    # Boxplot Mejorado
    fig_phys = px.box(
        df_filtered, 
        x='WeightClass', 
        y=metric_col, 
        color='Gender',
        title=f"Distribución de {physical_metric} en Ganadores (Ordenado por Peso)",
        template="plotly_dark",
        points="outliers", # Keep outliers clean
        category_orders={"WeightClass": available_classes},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_phys.update_layout(
        xaxis_title="Categoría de Peso", 
        yaxis_title=physical_metric, 
        height=600,
        xaxis={'categoryorder':'array', 'categoryarray': available_classes}
    )
    st.plotly_chart(fig_phys, width='stretch')
    
    st.markdown(f"> **Mejora Visual:** Ahora las categorías están ordenadas por peso ascendente para facilitar la comparación de escalas.")

# --- Tab 2: Dimensión Estratégica ---
with tab2:
    st.header("2. Estilos de Victoria: ¿Volumen vs Control?")
    st.markdown("Mapeo de ganadores basado en sus promedios históricos de golpeo y derribo.")
    
    fig_strat = px.scatter(
        df_filtered,
        x='WinnerAvgStrikes',
        y='WinnerAvgTD',
        color='Finish',
        hover_data=['Date', 'WeightClass'],
        title="Estilo del Ganador: Golpes Significativos vs Derribos Promedio",
        labels={'WinnerAvgStrikes': 'Golpes Significativos (Promedio por 15m)', 'WinnerAvgTD': 'Derribos (Promedio por 15m)'},
        template="plotly_dark",
        color_discrete_map={
            'KO/TKO': '#FF4B4B', 
            'SUB': '#FFA500', 
            'U-DEC': '#00CC96', 
            'S-DEC': '#AB63FA',
            'M-DEC': '#19D3F3'
        },
        height=700
    )
    fig_strat.update_traces(marker=dict(size=8, opacity=0.7))
    st.plotly_chart(fig_strat, width='stretch')

# --- Tab 3: Dimensión Mercado ---
with tab3:
    st.header("3. Eficiencia del Mercado de Apuestas")
    st.markdown("¿Con qué frecuencia ganan los favoritos frente a las sorpresas (Underdogs)?")
    
    betting_counts = df_filtered['BettingResult'].value_counts(normalize=True).reset_index()
    betting_counts.columns = ['Resultado', 'Porcentaje']
    betting_counts['Porcentaje'] = betting_counts['Porcentaje'] * 100
    betting_counts = betting_counts[betting_counts['Resultado'].isin(['Favorite', 'Underdog', 'PickEm'])]
    
    fig_mkt = px.bar(
        betting_counts,
        x='Resultado',
        y='Porcentaje',
        color='Resultado',
        text_auto='.1f',
        title="Frecuencia de Victoria: Favoritos vs Underdogs",
        template="plotly_dark",
        color_discrete_map={'Favorite': '#00CC96', 'Underdog': '#FF4B4B', 'PickEm': '#636EFA'}
    )
    fig_mkt.update_layout(yaxis_title="Porcentaje de Victorias (%)", height=500)
    st.plotly_chart(fig_mkt, width='stretch')
    
    st.subheader("Evolución Temporal de la Eficiencia")
    df_yearly = df_filtered.groupby('Year')['BettingResult'].value_counts(normalize=True).unstack().fillna(0)
    if 'Favorite' in df_yearly.columns:
        df_yearly['FavoritePct'] = df_yearly['Favorite'] * 100
        fig_trend = px.line(
            df_yearly, 
            y='FavoritePct', 
            markers=True,
            title="Porcentaje de Victorias de Favoritos por Año",
            template="plotly_dark",
            labels={'FavoritePct': '% Victorias Favorito', 'Year': 'Año'}
        )
        fig_trend.update_traces(line_color='#00CC96')
        st.plotly_chart(fig_trend, width='stretch')

# --- Tab 4: Factor Edad ---
with tab4:
    st.header("4. Juventud vs Experiencia")
    st.markdown("¿La edad es solo un número? Analizamos la distribución de edad de los campeones.")

    col_age1, col_age2 = st.columns(2)
    
    with col_age1:
        # Histograma de Edad del Ganador
        fig_age_dist = px.histogram(
            df_filtered, 
            x="WinnerAge", 
            nbins=20, 
            title="Distribución de Edad de los Ganadores",
            template="plotly_dark",
            color_discrete_sequence=['#AB63FA']
        )
        fig_age_dist.update_layout(bargap=0.1, xaxis_title="Edad del Ganador (Años)")
        st.plotly_chart(fig_age_dist, width='stretch')

    with col_age2:
        # Edad vs Diferencia de Edad
        # ¿Ganan más cuando son más jóvenes que el oponente?
        # Aquí 'WinnerAgeDiff' es (AgeWinner - AgeLoser). Si es negativo, el ganador es más joven.
        
        fig_age_diff = px.histogram(
            df_filtered,
            x="WinnerAgeDiff",
            nbins=30,
            title="Diferencia de Edad (Ganador - Perdedor)",
            template="plotly_dark",
            color_discrete_sequence=['#FFA15A']
        )
        fig_age_diff.update_layout(
            xaxis_title="Diferencia de Edad (Años)",
            bargap=0.1,
            shapes=[dict(type="line", x0=0, x1=0, y0=0, y1=1, yref="paper", line=dict(color="white", dash="dash"))]
        )
        st.plotly_chart(fig_age_diff, width='stretch')
        st.caption("Valores negativos (izq) indican que el Ganador era MÁS JOVEN que el perdedor.")

# --- Tab 5: Momento Finalización ---
with tab5:
    st.header("5. ¿Cuándo terminan las peleas?")
    st.markdown("Análisis del asalto (round) de finalización según el método de victoria.")
    
    # Filter only finishes (not Decisions)
    finishes = df_filtered[~df_filtered['Finish'].str.contains('DEC', na=False)]
    
    if not finishes.empty:
        fig_rounds = px.histogram(
            finishes,
            x="FinishRound",
            color="Finish",
            barmode="group",
            title="Distribución de Finalizaciones por Asalto (Solo KO/Sumisión)",
            template="plotly_dark",
            labels={'FinishRound': 'Asalto de Finalización'},
            category_orders={"Finish": ["KO/TKO", "SUB", "DQ"]}
        )
        fig_rounds.update_layout(xaxis=dict(tickmode='linear', tick0=1, dtick=1))
        st.plotly_chart(fig_rounds, width='stretch')
    else:
        st.info("No hay suficientes datos de finalizaciones para el filtro seleccionado.")
    
