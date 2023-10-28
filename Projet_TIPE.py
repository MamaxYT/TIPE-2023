#Importations nécessaires à tout le TIPE#
from math import *
import csv
import networkx as nx
import pandas as pa
import plotly.graph_objects as go
import bellmanford as bf
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
import random as rd
###

###Traitements des sommets du graphe###
f = open('stops.csv')

lignecompt = 0
arrets = []
nomdejavu = []
for ligne in f:
    tempo = []
    if (lignecompt >= 1):
        x = ligne.split(",")
        if x[2] not in nomdejavu:
            tempo.append(x[2])
            nomdejavu.append(x[2])
            tempo.append(x[4])
            tempo.append(x[5])
            arrets.append(tempo)

    lignecompt +=1


f.close()

fic = open("bus_metz.csv", "w", newline="")

writer = csv.writer(fic)
writer.writerow(("name","lat","lon","display_name"))
writer = csv.writer(fic, lineterminator='\n',
                    quoting=csv.QUOTE_NONE, quotechar=None)

#Fonction pour créer le nom d'affichage
def transname(name):
    newname = name.replace(" ","<br>")
    diplayname = []
    listename = list(newname)
    for j in range(len(listename)):
        if listename[j] != ('"' or ' '):

            diplayname.append(listename[j])

    final = "".join(diplayname)
    return final

for i in range(len(arrets)):
    name,lat,lon= arrets[i]
    diplayname = transname(name)
    writer.writerow((name, lat, lon, diplayname))

fic.close()

###Traitement des arêtes du graphe##

url = [
    ['A', 'Lignes\mettis a.csv'],
    ['B', 'Lignes\mettis b.csv'],
    ['1', 'Lignes\l1.csv'],
    ['2', 'Lignes\l2.csv'],
    ['3', 'Lignes\l3.csv'],
    ['4', 'Lignes\l4 normal.csv'],
    ['4a', 'Lignes\l4a.csv'],
    ['4b', 'Lignes\l4b.csv'],
    ['5', 'Lignes\l5 normal.csv'],
    ['5e', 'Lignes\l5e.csv'],
    ['5f', 'Lignes\l5f.csv']
]

arrets = []
def ajoutligne(lignebus):
    f = open(lignebus[1])
    lignecompt = 0
    for ligne in f:
        tempo = []
        if (lignecompt >= 1):
            x = ligne.split(",")
            tempo.append(lignebus[0])
            tempo.append(x[2])
            arrets.append(tempo)

        lignecompt += 1

    f.close()


for k in range(len(url)):
    ajoutligne(url[k])

fic = open('bus_metz_lignes.csv', 'w', newline='')

writer = csv.writer(fic)
writer.writerow(('line', 'station_name1', 'station_name2', 'distance'))
writer = csv.writer(fic, lineterminator='\n',
                    quoting=csv.QUOTE_NONE, quotechar=None)

def arretsuivant(arrets, i):
    line, arret = arrets[i]
    if (i+1)< len(arrets):
        linesuiv, arretsuiv = arrets[i + 1]
        if line == linesuiv:
            return True, arretsuiv
        else:
            return False, arretsuiv

def deg2rad(dd):

    return float(dd)/180*pi

def distance(arret,arretsuiv):

    fichier = open('bus_metz.csv')
    lignecompteur = 0
    for ligne in fichier:
        x = ligne.split(",")
        if lignecompteur >= 1:
            if x[0] == arret:
                latA = deg2rad(x[1])
                longA = deg2rad(x[2])

            if x[0] == arretsuiv:
                latB = deg2rad(x[1])
                longB = deg2rad(x[2])

        lignecompteur += 1
    RT = 6378137
    S = acos(sin(latA) * sin(latB) + cos(latA) * cos(latB) * cos(abs(longB - longA)))
    # distance entre les 2 points, comptée sur un arc de grand cercle
    fichier.close()
    return int(S * RT)

for i in range(len(arrets)):

    line, arret = arrets[i]
    statut, arretsuiv = arretsuivant(arrets, i)

    newarret = arret.replace('"','')
    newarretsuiv = arretsuiv.replace('"', '')

    if statut == True:
        dist = distance(arret, arretsuiv)
        writer.writerow((line , newarret , newarretsuiv,dist))

fic.close()



### Visualisation de la première approche ###

T = pa.read_csv('bus_metz_lignes_backup.csv')

G = nx.from_pandas_edgelist(T, source='station_name1', target='station_name2', edge_attr='distance')
M = pa.read_csv('bus_metz_backup.csv')

fig = go.Figure()

fig.add_trace(
    go.Scattergeo(
        mode='markers + text',
        lon=M['lon'],
        lat=M['lat'],
        text=M['display_name'].apply(lambda x: \
                                         '<b>' + str(x) \
                                         + '</b>'),
        textposition='middle center',
        textfont=dict(color="black", size=8, family='bold'),
        showlegend=False,
        marker={'symbol': 'circle-dot',
                'size': 30,
                'opacity': 0.8,
                'color': 'gray'}
    )
)
fig.update_layout(
    showlegend=True,
    legend={'x': 0,
            'y': 0.1,
            'title': '<b>Lignes : </b>',
            'orientation': 'h',
            'bordercolor': 'gray',
            'font': {'family': 'Verdana', 'size': 14},
            'borderwidth': 2,
            },
    title={'text': "<b>Lignes de Bus à Metz</b>",
           'font': {'family': 'Verdana'},
           'y': 0.93,
           'x': 0.5}
)
fig.update_geos(
    fitbounds='locations',
    showland=True,
    landcolor='white',
    projection_type='natural earth'
)


N = M.groupby('name').first()

T['x1'] = [N.loc[n, 'lon'] for n in T['station_name1']]
T['y1'] = [N.loc[n, 'lat'] for n in T['station_name1']]
T['x2'] = [N.loc[n, 'lon'] for n in T['station_name2']]
T['y2'] = [N.loc[n, 'lat'] for n in T['station_name2']]

couleurs = ['black', 'green', 'blue', 'red', 'chocolate']
dot = ['dot', 'solid']
L= []
ListeLigne = ["A","B","1","2","3","4","4a","4b","5","5e","5f"]
compteur=0
for i in ListeLigne:
    A = T.query('line == @i')
    for k in A.index:
        fig.add_trace(
            go.Scattergeo(
                mode = 'lines',
                lon = [A.loc[k, 'x1'], A.loc[k, 'x2']],
                lat = [A.loc[k, 'y1'], A.loc[k, 'y2']],
                hovertext = A['distance'],
                opacity= 0.5,
                showlegend= True if i not in L else False,
                name = i,
                line = {'color' : couleurs[compteur%5 - 1],
                        'dash' : dot[compteur%2],
                        'width' : 4}
                        )
            )
        L.append(i)
    compteur += 1

fig.show()


### Algorithme du plus court chemin en fonction des distances###

def transname(name):
    diplayname = []
    listename = list(name)
    for j in range(len(listename)):
        if listename[j] != ('"' or ' '):

            diplayname.append(listename[j])

    final = "".join(diplayname)
    return final


dico = {}
arrets = open('gtfs\stops.csv')
read = csv.reader(arrets)
for ligne in read:
    if ligne[2] == 'stop_name':
        continue
    if transname(ligne[2]) not in dico:
        dico[transname(ligne[2])] = [ligne[0]]
    else:
        listetempo = dico[transname(ligne[2])]
        dico[transname(ligne[2])] = listetempo + [ligne[0]]

arrets.close()

T = pa.read_csv('bus_metz_lignes_backup.csv')
G = nx.from_pandas_edgelist(T, source='station_name1', target='station_name2', edge_attr='distance')

longueur, noeuds, cyclenegatif = bf.bellman_ford(G, source="GARE", target="PEUPLIERS", weight="distance")
print("Distance la plus courte: {0}".format(longueur))
print("Chemin le plus court: {0}".format(noeuds))


##Traitement de données des lignes##
##Tri de toutes les lignes##

fic = open('gtfs/trips.csv')
f = csv.reader(fic)
dejavu = []
for ligne in f:
    if ligne[3] == 'trip_headsign':
        continue
    if ligne[3] not in dejavu:
        dejavu.append(ligne[3])

        lignecsv = open('Lignes2/'+str(ligne[3])+'.csv', 'w', newline='')
        writer = csv.writer(lignecsv)
        writer.writerow(('stop_id',))
        writer = csv.writer(lignecsv, lineterminator='\n',
                            quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')

        trip_id = ligne[2]
        temps = open('gtfs/stop_times.csv')
        read = csv.reader(temps)
        for ligne1 in read:
            if ligne1[0] == trip_id:
                writer.writerow((ligne1[3], ))
        lignecsv.close()

fic.close()

##Création des fiches horraires pour tous les arrêts du réseau##

fic = open('bus_metz_lignes.csv', 'w', newline='')

writer = csv.writer(fic)
writer.writerow(('line', 'station_name1', 'station_name2', 'distance'))
writer = csv.writer(fic, lineterminator='\n',
                    quoting=csv.QUOTE_NONE, quotechar=None)


def transname(name):
    diplayname = []
    listename = list(name)
    for j in range(len(listename)):
        if listename[j] != ('"' or ' '):

            diplayname.append(listename[j])

    final = "".join(diplayname)
    return final




dico = {}
arrets = open('gtfs\stops.csv')
read = csv.reader(arrets)
for ligne in read:
    if ligne[2] == 'stop_name':
        continue
    if transname(ligne[2]) not in dico:
        dico[transname(ligne[2])] = [ligne[0]]
    else:
        listetempo = dico[transname(ligne[2])]
        dico[transname(ligne[2])] = listetempo + [ligne[0]]

arrets.close()

def fiche_horaire(stop_id):
    fiche = open('fichehoraire/' + stop_id +'.csv', 'w', newline='')
    writer = csv.writer(fiche)


    writer.writerow(("trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence","trip_headsign"))
    writer = csv.writer(fiche, lineterminator='\n',
                       quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')



    f = open('gtfs\stop_times.csv')
    read = csv.reader(f)
    for ligne in read:
        if ligne[3] == stop_id:
            fich = open('gtfs/trips.csv')
            read2 = csv.reader(fich)
            for ligne2 in read2:
                if ligne2[2]==ligne[0]:
                    writer.writerow((ligne[0],ligne[1],ligne[2],ligne[3],ligne[4],ligne2[3]))
                    break
    f.close()
    fiche.close()


for liste_arrets in dico.values():
    for elts in liste_arrets:
        fiche_horaire(elts)


##Algorithme de plus court chemin à l'aide des horaires##

f = open('gtfs/stops.csv')
depart = input("Quel est le lieu de départ: ")
verif = False
for ligne in f:
    if depart in ligne:
        verif = True

if verif == False:
    raise ValueError("Mauvais nom d'arrêt")
f.close()

f = open('gtfs/stops.csv')
arrivee = input("Quel est le lieu d'arrivee: ")

verif2 = False
for ligne in f:
    if arrivee in ligne:
        verif2 = True

if verif2 == False:
    raise ValueError("Mauvais nom d'arrêt")
f.close()
jour = input("Quel jour: ")
heure = input("Quelle heure (Format HH:MM:SS):  ")


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


def transformeheure(heure):
    h = heure.split(":")
    return int(h[0]) * 3600 + int(h[1]) * 60 + int(h[2])


def transformeheureinverse(temps):
    heures = temps // 3600
    minutes = (temps % 3600) // 60
    secondes = temps % 60

    temps_formatte = "{:02d}:{:02d}:{:02d}".format(heures, minutes, secondes)
    return temps_formatte


def transname(name):
    diplayname = []
    listename = list(name)
    for j in range(len(listename)):
        if listename[j] != ('"' or ' '):
            diplayname.append(listename[j])

    final = "".join(diplayname)
    return final


dico = {}
arrets = open('gtfs\stops.csv')
read = csv.reader(arrets)
for ligne in read:
    if ligne[2] == 'stop_name':
        continue
    if transname(ligne[2]) not in dico:
        dico[transname(ligne[2])] = [ligne[0]]
    else:
        listetempo = dico[transname(ligne[2])]
        dico[transname(ligne[2])] = listetempo + [ligne[0]]

arrets.close()


def diffheure(h1, h2):
    return transformeheure(h1) - transformeheure(h2)


def min_dif(liste, heure_min_dif):
    if liste == []:
        return None
    minimum = liste[0]
    for elt in liste:
        if diffheure(elt[1], heure_min_dif) < diffheure(minimum[1], heure_min_dif):
            minimum = elt
    return minimum


def recherche_heure(trip_headsign, stop_id, day, heure):
    f = open('fichehoraire/' + str(stop_id) + '.csv')
    fic = csv.reader(f)
    listeheure = []
    for ligne in fic:
        if verifday(day, ligne[0]):
            if ligne[5] == trip_headsign:
                if transformeheure(ligne[1]) >= transformeheure(heure):
                    listeheure.append(ligne)
    return min_dif(listeheure, heure)


dicodejavu = {}
arrets = open('gtfs/stops.csv')
arretsR = csv.reader(arrets)
for ligne in arretsR:
    if ligne[2] in dicodejavu:
        continue
    dicodejavu[ligne[2]] = False

fic2 = open('gtfs/trips.csv')
f2 = csv.reader(fic2)
liste_trip_id = []
dico_trip_id = {}

for ligne in f2:
    if ligne[3] == 'trip_headsign':
        continue
    if ligne[3] not in liste_trip_id:
        liste_trip_id.append(ligne[3])
        dico_trip_id[ligne[3]] = [None, None]

fic2.close()


def ponderation(trip, stop_id_arrivee, heure_depart, day):
    result = recherche_heure(trip, stop_id_arrivee, day, heure_depart)
    return diffheure(result[1], heure_depart)


def ponderation2(trip_id, stop_id_suiv):
    fic = open('fichehoraire/' + str(stop_id_suiv) + '.csv')
    f = csv.reader(fic)
    for ligne in f:
        if ligne[0] == trip_id:
            return ligne


def arret_suivant(trip_id, stop_id):  # Renvoie l'arret suivant d'une ligne donnée
    fic = open('Lignes2/' + str(trip_id) + '.csv')
    f = csv.reader(fic)
    compteur = 0
    for ligne in f:
        if compteur == 1:
            return ligne[0]
        if ligne[0] == stop_id:
            compteur += 1

    return None
    fic.close()


fic = open('bus_metz_lignes.csv', 'w', newline='')

writer = csv.writer(fic)
writer.writerow(('line', 'station_name1', 'station_name2', 'time', 'name_depart'))
writer = csv.writer(fic, lineterminator='\n',
                    quoting=csv.QUOTE_NONE, quotechar=None)


def min_ponderation(liste):
    mini = min(liste, key=lambda x: x[1])
    return mini


def min_ponderation2(liste):
    mini = min(liste, key=lambda x: transformeheure(x[1]))
    return mini


def evo(dico):
    compttot = len(dico)
    compt = 0
    for elts in dico.items():
        if elts[1] == True:
            compt += 1
    print(str(compt) + "/" + str(compttot))


#

def verif_en_arriere(ligne, dico):
    stop_id = ligne[3]
    trip_headsign = ligne[5]
    if dico[ligne[5]] == [None,None]:
        return False
    stop_id_decouverte = dico[ligne[5]][1]
    fic = open('Lignes2/' + str(trip_headsign) + '.csv')
    f = csv.reader(fic)
    compteur = 0
    for row in f:

        if row[0] == stop_id_decouverte:
            if compteur == 1:
                return False
            else:
                return True

        if row[0] == stop_id:
            compteur += 1
    fic.close()

def verif_en_arriere2(ligne, dico):
    stop_id = ligne[3]

    trip_headsign = ligne[5]
    if dico[ligne[5]] == [None,None]:
        return False
    stop_id_decouverte = dico[ligne[5]][1]
    if stop_id == stop_id_decouverte:
        return False
    fic = open('Lignes2/' + str(trip_headsign) + '.csv')
    f = csv.reader(fic)
    compteur = 0
    for row in f:
        if row[0] == stop_id_decouverte:
            if compteur == 1:
                return True
            else:
                return False

        if row[0] == stop_id:
            compteur += 1
    fic.close()



statut = False
liste_mini = []

dicotripidtemps = {}
def letestmeilleur(info,elt):
    trip_id_avant = info[0]
    stop_id_decouverte_avant = info[1]
    fich2 = open('fichehoraire/' + stop_id_decouverte_avant + '.csv')
    f = csv.reader(fich2)
    next(f)
    h1 = None
    h2 = None
    for row in f:
        if row[0] == trip_id_avant:
            h1 = transformeheure(row[1])
        if row[0] == elt[0]:
            h2 = transformeheure(row[1])
    if h1 == None or h2 == None:
        return False
    if h2<h1:
        return True
    else:
        return False

    fich2.close()


def creation_arretes(stop_name_D, stop_name_A, heure, day):
    print("Départ: ", stop_name_D, "heure: ",heure)
    global statut

    if statut:
        return
    liste_stop_id_D = dico[stop_name_D]
    liste_trip_headsign_depart = []  # Toutes les lignes qui passent par l'arrêt de départ

    for elt in liste_trip_id:  # Remplissage de la liste trip_headsign
        for stop_id in liste_stop_id_D:
            fic = open('Lignes2/' + str(elt) + '.csv')
            f = csv.reader(fic)
            for ligne in f:
                if ligne[0] == stop_id:
                    liste_trip_headsign_depart.append(elt)
                    break
            fic.close()

    #Liste des candidats possibles, cela donne l'horaire la plus proche
    #pour chaque ligne.
    liste_tempo = []
    for trip in liste_trip_headsign_depart:
        for stop_id in liste_stop_id_D:

            result = recherche_heure(trip, stop_id, day, heure)
            if result == None:
                continue
            liste_tempo.append(result)

    # Si une ligne n'a jamais été vue, ajouté le trip_id de découverte, et le stop_id qui a fait la découverte.
    for elt in liste_tempo:
        if dico_trip_id[elt[5]] == [None, None]:
            dico_trip_id[elt[5]] = [elt[0], elt[3]]
        elif elt[1] != dico_trip_id[elt[5]][0] and dico_trip_id[elt[5]] != [None, None]:
            if letestmeilleur(dico_trip_id[elt[5]],elt):
                dico_trip_id[elt[5]] = [elt[0], elt[3]]


    liste_recherche_heure = []
    for stop_id in liste_stop_id_D:
        for elt in liste_trip_headsign_depart:
            trip_id = dico_trip_id[elt]
            ligne = ponderation2(trip_id[0], stop_id)
            if ligne == None:
                continue
            if verif_en_arriere(ligne, dico_trip_id):
                liste_recherche_heure.append(ligne)

    if liste_recherche_heure == []:
        return

    minimum = min_ponderation2(liste_recherche_heure)
    liste_mini.append(minimum)

    newheure = minimum[1]
    if stop_name_D == stop_name_A:
        statut = True
        fin(stop_name_D, stop_name_A, liste_mini, newheure)


    #Remplir la liste des arrêts suivants à l'arrêt considéré
    liste_stop_id_suiv = []
    for result in liste_tempo:
        for stop_id in liste_stop_id_D:

            stop_id_suiv = arret_suivant(result[5], stop_id)
            if stop_id_suiv == None:
                continue
            if stop_id_suiv in liste_stop_id_suiv:
                continue

            liste_stop_id_suiv.append(stop_id_suiv)


    liste_tempo_suiv = []
    for stop_id_suiv in liste_stop_id_suiv:
        liste_trip_headsign_suiv = []  # Liste des trip_headsign qui sont à l'arrêt suivent
        for elt in liste_trip_id:
            fic = open('Lignes2/' + str(elt) + '.csv')
            f = csv.reader(fic)
            for ligne in f:
                if ligne[0] == stop_id_suiv:
                    liste_trip_headsign_suiv.append(elt)
                    break
            fic.close()

        for elt in liste_trip_headsign_suiv:
            if dico_trip_id == [None, None]:
                continue
            trip_id = dico_trip_id[elt][0]
            result = ponderation2(trip_id, stop_id_suiv)
            if result == None:
                continue
            if verif_en_arriere2(result, dico_trip_id):
                continue

            temps_total = diffheure(result[1], newheure)
            if dicodejavu[stopid_to_name(stop_id_suiv)] == True:
                continue

            liste_tempo_suiv.append([stop_id_suiv, temps_total, stopid_to_name(stop_id_suiv)])

    dicodejavu[stop_name_D] = True
    evo(dicodejavu)

    liste_tempo_suiv_triee = sorted(liste_tempo_suiv, key=lambda x: x[1])

    for elt in liste_tempo_suiv_triee:
        stop_id_suiv2 = elt[0]
        temps = elt[1]
        stop_name_suiv_liste = [k for k, v in dico.items() if stop_id_suiv2 in v]
        stop_name_suiv = stop_name_suiv_liste[0]
        if dicodejavu[stop_name_suiv] == True:
            continue
        creation_arretes(stop_name_suiv, stop_name_A, transformeheureinverse(transformeheure(newheure) + temps), day)


def stopid_to_name(stop_id):
    fic = open('gtfs/stops.csv')
    f = csv.reader(fic)
    for row in f:
        if row[0] == str(stop_id):
            return row[2]


# Faire un dico avec tous les trip_id parcourus avec le temps qui correspond

pathtot = []
chemin_trip_id = []
def fin(stop_name_D, stop_name_A, liste_mini, newheure):
    global pathtot
    trip_id_ini, heure, _, stop_id, _, trip_headsign = liste_mini[len(liste_mini) - 1]
    trip_id_debut = liste_mini[0][0]
    stopiddebut = liste_mini[0][3]
    path = []
    def aux(trip_id, stop_id, trip_headsign):
        path = []
        global chemin_trip_id
        global pathtot
        info_avant = [v for k, v in dico_trip_id.items() if trip_id in v]
        stop_id_avant = info_avant[0][1]

        fich = open('Lignes2/' + str(trip_headsign) + '.csv')
        f = csv.reader(fich)
        next(f)
        statusboucle = False
        for ligne in f:

            if int(ligne[0]) == int(stop_id_avant):
                statusboucle = True
            if statusboucle:
                path.append(int(ligne[0]))
            if int(ligne[0]) == int(stop_id):
                statusboucle = False


        # comparer les noms
        for k in liste_mini:
            if stopid_to_name(k[3]) == stopid_to_name(stop_id_avant):
                next_info = k


        nexttrip_id = next_info[0]
        nexttripheadsign = next_info[5]
        nextstop_id = next_info[3]

        #Récupérer les correspondances
        trip_id_corr = info_avant[0][0]
        stop_id_corr = info_avant[0][1]
        fic = open('fichehoraire/' + str(stop_id_corr) + '.csv')
        f = csv.reader(fic)
        for ligne in f:
            if ligne[0] == trip_id_corr:
                chemin_trip_id = [ligne[5],stopid_to_name(ligne[3]),ligne[1]] + chemin_trip_id
        pathtot = path + pathtot
        if nextstop_id == stopiddebut:
            chemin_stop_name = [stopid_to_name(i) for i in pathtot]
            print("Heure d'arrivée :", newheure)
            print('Chemin final :', chemin_stop_name)
            print("Correspondances: ", chemin_trip_id)
            return
        else:
            aux(nexttrip_id, nextstop_id, nexttripheadsign)

    aux(trip_id_ini, stop_id, trip_headsign)

creation_arretes(depart, arrivee, heure, day)

##Création d'un fichier qui contient tous les arrêts de tout le réseau##

fich = open('gtfs/stops.csv')
f = csv.reader(fich)

lignecompt = 0
arrets = []
nomdejavu = []
for ligne in f:
    tempo = []
    if (lignecompt >= 1):
        tempo.append(ligne[2])
        tempo.append(ligne[4])
        tempo.append(ligne[5])
        tempo.append(ligne[0])
        arrets.append(tempo)

    lignecompt +=1


fich.close()

fic = open("bus_metz.csv", "w", newline="")

writer = csv.writer(fic)
writer.writerow(("stop_id","lat","lon","display_name"))
writer = csv.writer(fic, lineterminator='\n',
                    quoting=csv.QUOTE_NONE, quotechar=None)


def transname(name):
    newname = name.replace(" ","<br>")
    diplayname = []
    listename = list(newname)
    for j in range(len(listename)):
        if listename[j] != ('"' or ' '):

            diplayname.append(listename[j])

    final = "".join(diplayname)
    return final

for i in range(len(arrets)):
    name,lat,lon, stop_id = arrets[i]
    diplayname = transname(name)
    writer.writerow((stop_id, lat, lon, diplayname))

fic.close()

##Création du nouveau visuel##

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
        correspondence = {Listetempo_stop_id_of_one_trip: order for order, Listetempo_stop_id_of_one_trip in
                          enumerate(Listetempo_stop_id_of_one_trip)}
        return col.map(correspondence)


    Mtemp.sort_values(by="stop_id", key=lambda column: column.map(lambda e: Listetempo_stop_id_of_one_trip.index(e)),
                      inplace=True)

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

##Algorithme de gestion du retard##

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
    if statut == 1 and dicoprogress[trip_id][0] <= dicoprogress[idbusretard][0] <= dicoprogress[trip_id][2] \
            and dicoverif[trip_id] == dicoverif[idbusretard] and statutdepassement == 1:
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
trip_id_total = []
for elt in trip_headsign_liste:
    stops = find_stops(elt)
    trip_id_list = get_trip_id(schedule, stops, trip_headsign_liste, day)
    trip_id_total += trip_id_list

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
                resultat = transformeheureinverse(transformeheure(str(horaireretard)) +
                                                  transformeheure(str(row[1])))
                if datetime.strptime(resultat, "%H:%M:%S").time() >= datetime.strptime\
                            (schedule_time, "%H:%M:%S").time():
                    name = stopid_to_name(stop_id)
                    writer.writerow((row[0], row[1], dicoretard[row[0]], row[3], name, row[5]))


stops_total = []
for elt in trip_headsign_liste:
    stops = find_stops(elt)
    stops_total += stops

fichehorairepostretard(newhoraire, stops_total, trip_id_total)
