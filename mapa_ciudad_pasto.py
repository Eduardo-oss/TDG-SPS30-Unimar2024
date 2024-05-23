#librerias
import folium

from folium.plugins import MiniMap

# Crear el mapa
map = folium.Map(location=[1.2238916, -77.2830765], zoom_start=15)

# Definir una lista de coordenadas para los marcadores
coordenadas = [
    (1.2326969,-77.2837347),
    (1.2244383,-77.2816525),
    (1.2200372,-77.2782958),
    (1.219889,-77.283487),
    (1.222668,-77.284886)
    # Agrega más coordenadas si es necesario
]

# segun indice de calidad de aire
#PM10
PM10=10
#PM2.5
PM25=321
# Iterar sobre las coordenadas y agregar marcadores a map
for coord in coordenadas:

    folium.Marker(location=[1.2326969,-77.2837347],
                  popup="Hotel Morasurco: {}".format(coord),
                  icon=folium.Icon(color='blue', icon='cloud'),
                  tooltip="Promedio PM10: 1.06 µg/m³ PM2.5: 0.828 µg/m³").add_to(map)
    folium.Marker(location=[1.2244383,-77.2816525],
                  popup="Versalles: {}".format(coord),
                  icon=folium.Icon(color='blue', icon='cloud'),
                  tooltip="Promedio PM10: 0.969 µg/m³ PM2.5: 0.792 µg/m³").add_to(map)
    folium.Marker(location=[1.2200372,-77.2782958],
                  popup="Calle 21 Cra. 29: {}".format(coord),
                  icon=folium.Icon(color='blue', icon='cloud'),
                  tooltip="Promedio PM10: 13.64 µg/m³ PM2.5: 13.65 µg/m³").add_to(map)
    folium.Marker(location=[1.219889,-77.283487],
                  popup="Calle 17 Cra 33: {}".format(coord),
                  icon=folium.Icon(color='blue', icon='cloud'),
                  tooltip="Promedio PM10: 1.69 µg/m³ PM2.5: 1.67 µg/m³").add_to(map)
    folium.Marker(location=[1.222668,-77.284886],
                  popup="Cra 35 #17-68: {}".format(coord),
                  icon=folium.Icon(color='blue', icon='cloud'),
                  tooltip="Promedio PM10: 6.91 µg/m³ PM2.5: 6.91 µg/m³").add_to(map)
# Iterar sobre las coordenadas y agregar círculos personalizados
for coord in coordenadas:
    if 1 <= PM10 <= 10:
            color="#33FF00"
            blue="blue"
            folium.Circle(location=[1.2326969,-77.2837347],
                    color=color,
                    fill_color=color,
                    radius=40,
                    weight=4,
                    fill_opacity=0.5,
                    tooltip="PM10 Max: {3}, PM2.5 Max: {2.3}").add_to(map)
            folium.Circle(location=[1.2244383,-77.2816525],
                    color=color,
                    fill_color=color,
                    radius=40,
                    weight=4,
                    fill_opacity=0.5,
                    tooltip="PM10 Max: {1.4}, PM2.5 Max: {1.4}").add_to(map)
            folium.Circle(location=[1.2200372,-77.2782958],
                    color=color,
                    fill_color=color,
                    radius=40,
                    weight=4,
                    fill_opacity=0.5,
                    tooltip="PM10 Max: {21.83}, PM2.5 Max: {21.84}").add_to(map)
            folium.Circle(location=[1.219889,-77.283487],
                    color=color,
                    fill_color=color,
                    radius=40,
                    weight=4,
                    fill_opacity=0.5,
                    tooltip="PM10 Max: {6.4}, PM2.5 Max: {6.4}").add_to(map)
            folium.Circle(location=[1.222668,-77.284886],
                    color=color,
                    fill_color=color,
                    radius=40,
                    weight=4,
                    fill_opacity=0.5,
                    tooltip="PM10 Max: {6.91}, PM2.5 Max: {6.91}").add_to(map)
# Agregar las capas de mapa base
folium.TileLayer().add_to(map)

# Agregar el minimapa
minimap = MiniMap()

# Mostrar el mapa con los círculos
display(map)


# Crear un mapa interactivo con folium
#map = folium.Map(location=[51.5074, -0.1278], zoom_start=10)
# Agregar un marcador al mapa
#folium.Marker([1.2136, -77.2811], popup='San Juan de Pasto').add_to(map)
# Mostrar el mapa
map
# Guardar el mapa como un archivo HTML localmente
map.save('mi_mapa_interactivo.html')
print('mapa guardado')