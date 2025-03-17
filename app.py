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

# Cargar nuevamente los datos sin caché para verificar actualización
df_cursos = pd.read_csv(url)  # Sin @st.cache_data

st.write("Columnas disponibles en la hoja de cálculo:", df_cursos.columns.tolist())

# Mostrar los primeros registros para verificar
st.subheader("Lista de cursos disponibles")
st.dataframe(df_cursos[["Código", "Nombre del Curso o Diplomado", "Cohorte", "Fecha", "Duración","Validación"]])

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

# Campo de entrada para la contraseña del estudiante
password_input = st.text_input("🔑 Ingrese su contraseña", type="password")

# Filtrar la hoja de estudiantes por el código del curso seleccionado
df_curso_estudiantes = df_estudiantes[df_estudiantes["Código"] == codigo_curso]

# Botón para validar
if st.button("Validar contraseña"):
    if password_input:
        # Buscar si la contraseña ingresada coincide con alguna en la hoja de cálculo
        estudiante = df_curso_estudiantes[df_curso_estudiantes["Contraseña"] == password_input]

        if not estudiante.empty:
            nombre_estudiante = estudiante["Nombre"].values[0]
            documento_estudiante = estudiante["Documento"].values[0]

            st.success(f"✅ Acceso concedido: {nombre_estudiante}")
            st.write(f"📄 Documento: `{documento_estudiante}`")
        else:
            st.error("❌ Contraseña incorrecta o estudiante no registrado en este curso.")
    else:
        st.warning("⚠️ Por favor, ingrese su contraseña.")

import qrcode
from io import BytesIO

# Obtener el enlace de validación para el curso seleccionado
url_validacion = df_cursos[df_cursos["Código"] == codigo_curso]["Validación"].values[0]

if "http" in url_validacion:  # Verificar que sea un enlace válido
    # Generar el código QR
    qr = qrcode.make(url_validacion)
    qr_img = BytesIO()
    qr.save(qr_img, format="PNG")
    qr_img.seek(0)

    # Mostrar el código QR en Streamlit
    st.subheader("Código QR de validación")
    st.image(qr_img, caption="Escanéalo para verificar tu certificado", use_container_width=True)
else:
    st.warning("⚠️ Este curso no tiene un enlace de validación asignado.")

import requests
from pptx import Presentation

# URL pública del archivo PPTX en GitHub
url_plantilla = "https://raw.githubusercontent.com/ciec-uptc/Certificados/main/Plantilla%20base.pptx"

def load_template():
    response = requests.get(url_plantilla)
    if response.status_code == 200:
        with open("Plantilla_base.pptx", "wb") as f:
            f.write(response.content)
        return Presentation("Plantilla_base.pptx")
    else:
        st.error("❌ No se pudo descargar la plantilla del certificado.")
        return None

# Cargar la plantilla sin almacenamiento en caché
plantilla_pptx = load_template()
