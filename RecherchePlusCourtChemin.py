import csv

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
    #print(ligne)
    trip_headsign = ligne[5]
    if dico[ligne[5]] == [None,None]:
        return False
    stop_id_decouverte = dico[ligne[5]][1]
    fic = open('Lignes2/' + str(trip_headsign) + '.csv')
    f = csv.reader(fic)
    compteur = 0
    for row in f:
        #print("ligne0", row, "stopiddecouverte", stop_id_decouverte)
        #print(compteur)

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
        #print("ligne0", row, "stopiddecouverte", stop_id_decouverte)
        #print(compteur)
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

'''def comparetrip_id(trip_id,trip_headsign,trip_id1, stop_id):
    fich2 = open('fichehoraire/' + stop_id + '.csv')
    f2 = csv.reader(fich2)
    next(f2)
    print(trip_id,trip_id1, trip_headsign)
    for ligne2 in f2:
        if trip_id in ligne2:
            info1 = ligne2
        if trip_id1 in ligne2:
            info2 = ligne2

    if transformeheure(info1[1]) < transformeheure(info2[1]):       #si le nouveau trip_id est mieux que l'ancien :
        return True'''


dicotripidtemps = {}
def letestmeilleur(info,elt):
    trip_id_avant = info[0]
    stop_id_decouverte_avant = info[1]
    fich2 = open('fichehoraire/' + stop_id_decouverte_avant + '.csv')
    f = csv.reader(fich2)
    next(f)
    print(stop_id_decouverte_avant)
    print(trip_id_avant)
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
            print(dico_trip_id[elt[5]],elt)
            if letestmeilleur(dico_trip_id[elt[5]],elt):
                dico_trip_id[elt[5]] = [elt[0], elt[3]]

    print("dicoo", dico_trip_id)
    # print(liste_trip_headsign_depart)

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
    # print("minimum", minimum)
    newheure = minimum[1]
    print(minimum)
    print(newheure)
    if stop_name_D == stop_name_A:
        statut = True
        fin(stop_name_D, stop_name_A, liste_mini, newheure)
        # print(liste_tempo)
        # raise ValueError("Fin du graphe :)")

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

    #print(liste_stop_id_suiv)
    #print(liste_tempo)

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

        # print(liste_trip_headsign_suiv)
    dicodejavu[stop_name_D] = True
    evo(dicodejavu)
    print("lt", liste_tempo)

    liste_tempo_suiv_triee = sorted(liste_tempo_suiv, key=lambda x: x[1])
    print("lts", liste_tempo_suiv_triee)
    for elt in liste_tempo_suiv_triee:
        stop_id_suiv2 = elt[0]
        temps = elt[1]
        stop_name_suiv_liste = [k for k, v in dico.items() if stop_id_suiv2 in v]
        stop_name_suiv = stop_name_suiv_liste[0]
        if dicodejavu[stop_name_suiv] == True:
            continue
        print(stop_name_suiv)
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
    # print(liste_mini[len(liste_mini) - 1])
    # print("listemini", liste_mini)
    path = []
    def aux(trip_id, stop_id, trip_headsign):
        path = []
        global chemin_trip_id
        global pathtot
        info_avant = [v for k, v in dico_trip_id.items() if trip_id in v]
        print("infoavant", info_avant)
        stop_id_avant = info_avant[0][1]
        #       if trip_id == info_avant[0][0]:
        #           print("TETEZETETE")

        fich = open('Lignes2/' + str(trip_headsign) + '.csv')
        f = csv.reader(fich)
        next(f)
        statusboucle = False
        print("lalalaal", stop_id_avant, stop_id)
        for ligne in f:
            print(path)
            if int(ligne[0]) == int(stop_id_avant):
                statusboucle = True
            if statusboucle:
                path.append(int(ligne[0]))
            if int(ligne[0]) == int(stop_id):
                statusboucle = False

        print(liste_mini)
        # comparer les noms
        for k in liste_mini:
            if stopid_to_name(k[3]) == stopid_to_name(stop_id_avant):
                next_info = k
                print("nextinfo", next_info)

        # next_info = [k for k in liste_mini if str(stop_id_avant) in k]

        nexttrip_id = next_info[0]
        nexttripheadsign = next_info[5]
        nextstop_id = next_info[3]
        #  if nexttripheadsign != trip_headsign
        print("nexttripid", nexttrip_id)
        print("nexttripheadsign", nexttripheadsign)
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


'''
def creation_arretes(stop_name, heure, day):
    liste_stop_id = dico[stop_name]
    liste_stop_id_suiv = []

    liste_trip_headsign_depart = []
    for stop_id in liste_stop_id:
          # Liste des trip_id que l'on va explorer

        for elt in liste_trip_id:  # Remplissage de la liste trip_id
            fic = open('Lignes2/' + str(elt) + '.csv')
            f = csv.reader(fic)
            for ligne in f:
                if ligne[0] == stop_id:
                    liste_trip_headsign_depart.append(elt)
                    break
            fic.close()

        liste_tempo = []
        for trip in liste_trip_headsign_depart:
            result = recherche_heure(trip,stop_id,day,heure)
            if result == None:
                continue
            liste_tempo.append(result)

        result2 = min_dif(liste_tempo,heure)
        if result2 == None:
            break
        stop_id_suiv = arret_suivant(result2[5],stop_id)
        if stop_id_suiv == None:
            break
        if dicodejavu[stop_id_suiv] == True:
            break

        info_arret_suiv = ponderation2(result2[0],stop_id_suiv)

        temps_entre_deux_stop = diffheure(info_arret_suiv[1],result2[1])

        temps_total = temps_entre_deux_stop + diffheure(result2[1],heure)
        liste_stop_id_suiv.append([stop_id_suiv, temps_total])
        writer.writerow((result2[5],stop_id,stop_id_suiv,temps_total,stop_name))
        dicodejavu[stop_id] = True

    evo(dicodejavu)

    for elt in liste_stop_id_suiv:
        stop_id_suiv2=elt[0]
        temps=elt[1]
        stop_name_suiv_liste = [k for k, v in dico.items() if stop_id_suiv2 in v]
        stop_name_suiv = stop_name_suiv_liste[0]
        if stop_name_suiv == arrivee:
            return
        print(stop_name_suiv)
        creation_arretes(stop_name_suiv, transformeheureinverse(transformeheure(heure) + temps), day)










def creation_arretes_nul(stop_name, heure, day):
    liste_stop_id = dico[stop_name]             #Liste des stop_id qui correspondent à l'arret stop name
    liste_trip_id_depart = []                   #Liste des trip_id que l'on va explorer
    for stop_id in liste_stop_id:
        for elt in liste_trip_id:               #Remplissage de la liste trip_id
            fic = open('Lignes2/'+str(elt)+'.csv')
            f = csv.reader(fic)
            for ligne in f:
                if ligne[0] == stop_id:
                    liste_trip_id_depart.append(elt)
                    break
            fic.close()


    for stop_id in liste_stop_id:
        liste_tempo=[]
        for trip_id in liste_trip_id_depart:
            stop_id_suiv = arret_suivant(trip_id,stop_id)
            if stop_id_suiv == None:
                break
            if dicodejavu[stop_id_suiv] == True:
                break

            temps = ponderation(trip_id,stop_id_suiv,heure,day)
            liste_tempo.append([trip_id,stop_id,stop_id_suiv,temps])

        print(liste_tempo)
        mini = min_ponderation(liste_tempo)
        writer.writerow((mini[0],mini[1],mini[2],mini[3]))

    dicodejavu[stop_id] = True
    for stop_id in liste_stop_id:
        for trip_id in liste_trip_id_depart:
            stop_id_suiv = arret_suivant(trip_id, stop_id)
            if stop_id_suiv == None:
                break
            if dicodejavu[stop_id_suiv] == True:
                break
            print("Coucou")
            stop_name_suiv_liste = [k for k, v in dico.items() if stop_id_suiv in v]
            stop_name_suiv = stop_name_suiv_liste[0]
            temps = ponderation(stop_id_suiv, heure, day)
            creation_arretes(stop_name_suiv,transformeheureinverse(transformeheure(heure)+temps), day)




'''
creation_arretes(depart, arrivee, heure, day)
