# BSC 26L Projekt 2

- Andrzej Pultyn
- 325213
- andrzej.pultyn.stud@pw.edu.pl
- bsc26

## Zadanie

Celem projektu było zbadanie odporności na atak dwóch typów PUF:

- XOR APUF,
- dowolny inny typ PUF, uważany za bezpieczniejszy.

Należało wykorzystać dwie różne, dowolnie wybrane metody ataków. Jako drugi rodzaj PUF wybrany został **Interpose PUF**, a wybranymi rodzajami ataków były **Logistic Regression Attack**, oraz **Multilayer Perceptron Attack**.

## Uruchomienie

Projekt można uruchomić przez narzędzie `uv`:

```bash
uv run main.py
```

Wygenerowane diagramy znajdują się w katalogu `output/`.

## Raport

Raport projektu znajduje się w pliku `REPORT.md`. Komenda użyta do jego wyrenderowania z pliku markdown:

```bash
pandoc -o REPORT.pdf  REPORT.md -V papersize=a4 -V documentclass=report -V geometry:margin=2cm
```
