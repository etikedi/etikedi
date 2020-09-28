# Lastenheft AERGIA


AERGIA ist eine Software, ähnlich zu kommerziellen Produkten wie https://labelbox.com/ oder https://prodi.gy/, welche für die Erstellung von gelabelten Datensätzen verwendet wird. Die Auswahl, welcher ungelabelter Datenpunkt als nächster vom Benutzer des Tools zu labeln ist, wird von einem externen Active Learning Modul (ALM) entschieden.

## Must have Features
- Text, Bild, Text+Mathematische Gleichungen, und HTML-Tabellen als Datentyp mit ALM labelbar
## Should have Features (unpriorisiert)
- neue Datensätze per GUI hochladbar
- gelabelte Daten per GUI herunterladbar
- "Grid" Darstellung gelabelter Datenpunkte (gelabelte sowohl als auch ungelabelte Datenpunkte)
- Label wieder zurücknehmbar ("Undo" Button)
- Bedienung des Label Interfaces per Tastatur (eine Taste pro Label) um schnell viele Samples labeln zu können
## Could have Features (Priorität in dieser Reihenfolge)
- Konfigurierung der Parameter vom ALM in der GUI
- Verschiedene Label Modi: 
         a) jede\*r Benutzer\*in erhält genau einen ungelabelten Datenpunkt (default) 
     	b) n Benutzer\*innen labeln diesselben Datenpunkte -> Label wird am Ende per majority-vote entschieden (oder von einem Admin in einem extra Interface)
- das ALM kann auch optional automatisch Label für Datenpunkte vergeben. Eine UI welche die Benutzer\*innen darüber informiert, wenn dies geschieht, mit der Möglichkeit, zu intervenieren wenn Daten falsch gelabelt wurden (sowas wie "diese 10 Bilder sehen für das ALM alle nach einer Giraffe aus, stimmt das?")
- einfache Visualisierung von Metriken aus dem ALM
- Bildausschnitte (mit der Maus Regionen markieren) als Datentyp
## Won't have Features (this time)
- Skalierbarkeit ist nicht wichtig (siehe "Einsatz")

## Technische Rahmenbedingungen
Das Tool soll am Ende auf einem Linux-basierten Server lauffähig sein, und von aktuellen Webbrowsern bedient werden können.

## Einsatz
Das Tool wird primär am Lehrstuhl für die Erstellung gelabelter Datensätze verwendet. Das bedeudet, dass AERGIA nicht von hunderten gleichzeitigen Benutzer\*innen verwendet wird, es werden eher maximal 5 Personen gleichzeitig sein.
Da es nicht wirklich Open-Source Alternativen zu AERGIA gibt, könnte es auch möglich sein, dass andere Menschen Interesse an dem Code haben, das sollte aber nicht unser Problem sein.

## Terminplan
Fertig werden muss das ganze dieses Semester, üblicherweise ist das Ende der Vorlesungszeit, also Samstag der 06.02.2021.