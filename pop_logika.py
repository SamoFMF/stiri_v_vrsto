###################
## LOGIKA POPOUT ##
###################

from logika import *

class Pop_logika(Igra):

    def kopija(self):
        '''Vrne kopijo te igre, brez zgodovine.'''
        k = Pop_logika()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.stevilo_potez = self.stevilo_potez
        return k

    def stanje_igre(self):
        '''Vrne nam trenutno stanje igre. Možnosti so:
            - (IGRALEC_R, stirka), če je igre konec in je zmagal IGRALEC_R z dano zmagovalno štirko,
            - (IGRALEC_Y, stirka), če je igre konec in je zmagal IGRALEC_Y z dano zmagovalno štirko,
            - (NEODLOCENO, None), če je igre konec in je neodločeno,
            - (NI_KONEC, None), če je igra še vedno v teku.'''
        # Najprej preverimo, če obstaja kakšna zmagovalna štirka
        zmagovalci = []
        stirke = []
        for s in Igra.stirke:
            ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
            barva = self.polozaj[i1][j1]
            if (barva != PRAZNO) and (barva == self.polozaj[i2][j2] == self.polozaj[i3][j3] == self.polozaj[i4][j4]):
                # s je naša zmagovalna štirka
                if barva in zmagovalci:
                    # Ta igralec že ima vsaj 1 zmagovalno štirko
                    continue
                else:
                    zmagovalci.append(barva)
                    stirke.append(s)
        if len(zmagovalci) == 1:
            return (zmagovalci[0], stirke)
        elif len(zmagovalci) == 2:
            # Imamo 2 zmagovalca, torej je igra neodločena
            return (NEODLOCENO, stirke)
        # Če zmagovalca ni, moramo preveriti, če je igre konec
        poteze = self.veljavne_poteze()
        if len(poteze) > 0:
            # Obstaja še vsaj 1 veljavna poteza
            return (NI_KONEC, None)
        else:
            # Če pridemo do sem, so vsa polja zasedena in ni več veljavnih potez
            # Pravtako tudi zmagovalca ni, torej je rezultat neodločen
            return (NEODLOCENO, None)

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        barva = self.na_potezi
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == 0:
                # V stolpcu je še vsaj 1 prosto mesto
                poteze.append(i+1)
            if barva and a[0] == barva:
                # Spodnji element stolpca je od igralca, ki je na potezi
                poteze.append(-i-1)
        return poteze
