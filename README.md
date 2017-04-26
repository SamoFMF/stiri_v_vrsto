# Štiri v vrsto
My Connect-Four game made in Python for school project. (Slovenian)

## Kako zagnati?
Igra se požene tako, da zaženete `stiri_v_vrsto.py`.

## Menu Igra
Prvi 'drop down' menu se imenuje `Igra`. V njem je več opcij:
1. `Nova igra`: prične novo igro. Rezultat se ponastavi na 0-0.
2. `Naslednja igra`: prične naslednjo igro. Če je bilo igre konec, se rezultat primerno prilagodi, sicer se ne spremeni.
3. `Štiri v vrsto`: klasična igra štiri v vrsto.
4. `Pet v vrsto`: podigra imenovana "Pet v vrsto" (več informacij spodaj).
5. `Pop Out`: podigra imenovana "Pop Out" (več informacij spodaj).
6. `Power Up`: podigra imenovana "Power Up" (več informacij spodaj).
7. `Pop 10`: podigra imenovana "Pop Ten" (več informacij spodaj).
8. `Izhod`: zapre igro.

## Menu Uredi
Drugi menu se imenuje `Uredi`. V njem sta opciji:
1. `Razveljavi`: razveljavi zadnjo potezo, ki jo je povlekel človek.
2. `Uveljavi`: uveljavi zadnjo razveljavljeno potezo, ki jo je povlekel človek.

## Menu Rdeči
Tretji menu se imenuje `Rdeči`. V tem menuju lahko določimo rdečega igralca. Na voljo so:
1. `Človek`: Rdečega igralca nadzira uporabnik.
2. `Računalnik - naključen`: Rdečega igralca nadzira računalnik s težavnostjo "naključen" (več informacij o težavnostih spodaj).
3. `Računalnik - lahek`: Podobno kot zgoraj, težavnost tukaj "lahek".
4. `Računalnik - srednji`: Podobno kot zgoraj, težavnost tukaj "srednji".
5. `Računalnik - zahteven`: Podobno kot zgoraj, težavnost tukaj "zahteven".
6. `Računalnik - nepremagljiv`: Podobno kot zgoraj, težavnost tukaj "nepremagljiv".

## Menu Rumeni
Četrti menu se imenuje `Rumeni` in je identičen menuju `Rdeči`, le da nastavlja rumenega igralca.

## Platno s podatki o igri
Levo zgoraj v oknu imamo platno, kjer se nahajajo podatki o trenutni igri, kot so imeni igralcev, njun trenutni rezultat, kdo je na potezi itd. Ime se da spremeniti.

## Stranski menu
Pod platnom s podatki o igri je stranski menu, kjer so bližnjice za najpogosteje uporabljene funkcije, to so `Nova igra`, `Naslednja igra`, `Razveljavi`, `Uveljavi` in `Izhod`. Zraven tega pa imamo še štiri polja, ki se uporabljajo v igri "Power Up" in niso na voljo v preostalih različicah.

## Igralna površina
Prikazuje trenutni položaj igre in omogoča igranje potez. Je prilagodljive velikosti.

## Pet v vrsto
Pravila enaka pravilom igre štiri v vrsto, le da moramo povezati pet žetonov. Za pomoč dobimo dva "dodatna" stolpca, ki sta že zapolnjena (označeno ob strani igralne površine).

## Pop Out
Pravila enaka kot pri štiri v vrsto, le da imamo na voljo dodatne poteze. In sicer lahko, ko smo na potezi, odstranimo spodnji žeton katerega koli stolpca, če je le naš.
To storimo tako, da kliknemo na željen žeton.

## Power Up
Normalna igra štiri v vrsto, kjer imamo na voljo štiri različne "powered up" poteze. Če želimo katero izmed njih igrati, jo izberemo v stranskem menuju in nato povlečemo potezo.
#### Poteptaj stolpec
Prvi "power up" nam omogoči, da igramo žeton, ki potepta vse že prej obstoječe žetone v svojem stolpcu.
#### Odstrani nasprotnikov žeton
Drugi "power up" nam omogoči, da namesto tega, da bi igrali svoj žeton, odstranimo poljubnega nasprotnikovega.
#### Dvojna poteza brez zmage
Tretji "power up" nam omogoči, da povlečemo dve potezi. Omejitev tukaj pa je, da druga poteza ne sme biti zmagovalna.
#### Dvojna poteza
Četrtji "power up" je identičen tretjemu, le da je brez omejitev.

## Pop Ten
Tukaj so pravila precej drugačna kot pri navadni igri štiri v vrsto. Igralca najprej izmenično vstavljata nasprotnikove žetone, kjer morata začeti z vstavljanjem v spodnjo vrstico. Ko se le-ta zapolni, vstavljata v naslednjo itd. vse dokler ni vseh 42 žetonov na igralnem območju. Nato se začne naslednja faza igre, kjer odstranjujeta svoje žetone. Ko odstraniš svoj žeton, se lahko zgodita dva primera:
1. Žeton je znotraj vsaj ene štirke. V tem primeru ga odstranimo iz igre.
2. Žeton ni znotraj nobene štirke. V tem primeru mora igralec odigrati z njim normalno potezo it klasične igre štiri v vrsto.
Prvi igralec, ki iz igre odstrani 10 žetonov, zmaga.

## Težavnosti
Računalnik ima pet različnih težavnosti, pri čemer `naključen` deluje po svojem algoritmu, preostali pa uporabljajo "alpha-beta pruning" oz. "alfa-beta rezanje", pri čemer je razlika le v globini (t.j. koliko potez vnaprej poračuna). Seveda pa to vpliva na to, koliko časa računalnik porabi za vsako potezo.
1. Naključen: algoritem vrne naključno potezo.
2. Lahek: globina je 2.
3. Srednji: globina je 4.
4. Zahteven: globina je 6.
5. Nepremagljiv: globina je 8.


## Kratka razlaga datotek / kode
V `stiri_v_vrsto.py` je koda za uporabniški vmesnik.
V datotekah `logika.py`, `pop_logika.py`, `five_logika.py` ter `powerup_logika.py` se nahajajo logike iger.
Možnosti človeka so v `clovek.py`, medtem ko je računalnik ustvarjen v `racunalnik.py`. Za odločanje o svojih potezah uporablja algoritma, ki sta zapisana v `rand_algoritem.py` ter `alphabeta.py`. Imamo še datoteko `minimax.py`, kjer je sedaj že zastareli algoritem.

