import streamlit as st
import pandas as pd

# Configuración básica de la aplicación
st.set_page_config(page_title="Generador de Certificados", layout="centered")

st.title("🎓 Generador de Certificados")

st.write("Bienvenido al generador de certificados. Ingrese la información requerida para generar su diploma.")

# URL pública de Google Sheets en formato CSV
url = "https://docs.google.com/spreadsheets/d/1XSzJ_cZWr7co6c_86CCzfWNgEKwxB8Wn5NBt4PpNAUc/gviz/tq?tqx=out:csv"

# Cargar la hoja de cálculo como un DataFrame
@st.cache_data
def load_data():
    return pd.read_csv(url)

df_cursos = load_data()

# Mostrar los primeros registros para verificar
st.subheader("Lista de cursos disponibles")
st.dataframe(df_cursos)

# Seleccionar el curso desde un selectbox
curso_seleccionado = st.selectbox("📚 Seleccione un curso o diplomado", df_cursos["Nombre del Curso o Diplomado"].unique())

# Obtener el código del curso seleccionado
codigo_curso = df_cursos[df_cursos["Nombre del Curso o Diplomado"] == curso_seleccionado]["Código"].values[0]

st.write(f"Has seleccionado el curso: **{curso_seleccionado}**")
st.write(f"Código del curso: `{codigo_curso}`")

# URL pública de la hoja de cálculo de estudiantes en formato CSV
url_estudiantes = "https://docs.google.com/spreadsheets/d/1prUt0i0EWolsX_LuGl_yKzXPUWmy6CzCxi28zued5BA/gviz/tq?tqx=out:csv"

# Cargar los datos de los estudiantes
@st.cache_data
def load_students():
    return pd.read_csv(url_estudiantes)

df_estudiantes = load_students()

