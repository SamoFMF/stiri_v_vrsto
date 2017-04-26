import random

######################
## ALGORITEM RANDOM ##
######################

class Rand_alg():
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
        print('igralec = {0}, poteza = {1}'.format(self.jaz, poteza))
        self.jaz = None
        self.igra = None
        
        if not self.prekinitev:
            # Če nismo bili prekinjeni, izvedemo potezo
            self.poteza = poteza

    def rand_algoritem(self):
        '''Vrne naključno potezo izmed vseh veljavnih.'''
        poteze = self.igra.veljavne_poteze()
        return random.choice(poteze)
