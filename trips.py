import csv

fic = open('gtfs/trips.csv')
f = csv.reader(fic)
dejavu = []
for ligne in f:
    if ligne[3] == 'trip_headsign':
        continue
    if ligne[3] not in dejavu:
        print(dejavu)
        dejavu.append(ligne[3])

        lignecsv = open('Trips/' + str(ligne[3]) + '.csv', 'w', newline='')
        writer = csv.writer(lignecsv)
        writer.writerow(('route_id', 'service_id', 'trip_id', 'trip_headsign', 'direction_id', 'block_id', 'shape_id'))
        writer = csv.writer(lignecsv, lineterminator='\n',
                            quoting=csv.QUOTE_NONE, quotechar=None, escapechar='\\')


        fic2 = open('gtfs/trips.csv')
        f2 = csv.reader(fic2)
        for ligne2 in f2:
            if ligne2[3]==ligne[3]:
                writer.writerow(ligne2)

        fic2.close()
fic.close()