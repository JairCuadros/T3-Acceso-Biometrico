import cv2
import numpy as np
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# Configuración de la interfaz web
st.set_page_config(page_title="Control de Acceso Biométrico", layout="centered")

# Inicializar estados globales de la página
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "bloqueado" not in st.session_state:
    st.session_state["bloqueado"] = False

# --- VISTA 1: PANEL DE CONTROL PROTEGIDO (ACCESO CONCEDIDO) ---
if st.session_state["autenticado"] and not st.session_state["bloqueado"]:
    st.success("¡Acceso Permitido! Bienvenido al sistema, JAIR.")
    st.title("Panel de Control de Seguridad")
    st.subheader("Sistemas Inteligentes - Universidad Privada del Norte")
    st.write("Has validado tu identidad biométrica de manera exitosa en la nube.")
    
    if st.button("Cerrar Sesión y Bloquear"):
        st.session_state["autenticado"] = False
        st.session_state["bloqueado"] = False
        st.rerun()

# --- VISTA 2: PANTALLA DE ALERTA DE INTRUSIÓN (SISTEMA BLOQUEADO) ---
elif st.session_state["bloqueado"]:
    st.error("¡ACCESO BLOQUEADO POR INTRUSIÓN!")
    st.title("Sistema de Seguridad Perimetral Activado")
    st.subheader("Se ha detectado un rostro no autorizado intentando vulnerar el perímetro.")
    st.warning("El incidente ha sido registrado y el acceso al panel se encuentra restringido.")
    
    if st.button("🔄 Reiniciar Escáner de Seguridad"):
        st.session_state["autenticado"] = False
        st.session_state["bloqueado"] = False
        st.sidebar.clear()
        st.rerun()

# --- VISTA 3: PANTALLA DE LOGEO BIOMÉTRICO TRADICIONAL ---
else:
    st.title("Sistema Web de Control de Acceso")
    st.subheader("Por favor, mire a la cámara para autenticarse")

    # Selector de perfil biométrico en la barra lateral para simular la discriminación de rostros
    st.sidebar.title("Simulación Biométrica")
    perfil_rostro = st.sidebar.selectbox(
        "Seleccione el rostro frente a la cámara:",
        ["Oscar Jair Cuadros Núñez (Autorizado)", "Usuario Desconocido / Intruso (No Autorizado)"]
    )

    es_jair = "Oscar Jair" in perfil_rostro

    # Clase secundaria: Procesa los fotogramas en tiempo real aplicando OpenCV dinámico
    class ProcesadorBiometrico(VideoTransformerBase):
        def __init__(self, es_autorizado):
            self.contador_fotogramas = 0
            self.es_autorizado = es_autorizado

        def transform(self, frame):
            cuadro = frame.to_ndarray(format="bgr24")
            cuadro = cv2.flip(cuadro, 1) # Efecto espejo natural
            
            self.contador_fotogramas += 1
            alto, ancho, _ = cuadro.shape
            
            # Coordenadas de la caja delimitadora dinámica (Padding del 25%)
            cv2.rectangle(cuadro, (int(ancho*0.3), int(alto*0.2)), (int(ancho*0.7), int(alto*0.8)), (0, 255, 0) if self.es_autorizado else (0, 0, 255), 2)
            
            if self.contador_fotogramas < 15:
                cv2.putText(cuadro, "INICIALIZANDO CAMARA...", (int(ancho*0.3), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 165, 255), 1)
            else:
                if self.es_autorizado:
                    cv2.putText(cuadro, "ROSTRO DETECTADO: JAIR", (int(ancho*0.3), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
                else:
                    cv2.putText(cuadro, "INTRUSO DETECTADO", (int(ancho*0.3), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
            
            return cuadro

    # Lanzar componente de streaming de video WebRTC pasando el parámetro de autorización
    ctx = webrtc_streamer(
        key="biometric-auth", 
        video_transformer_factory=lambda: ProcesadorBiometrico(es_autorizado=es_jair),
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False}
    )
    
    # Evaluación lógica del backend síncrono según la selección de la barra lateral
    if ctx.video_receiver:
        if es_jair:
            st.success("¡Rostro de JAIR Verificado Exitosamente!")
            if st.button("Entrar al Sistema Autorizado"):
                st.session_state["autenticado"] = True
                st.session_state["bloqueado"] = False
                st.rerun()
        else:
            st.error("Alerta: Rostro no registrado detectado en el perímetro.")
            if st.button(" Bloquear Sistema por Seguridad"):
                st.session_state["autenticado"] = False
                st.session_state["bloqueado"] = True
                st.rerun()
    else:
        st.warning(" Estado: Esperando activación del hardware de captura perimetral...")
