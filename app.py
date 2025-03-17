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

# Definir variables globales para que estén disponibles en toda la app
estudiante = pd.DataFrame()
nombre_estudiante = ""
documento_estudiante = ""

# Inicializar valores en session_state si no existen
if "nombre_estudiante" not in st.session_state:
    st.session_state.nombre_estudiante = ""
    st.session_state.documento_estudiante = ""
    st.session_state.validado = False

# Campo de entrada para la contraseña del estudiante
password_input = st.text_input("🔑 Ingrese su contraseña", type="password")

# Filtrar la hoja de estudiantes por el código del curso seleccionado
df_curso_estudiantes = df_estudiantes[df_estudiantes["Código"] == codigo_curso]

# Botón para validar
if st.button("Validar contraseña"):
    if password_input:
        estudiante = df_curso_estudiantes[df_curso_estudiantes["Contraseña"] == password_input]

        if not estudiante.empty:
            # Guardar los datos en session_state para que se conserven entre interacciones
            st.session_state.nombre_estudiante = estudiante["Nombre"].values[0]
            st.session_state.documento_estudiante = estudiante["Documento"].values[0]
            st.session_state.validado = True

            st.success(f"✅ Acceso concedido: {st.session_state.nombre_estudiante}")
            st.write(f"📄 Documento: `{st.session_state.documento_estudiante}`")
        else:
            st.session_state.validado = False
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

import requests
from pptx import Presentation
from pptx.util import Inches
from io import BytesIO

# URL de la plantilla base en GitHub (raw)
url_plantilla = "https://github.com/ciec-uptc/Certificados/blob/main/Plantilla%20base.pptx?raw=true"

# Descargar la plantilla base desde GitHub
@st.cache_data
def cargar_plantilla():
    response = requests.get(url_plantilla)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        st.error("❌ Error al cargar la plantilla de PowerPoint.")
        return None

plantilla_stream = cargar_plantilla()

from pptx.dml.color import RGBColor

#Generar certificado
def generar_certificado(nombre, documento, curso, duracion, fecha, qr_img):
    if plantilla_stream:
        prs = Presentation(plantilla_stream)  # Cargar la plantilla en memoria

        # Asegurar que los valores no sean NaN ni None
        nombre = str(nombre) if pd.notna(nombre) else ""
        documento = str(documento) if pd.notna(documento) else ""
        curso = str(curso) if pd.notna(curso) else ""
        duracion = str(duracion) if pd.notna(duracion) else ""
        fecha = str(fecha) if pd.notna(fecha) else ""

        # Modificar los textos sin perder formato
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame and shape.text_frame.text:
                    text = shape.text_frame.text.strip()

                    for para in shape.text_frame.paragraphs:
                        for run in para.runs:  # Mantiene el formato original
                            if "Nombres y Apellidos" in text:
                                run.text = nombre
                            elif "Documento" in text:
                                run.text = documento
                            elif "Título" in text:
                                run.text = curso
                            elif "Dur" in text:
                                run.text = duracion
                            elif "Fecha" in text:
                                run.text = fecha

        # Insertar el código QR reemplazando el cuadro de texto "QR AQUÍ"
        for slide in prs.slides:
            for shape in slide.shapes:
                if shape.has_text_frame and "QR AQUÍ" in shape.text_frame.text:
                    left, top, width, height = shape.left, shape.top, shape.width, shape.height

                    # Eliminar el cuadro de texto original
                    slide.shapes._spTree.remove(shape._element)

                    # Guardar el QR como imagen
                    qr_stream = BytesIO()
                    qr_img.save(qr_stream, format="PNG")
                    qr_stream.seek(0)

                    # Insertar el QR en la misma posición
                    slide.shapes.add_picture(qr_stream, left, top, width, height)
                    break  # Detener la búsqueda después de insertar el QR

        # Guardar el certificado como un archivo en memoria
        certificado_stream = BytesIO()
        prs.save(certificado_stream)
        certificado_stream.seek(0)
        
        return certificado_stream
    else:
        st.error("❌ No se pudo generar el certificado.")
        return None

import requests
import json
import time

# API Key de CloudConvert
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiY2ZjZDIyZjRlYjE3MTFiZDEwODk5MDY4M2JjNjM5MDFlNTViMjU0ZTlmYmEyYzg3YWVkMDMzZDYwMGZkM2Y2OWJlZjg3MjczMmM5NTI4N2QiLCJpYXQiOjE3NDIwODc3MjYuNTQ1MTg3LCJuYmYiOjE3NDIwODc3MjYuNTQ1MTg5LCJleHAiOjQ4OTc3NjEzMjYuNTQwNTksInN1YiI6IjcxMzQ2NDY4Iiwic2NvcGVzIjpbInRhc2sucmVhZCIsInRhc2sud3JpdGUiXX0.mBzno6enxy7JHNpNm3Q5iP5lN4uqYrokU_avbVg0e0AIAtvqNK8oILKaBf9iLNZWtguqaY5sUfHTQe5-taduwn5JoNDqngUKOr6kPrk2F0cEnuGfHJGZ2Q8tKbgZ_cSbvbm-_ge1Mb1f0P0HZDIejq5alD-YTBn_hJ1aA8qe7jy35cGoE70FlU_dzZ8rh-kExU_RBb10hHYjVBWjOqlJPKlYCr89mrE_Sb2sybcYxebE5-bFHsds5BMPAiHr5mDBeUyQOyanwPgn1IocNQWNznmF4mWSuqXm6WftR-9WNjBpcVjSYENwpj8yLPwqNolJC1nteD4d_2PqTPmsZo6xSxL2_SPdziWY7EGpumAcNrEyYc2ijwDBFmQPGv3z8-7Gt5zpARwKbeg5f_C1nJtlhhpfgzoRMsX24WApJYngSYuoj9MjGEyjVwg-3VJFY1idhbXFAfYUUbxsstdvJc6j04aebAz6UbwBIoXXbuUOuO50D7MEox4QosIs6KVYPh3cVTzesbYBfQSqofqOxH0ogS6uxrN8578ihGIQUu2opITkUZTsi4Ff8AAwesGwdytX52BGGdSsBWHbftxuxwqQK3qnuVS3dm5aKBctn0Jw6uwis9W1hnCVfWCaiaZgypLndaKGwuFm2JcmL7AD0azH5w6zdjkXQZEUIlHJXB_ozIE"

def pptx_a_pdf(certificado_pptx):
    """Convierte un archivo PPTX a PDF usando CloudConvert API y devuelve el PDF en memoria."""
    
    # 🔹 Encabezados para la API
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    st.info("📤 Subiendo archivo a CloudConvert...")

    # 🔹 Paso 1: Crear una tarea de importación (subida de archivo)
    upload_task_response = requests.post("https://api.cloudconvert.com/v2/import/upload", headers=headers)

    if upload_task_response.status_code != 201:
        st.error(f"❌ Error al crear la tarea de importación: {upload_task_response.text}")
        return None

    upload_task = upload_task_response.json()
    st.success("✅ Tarea de importación creada con éxito.")

    if "data" not in upload_task:
        st.error("❌ No se recibió 'data' en la respuesta de importación.")
        return None

    upload_url = upload_task["data"]["result"]["form"]["url"]
    parameters = upload_task["data"]["result"]["form"]["parameters"]
    import_task_id = upload_task["data"]["id"]

    # 🔹 Paso 2: Subir el archivo PPTX a CloudConvert
    files = {"file": certificado_pptx.getvalue()}
    st.info("📤 Subiendo archivo PPTX...")
    upload_response = requests.post(upload_url, data=parameters, files=files)

    if upload_response.status_code != 201:
        st.error(f"❌ Error al subir el archivo: {upload_response.text}")
        return None
    else:
        st.success("✅ Archivo PPTX subido exitosamente.")

    # 🔹 Paso 3: Crear la tarea de conversión a PDF
    st.info("🔄 Creando tarea de conversión en CloudConvert...")
    convert_task_response = requests.post(
        "https://api.cloudconvert.com/v2/jobs",
        headers=headers,
        data=json.dumps({
            "tasks": {
                "convert": {
                    "operation": "convert",
                    "input": import_task_id,
                    "output_format": "pdf"
                },
                "export": {
                    "operation": "export/url",
                    "input": "convert"
                }
            }
        })
    )

    if convert_task_response.status_code != 201:
        st.error(f"❌ Error al crear la tarea de conversión: {convert_task_response.text}")
        return None

    convert_task = convert_task_response.json()
    st.success("✅ Tarea de conversión creada con éxito.")

    if "data" not in convert_task:
        st.error("❌ No se recibió 'data' en la respuesta de conversión.")
        return None

    convert_task_id = convert_task["data"]["id"]

    # 🔹 Paso 4: Esperar la conversión
    st.info("⏳ Convirtiendo a PDF...")

    while True:
        task_status_response = requests.get(f"https://api.cloudconvert.com/v2/jobs/{convert_task_id}", headers=headers)

        if task_status_response.status_code != 200:
            st.error(f"❌ Error al verificar el estado de la conversión: {task_status_response.text}")
            return None

        task_status = task_status_response.json()
        estado = task_status["data"]["status"]

        if estado == "finished":
            st.success("✅ Conversión completada.")
            break
        elif estado == "failed":
            st.error(f"❌ Error en la conversión: {task_status}")
            return None
        else:
            st.info(f"⏳ Estado actual: {estado}... esperando...")
            time.sleep(5)

    # 🔹 Paso 5: Obtener el enlace de descarga del PDF
    st.info("📥 Buscando enlace de descarga...")
    export_task = next((task for task in task_status["data"]["tasks"] if task["operation"] == "export/url"), None)

    if not export_task:
        st.error("❌ No se encontró la tarea de exportación.")
        return None

    file_url = export_task["result"]["files"][0]["url"]
    st.success("✅ Enlace de descarga obtenido.")

    pdf_response = requests.get(file_url)
    
    if pdf_response.status_code == 200:
        st.success("✅ Archivo PDF descargado correctamente.")
        return BytesIO(pdf_response.content)
    else:
        st.error("❌ Error al descargar el archivo PDF.")
        return None
        
# Botón para generar el certificado
if st.button("🎓 Generar Certificado en PDF"):
    if st.session_state.validado:
        certificado_pptx = generar_certificado(
            st.session_state.nombre_estudiante,
            st.session_state.documento_estudiante,
            curso_seleccionado,
            df_cursos[df_cursos["Código"] == codigo_curso]["Duración"].values[0],
            df_cursos[df_cursos["Código"] == codigo_curso]["Fecha"].values[0],
            qr
        )

        if certificado_pptx:
            certificado_pdf = pptx_a_pdf(certificado_pptx)

            if certificado_pdf:
                st.success("✅ Certificado generado en PDF.")
                st.download_button(
                    label="📥 Descargar Certificado en PDF",
                    data=certificado_pdf,
                    file_name=f"Certificado_{st.session_state.nombre_estudiante}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("❌ No se pudo convertir el archivo a PDF.")
    else:
        st.error("⚠️ No se puede generar el certificado sin validación.")
