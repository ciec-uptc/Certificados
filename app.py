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

# URL del archivo de Google Slides en formato PowerPoint (.pptx)
url_plantilla = "https://docs.google.com/presentation/d/1Ta3jm56rKw1Q6i4cPQ-Sj0WzrCyveLNj/export/pptx"

# Descargar la plantilla
st.subheader("Descargando plantilla de certificado...")
response = requests.get(url_plantilla)

if response.status_code == 200:
    with open("plantilla_certificado.pptx", "wb") as f:
        f.write(response.content)
    st.success("✅ Plantilla descargada correctamente.")
else:
    st.error("❌ No se pudo descargar la plantilla.")

from pptx import Presentation
from pptx.util import Inches
from io import BytesIO

# Cargar la plantilla
prs = Presentation("plantilla_certificado.pptx")

# Buscar y reemplazar texto en la diapositiva
for slide in prs.slides:
    for shape in slide.shapes:
        if hasattr(shape, "text"):
            if "{NOMBRE_ESTUDIANTE}" in shape.text:
                shape.text = shape.text.replace("{NOMBRE_ESTUDIANTE}", nombre_estudiante)
            if "{DOCUMENTO}" in shape.text:
                shape.text = shape.text.replace("{DOCUMENTO}", documento_estudiante)
            if "{NOMBRE_CURSO}" in shape.text:
                shape.text = shape.text.replace("{NOMBRE_CURSO}", curso_seleccionado)
            if "{FECHA_CURSO}" in shape.text:
                shape.text = shape.text.replace("{FECHA_CURSO}", df_cursos[df_cursos["Código"] == codigo_curso]["Fecha"].values[0])
            if "{DURACION}" in shape.text:
                shape.text = shape.text.replace("{DURACION}", df_cursos[df_cursos["Código"] == codigo_curso]["Duración"].values[0])
            if "{DOCENTE}" in shape.text:
                shape.text = shape.text.replace("{DOCENTE}", df_cursos[df_cursos["Código"] == codigo_curso]["Docente"].values[0])

# Insertar el código QR en la plantilla
slide = prs.slides[0]  # Suponiendo que la primera diapositiva es la del certificado
left = Inches(6)  # Ajustar posición
top = Inches(4)
pic = slide.shapes.add_picture(qr_img, left, top, width=Inches(2), height=Inches(2))

# Guardar el nuevo certificado como archivo
output = BytesIO()
prs.save(output)
output.seek(0)

# Permitir descarga del certificado en Streamlit
st.subheader("🎉 ¡Certificado Generado!")
st.download_button(label="📥 Descargar Certificado",
                   data=output,
                   file_name=f"Certificado_{nombre_estudiante}.pptx",
                   mime="application/vnd.openxmlformats-officedocument.presentationml.presentation")
