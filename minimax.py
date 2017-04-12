import logging

from igra import IGRALEC_R, IGRALEC_Y, PRAZNO, NEODLOCENO, NI_KONEC, nasprotnik, NEVELJAVNO
import random

#######################
## ALGORITEM MINIMAX ##
#######################

class Minimax:
    # Algoritem minimax

    def __init__(self, globina):
        self.globina = globina # Kako globoko iščemo?
        self.prekinitev = False # Želimo algoritem prekiniti?
        self.igra = None # Objekt, ki predstavlja igro
        self.jaz = None # Katerega igralca igramo?
        self.poteza = None # Sem vpišemo potezo, ko jo najdemo

    def prekini(self):
        '''Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
            je uporabnik zapr okno ali izbral novo igro.'''
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        '''Izračunaj potezo za trenutno stanje dane igre.'''
        # To metodo pokličemo iz vzporednega vlakna
        self.igra = igra
        self.jaz = self.igra.na_potezi
        self.prekinitev = False # Glavno vlakno bo to nastavilo na True, če bomo morali prekiniti
        self.poteza = None # Sem napišemo potezo, ko jo najdemo

        # Poženemo minimax
        (poteza, vrednost) = self.minimax(self.globina, True)
        print('poteza = {0}, vrednost = {1}'.format(poteza, vrednost))
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Nismo bili prekinjeni, torej potezo izvedemo
            self.poteza = poteza

    # Vrednosti igre
    ZMAGA = 10**5
    NESKONCNO = ZMAGA + 1 # Več kot zmaga

    def vrednost_pozicije(self):
        '''Ocena vrednosti polozaja.'''
        vrednost = 0
        if self.igra is None:
            # Če bi se slučajno zgodilo, da ne bi bila izbrana nobena igra
            return vrednost
        elif self.igra.na_potezi is None:
            return vrednost
        else:
            # Najprej preverimo ker tip igre imamo
            #if isinstance(self.igra, five_logika):
            if 3 > 5:
                # TODO
                stirke_R = self.igra.stirke_R
                stirke_Y = self.igra.stirke_Y
                petke = self.igra.petke
                tocke = [0, 0]
                pass
            else:
                # Imamo normalno ali popout igro, torej so štirke definirane sledeče
                stirke = self.igra.stirke
                # Pojdimo sedaj skozi vse možne zmagovalne štirke in jih
                # primerno ovrednotimo
                # Stirke, ki ze vsebujejo zetone obeh igralec so vredne 0 tock
                # Prazne stirke so vredne 0.1 tocke
                # Ostale so vredne a/4 tock, kjer je a stevilo zetonov znotraj stirke
                tocke = [0, 0] # Sem bomo shranili stevilo tock igralcev [R,Y]
                for s in stirke:
                    ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                    stirka = [self.igra.polozaj[i1][j1], self.igra.polozaj[i2][j2],
                             self.igra.polozaj[i3][j4], self.igra.polozaj[i4][j4]]
                    barve = list(set(stirka))
                    # barve bo dolžine 2 ali 3, če bi bilo dolžine 1,
                    # bi bilo igre že konec
                    if len(barve) == 2:
                        if PRAZNO in barve:
                            # V štirki so žetoni samo 1 barve
                            b = list(set(barve) - set([PRAZNO]))[0]
                            if b == IGRALEC_R:
                                tocke[0] += stirka.count(b) / 4
                            else:
                                tocke[1] += stirka.count(b) / 4
                        else:
                            continue
                    else:
                        continue
            (dos1, dos2) = tocke
            if self.igra.na_potezi == IGRALEC_R:
                vrednost += (dos1 - dos2) / 69 * 0.1 * Minimax.ZMAGA
            else:
                vrednost += (dos2 - dos1) / 69 * 0.1 * Minimax.ZMAGA
            vrednost *= 1 - self.igra.stevilo_zetonov() / (2*6*7)
        return vrednost

    def minimax(self, globina, maksimiziramo):
        '''Glavna metoda Minimax.'''
        if self.prekinitev:
            # Sporočili so nam, da moramo prekiniti
            return (None, 0)

        (zmagovalec, stirka) = self.igra.stanje_igre()
        if zmagovalec in (IGRALEC_R, IGRALEC_Y, NEODLOCENO):
            k = 1 - self.igra.stevilo_zetonov() / (2*6*7)
            # Igre je konec, vrnemo njeno vrednost
            if zmagovalec == self.jaz:
                return (None, Minimax.ZMAGA * k)
            elif zmagovalec == nasprotnik(self.jaz):
                return (None, -Minimax.ZMAGA * k)
            else:
                return (None, 0)
        elif zmagovalec == NI_KONEC:
            # Igre ni konec
            if globina == 0:
                return (None, self.vrednost_pozicije())
            else:
                # Naredimo en korak minimax metode
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    sez_naj_potez = []
                    vrednost_najboljse = -Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            sez_naj_potez = [p]
                            vrednost_najboljse = vrednost
                        elif vrednost == vrednost_najboljse:
                            sez_naj_potez.append(p)
                    najboljsa_poteza = random.choice(sez_naj_potez)
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    sez_naj_potez = []
                    vrednost_najboljse = Minimax.NESKONCNO
                    for p in self.igra.veljavne_poteze():
                        self.igra.povleci_potezo(p)
                        vrednost = self.minimax(globina-1, not maksimiziramo)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            sez_naj_potez = [p]
                            vrednost_najboljse = vrednost
                        elif vrednost == vrednost_najboljse:
                            sez_naj_potez.append(p)
                    najboljsa_poteza = random.choice(sez_naj_potez)
                assert (najboljsa_poteza is not None), 'minimax: izračunana poteza je None'
                return (najboljsa_poteza, vrednost_najboljse)
        else:
            assert False, 'minimax: nedefinirano stanje igre'
