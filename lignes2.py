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
