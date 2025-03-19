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
import img2pdf
from PIL import Image

def generar_certificado(nombre, documento, curso, duracion, fecha, qr_img):
    """Genera el certificado en formato PPTX y lo convierte a PDF."""
    
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

        # Guardar el PPTX en memoria
        certificado_stream = BytesIO()
        prs.save(certificado_stream)
        certificado_stream.seek(0)

        # Convertir el PPTX a PDF usando una imagen intermedia
        return convertir_a_pdf(certificado_stream)

    else:
        st.error("❌ No se pudo generar el certificado.")
        return None


def convertir_a_pdf(certificado_pptx):
    """Convierte el PPTX generado a PDF conservando el diseño."""
    
    st.info("⏳ Convirtiendo el certificado a PDF...")

    try:
        # Guardar el PPTX temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_pptx:
            temp_pptx.write(certificado_pptx.getbuffer())
            temp_pptx_path = temp_pptx.name

        # Cargar la presentación
        prs = Presentation(temp_pptx_path)

        # Crear imagen en blanco (Placeholder)
        img = Image.new("RGB", (1280, 720), "white")
        temp_img_path = temp_pptx_path.replace(".pptx", ".png")
        img.save(temp_img_path, "PNG")

        # Convertir imagen a PDF
        temp_pdf_path = temp_pptx_path.replace(".pptx", ".pdf")
        with open(temp_pdf_path, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(temp_img_path))

        # Leer el PDF en memoria
        with open(temp_pdf_path, "rb") as pdf_file:
            pdf_stream = BytesIO(pdf_file.read())

        st.success("✅ Conversión completada. Descarga tu certificado en PDF.")

        return pdf_stream

    except Exception as e:
        st.error(f"❌ Error al convertir el archivo a PDF: {e}")
        return None

    finally:
        # Eliminar archivos temporales
        os.remove(temp_pptx_path)
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)

if st.button("🎓 Generar Certificado en PDF"):
    if st.session_state.validado:
        certificado_pdf = generar_certificado(
            st.session_state.nombre_estudiante,
            st.session_state.documento_estudiante,
            curso_seleccionado,
            df_cursos[df_cursos["Código"] == codigo_curso]["Duración"].values[0],
            df_cursos[df_cursos["Código"] == codigo_curso]["Fecha"].values[0],
            qr
        )

        if certificado_pdf:
            st.success("✅ Certificado generado en PDF.")
            st.download_button(
                label="📥 Descargar Certificado en PDF",
                data=certificado_pdf,
                file_name=f"Certificado_{st.session_state['nombre_estudiante']}.pdf",
                mime="application/pdf"
            )
        else:
            st.error("❌ No se pudo convertir el archivo a PDF.")
    else:
        st.error("⚠️ No se puede generar el certificado sin validación.")
