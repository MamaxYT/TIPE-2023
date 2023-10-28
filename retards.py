
from datetime import timedelta, datetime
import random as rd
import plotly.graph_objects as go
import csv
import pandas as pd

def is_valid_time(time_str):
    try:
        time = datetime.strptime(time_str, "%H:%M:%S")
        return True
    except ValueError:
        return False


schedule = ""

color = ["red", "blue", "green", "lime", "seagreen", "violet"]
while not is_valid_time(schedule):
    schedule = input("Quelle heure (Format HH:MM:SS):  ")

jour = input("Quel jour: ")


def journee(day):
    if day == "Dimanche":
        return ["HIV2223-HDim2223-Dimanche-40"]
    elif day == "Samedi":
        return ["HIV2223-HSam2223-Samedi-20"]
    elif day == "Lundi":
        return ["HIV2223-HSem2223-L-Ma-J-V-01", "HV2223_PVS-PVS_2223-Semaine-01",
                "HIV2223-HSem2223-L-Ma-J-V-01-1101100"]
    elif day == "Mardi":
        return ["HIV2223-HSem2223-L-Ma-J-V-01", "HV2223_PVS-PVS_2223-Semaine-01",
                "HV2223_PVS-PVS_2223-Semaine-01-0100100", "HIV2223-HSem2223-L-Ma-J-V-01-0100100",
                "HIV2223-HSem2223-L-Ma-J-V-01-1101100"]
    elif day == "Mercredi":
        return ["HIV2223-HMer2223-Mercredi-10", "HV2223_PVS-PVS_2223-Semaine-01",
                "HV2223_PVS-PVS_2223-Semaine-01-0010000"]
    elif day == "Jeudi":
        return ["HIV2223-HSem2223-L-Ma-J-V-01", "HV2223_PVS-PVS_2223-Semaine-01",
                "HIV2223-HSem2223-L-Ma-J-V-01-1101100"]
    elif day == "Vendredi":
        return ["HIV2223-HSem2223-L-Ma-J-V-01", "HV2223_PVS-PVS_2223-Semaine-01",
                "HV2223_PVS-PVS_2223-Semaine-01-0100100", "HIV2223-HSem2223-L-Ma-J-V-01-0100100",
                "HIV2223-HSem2223-L-Ma-J-V-01-1101100"]
    raise ValueError("Mauvais format jour")


day = journee(jour)


def verifday(day, trip):
    statuts = False
    for elt in day:
        if elt in trip:
            statuts = True
    return statuts

#Initialisation de listes pour la visualtion
pt_lat = []
pt_lon = []
colorlist = []
textlist = []
statutdepassement = 0

def find_stops(trip_headsign):
    fich = open("Lignes2/" + str(trip_headsign) + ".csv")
    f = csv.reader(fich)
    next(f)
    stops = []
    for row in f:
        stops.append(row[0])
    return stops

def transformeheure(heure):
    h = heure.split(":")
    return int(h[0]) * 3600 + int(h[1]) * 60 + int(h[2])

def transformeheureinverse(temps):
    heures = temps // 3600
    minutes = (temps % 3600) // 60
    secondes = temps % 60

    temps_formatte = "{:02d}:{:02d}:{:02d}".format(heures, minutes, secondes)
    return temps_formatte


M = pd.read_csv('bus_metz.csv')

# Demander à l'utilisateur de saisir le trip_headsign de la ligne à représenter
trip = input("Veuillez entrer le nom de la ligne à représenter: ")

with open('gtfs/routes.txt') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if row[3] == trip:
            route_id = row[1]

# Récupérer tous les trip_headsign en fonction d'un numéro de route
trip_headsign_liste = []
with open('gtfs/trips.txt') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['route_id'] == route_id:
            if row['trip_headsign'] not in trip_headsign_liste:
                trip_headsign_liste.append(row['trip_headsign'])

# Récupérer les stop_id associés au trip_headsign dans le dossier Lignes2

#Création de la figure vide
fig = go.Figure(go.Scattermapbox(

))

#On ajoute les lignes sur la figure
for i in range(len(trip_headsign_liste)):
    trip_headsign = trip_headsign_liste[i]
    with open('Lignes2/{}.csv'.format(trip_headsign)) as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        stop_ids = [int(row[0]) for row in reader]


    # Trier les arrêts en fonction de leur ordre dans la ligne
    M_temp = M[M['stop_id'].isin(stop_ids)]


    def sorter(col):
        correspondence = {stop_ids: order for order, stop_ids in
                          enumerate(stop_ids)}
        return col.map(correspondence)


    M_temp.sort_values(by="stop_id", key=lambda column: column.map(lambda e: stop_ids.index(e)),
                       inplace=True)

    # Créer le visuel de la ligne
    fig.add_trace(go.Scattermapbox(
        mode="markers+lines+text",
        lon=M_temp['lon'],
        lat=M_temp['lat'],
        name=trip_headsign,
        line=dict(color=color[i]),
        showlegend=True,
        marker=go.scattermapbox.Marker(size=9),
        text=M_temp['display_name'].apply(lambda x: '<b>' + str(x) + '</b>'),
        textfont=dict(color="black", size=8, family='bold'),
        textposition='middle center'
    ))

# Dictionnaire pour vérifier si un trip_id appartient au bon trip_headsign
dicoverif = {}
#Dictionnaire qui sert à obtenir le poucentage de progression de l'arret retard dans pointinter
dicolatlonretard = {}

#Fonction qui permet de positionner les bus sur la ligne
def pointinter(stop_id, stop_id_suiv, arrival_time, next_arrival_time, schedule_time, colornb, trip_id, statut):
    global statutdepassement
    h2 = transformeheure(next_arrival_time)
    h1 = transformeheure(arrival_time)
    h = transformeheure(schedule_time)
    dureetot = h2 - h1
    temps = h - h1
    pourcentageprogression = (100 * temps) / dureetot
    f = open('gtfs/stops.csv')
    reader = csv.reader(f)
    for row in reader:
        if row[0] == stop_id:
            lat1 = row[4]
            lon1 = row[5]
        if row[0] == stop_id_suiv:
            lat2 = row[4]
            lon2 = row[5]

    difftotlat = float(lat2) - float(lat1)
    difflat = (difftotlat * pourcentageprogression) / 100
    newlat = float(lat1) + difflat
    difftotlon = float(lon2) - float(lon1)
    difflon = (difftotlon * pourcentageprogression) / 100
    newlon = float(lon1) + difflon
    if statut == 0:
        dicolatlonretard[trip_id] = [pourcentageprogression,lat1,lat2,lon1,lon2,temps,stop_id]

    dicoprogress[trip_id].append(pourcentageprogression)
    #Si on veut un train de bus
    #Verification si un arret été avant le décalage dans le temps et si il est après le bus en retard après le décalage
    if statut == 1 and dicoprogress[trip_id][0] <= dicoprogress[idbusretard][0] <= dicoprogress[trip_id][2] and dicoverif[trip_id] == dicoverif[idbusretard] and statutdepassement == 1:
        pourcentageprogressionr, lat1r, lat2r, lon1r, lon2r, tempsr,stop_idr = dicolatlonretard[idbusretard]
        difftotlatr = float(lat2r) - float(lat1r)
        rand = rd.uniform(0,4)
        difflatr = (difftotlatr * (pourcentageprogressionr - rand)) / 100
        newlatr= float(lat1r) + difflatr
        difftotlonr = float(lon2r) - float(lon1r)
        difflonr = (difftotlonr * (pourcentageprogressionr - rand)) / 100
        newlonr = float(lon1r) + difflonr

        #Avoir le temps de retard qui le bus prends à l'aide d'un fonction
        recherchetempsretard(schedule_time,tempsr,stop_idr,trip_id)

        pt_lat.append(newlatr)
        pt_lon.append(newlonr)
        colorlist.append(color[colornb])
        textlist.append(trip_id)
    #Si on ne veux pas de train de bus
    else:

        pt_lat.append(newlat)
        pt_lon.append(newlon)
        colorlist.append(color[colornb])
        textlist.append(trip_id)


dicoprogress = {}

def recherchetempsretard(schedule_time,temps,stop_id,trip_id):
    fich2 = open("fichehoraire/" + str(stop_id) + ".csv")
    reader2 = csv.reader(fich2)
    for row in reader2:
        if row[0] == trip_id and trip_id != idbusretard:
            trip_id, arrival_time, departure_time, stop_id, stop_sequence, trip_headsign = row

            temps_perdu = transformeheure(schedule_time) - transformeheure(arrival_time) - temps
            print(temps_perdu)
            diff_heure = temps_perdu // 3600
            diff_minute = (temps_perdu % 3600) // 60
            diff_seconde = temps_perdu % 60

            diff_format = "{:02d}:{:02d}:{:02d}".format(diff_heure, diff_minute, diff_seconde)
            dicoretard[trip_id] = diff_format

#Fonction pour connaître tous les bus en circulation à l'heure voulue
def get_trip_id(schedule_time, stops, trip_headsign_liste, day):
    trip_id_list = []
    for k in range(len(stops) - 1):
        stop_id, stop_id_suiv = stops[k], stops[k + 1]
        fich = open("fichehoraire/" + str(stop_id) + ".csv")
        reader1 = csv.reader(fich)
        for row in reader1:
            trip_id, arrival_time, departure_time, stop_id, stop_sequence, trip_headsign = row
            if trip_id in trip_id_list:
                continue
            if row[5] in trip_headsign_liste:
                nbcolor = trip_headsign_liste.index(row[5])
                fich2 = open("fichehoraire/" + str(stop_id_suiv) + ".csv")
                reader2 = csv.reader(fich2)
                for row2 in reader2:
                    if row2[0] == trip_id:
                        next_arrival_time = row2[1]
                        if transformeheure(arrival_time) >= transformeheure("23:59:59"):
                            continue
                        if transformeheure(next_arrival_time) >= transformeheure("23:59:59"):
                            continue

                        arrival_time1 = datetime.strptime(arrival_time, "%H:%M:%S").time()
                        next_arrival_time1 = datetime.strptime(next_arrival_time, "%H:%M:%S").time()

                        if arrival_time1 <= datetime.strptime(schedule_time, "%H:%M:%S").time() <= next_arrival_time1:
                            if verifday(day, trip_id):
                                dicoprogress[trip_id] = [k]
                                dicoverif[trip_id] = trip_headsign
                                pointinter(stop_id, stop_id_suiv, arrival_time, next_arrival_time, schedule_time,
                                           nbcolor, trip_id, 0)
                                trip_id_list.append(trip_id)
                                break
    return trip_id_list


pt_lat = []
pt_lon = []
colorlist = []
textlist = []
print("tripheadsignlist", trip_headsign_liste)
trip_id_total = []
for elt in trip_headsign_liste:
    stops = find_stops(elt)
    trip_id_list = get_trip_id(schedule, stops, trip_headsign_liste, day)
    trip_id_total += trip_id_list
    print("trip_id:", trip_id_total)

#Création d'une nouvelle "couche" pour les bus qui sont en circulation
trace2 = go.Scattermapbox(
    mode="markers",
    lon=pt_lon,
    lat=pt_lat,
    marker=go.scattermapbox.Marker(size=19, color=colorlist),
    text=textlist
)

#On ajoute la couche et on affiche
fig.add_trace(trace2)
fig.update_layout(mapbox_style="open-street-map")
fig.show()

#Dictionnaire pour suivre le retard de chaque bus
dicoretard = {}
for tripid in trip_id_total:
    dicoretard[tripid] = 0

### Gestion du retard ###

print("Parmi les différents bus suivants, lequel voulez vous qu'il subisse un retard")
DicoTrip_id = {}
compt = 0
for k in textlist:
    DicoTrip_id[compt] = k
    compt += 1

print(DicoTrip_id)
indicebusretard = int(input(""))
idbusretard = DicoTrip_id[indicebusretard]
newcolorlist = colorlist.copy()
# Garder en mémoire les lon et lat de l'arrêt qui doit subir un arret
longitudes = trace2.lon
latitudes = trace2.lat

latretard = latitudes[indicebusretard]
lonretard = longitudes[indicebusretard]

#On change uniquement la couleur du bus qui subit un arêt.
newcolorlist[indicebusretard] = "black"


# Convertir fig.data en liste
fig_data_list = list(fig.data)

# Supprimer la trace souhaitée
fig_data_list.remove(trace2)

# Reconvertir fig_data_list en tuple
fig.data = tuple(fig_data_list)

trace2 = go.Scattermapbox(
    mode="markers",
    lon=pt_lon,
    lat=pt_lat,
    marker=go.scattermapbox.Marker(size=19, color=newcolorlist),
    text=textlist
)

fig.add_trace(trace2)
fig.update_layout(mapbox_style="open-street-map")

fig.show()

statutdepassement = int(input("Voulez-vous simulez un dépassement (0) ou un train de bus (1): "))

newhoraire = ""

while not is_valid_time(newhoraire):
    newhoraire = input("Quelle heure (Format HH:MM:SS):  ")

difftime = datetime.strptime(newhoraire, "%H:%M:%S") - datetime.strptime(schedule, "%H:%M:%S")

diff_timedelta = timedelta(seconds=difftime.seconds)

# Extraction des heures, minutes et secondes de la différence
diff_heure = diff_timedelta.seconds // 3600
diff_minute = (diff_timedelta.seconds % 3600) // 60
diff_seconde = diff_timedelta.seconds % 60
diff_format = "{:02d}:{:02d}:{:02d}".format(diff_heure, diff_minute, diff_seconde)

dicoretard[idbusretard] = diff_format
print(dicoretard)
print(diff_format)


def nouveaux_horaires(schedule_time, stops, trip_headsign_liste, day, trip_id_total):
    for k in range(len(stops) - 1):
        stop_id, stop_id_suiv = stops[k], stops[k + 1]
        fich = open("fichehoraire/" + str(stop_id) + ".csv")
        reader1 = csv.reader(fich)
        for row in reader1:
            trip_id, arrival_time, departure_time, stop_id, stop_sequence, trip_headsign = row
            if trip_id in trip_id_total:

                nbcolor = trip_headsign_liste.index(row[5])
                fich2 = open("fichehoraire/" + str(stop_id_suiv) + ".csv")
                reader2 = csv.reader(fich2)
                for row2 in reader2:
                    if row2[0] == trip_id:
                        next_arrival_time = row2[1]
                        if transformeheure(arrival_time) >= transformeheure("23:59:59"):
                            continue
                        if transformeheure(next_arrival_time) >= transformeheure("23:59:59"):
                            continue
                        arrival_time1 = datetime.strptime(arrival_time, "%H:%M:%S").time()
                        next_arrival_time1 = datetime.strptime(next_arrival_time, "%H:%M:%S").time()

                        if arrival_time1 <= datetime.strptime(schedule_time, "%H:%M:%S").time() <= next_arrival_time1:
                            if verifday(day, trip_id):
                                dicoprogress[trip_id].append(k)
                                pointinter(stop_id, stop_id_suiv, arrival_time, next_arrival_time, schedule_time,
                                           nbcolor, trip_id, 1)
                                break


pt_lat = []
pt_lon = []
colorlist = []
textlist = []
for elt in trip_headsign_liste:
    stops = find_stops(elt)
    trip_id_list = nouveaux_horaires(newhoraire, stops, trip_headsign_liste, day, trip_id_total)

# Convertir fig.data en liste
fig_data_list = list(fig.data)

# Supprimer la trace souhaitée
fig_data_list.remove(trace2)

# Reconvertir fig_data_list en tuple
fig.data = tuple(fig_data_list)


# Obtenir le nouvel indice du bus à l'arret
textliststop = trace2.text
for i, text in enumerate(textliststop):
    if text == idbusretard:
        special_point_index = i
        break

# Changer les attributs du bus à l'arret
colorlist[special_point_index] = "black"
pt_lat[special_point_index] = latretard
pt_lon[special_point_index] = lonretard

trace2 = go.Scattermapbox(
    mode="markers",
    lon=pt_lon,
    lat=pt_lat,
    marker=go.scattermapbox.Marker(size=19, color=colorlist),
    text=textlist
)

fig.add_trace(trace2)

fig.show()


def stopid_to_name(stop_id):
    fic = open('gtfs/stops.csv')
    f = csv.reader(fic)
    for row in f:
        if row[0] == str(stop_id):
            return row[2]

#Création des fiches horaires avec le retard
def fichehorairepostretard(schedule_time, stops, trip_id_total):
    fiche = open('resultretard/' + "retard" + '.csv', 'w', newline='')
    writer = csv.writer(fiche)

    writer.writerow(("trip_id", "arrival_time", "late_time", "stop_id", "stop_name", "trip_headsign"))
    writer = csv.writer(fiche, lineterminator='\n',
                        quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')
    for stop_id in stops:
        fich = open("fichehoraire/" + str(stop_id) + ".csv")
        reader1 = csv.reader(fich)
        for row in reader1:
            if row[0] in trip_id_total:
                horaireretard = dicoretard[row[0]]
                if horaireretard == 0:
                    horaireretard = "00:00:00"
                resultat = transformeheureinverse(transformeheure(str(horaireretard)) + transformeheure(str(row[1])))
                print(resultat)
                if datetime.strptime(resultat, "%H:%M:%S").time() >= datetime.strptime(schedule_time, "%H:%M:%S").time():
                    name = stopid_to_name(stop_id)
                    writer.writerow((row[0], row[1], dicoretard[row[0]], row[3], name, row[5]))


stops_total = []
for elt in trip_headsign_liste:
    stops = find_stops(elt)
    stops_total += stops

fichehorairepostretard(newhoraire, stops_total, trip_id_total)
print(dicoprogress)
