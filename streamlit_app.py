import streamlit as st
from scraper_providers import buscar_y_analizar

# Título de la aplicación
st.title("Evaluador de Riesgo de Proveedores")

# Entrada del usuario
st.subheader("Introduce el nombre del proveedor que deseas evaluar:")
nombre_proveedor = st.text_input("Nombre del proveedor:")

# Configuración adicional
meses = st.slider("Meses a analizar:", min_value=1, max_value=24, value=12)

# Botón para iniciar el análisis
if st.button("Analizar riesgos"):
    if nombre_proveedor:
        st.write(f"Buscando información para: **{nombre_proveedor}**...")
        with st.spinner("Analizando datos, por favor espera..."):
            resultados = buscar_y_analizar(nombre_proveedor, meses_atras=meses)

        # Mostrar resultados
        if resultados:
            st.success(f"Se encontraron {len(resultados)} resultados relevantes.")
            for resultado in resultados:
                st.markdown(f"### {resultado['titulo']}")
                st.write(f"**Descripción:** {resultado['descripcion']}")
                st.write(f"**Nivel de Riesgo:** {resultado['riesgo']}")
                st.markdown(f"[Enlace a la fuente]({resultado.get('enlace', '#')})", unsafe_allow_html=True)
                st.write("---")
        else:
            st.warning("No se encontraron riesgos significativos.")
    else:
        st.error("Por favor, introduce un nombre de proveedor.")