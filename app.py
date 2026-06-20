import cv2
import face_recognition_models
import numpy as np
import streamlit as st
import os
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

st.set_page_config(page_title="Control de Acceso Biométrico", layout="centered")

LOG_FILE = "access_log.txt"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario_autorizado" not in st.session_state:
    st.session_state["usuario_autorizado"] = None

# --- VISTA 1: PANEL DE CONTROL PROTEGIDO ---
if st.session_state["autenticado"]:
    st.success(f"¡Acceso Permitido! Bienvenido al sistema, {st.session_state['usuario_autorizado']}.")
    st.title("🖥️ Panel de Control de Seguridad")
    st.subheader("Sistemas Inteligentes - Universidad Privada del Norte")
    st.write("Has validado tu identidad biométrica de manera exitosa en la nube.")

    if st.button("Cerrar Sesión y Bloquear"):
        if os.path.exists(LOG_FILE):
            os.remove(LOG_FILE)
        st.session_state["autenticado"] = False
        st.session_state["usuario_autorizado"] = None
        st.clear_cache()
        st.rerun()

# --- VISTA 2: PANTALLA DE LOGEO BIOMÉTRICO ---
else:
    st.title("Sistema Web de Control de Acceso")
    st.subheader("Por favor, mire a la cámara para autenticarse")

    @st.cache_resource
    def cargar_base_datos():
        try:
            img_jair = face_recognition.load_image_file("jair.jpg")
            encoding_jair = face_recognition.face_encodings(img_jair)[0]

            img_cataleya = face_recognition.load_image_file("cataleya.jpg")
            encoding_cataleya = face_recognition.face_encodings(img_cataleya)[0]

            return [encoding_jair, encoding_cataleya], ["JAIR", "CATALEYA"]
        except Exception as e:
            st.error(f"Error al cargar imágenes base: {e}")
            return [], []

    known_encodings, known_names = cargar_base_datos()

    class ProcesadorBiometrico(VideoTransformerBase):
        def transform(self, frame):
            cuadro = frame.to_ndarray(format="bgr24")
            cuadro = cv2.flip(cuadro, 1)

            cuadro_pequeno = cv2.resize(cuadro, (0, 0), fx=0.25, fy=0.25)
            cuadro_rgb = cv2.cvtColor(cuadro_pequeno, cv2.COLOR_BGR2RGB)

            locations = face_recognition.face_locations(cuadro_rgb)
            encodings = face_recognition.face_encodings(cuadro_rgb, locations)

            nombre_actual = "DESCONOCIDO"

            for (top, right, bottom, left), encoding in zip(locations, encodings):
                if len(known_encodings) > 0:
                    distances = face_recognition.face_distance(known_encodings, encoding)
                    best_match = np.argmin(distances)

                    if distances[best_match] < 0.6:
                        nombre_actual = known_names[best_match]
                        with open(LOG_FILE, "w") as f:
                            f.write(nombre_actual)

                top *= 4; right *= 4; bottom *= 4; left *= 4

                h, w, _ = cuadro.shape
                p_h, p_w = int((bottom-top)*0.25), int((right-left)*0.20)
                top = max(0, top - p_h); bottom = min(h, bottom + p_h)
                left = max(0, left - p_w); right = min(w, right + p_w)

                color = (0, 0, 255) if nombre_actual == "DESCONOCIDO" else (0, 255, 0)
                cv2.rectangle(cuadro, (left, top), (right, bottom), color, 2)
                cv2.rectangle(cuadro, (left, top - 35), (right, top), color, cv2.FILLED)
                cv2.putText(cuadro, nombre_actual, (left + 6, top - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            return cuadro

    if len(known_encodings) > 0:
        webrtc_streamer(key="biometric-auth", video_transformer_factory=ProcesadorBiometrico)

        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                usuario_encontrado = f.read().strip()

            if usuario_encontrado in known_names:
                st.success(f"👤 Rostro de {usuario_encontrado} reconocido correctamente.")
                st.session_state["usuario_autorizado"] = usuario_encontrado

                if st.button("Ingresar al Panel Autorizado"):
                    st.session_state["autenticado"] = True
                    st.rerun()
        else:
            st.warning("Estado: Esperando rostro registrado frente a la cámara...")
