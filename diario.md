# Diario di sviluppo

## Comuni

Partiamo dalle basi dati: i comuni.

Fonte: [Ministero dell'interno](https://dait.interno.gov.it/territorio-e-autonomie-locali/sut/elenco_codici_comuni.php)

Ho esportato a mano i dati su `comuni.csv`.

### Codice

     python init_comuni.py

Questo popola la tabella `comuni(id, nome, provincia, elettorale, istat, belfiore)`.  
Ho tenuto i tutti i vari codici, perché non si sa mai.  
L'id è il numero della riga, perché non avevo altre idee all'inizio,
non sapevo cosa avrei riutilizzato o sarebbe stato più utile,
purtroppo il solo nome del comune non basta perché ci sono comuni omonimi:

- Castro [\[1\]](https://it.wikipedia.org/wiki/Castro_\(Lombardia\)) [\[2\]](https://it.wikipedia.org/wiki/Castro_\(Puglia\))
- Livo [\[1\]](https://it.wikipedia.org/wiki/Livo_\(Lombardia\)) [\[2\]](https://it.wikipedia.org/wiki/Livo_\(Trentino-Alto_Adige\))
- Peglio [\[1\]](https://it.wikipedia.org/wiki/Peglio_\(Lombardia\)) [\[2\]](https://it.wikipedia.org/wiki/Peglio_\(Marche\))
- Samone [\[1\]](https://it.wikipedia.org/wiki/Samone_\(Piemonte\)) [\[2\]](https://it.wikipedia.org/wiki/Samone_\(Trentino-Alto_Adige\))
- San Teodoro [\[1\]](https://it.wikipedia.org/wiki/San_Teodoro_\(Sicilia\)) [\[2\]](https://it.wikipedia.org/wiki/San_Teodoro_\(Sardegna\))

## Capoluoghi

Altro dato piatto, sapere quali città sono capoluoghi:

Fonte: [Wikipedia](https://it.wikipedia.org/wiki/Capoluogo_(Italia)#Lista_dei_capoluoghi_di_regione_e_provincia_o_citt%C3%A0_metropolitana_italiani)

Ho esportato a mano i dati su `capoluoghi.csv`.

## Codice

     python init_capoluoghi.py

Questo popola la tabella `capoluoghi(id)`.  
Con gli id dei comuni che sono capoluoghi.

## Coordinate

Ora mi serve associare ad ogni comune le coordinate, due strade:

### Coordinates Finder

Ho caricato la lista dei comuni su questo sito e ottenuto [questo risultato](https://www.coordinatesfinder.com/results/v8JTFUv85eVKy7eQ9DgL).

Per alcuni ci sono errori o non trovati, per cui la seconda opzione.

### GeoApify

Per tutti i casi non gestiti o con errori di _Coordinate Finder_, ho usato le API di _GeoApify_
(mi sono precedentemente registrato con il profilo free).

### Codice

    python missing_coords.py

Sfoglia il file `geoname.csv`,
se trova una riga con una solo colonna (cioè il comune e non le coordinate)
chiede a _GeoApify_ le coordinate di quel comune, salvandole nello stesso file.

    python init_coords.py

Carica i dati sia da Coordinates Finder che da GeoApify.

## Il capoluogo più vicino

Ora si entra nel vivo, devo accoppiare ogni comune con il capoluogo più vicino.

Prima di tutto cerco il capoluogo più vicino in linea d'aria
e poi gli altri entro 135% (controlla nel codice!) volte questa distanza.

Se un solo capoluogo è stato trovato,
allora lo do per buono come più vicino,
altrimenti salvo il risultato per un'analisi più approfondita.

**Nota**: non sono bastate le soluzioni sotto, alcune isole (es: Lampedusa)
non sono ben gestite da _GeoAapify_ quindi le ho inserite a mano nel db.  
In altri casi i dati erano sbagliati per vari motivi
(coordinate sbagliate, strade mancanti, ...)
quindi ho cercato a mano il risultato e forzato sul database.

### Codice

    python near_capoluoghi.py

Carica su `matches(comune, capoluogo)` gli accoppiamenti facili.

Carica su `distances (distance_id, comune, capoluogo, walk, walk_rsp)` quelli da approfondire.

Utilizza la libreria `geopy` per il calcolo della distanza,
perché la superficie della terra non è uno spazio euclideo, quindi niente teorema di Pitagora.

    python solve_distances.py

Prende in carico tutte le righe senza `walk`, chiede a _GeoApify_ una strada e salva la risposta.

    python solve_match.py

Una volta finite tutte le `distances`,
questo script calcola il capoluogo più vicino per ogni comune
e lo scrive su `matches`, chiudendo il giro.


    UPDATE matches SET capoluogo = (SELECT id FROM comuni WHERE nome = 'CAPOLUOGO') WHERE comune IN (SELECT id FROM comuni WHERE nome = 'COMUNE');

Per aggiustare a mano, prestando attenzione al numero di righe modificate,
perché alcuni comuni sono omonimi.

## Mappe

Per disegnare le mappe ho bisogno della geografia dei comuni di'Italia,
per fortuna ho trovato il geojson di [OpenPolis](https://github.com/openpolis/geojson-italy),
che poi ho pulito con [MapShaper](https://mapshaper.org/).

In particolare con:

- `-clean` ho rimosso qualche piccola impurità
- `-filter-fields com_istat_code` ho mantenuto solo il codice istat rispetto a tutti gli altri dati dei comuni presenti nel geojson

Ho usato lo stresso strumento per assegnare ad ogni provincia un colore diverso dalle adiacenti,
sia nella nuova cartina che in quella originale. 
Per fare questo, ho composto a mano una cartina
in cui le province hanno le collisioni della originale e di quella nuova,
partendo dal topojson di OpenPolis.
 
In MapShaper il comando `dissolve prov_acr` unisce i comuni nelle province, a parità di provincia originale (`prov_acr`);
il comando `-classify non-adjacent` associa ad ogni provincia un attributo `class` che indica il colore.
Infine uso `jq` sul JSON esportato per ottenere l'associazione provincia->colore, con la sintassi `map( {(.prov_acr) : .class } ) | add`.

## Visualizzazione

Ho trovato pro e contro in tutte le opzioni possibili, quindi ho percorso tutte le strade

### PNG Locale

Un grafico generato dal geojson, incrociato con i risultati dell'analisi.

Questo è personalizzato secondo i miei gusti, ma non interattivo.
Inoltre è molto preciso, perché usa il geojson
e non il topojson (che è semplificato all'80%),
quindi non è rapidissimo.

#### Codice

    python paint.py

Produce una PNG in locale, usa `matplotlib` per il grafico e `shapely` per calcolare il centro della provincia, in modo da scrivere l'etichetta (gestisce nativamente le strutture geojson e avevo già usato la libreria).  
Il grafico è "distorto" per adattarlo al 42esimo parallelo, altrimenti la mappa sembra appiattita.

Con il parametro `-o` genera un'immagine con le province originali. Invece `-c` serve per colorare diversamente i comuni all'interno della stessa provincia, in base al loro stato.

### DataWrapper

Un bel grafico interattivo, ma ha una gestione manuale dei colori e la mappa non è aggiornata (ma dell'anno scorso).

In particolare sono vecchi:

- 041060 è diventato 099031
- 041033 è diventato 099030
- 081025 è nuovo, da una parte del comune di Trapani


#### Codice

    python to_csv.py

Produce un CSV da dare in pasto a _DataWrapper_, include codice ISTAT (per correlare dati e mappa) e TUTTI i dati da visualizzare.

Per venire incontro a DataWrapper, ho filtrato il topojson di OpenPolis mantenendo solo codice ISTAT (`-filter-fields com_istat_code`).

### HTML interattivo custom

Non sono riuscito a generare un DataWrapper come volevo,
soprattutto per i comuni diversi ma anche per l'assegnazione dei colori,
quindi ho provato a creare una visualizzazione a mano con [d3](https://d3js.org/).

Inoltre ho gestito zoom e tooltip come preferivo, non è stato neanche complicatissimo.

#### Codice

    python to_topojson.py

Produce un topojson da usare nella pagina dedicata.

La pagina usa `d3` per la visualizzazione e `topojson` per processare il topojson (snello) nel geojson (l'unico che d3 capisca).
