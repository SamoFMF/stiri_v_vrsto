from igra import IGRALEC_R, IGRALEC_Y, PRAZNO, NEODLOCENO, NI_KONEC, NEVELJAVNO, nasprotnik
import random

######################
## ALGORITEM RANDOM ##
######################

class rand_alg():
    # Preprost algoritem, ki izbere naključno potezo

    def __init__(self):
        self.prekinitev = False
        self.igra = None # Objekt, ki opisuje igro
        self.jaz = None # Katerega igralca igramo
        self.poteza = None # Poteza, ki jo bomo izvedli

    def prekini(self):
        '''Metodo pokliče GUI, če je potrebno prekiniti razmišljanje.'''
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        '''Izračunamo potezo za trenutno stanje dane igre.'''
        # To metodo pokličemo iz vzporednega vlakna
        self.igra = igra
        self.prekinitev = False # Glavno vlakno bo nastavilo na True, če moramo ustaviti
        self.jaz = self.igra.na_potezi
        self.poteza = None # Vpišemo potezo, ko jo najdemo

        # Poženemo metodo za iskanje poteze
        poteza = self.rand_algoritem()
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            # Če nismo bili prekinjeni, izvedemo potezo
            self.poteza = poteza

    def rand_algoritem(self):
        poteze = self.igra.veljavne_poteze()
        stevilo = int(random.random() * len(poteze))
        return poteze[stevilo]
