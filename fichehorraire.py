import csv



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
print(dico)




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
    print("done")
    f.close()
    fiche.close()


for liste_arrets in dico.values():
    for elts in liste_arrets:
        fiche_horaire(elts)








'''

def fiche_horraire(stop_id):
    fiche = open('fichehorraire/' + stop_id +'.csv', 'w', newline='')
    writer = csv.writer(fiche)


    writer.writerow(("trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence", "pickup_type","drop_off_type"))
    writer = csv.writer(fiche, lineterminator='\n',
                       quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')



    f = open('gtfs\stop_times.csv')
    read = csv.reader(f)
    for ligne in read:
        if ligne[3] == stop_id:
            writer.writerow(ligne)
    print("done")
    f.close()
    fiche.close()


for liste_arrets in dico.values():
    for elts in liste_arrets:
        fiche_horraire(elts)

'''