# Raport projektowy BSC 2

## Autor

- Andrzej Pultyn
- 325213
- andrzej.pultyn.stud@pw.edu.pl
- bsc26

## Cel projektu

Celem projektu było zbadanie odporności na atak dwóch typów PUF:

- XOR APUF,
- dowolny inny typ PUF, uważany za bezpieczniejszy.

Należało wykorzystać dwie różne, dowolnie wybrane metody ataków. Jako drugi rodzaj PUF wybrany został **Interpose PUF**, a wybranymi rodzajami ataków były **Logistic Regression Attack**, oraz **Multilayer Perceptron Attack**.

## Charakterystyka badanych PUF

### XOR Arbiter PUF (XOR APUF)

XOR Arbiter PUF jest rozszerzeniem klasycznego Arbiter PUF. Pojedynczy Arbiter PUF składa się z łańcucha $n$ par multiplekserów, przez które propaguje sygnał. Każdy bit wyzwania (challenge) przełącza odpowiednią parę, zmieniając ścieżkę sygnału. Na końcu łańcucha arbiter mierzy, która ze ścieżek jest szybsza, i na tej podstawie generuje 1-bitową odpowiedź (response).

W wariancie XOR APUF stosuje się $k$ niezależnych Arbiter PUF, a wynik końcowy jest bitowym XOR ich odpowiedzi. Parametr $k$ bezpośrednio wpływa na złożoność obliczeniową modelu, ponieważ każde dodatkowe XOR-owanie eksponencjalnie zwiększa liczbę możliwych kombinacji wewnętrznych opóźnień.

Charakterystyczne parametry XOR APUF:

- $n$ -- liczba segmentów (etapów) łańcucha opóźniającego; wpływa na przestrzeń wyzwań ($2^n$ możliwych wyzwań),
- $k$ -- liczba Arbiter PUF łączonych operacją XOR; zwiększenie $k$ utrudnia atak modelowy.

### Interpose PUF (IPUF)

Interpose PUF został zaproponowany jako konstrukcja odporna na ataki modelowe, które skutecznie łamią XOR APUF. Składa się z dwóch warstw XOR APUF:

- **górna (up)** -- XOR APUF z $k_{up}$ bramkami,
- **dolna (down)** -- XOR APUF z $k_{down}$ bramkami.

Kluczową cechą jest **interpozycja**: bit odpowiedzi górnej warstwy jest wstawiany w środek wyzwania podawanego do dolnej warstwy. Tworzy to nieliniową zależność między wyzwaniem a odpowiedzią, która nie daje się wyrazić prostą funkcją liniową. Oznacza to, że atakujący nie może trenować obu warstw jednocześnie w prosty sposób -- wyzwania efektywnie widoczne przez warstwę dolną zależą od odpowiedzi warstwy górnej, która sama jest nieznana.

Charakterystyczne parametry IPUF:

- $n$ -- długość wyzwania (liczba segmentów każdego APUF),
- $k_{up}$ -- liczba APUF w warstwie górnej (w eksperymencie: $k_up = 1$),
- $k_{down}$ -- liczba APUF w warstwie dolnej; główny parametr trudności.

## Metody ataków

### Logistic Regression Attack (LR)

Atak regresją logistyczną polega na wyznaczeniu modelu matematycznego PUF na podstawie zbioru par wyzwanie-odpowiedź (CRP). Bazuje na fakcie, że Arbiter PUF można opisać jako iloczyn skalarny wektora cech wyzwania z wektorem opóźnień układu. Odpowiedź zależy od znaku tego iloczynu.

Trening polega na iteracyjnym dopasowywaniu wag modelu tak, by minimalizować błąd predykcji odpowiedzi na znanych wyzwaniach. Dla pojedynczego APUF lub XOR APUF funkcja straty jest (w przybliżeniu) wypukła, co sprawia, że jej gradient zbiega do dobrego rozwiązania.

Parametry użyte w eksperymencie:

- zbiór CRP: $N = 100 000$,
- rozmiar mini-batcha: $bs = 1000$,
- współczynnik uczenia: $lr = 0.001$,
- liczba epok: $100$,
- dla XOR APUF: $k$ dopasowane do liczby XOR w atakowanym PUF,
- dla Interpose PUF: $k = k_{down} + 1$ (dodatkowa bramka na warstwę górną).

### Multilayer Perceptron Attack (MLP)

Atak z użyciem wielowarstwowej sieci neuronowej (MLP) jest metodą bardziej ogólną -- sieć uczy się odwzorowania wyzwania na odpowiedź bez zakładania konkretnej struktury matematycznej PUF. Sieć traktuje problem jako klasyfikację binarną i minimalizuje binarną entropię krzyżową.

Parametry użyte w eksperymencie:

- zbiór CRP: $N = 100 000$,
- architektura sieci: dwie ukryte warstwy, każda o szerokości $2^k$ (dla XOR APUF) lub $2^{k_{down}+1}$ (dla IPUF),
- rozmiar mini-batcha: $bs = 1000$,
- współczynnik uczenia: $lr = 0.001$,
- liczba epok: $100$,
- wczesne zatrzymanie przy stracie $<= 0.01$.

## Wyniki eksperymentów

Miara skuteczności ataku to **podobieństwo modelu** (ang. _model similarity_) -- odsetek wyzwań, na które model predykuje odpowiedź zgodną z oryginalnym PUF. Wartość 1.0 oznacza doskonałe dopasowanie; wartość 0.5 odpowiada losowemu zgadywaniu (dla odpowiedzi binarnej).

### XOR APUF -- LR Attack

![LRAttack2021 na XOR APUF](output/APUF_LR_attack.png)

| $n$ \ $k$ | $k=1$ | $k=2$ | $k=3$ | $k=4$ |
|-----------|-------|-------|-------|-------|
| $n=8$     | 0.964 | 0.945 | 0.873 | 0.965 |
| $n=16$    | 0.950 | 0.947 | 0.959 | 0.929 |
| $n=24$    | 0.966 | 0.943 | 0.948 | 0.960 |
| $n=32$    | 0.958 | 0.948 | 0.909 | 0.954 |

Atak LR na XOR APUF uzyskał podobieństwo modelu w zakresie **0.88-0.96** dla wszystkich badanych konfiguracji ($n \in \{8, 16, 24, 32\}, k \in \{1, 2, 3, 4\}$). Wyniki są konsekwentnie wysokie, co potwierdza, że XOR APUF jest podatny na atak regresją logistyczną. Zmiany pomiędzy konfiguracjami nie wydają się liniowo zależne od wartości $n$ czy $k$.

### XOR APUF -- MLP Attack

![MLPAttack2021 na XOR APUF](output/APUF_MLP_attack.png)

| $n$ \ $k$ | $k=1$ | $k=2$ | $k=3$ | $k=4$ |
|-----------|-------|-------|-------|-------|
| $n=8$     | 1.000 | 1.000 | 1.000 | 1.000 |
| $n=16$    | 1.000 | 0.997 | 0.995 | 0.986 |
| $n=24$    | 1.000 | 0.997 | 0.997 | 0.990 |
| $n=32$    | 0.996 | 0.995 | 0.993 | 0.991 |

Atak MLP osiągnął jeszcze wyższe wyniki: podobieństwo modelu w zakresie **0.986-1.000**. Sieć neuronowa lepiej radzi sobie z nieliniowością XOR, dlatego dokładność jest wyraźnie wyższa niż w przypadku regresji logistycznej. Dla każdej badanej konfiguracji model praktycznie doskonale odwzorował zachowanie PUF.

### Interpose PUF -- LR Attack

![LRAttack2021 na InterposePUF](output/InterposePUF_LR_attack.png)

| $n$ \ $k_{down}$ | $k_{down}=2$ | $k_{down}=4$ | $k_{down}=8$ |
|------------------|--------------|--------------|--------------|
| $n=8$            | 0.918        | 0.943        | 0.955        |
| $n=16$           | 0.739        | 0.757        | 0.554        |
| $n=24$           | 0.763        | 0.752        | 0.504        |
| $n=32$           | 0.790        | 0.652        | 0.518        |
| $n=64$           | 0.721        | 0.542        | 0.527        |

Atak LR na Interpose PUF okazał się znacznie mniej skuteczny. Dla $k_{down}$ = 2 podobieństwo wynosiło między $0.7$ a $0.8$. Dla $k_{down} = 4$ istotna była wartość $n$ -- dla wartości $n \in \{16, 24\}$ wynosiła ona nadal ok. $0.75$, dla $n = 32$ było to już tylko ok. $0.65$, a dla $n = 64$ odpowiedź była praktycznie losowa. Dla $k_{down} = 8$ atak regresją logistyczną nie miał szans dla praktycznie żadnej konfiguracji. Pewną anomalią jest $n = 8$, dla którego wszystkie wartości podobieństwa wyniosły ponad $0.9$. Mało tego, podobieństwa rosły a nie malały wraz ze wzrostem $k_{down}$.

### Interpose PUF -- MLP Attack

![MLPAttack2021 na InterposePUF](output/InterposePUF_MLP_attack.png)

| $n$ \ $k_{down}$ | $k_{down}=2$ | $k_{down}=4$ | $k_{down}=8$ |
|------------------|--------------|--------------|--------------|
| $n=8$            | 1.000        | 1.000        | 1.000        |
| $n=16$           | 0.969        | 0.962        | 0.826        |
| $n=24$           | 0.983        | 0.963        | 0.507        |
| $n=32$           | 0.973        | 0.866        | 0.521        |
| $n=64$           | 0.975        | 0.758        | 0.507        |

Atak MLP jest skuteczniejszy niż LR, jednak nadal znacznie gorszy niż na XOR APUF. Przy $k_{down} = 2$ sieć osiąga podobieństwo ok. $0.97$ dla wszystkich wartości $n$ -- wynik zbliżony do osiąganego na XOR APUF. Jednak wraz ze wzrostem $k_{down}$ skuteczność gwałtownie spada -- im większa wartość $n$, tym większy spadek. Gdy $k_{down} = 8$, dla $n \in \{24, 32, 64\}$ wartości podobieństwa są praktycznie równe $0.5$, co oznacza pełną losowość. Głębsza sieć potrzebowałaby znacznie większego zbioru CRP lub dłuższego treningu, by pokonać silniejsze konfiguracje IPUF. Analogicznie dla ataku LR, przy $n = 8$ model ma prawie stuprocentową skuteczność odpowiedzi. Jedną różnicą jest $n = 16$, dla którego w przypadku ataku LR podobieństwo wynosiło $0.554$, a tutaj wynosi aż $0.826$.

## Wnioski

1. **XOR APUF jest podatny na oba ataki.** Zarówno regresja logistyczna, jak i MLP osiągają wysokie podobieństwo modelu ($> 0.88$ dla LR, $> 0.98$ dla MLP) nawet przy użyciu 100 000 CRP i stosunkowo krótkim treningu. Wzrost liczby segmentów $n$ i liczby bramek XOR $k$ w zbadanym zakresie nie stanowi skutecznej ochrony.

2. **MLP przewyższa LR na XOR APUF.** Sieć neuronowa lepiej modeluje nieliniowość operacji XOR, osiągając niemal doskonałe dopasowanie we wszystkich konfiguracjach.

3. **Interpose PUF wykazuje znacznie wyższą odporność na atak LR.** Już przy $k_{down} = 4$ i $n = 64$ podobieństwo spada do poziomu zbliżonego do losowego. Interpozycja bitu skutecznie zakłóca gradient, uniemożliwiając zbieżność regresji logistycznej.

4. **MLP radzi sobie z IPUF lepiej niż LR, ale jego skuteczność szybko maleje.** Przy $k_{down} = 2$ sieć MLP osiąga ok. $0.96$, lecz przy $k_{down} = 8$ jej wyniki są zbliżone do losowego odgadywania. Zwiększenie $k_{down}$ stanowi efektywną obronę również przed atakiem MLP w ograniczonym budżecie obliczeniowym.

5. **Długość wyzwania n ma większy wpływ na IPUF niż na XOR APUF.** Przy $n=64$ ataki na Interpose PUF są trudniejsze niż przy $n=32$, co wskazuje, że zarówno $k_{down}$, jak i $n$ konfigurują skuteczną obronę.

6. **Interpose PUF jest bezpieczniejszym wyborem niż XOR APUF** dla parametrów $k_{down} >= 4$, gdy atakujący dysponuje 100 000 CRP i ograniczonym budżetem obliczeniowym. Jednak przy niskich wartościach $k_{down}$ (np. $k_{down} = 2$) nawet IPUF pozostaje podatny na atak MLP.
