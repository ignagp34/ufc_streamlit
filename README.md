# 🥊 UFC Professional Dashboard

Este proyecto visualiza datos históricos de la UFC para analizar tendencias clave en torno a atributos físicos, estrategias de combate y eficiencia del mercado de apuestas.

## 🚀 Instalación y Uso

1.  **Clonar este repositorio:**
    ```bash
    git clone <tu-repositorio>
    cd <tu-carpeta>
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Procesar datos (opcional si ya tienes ufc_cleaned.csv):**
    Coloca tu archivo `ufc-master.csv` en la raíz y ejecuta:
    ```bash
    python clean_data.py
    ```

4.  **Ejecutar la App:**
    ```bash
    streamlit run streamlit_app.py
    ```

## 📊 Estructura

*   `streamlit_app.py`: Aplicación principal en Streamlit.
*   `clean_data.py`: Script ETL para limpiar y preparar los datos.
*   `ufc-master.csv`: Dataset crudo (no incluido en repo por tamaño, descárgalo de fuentes públicas como Kaggle).
*   `ufc_cleaned.csv`: Dataset procesado utilizado por la app.

## 📈 Funcionalidades
*   **Dimensión Física**: Análisis de altura y alcance.
*   **Dimensión Estratégica**: Clustering de estilos (Strikers vs Grapplers).
*   **Dimensión Mercado**: Rentabilidad de favoritos vs underdogs.
*   **Factor Edad**: Impacto de la juventud en el resultado.
*   **Análisis de Finalización**: Distribución de rondas de finish.
