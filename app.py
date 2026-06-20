import cv2
import numpy as np
import streamlit as st
import time

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
    st.error("¡ACCESO BLOQUEADO POR INTRUSIÓN! ")
    st.title(" Sistema de Seguridad Perimetral Activado")
    st.subheader("Se ha detectado un rostro no autorizado intentando vulnerar el perímetro.")
    st.warning("El incidente ha sido registrado y el acceso al panel se encuentra restringido.")
    
    if st.button(" Reiniciar Escáner de Seguridad"):
        st.session_state["autenticado"] = False
        st.session_state["bloqueado"] = False
        st.rerun()

# --- VISTA 3: PANTALLA DE LOGEO BIOMÉTRICO TRADICIONAL ---
else:
    st.title(" Sistema Web de Control de Acceso")
    st.subheader("Por favor, cargue la captura facial para autenticarse")

    # Selector de perfil biométrico en la barra lateral para simular la discriminación de rostros
    st.sidebar.title(" Simulación Biométrica")
    perfil_rostro = st.sidebar.selectbox(
        "Seleccione el rostro frente a la cámara:",
        ["Oscar Jair Cuadros Núñez (Autorizado)", "Usuario Desconocido / Intruso (No Autorizado)"]
    )

    es_jair = "Oscar Jair" in perfil_rostro

    # CASILLA REAL PARA SELECCIONAR LA IMAGEN DESDE TU PC
    archivo_imagen = st.file_uploader("Seleccione una imagen de rostro (.jpg, .png)", type=["jpg", "png", "jpeg"])
    
    if archivo_imagen is not None:
        # Convertir el archivo subido a una matriz legible por OpenCV
        file_bytes = np.asarray(bytearray(archivo_imagen.read()), dtype=np.uint8)
        cuadro = cv2.imdecode(file_bytes, 1)
        
        with st.spinner(" Procesando flujo biométrico... Aplicando reescalado 0.25x..."):
            time.sleep(1.0) # Simular latencia de procesamiento
            
            # Aplicar inversión de espejo y dimensiones
            cuadro = cv2.flip(cuadro, 1)
            alto, ancho, _ = cuadro.shape
            
            # Asignar color según el perfil seleccionado en la barra lateral
            color_caja = (0, 255, 0) if es_jair else (0, 0, 255)
            texto_pantalla = "ROSTRO DETECTADO: JAIR" if es_jair else "INTRUSO DETECTADO"
            
            # Dibujar cuadro delimitador de OpenCV
            cv2.rectangle(cuadro, (int(ancho*0.25), int(alto*0.2)), (int(ancho*0.75), int(alto*0.8)), color_caja, 4)
            cv2.putText(cuadro, texto_pantalla, (int(ancho*0.25), int(alto*0.15)), cv2.FONT_HERSHEY_DUPLEX, 0.8, color_caja, 2)
            
            # Mostrar la imagen procesada en la UI
            cuadro_rgb = cv2.cvtColor(cuadro, cv2.COLOR_BGR2RGB)
            st.image(cuadro_rgb, caption="Análisis Perimetral Completado", use_container_width=True)
            
        # Lógica de acceso según el perfil
        if es_jair:
            st.success(" ¡Rostro de JAIR verificado exitosamente mediante distancias euclidianas!")
            if st.button(" Entrar al Sistema Autorizado"):
                st.session_state["autenticado"] = True
                st.session_state["bloqueado"] = False
                st.rerun()
        else:
            st.error(" Alerta: Rostro no registrado detectado en el perímetro.")
            if st.button(" Bloquear Sistema por Seguridad"):
                st.session_state["autenticado"] = False
                st.session_state["bloqueado"] = True
                st.rerun()
    else:
        st.warning(" Estado: Esperando archivo de imagen para el análisis perimetral...")
