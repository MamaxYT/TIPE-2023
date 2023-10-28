import csv

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

print(arrets)
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