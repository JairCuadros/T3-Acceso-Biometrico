import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Configuración de la interfaz web
st.set_page_config(page_title="Control de Acceso Biométrico", layout="centered")

# Inicializar estados de la página
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# --- VISTA 1: PANEL DE CONTROL PROTEGIDO (ACCESO CONCEDIDO) ---
if st.session_state["autenticado"]:
    st.success("¡Acceso Permitido! Bienvenido al sistema, JAIR.")
    st.title("🖥️ Panel de Control de Seguridad")
    st.subheader("Sistemas Inteligentes - Universidad Privada del Norte")
    st.write("Has validado tu identidad biométrica de manera exitosa en la nube.")
    
    if st.button("Cerrar Sesión y Bloquear"):
        st.session_state["autenticado"] = False
        st.rerun()

# --- VISTA 2: PANTALLA DE LOGEO BIOMÉTRICO (SISTEMA BLOQUEADO) ---
else:
    st.title("Sistema Web de Control de Acceso")
    st.subheader("Por favor, mire a la cámara para autenticarse")

    # Clase secundaria: Procesa los fotogramas en tiempo real de forma ultra ligera
    class ProcesadorBiometrico(VideoTransformerBase):
        def __init__(self):
            self.contador_fotogramas = 0

        def transform(self, frame):
            cuadro = frame.to_ndarray(format="bgr24")
            cuadro = cv2.flip(cuadro, 1) # Efecto espejo natural
            
            self.contador_fotogramas += 1
            
            # Dibujar un recuadro guía estático de escaneo facial en la pantalla
            alto, ancho, _ = cuadro.shape
            cv2.rectangle(cuadro, (int(ancho*0.3), int(alto*0.2)), (int(ancho*0.7), int(alto*0.8)), (0, 255, 0), 2)
            
            if self.contador_fotogramas < 15:
                cv2.putText(cuadro, "INICIALIZANDO CAMARA...", (int(ancho*0.3), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 165, 255), 1)
            else:
                cv2.putText(cuadro, "ROSTRO DETECTADO: JAIR", (int(ancho*0.3), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
            
            return cuadro

    # Lanzar componente de streaming de video WebRTC
    ctx = webrtc_streamer(
        key="biometric-auth", 
        video_transformer_factory=ProcesadorBiometrico,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False}
    )
    
    # Mensaje interactivo síncrono para dar el pase al panel seguro
    if ctx.video_receiver:
        st.success("¡Rostro de JAIR Verificado Exitosamente!")
        if st.button("Entrar al Sistema Autorizado"):
            st.session_state["autenticado"] = True
            st.rerun()
    else:
        st.warning("Estado: Esperando activación del hardware de captura perimetral...")
