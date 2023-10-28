import pandas as pa
import plotly.graph_objects as go
import csv

M = pa.read_csv('bus_metz.csv')

fig = go.Figure()

fig = go.Figure(go.Scattermapbox(
    mode = "markers+text",
    lon = M['lon'],
    lat = M['lat'],
    showlegend=True,
    marker = go.scattermapbox.Marker(size=9),
    text=M['display_name'].apply(lambda x: \
                                         '<b>' + str(x) \
                                         + '</b>'),
    textfont=dict(color="black", size=8, family='bold'),
    textposition='middle center'
))

fic2 = open('gtfs/trips.csv')
f2 = csv.reader(fic2)
liste_trip_id = []
for ligne in f2:
    if ligne[3] == 'trip_headsign':
        continue
    if ligne[3] not in liste_trip_id:
        liste_trip_id.append(ligne[3])
fic2.close()


for elt in liste_trip_id:
    fic = open('Lignes2/' + str(elt) + '.csv')
    f = csv.reader(fic)
    Listetempo_stop_id_of_one_trip = []
    for ligne in f:
        if ligne[0] == "stop_id":
            continue
        else:
            Listetempo_stop_id_of_one_trip.append(int(ligne[0]))
    Mtemp = M[M['stop_id'].isin(Listetempo_stop_id_of_one_trip)]
    def sorter(col):
        correspondence = {Listetempo_stop_id_of_one_trip: order for order, Listetempo_stop_id_of_one_trip in enumerate(Listetempo_stop_id_of_one_trip)}
        return col.map(correspondence)


    Mtemp.sort_values(by="stop_id", key=lambda column: column.map(lambda e: Listetempo_stop_id_of_one_trip.index(e)), inplace=True)

    fig.add_trace(go.Scattermapbox(
        mode="markers+lines+text",
        lon=Mtemp['lon'],
        lat=Mtemp['lat'],
        showlegend=True,
        marker=go.scattermapbox.Marker(size=9),
        text=Mtemp['display_name'].apply(lambda x: \
                                         '<b>' + str(x) \
                                         + '</b>'),
        textfont=dict(color="black", size=8, family='bold'),
        textposition='middle center'
    ))

fig.update_layout(mapbox_style="open-street-map")
fig.show()
