from logika import *

#####################
## LOGIKA POWER UP ##
#####################

class Powerup_logika(Logika):

    def __init__(self):
        # Prekopiramo __init__ iz objekta Logika
        super(Powerup_logika, self).__init__()

        # Vsak igralec ima na voljo 4x 'power up'
        # V tem seznamu seznamov bomo hranili kateri 'power up' še ima
        # kateri igralec na voljo
        # Po vrsti so: Poteptaj stolpec, odstrani nasprotnikov žeton, 2x non-winning move, 2x move
        self.powerups = [[1, 1, 1, 1], [1, 1, 1, 1]]

        # Shranimo stanje, ki nam pove, če igralec sme v naslednji potezi zmagati
        # Vrednost False bo zaseglo, če bo uporabljen 2x non-winning power up
        self.sme_zmagati = True

        # Shranimo stanje, ki nam pove, če bo igralec ponovno na potezi
        # V tem stanju lahko igra le 'normalno' potezo
        self.dvojna_poteza = False

    def ima_zmagovalca(self, p):
        '''Vrne zmagovalca, če obstaja po potezi p, None sicer.'''
        i = p-1
        j = self.vrstica(i)
        for s in Logika.stirke:
            if (i,j) in s:
                ((i1,j1),(i2,j2),(i3,j3),(i4,j4)) = s
                stirka = [self.polozaj[i1][j1], self.polozaj[i2][j2],
                          self.polozaj[i3][j3], self.polozaj[i4][j4]]
                if stirka.count(self.na_potezi) == 3:
                    # Imamo že 3 žetone naše barve,
                    # poteza p bo torej zmagovalna
                    return self.na_potezi
        return None

    def kopija(self):
        '''Vrne kopijo te igre, brez zgodovine.'''
        k = Powerup_logika()
        k.polozaj = [self.polozaj[i][:] for i in range(7)]
        k.na_potezi = self.na_potezi
        k.stevilo_potez = self.stevilo_potez
        k.powerups = [self.powerups[i][:] for i in range(2)]
        k.sme_zmagati = self.sme_zmagati
        k.dvojna_poteza = self.dvojna_poteza
        return k

    def povleci_potezo(self, p, racunalnik=False):
        '''Povleci potezo p, če je veljavna, sicer ne naredi nič.
            Veljavna igra -> vrne stanje_igre() po potezi, sicer None.'''
        assert (p is not None), 'Nekako smo prišli do tega, da je p = {0}'.format(p)
        if racunalnik:
            # Računalnik izbira samo med veljavnimi potezami
            # S tem si prihranimo ponovno računanje veljavnih potez
            pass
        else:
            # Potezo vleče človek
            poteze = self.veljavne_poteze()
        osvezi = False # Če moramo osvežiti igralno površino, ker smo izbrisali kakšne žetone

        # Preverimo, če je poteza veljavna
        if racunalnik or p in poteze:
            # Poteza je veljavna
            kateri_igr = 0 if self.na_potezi == IGRALEC_R else 1 # Potrebujemo za knjiženje 'power up'-ov
            
            if len(self.zgodovina) > self.stevec:
                self.zgodovina = self.zgodovina[:self.stevec]
            self.shrani_polozaj()

            # Ker se bo poteza povlekla, lahko sedaj ponastavimo stanji
            self.sme_zmagati = True
            self.dvojna_poteza = False
            
            if p < 11:
                # Imamo 'normalno' potezo
                j = self.vrstica(p-1)
                self.polozaj[p-1][j] = self.na_potezi
            elif p < 21:
                # Imamo potezo, ki potepta stolpec
                stolpec = p - 11
                self.polozaj[stolpec] = [self.na_potezi, PRAZNO, PRAZNO, PRAZNO, PRAZNO, PRAZNO]
                self.powerups[kateri_igr][0] -= 1
                osvezi = True
            elif p < 71:
                # Imamo potezo, ki odstrani nasprotnikov žeton
                stolpec = (p - 21) % 7
                vrstica = (p - 21) // 7
                del self.polozaj[stolpec][vrstica]
                self.polozaj[stolpec].append(PRAZNO)
                self.powerups[kateri_igr][1] -= 1
                osvezi = True
            elif p < 81:
                # Imamo dvojno potezo brez dovoljene zmage
                j = self.vrstica(p-71)
                self.polozaj[p-71][j] = self.na_potezi
                self.powerups[kateri_igr][2] -= 1
                self.sme_zmagati = False
                self.dvojna_poteza = True
            else:
                # Imamo dvojno potezo z dovoljeno zmago
                j = self.vrstica(p-81)
                self.polozaj[p-81][j] = self.na_potezi
                self.powerups[kateri_igr][3] -= 1
                self.dvojna_poteza = True
        else:
            # Poteza ni veljavna
            return None
        (zmagovalec, stirka) = self.stanje_igre()
        if zmagovalec == NI_KONEC:
            # Igra se nadaljuje
            if self.dvojna_poteza:
                # Na potezi je ponovno isti igralec
                pass
            else:
                # Na potezi je nasprotnik
                self.na_potezi = nasprotnik(self.na_potezi)
        else:
            # Igra se je zaključila
            self.na_potezi = None
        self.zadnja = ([self.polozaj[i][:] for i in range(7)], self.na_potezi, self.powerups, self.sme_zmagati, self.dvojna_poteza)
        return (zmagovalec, stirka, (p%10-1,j) if (p<11 or p>70) else (0,0), osvezi) # Ko je (0,0), je osvezi = 1, torej ni pomembno katera poteza je

    def razveljavi(self, i=1):
        '''Razveljavi potezo in se vrne v prejšnje stanje.'''
        if self.stevec > i-1:
            self.stevec -= i
            (self.polozaj, self.na_potezi, self.powerups,
             self.sme_zmagati, self.dvojna_poteza) = self.zgodovina[self.stevec]
            self.stevilo_potez -= i
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def shrani_polozaj(self):
        '''Shrani trenutni položaj igre, da se lahko vanj vrnemo
            s klicem metode 'razveljavi'.'''
        p = [self.polozaj[i][:] for i in range(7)] # Položaj
        pup = [self.powerups[i][:] for i in range(2)] # Power-Ups
        self.zgodovina.append((p, self.na_potezi, pup,
                               self.sme_zmagati, self.dvojna_poteza))
        self.stevec += 1
        self.stevilo_potez += 1

    def uveljavi(self, i=1):
        '''Uveljavi zadnjo razveljavljeno potezo in se vrne v njeno stanje.'''
        if self.stevec < len(self.zgodovina)-i:
            self.stevec += i
            (self.polozaj, self.na_potezi, self.powerups,
             self.sme_zmagati, self.dvojna_poteza) = self.zgodovina[self.stevec]
            self.stevilo_potez += i
            return (self.polozaj, self.na_potezi)
        elif self.stevec == len(self.zgodovina)-i:
            self.stevec += i
            (self.polozaj, self.na_potezi, self.powerups,
             self.sme_zmagati, self.dvojna_poteza) = self.zadnja
            self.stevilo_potez += i
            return (self.polozaj, self.na_potezi)
        else:
            return None

    def veljavne_poteze(self):
        '''Vrne seznam veljavnih potez.'''
        poteze = []
        # Izdelajmo si indikator, ki bo =0, če igra rdeči in 1 sicer
        kateri_igr = 0 if self.na_potezi == IGRALEC_R else 1
        # Najprej dodajmo 'normalne' poteze
        for (i,a) in enumerate(self.polozaj):
            if a[-1] == PRAZNO:
                if self.sme_zmagati:
                    poteze.append(i+1)
                else:
                    zmagovalec = self.ima_zmagovalca(i+1)
                    if zmagovalec is None:
                        # Zmaga lahko igralec, ki je na potezi, ali nihče,
                        # saj povleče 'normalno' potezo
                        poteze.append(i+1)
                    else:
                        # Isto kot zgoraj, torej je igralec zmagal
                        # Poteza ni dovoljena
                        pass
        if self.dvojna_poteza:
            # Druga poteza je lahko samo 'normalna' poteza, brez uporabe 'power up'-ov
            return poteze

        # Dodajmo poteze, kjer poteptamo stolpec
        # Označimo jih z 11-17
        if self.powerups[kateri_igr][0] > 0:
            for (i,a) in enumerate(self.polozaj):
                if a[0] == PRAZNO:
                    # Stolpec je prazen
                    # To je kar navadna poteza, nočemo se ponavljati ali porabiti 'power up-a'
                    continue
                else:
                    poteze.append(11+i)
                
        # Dodajmo poteze, kjer odstranimo nasprotnikov žeton
        # Označimo jih z 21-62
        if self.powerups[kateri_igr][1] > 0:
            for (i,a) in enumerate(self.polozaj):
                for (j,barva) in enumerate(a):
                    if barva == nasprotnik(self.na_potezi):
                        poteze.append(21+i+7*j)

        # Dodajmo poteze, kjer bo naslednja poteza zaporedna brez možnosti zmage
        # Označimo jih z 71-77
        if self.powerups[kateri_igr][2] > 0:
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == PRAZNO:
                    zmagovalec = self.ima_zmagovalca(i+1)
                    if zmagovalec is None:
                        # Preverimo, da poteza ni zmagovalna, če je,
                        # je to kar navadna poteza, saj bo konec preden naredimo dvojno
                        poteze.append(71+i)

        # Dodajmo poteze, kjer bo naslednja poteza zaporedna z možnostjo zmage
        # Označimo jih z 81-88
        if self.powerups[kateri_igr][3] > 0:
            for (i,a) in enumerate(self.polozaj):
                if a[-1] == PRAZNO:
                    zmagovalec = self.ima_zmagovalca(i+1)
                    if zmagovalec is None:
                        # Preverimo, da poteza ni zmagovalna, če je,
                        # je to kar navadna poteza, saj bo konec preden naredimo dvojno
                        poteze.append(81+i)
        
        return poteze
