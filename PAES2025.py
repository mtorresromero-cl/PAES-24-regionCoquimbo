import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
from branca.colormap import linear

# Configuración de Streamlit para hacer el mapa más grande y ocupar toda la pantalla
st.set_page_config(layout="wide")

# Sidebar más grande
st.sidebar.markdown('<style> .css-1d391kg { width: 500px !important;} </style>', unsafe_allow_html=True)

# Cargar el logo en la parte superior del sidebar
st.sidebar.image("/Users/migueltorresromero/Documents/Páginas/OPRC/Diseño web/logo_web_200x100.png", width=100)  # Ajusta el tamaño con 'width'

# Título
st.sidebar.title("Resultados PAES 2024 - Región de Coquimbo | MAPA DE CALOR")

# Cargar los datos desde el CSV
datos = pd.read_csv("/Users/migueltorresromero/Documents/Páginas/OPRC/Estudios/PAES 2025/datos_con_coordenadas.csv")

# Verifica que las coordenadas sean numéricas
datos["LATITUD"] = pd.to_numeric(datos["LATITUD"], errors='coerce')
datos["LONGITUD"] = pd.to_numeric(datos["LONGITUD"], errors='coerce')

# Eliminar filas con valores NaN en las columnas LATITUD o LONGITUD
datos = datos.dropna(subset=["LATITUD", "LONGITUD"])

# Crear lista personalizada de comunas
comunas_ordenadas = [
    "Región de Coquimbo",  # Región de Coquimbo (por defecto)
    "LA HIGUERA",
    "LA SERENA",
    "COQUIMBO",
    "VICUÑA",
    "PAIGUANO",
    "ANDACOLLO",
    "RIO HURTADO",
    "MONTE PATRIA",
    "OVALLE",
    "PUNITAQUI",
    "COMBARBALA",
    "CANELA",
    "ILLAPEL",
    "SALAMANCA",
    "LOS VILOS"
]

# Selección de la comuna
comuna_seleccionada = st.sidebar.selectbox("Selecciona una comuna", comunas_ordenadas)

# Sidebar para seleccionar el tipo de dependencia
tipos_dependencia = ["Todos", "Particular pagado", "Particular subvencionado", "Municipal", "Servicio Local de Educación"]
tipo_dependencia_seleccionado = st.sidebar.selectbox("Selecciona un tipo de dependencia", tipos_dependencia)


# Filtrar los datos por la comuna seleccionada
if comuna_seleccionada == "Región de Coquimbo":
    # Filtrar los datos de la región, no importa el tipo de dependencia
    datos_comuna = datos  # Mostrar todos los datos de la región
else:
    datos_comuna = datos[datos["COM_NOMBRE"] == comuna_seleccionada]  # Filtrar por comuna seleccionada

# Filtrar los datos por el tipo de dependencia seleccionado si no es "Todos"
if tipo_dependencia_seleccionado != "Todos":
    datos_comuna = datos_comuna[datos_comuna["GRUPO_DEPENDENCIA"] == tipo_dependencia_seleccionado]

# Verificar si hay datos para mostrar después de filtrar
if datos_comuna.empty:
    # Si no hay datos, mostrar un mensaje y no generar el mapa con puntos
    if comuna_seleccionada == "Región de Coquimbo":
        st.sidebar.write("No hay colegios de este tipo en la región")
    else:
        st.sidebar.write("No hay colegios de este tipo en esta comuna")
else:
    # Mostrar el listado de establecimientos ordenados por promedio en el sidebar
    if comuna_seleccionada == "Región de Coquimbo":
        # Ordenar a nivel regional
        datos_comuna_sorted = datos_comuna.sort_values(by="PROMEDIO_ESTABLECIMIENTO", ascending=False)
    else:
        # Ordenar solo la comuna seleccionada
        datos_comuna_sorted = datos_comuna.sort_values(by="PROMEDIO_ESTABLECIMIENTO", ascending=False)

    # Renombrar las columnas según lo solicitado
    datos_comuna_sorted = datos_comuna_sorted[["ESTABLECIMIENTO", "COM_NOMBRE", "PROMEDIO_ESTABLECIMIENTO", "GRUPO_DEPENDENCIA"]]
    datos_comuna_sorted = datos_comuna_sorted.rename(columns={
        "PROMEDIO_ESTABLECIMIENTO": "PROMEDIO",
        "COM_NOMBRE": "COMUNA",
        "GRUPO_DEPENDENCIA": "TIPO"
    })

    # Crear una nueva columna "TIPO" según el valor de "GRUPO_DEPENDENCIA"
    def asignar_tipo_dependencia(grupo):
        if grupo == "Particular Pagado":
            return "PP"
        elif grupo == "Particular Subvencionado":
            return "PS"
        elif grupo == "Municipal":
            return "MU"
        elif grupo == "Servicio Local de Educación":
            return "SLE"
        return "Desconocido"  # En caso de que no se reconozca el grupo

    # Reiniciar el índice para que comience desde 1 y no 0
    datos_comuna_sorted.index = range(1, len(datos_comuna_sorted) + 1)

    # Mostrar el listado de establecimientos ordenados en el sidebar
    st.sidebar.subheader(f"Listado de establecimientos en {comuna_seleccionada}")

    # Cambiar el tamaño de la fuente usando HTML en Markdown
    html_table = datos_comuna_sorted.to_html(classes='styled-table', index=True)

    # Aplicar estilos de CSS directamente al HTML generado
    st.sidebar.markdown("""
        <style>
            .styled-table {
                font-size: 12px;  /* Ajuste del tamaño de la letra */
                width: 100%;
                border-collapse: collapse;
            }
            .styled-table th, .styled-table td {
                padding: 10px;
                border: 1px solid #ddd;
                text-align: left;
            }
        </style>
    """, unsafe_allow_html=True)

    # Mostrar la tabla con el tamaño de letra ajustado
    st.sidebar.markdown(html_table, unsafe_allow_html=True)

   # Verificar si hay datos para mostrar después de filtrar
if datos_comuna.empty:
    # Si no hay datos, mostrar un mensaje y no generar el mapa con puntos
    if comuna_seleccionada == "Región de Coquimbo":
        st.sidebar.write(" ")
    else:
        st.sidebar.write(" ")

    # Evitar que se agregue un mapa vacío
    mapa = None  # Establecer el mapa como None

else:
    # Si hay datos, proceder con la creación del mapa y el colormap
    if comuna_seleccionada == "Región de Coquimbo":
        # Centrar el mapa en la región de Coquimbo
        mapa = folium.Map(location=[-30, -65.5], zoom_start=7.5)  # Coordenadas centradas en la región de Coquimbo
    else:
        # Centrar el mapa en la comuna seleccionada
        mapa = folium.Map(location=[datos_comuna["LATITUD"].mean(), datos_comuna["LONGITUD"].mean()], zoom_start=10)

    # Crear la escala de colores de rojo a verde solo si hay datos
    colormap = linear.RdYlGn_09.scale(datos_comuna["PROMEDIO_ESTABLECIMIENTO"].min(), datos_comuna["PROMEDIO_ESTABLECIMIENTO"].max())

    # Agregar el mapa de calor para los datos de la comuna seleccionada
    heat_data = [[row["LATITUD"], row["LONGITUD"], row["PROMEDIO_ESTABLECIMIENTO"]] for index, row in datos_comuna.iterrows()]
    HeatMap(heat_data).add_to(mapa)

    # Agregar círculos con el mismo color para el borde y el relleno para la comuna seleccionada
    for _, row in datos_comuna.iterrows():
        color = colormap(row["PROMEDIO_ESTABLECIMIENTO"])

        # Crear el popup con estilo personalizado
        popup_content = f"""
        <html>
        <head>
        <style>
        .popup-text {{
            font-size: 14px;
            color: black;
        }}
        .popup-bold {{
            font-weight: bold;
            font-size: 16px;
        }}
        </style>
        </head>
        <body>
        <div class="popup-text">
            Establecimiento: {row['ESTABLECIMIENTO']}<br>
            Comuna: {row['COM_NOMBRE']}<br>
            <span class="popup-bold">Promedio: {row['PROMEDIO_ESTABLECIMIENTO']}</span>
        </div>
        </body>
        </html>
        """

        folium.CircleMarker(
            location=[row["LATITUD"], row["LONGITUD"]],
            radius=10,
            color=color,
            weight=2,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_content, max_width=300),
        ).add_to(mapa)

    # Añadir la leyenda para la escala de colores
    colormap.add_to(mapa)
    mapa.fit_bounds(mapa.get_bounds())

# Usar `st.columns([1, 8])` para dividir el espacio entre el sidebar y el mapa
col1, col2 = st.columns([1, 8])  # 1 parte para el sidebar y 8 partes para el mapa

with col2:
    # Si hay un mapa (no vacío), mostrarlo
    if mapa:
        # Ajustamos el tamaño del mapa al 100% de la columna, usando un número para el ancho
        folium_static(mapa, height=900)  # Ajusta el ancho y la altura del mapa (en píxeles)




# Agregar AUTOR en el footer fijo en la parte inferior
st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: rgba(0, 0, 0, 0.7);  /* Fondo semitransparente */
            color: white;
            text-align: right;
            padding: 10px;
            font-size: 14px;
        }
    </style>
    <div class="footer">
        Diseñado por <strong>Miguel Torres Romero</strong>, Politólogo, Mg. (c) en Investigación en Ciencias Sociales, Universidad de Buenos Aires.<br>Todos los derechos reservados © 2025.
    </div>
""", unsafe_allow_html=True)








import streamlit as st

# Deshabilitar la selección de texto y el clic derecho
st.markdown("""
    <style>
        body {
            user-select: none;  /* Evitar selección de texto */
        }
    </style>
    <script>
        // Deshabilitar el clic derecho (botón de contexto)
        document.addEventListener("contextmenu", function(event){
            event.preventDefault();
        });
        
        // Deshabilitar la combinación Ctrl+C para copiar
        document.addEventListener("keydown", function(event){
            if(event.key === "c" && event.ctrlKey) {
                event.preventDefault();
            }
        });
    </script>
""", unsafe_allow_html=True)
