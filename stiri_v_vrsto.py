import tkinter # Uvozimo tkinter za uporabniški vmesnik
from math import sqrt

from logika import *
from clovek import *
from racunalnik import *
from rand_algoritem import *
from minimax import *
from pop_logika import *
from five_logika import *
from alphabeta import *

#########################
## UPORABNIŠKI VMESNIK ##
#########################

# Najboljše, če se ne spreminja preveč, ker izgleda najlepše pri teh številkah
MIN_SIRINA = 500
MIN_VISINA = 555
ZVP = 100 # Zacetna velikost polja

class Gui():
    # To so vsi grafični elementi v self.platno, ki 'pripadajo'
    # igralcema, torej krožci, ki so bili igrani
    TAG_FIGURA = 'figura'

    # Oznaka za črte, ki sestavljajo okvir
    TAG_OKVIR = 'okvir'

    # Oznaka za gumbe, ki so na voljo v meniju levo od igralne površine
    TAG_GUMB = 'gumb'

    # Oznaka za spremenljive dele na platno_menu
    TAG_SPREMENLJIVI = 'spremenljivi'

    # Velikost okvirja za stranski menu
    OKVIR = 5

    # Visina in sirina platna z rezultatom itd.
    # ODSVETUJEM SPREMINJANJE
    VISINA_PLATNO_MENU = 0.55 * MIN_VISINA
    SIRINA_PLATNO_MENU = 0.8 * MIN_SIRINA - 3*OKVIR

    def __init__(self, master):
        self.igralec_r = None # Objekt, ki igra rdeče krogce
        self.igralec_y = None # Objekt, ki igra rumene krogce
        self.igra = None # Objekt, ki predstavlja igro
        self.tip = tkinter.IntVar() # Katero igro igramo - 0='4inarow',1='5inarow',2='popout'
        self.VELIKOST_POLJA = ZVP # Velikost polja
        self.VELIKOST_GAP = self.VELIKOST_POLJA / 20 # Razdalja med okvirjem in figuro
        self.rezultat = [0, 0] # Trenutni rezultat

        self.tip_rdeci = tkinter.IntVar() # Kakšen je rdeči, 0='človek',1='rac-rand',2='rac-easy',3='rac-med',4='rac-hard'
        self.tip_rumeni = tkinter.IntVar() # Kot pri rdečem

        # Slovar 'tipov' igralcev
        self.tip_igralca = {0: lambda: Clovek(self),
                               1: lambda: Racunalnik(self, rand_alg()),
                               2: lambda: Racunalnik(self, AlphaBeta(2)),
                               3: lambda: Racunalnik(self, AlphaBeta(4)),
                               4: lambda: Racunalnik(self, AlphaBeta(6)),
                               5: lambda: Racunalnik(self, AlphaBeta(8)),
                               99: lambda: Racunalnik(self, Minimax(2))} # 99 - za testne namene, če še želimo star algoritem preizkušati

        # Slovar 'tipov' igre
        self.tip_igre = {0: lambda: Igra(),
                         1: lambda: five_logika(),
                         2: lambda: pop_logika()}

        # Nastavimo imeni igralcev, ki jih lahko uporabnik nato spreminja
        self.ime_r = tkinter.StringVar() # Ime igralca z rdečimi žetoni
        self.ime_r.set('Rdeči') # Po defaultu je rdečemu ime 'Rdeči'
        self.ime_y = tkinter.StringVar() # Ime igralca z rumenimi žetoni
        self.ime_y.set('Rumeni') # Po defaultu je rumenemu ime 'Rumeni'
        # Beležiti želimo tudi spremembe imena in ga primerno urediti
        self.ime_r.trace('w', lambda name, index, mode: self.uredi_ime(self.ime_r))
        self.ime_y.trace('w', lambda name, index, mode: self.uredi_ime(self.ime_y))
        
        # Če uporabnik zapre okno, naj se pokliče self.zapri_okno
        master.protocol('WM_DELETE_WINDOW', lambda: self.zapri_okno(master))

        # Glavni menu
        menu = tkinter.Menu(master)
        master.config(menu=menu)

        # Podmenu "Igra"
        menu_igra = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Igra', menu=menu_igra)
        menu_igra.add_command(label='Nova igra',
                              command=lambda: self.zacni_igro(nova=True))
        menu_igra.add_command(label='Naslednja igra', command=self.naslednja_igra)
        menu_igra.add_separator()
        menu_igra.add_radiobutton(label='Štiri v vrsto',
                                  variable=self.tip, value=0,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Pet v vrsto',
                                  variable=self.tip, value=1,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_radiobutton(label='Pop Out',
                                  variable=self.tip, value=2,
                                  command=lambda: self.naslednja_igra())
        menu_igra.add_separator()
        menu_igra.add_command(label='Izhod',
                              command=lambda: self.zapri_okno(master))

        # Podmenu "Uredi"
        menu_uredi = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Uredi', menu=menu_uredi)
        menu_uredi.add_command(label='Razveljavi', command=self.platno_razveljavi)
        menu_uredi.add_command(label='Uveljavi', command=self.platno_uveljavi)

        # Podmenu "Rdeči"
        menu_rdeci = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Rdeči', menu=menu_rdeci)
        menu_rdeci.add_radiobutton(label='Človek',
                                   variable=self.tip_rdeci, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_igra.add_separator()
        menu_rdeci.add_radiobutton(label='Računalnik - naključen',
                                   variable=self.tip_rdeci, value=1,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - lahek',
                                   variable=self.tip_rdeci, value=2,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - srednji',
                                   variable=self.tip_rdeci, value=3,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - težek',
                                   variable=self.tip_rdeci, value=4,
                                   command=lambda: self.zacni_igro(True))
        menu_rdeci.add_radiobutton(label='Računalnik - nepremagljiv',
                                   variable=self.tip_rdeci, value=5,
                                   command=lambda: self.zacni_igro(True))

        # Podmenu "Rumeni"
        menu_rumeni = tkinter.Menu(menu, tearoff=0)
        menu.add_cascade(label='Rumeni', menu=menu_rumeni)
        menu_rumeni.add_radiobutton(label='Človek',
                                   variable=self.tip_rumeni, value=0,
                                   command=lambda: self.zacni_igro(True))
        menu_igra.add_separator()
        menu_rumeni.add_radiobutton(label='Računalnik - naključen',
                                   variable=self.tip_rumeni, value=1,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - lahek',
                                   variable=self.tip_rumeni, value=2,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - srednji',
                                   variable=self.tip_rumeni, value=3,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - težek',
                                   variable=self.tip_rumeni, value=4,
                                   command=lambda: self.zacni_igro(True))
        menu_rumeni.add_radiobutton(label='Računalnik - nepremagljiv',
                                   variable=self.tip_rumeni, value=5,
                                   command=lambda: self.zacni_igro(True))

        ###############################################################
        ###############################################################
        ##                      IGRALNO OBMOČJE                      ##
        ###############################################################
        ###############################################################
        self.platno = tkinter.Canvas(master,
                                     width=8*self.VELIKOST_POLJA,
                                     height=7*self.VELIKOST_POLJA)
        self.platno.pack(fill=tkinter.BOTH, expand=1, side=tkinter.RIGHT)

        # Narišemo črte na igralnem polju (ustvarimo igralno površino)
        self.narisi_okvir()

        # Določimo, kaj se zgodi, ko uporabnik pritisne določene tipke
        self.platno.bind('<Button-1>', self.platno_klik)
        self.platno.bind_all('<Control-z>', self.platno_razveljavi)
        self.platno.bind_all('<Control-y>', self.platno_uveljavi)
        self.platno.bind('<Configure>', self.spremeni_velikost)

        ###############################################################
        ###############################################################
        ##                    UREJEVALNO OBMOČJE                     ##
        ###############################################################
        ###############################################################
        # Dodamo frame, kamor bomo postavili platno z rezultatom
        # ter meni z možnostmi
        self.frame1 = tkinter.Frame(master,
                                    width=0.8 * MIN_SIRINA,
                                    height=MIN_VISINA,
                                    relief=tkinter.GROOVE,
                                    borderwidth=Gui.OKVIR,
                                    bg='black')
        self.frame1.pack(side=tkinter.LEFT, anchor=tkinter.NW)
        self.frame1.grid_propagate(0)

        # Narišemo platno
        self.platno_menu = tkinter.Canvas(self.frame1,
                                          width=Gui.SIRINA_PLATNO_MENU,
                                          height=Gui.VISINA_PLATNO_MENU)
        self.platno_menu.config(bg='black') # Za čas testiranja
        self.platno_menu.grid(row=0, column=0, sticky=tkinter.NW)

        # Dodamo možnosti
        self.gumb_nova_igra = tkinter.Button(self.frame1, text='Nova igra',
                                             width=int(0.4*MIN_SIRINA/7.25),
                                             command=lambda: self.zacni_igro(nova=True))
        self.gumb_nova_igra.grid(row=1, column=0, pady=5)
        self.gumb_naslednja_igra = tkinter.Button(self.frame1, text='Naslednja igra',
                                                  width=int(0.4*MIN_SIRINA/7.25),
                                                  command=self.naslednja_igra)
        self.gumb_naslednja_igra.grid(row=2, column=0, pady=5)
        self.gumb_razveljavi = tkinter.Button(self.frame1, text='Razveljavi',
                                              width=int(0.4*MIN_SIRINA/7.25),
                                              command=self.platno_razveljavi)
        self.gumb_razveljavi.grid(row=3, column=0, pady=(20,5))
        self.gumb_uveljavi = tkinter.Button(self.frame1, text='Uveljavi',
                                            width=int(0.4*MIN_SIRINA/7.25),
                                            command=self.platno_uveljavi)
        self.gumb_uveljavi.grid(row=4, column=0, pady=5)
        self.gumb_izhod = tkinter.Button(self.frame1, text='Izhod',
                                         width=int(0.3*0.8*MIN_SIRINA/7.25),
                                         command=lambda: self.zapri_okno(master))
        self.gumb_izhod.grid(row=5, column=0, pady=(30,5))

        # Narišemo figure za platno_menu
        # Najprej nespremenljiv del
        dx = 0.15 * Gui.VISINA_PLATNO_MENU

        self.platno_ime_r = tkinter.Entry(master, fg='red', bg='black',
                                font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/12)),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_r)
                                    
        self.platno_ime_y = tkinter.Entry(master, fg='yellow', bg='black',
                                font=('Helvetica', '{0}'.format(int(Gui.VISINA_PLATNO_MENU/12)),
                                           'bold'),
                                width='10', borderwidth='0', justify='center',
                                textvariable=self.ime_y)
        
        self.platno_menu.create_window(50+dx, 10, anchor=tkinter.N, window=self.platno_ime_r)
        
        self.platno_menu.create_window(Gui.SIRINA_PLATNO_MENU-50-dx, 10,
                                       anchor=tkinter.N, window=self.platno_ime_y)
        
        # Pričnemo igro
        self.zacni_igro(nova=True)

    def koncaj_igro(self, zmagovalec, stirka):
        '''Nastavi stanje igre na 'konec igre'.'''
        self.narisi_platno_menu(zmagovalec)
        if stirka is not None:
            self.obkrozi(stirka)

    def narisi_okvir(self):
        '''Nariše črte (okvir) na igralno povrčino.'''
        self.platno.delete(Gui.TAG_OKVIR)
        d = self.VELIKOST_POLJA
        for i in range(8):
            self.platno.create_line(d/2 + i*d, d/2,
                                    d/2 + i*d, 13*d/2,
                                    tag=Gui.TAG_OKVIR)
        for i in range(7):
            self.platno.create_line(d/2, d/2 + i*d,
                                    15*d/2, d/2 + i*d,
                                    tag=Gui.TAG_OKVIR)

    def narisi_R(self, p):
        d = self.VELIKOST_POLJA
        x = (p[0] + 1) * d
        y = (6 - p[1]) * d
        gap = self.VELIKOST_GAP
        self.platno.create_oval(x - d/2 + gap, y - d/2 + gap,
                                x + d/2 - gap, y + d/2 - gap,
                                fill = 'red',
                                width=0,
                                tag=Gui.TAG_FIGURA)

    def narisi_platno_menu(self, zmagovalec=None):
        self.platno_menu.delete(Gui.TAG_SPREMENLJIVI)
        dy = 5 * Gui.VISINA_PLATNO_MENU / 30
        dx = 0.15 * Gui.VISINA_PLATNO_MENU
        self.platno_menu.create_text(50+dx, 10+dy,
                                     text='{0}'.format(self.rezultat[0]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU-50-dx, 10+dy,
                                     text='{0}'.format(self.rezultat[1]),
                                     fill='white', anchor=tkinter.N,
                                     font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                           'bold'),
                                     tag=Gui.TAG_SPREMENLJIVI)
        if zmagovalec==NEODLOCENO:
            # Izid je neodločen
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 3.5*dy,
                                         text='Izid je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 4.5*dy,
                                         text='NEODLOČEN',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        elif zmagovalec:
            # Imamo zmagovalca
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Konec igre!',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 3.5*dy,
                                         text='Zmagovalec je:',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 4.5*dy,
                                         text='{0}'.format('RDEČI' if zmagovalec==IGRALEC_R else 'RUMENI'),
                                         fill='{0}'.format('red' if zmagovalec==IGRALEC_R else 'yellow'), anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
        else:
            self.platno_menu.create_text(Gui.SIRINA_PLATNO_MENU / 2, 10 + 2.5*dy,
                                         text='Na potezi je',
                                         fill='white', anchor=tkinter.N,
                                         font=('Helvetica','{0}'.format(int(Gui.VISINA_PLATNO_MENU/10)),
                                               'bold'),
                                         tag=Gui.TAG_SPREMENLJIVI)
            self.platno_menu.create_oval(Gui.SIRINA_PLATNO_MENU / 2 - 0.5*dy, 10 + 3.75*dy,
                                         Gui.SIRINA_PLATNO_MENU / 2 + dy, 10 + 5.25*dy,
                                         fill='{0}'.format('red' if self.igra.na_potezi==IGRALEC_R else 'yellow'),
                                         tag=Gui.TAG_SPREMENLJIVI)

    def narisi_polozaj(self, polozaj): # Premisli, če rabiš polozaj
        for (i, a) in enumerate(polozaj):
            for (j, b) in enumerate(a):
                if b == IGRALEC_R:
                    self.narisi_R((i,j))
                elif b == IGRALEC_Y:
                    self.narisi_Y((i,j))

        if isinstance(self.igra, five_logika):
            self.narisi_crtice()

    def narisi_crtice(self):
        # Pomožne črte za 5 v vrsto
        d = self.VELIKOST_POLJA
        for i in range(6):
            barva1 = 'yellow' if i%2 == 0 else 'red'
            barva2 = 'red' if i%2 == 0 else 'yellow'
            self.platno.create_line(d/4, d/2 + d/4 + i*d,
                                    d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva1,
                                    width=5)
            self.platno.create_line(8*d - d/4, d/2 + d/4 + i*d,
                                    8*d - d/4, d/2 + 3*d/4 + i*d,
                                    tag=Gui.TAG_FIGURA,
                                    fill=barva2,
                                    width=5)

    def narisi_Y(self, p):
        d = self.VELIKOST_POLJA
        x = (p[0] + 1) * d
        y = (6 - p[1]) * d
        gap = self.VELIKOST_GAP
        self.platno.create_oval(x - d/2 + gap, y - d/2 + gap,
                                x + d/2 - gap, y + d/2 - gap,
                                fill = 'yellow',
                                width=0,
                                tag=Gui.TAG_FIGURA)

    def naslednja_igra(self):
        if self.igra.na_potezi is None:
            (zmagovalec, stirka) = self.igra.stanje_igre()
            if zmagovalec == IGRALEC_R:
                self.rezultat[0] += 1
            elif zmagovalec == IGRALEC_Y:
                self.rezultat[1] += 1
            else:
                self.rezultat[0] += 0.5
                self.rezultat[1] += 0.5
                if self.rezultat[0] == int(self.rezultat[0]):
                    self.rezultat[0] = int(self.rezultat[0])
                    self.rezultat[1] = int(self.rezultat[1])
        self.zacni_igro()

    def nova_igra(self):
        self.rezultat = [0, 0]
        self.zacni_igro()

    def obkrozi(self, stirke):
        d = self.VELIKOST_POLJA
        w = 5 # Odsvetujem spreminjanje (namenoma je fiksna vrednost)
        for stirka in stirke: # Gremo po vseh štirkah
            (i1,j1) = stirka[0]
            (i2,j2) = stirka[-1]
            if (i1 == i2) or (j1 == j2):
                x1 = d/2 + i1*d
                y1 = 13*d/2 - j1*d
                x2 = d/2 + (i2+1)*d
                y2 = 13*d/2 - (j2+1)*d
                self.platno.create_rectangle(x1, y1, x2, y2,
                                             width=w,
                                             tag=Gui.TAG_FIGURA)
            else: # Diagonalni - popravi jih še v kotih
                # Najprej izračunamo središče S = (xt1,yt1)
                # najbolj levega kvadratka
                xt1 = (i1+1)*d
                yt1 = (6-j1)*d

                # Zarotiramo kvadrat za pi/4 v levo
                r = sqrt(2)*d/2
                x1 = xt1 - r
                y1 = yt1
                x2 = xt1
                # Če je štirka desno dol samo preslikamo y2 čez S
                y2 = yt1 + r if j1 < j2 else yt1 - r

                dxy = (sqrt(2) + 6) * d / 2 + (i2-i1-3)*d
                x3 = x1 + dxy
                x4 = x2 + dxy

                if j1 < j2:
                    y3 = y1 - dxy
                    y4 = y2 - dxy
                else:
                    y3 = y1 + dxy
                    y4 = y2 + dxy

                self.platno.create_line(x1, y1, x3, y3,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x2, y2, x4, y4,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x1, y1, x2, y2,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)
                self.platno.create_line(x3, y3, x4, y4,
                                        width=w,
                                        tag=Gui.TAG_FIGURA)

    def platno_klik(self, event):
        (x,y) = (event.x, event.y)
        d = self.VELIKOST_POLJA
        if (x < d/2) or (x > 15*d/2) or (y < d/2) or (y > 13*d/2):
            # V tem primeru smo zunaj igralnega območja
            pass
        else:
            # TODO - preveri za robne pogoje
            i = int((x - d/2) // self.VELIKOST_POLJA) + 1
            j = 5 - int((y - d/2) // self.VELIKOST_POLJA) # BRIŠI?
            if isinstance(self.igra, pop_logika) and j == 0:
                i = -i
            if self.igra.na_potezi == IGRALEC_R:
                self.igralec_r.klik(i)
            elif self.igra.na_potezi == IGRALEC_Y:
                self.igralec_y.klik(i)
            else:
                # Nihče ni na potezi
                pass

    def platno_razveljavi(self, event=None):
        '''Razveljavimo zadnjo potezo in prikažemo prejšnje stanje.'''

        # Razveljavimo prejšnjo potezo
        if isinstance(self.igralec_r, Racunalnik):
            if self.igra.na_potezi == IGRALEC_R:
                # Na potezi računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_Y:
                novo_stanje = self.igra.razveljavi(2)
            else:
                # Igre je konec
                novo_stanje = self.igra.razveljavi(2)
        elif isinstance(self.igralec_y, Racunalnik):
            if self.igra.na_potezi == IGRALEC_Y:
                # Na potezi računalnik, ne naredi ničesar
                return
            elif self.igra.na_potezi == IGRALEC_R:
                novo_stanje = self.igra.razveljavi(2)
            else:
                # TODO
                novo_stanje = self.igra.razveljavi(2)
        else:
            novo_stanje = self.igra.razveljavi()

        if novo_stanje: # Uspešno smo razveljavili potezo
            # Pobrišemo vse figure iz igralne površine        
            self.platno.delete(Gui.TAG_FIGURA)

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj(novo_stanje[0])

            # Popravimo napis nad igralno površino
            self.narisi_platno_menu()
            if self.igra.na_potezi == IGRALEC_R:
                #self.napis.set('Na potezi je RDEČI!')
                self.igralec_r.igraj()
            elif self.igra.na_potezi == IGRALEC_Y:
                #self.napis.set('Na potezi je RUMENI!')
                self.igralec_y.igraj()
        else:
            # Smo na začetku 'zgodovine' (igre)
            pass

    def platno_uveljavi(self, event=None):
        '''Uveljavimo zadnjo razveljavljeno potezo in se vrnemo v njeno stanje.'''

        # Uveljavimo prejšnjo potezo
        novo_stanje = self.igra.uveljavi()

        if novo_stanje: # Uspešno smo uveljavili potezo
            # Pobrišemo vse figure iz igralne površine
            self.platno.delete(Gui.TAG_FIGURA)

            # Narišemo novi (trenutni) položaj
            self.narisi_polozaj(novo_stanje[0])

            # Uredimo grafični prikaz
            if self.igra.na_potezi == IGRALEC_R:
                self.narisi_platno_menu()
                self.igralec_r.igraj()
            elif self.igra.na_potezi == IGRALEC_Y:
                self.narisi_platno_menu()
                self.igralec_y.igraj()
            else:
                (zmagovalec, stirka) = self.igra.stanje_igre()
                self.koncaj_igro(zmagovalec, stirka)
        else:
            # Smo na koncu 'zgodovine' (igre)
            pass

    def pojdi_nazaj(self):
        # TODO
        pass
    
    def povleci_potezo(self, p):
        igralec = self.igra.na_potezi
        t = self.igra.povleci_potezo(p)

        if t is None:
            # Poteza ni bila veljavna
            pass
        else:
            # Premisli še, če res potrebuješ cel p, ali lahko spremeniš,
            # da bodo funkcije vračale le x koordinato
            (zmagovalec, stirka, p1, je_popout) = t # Tukaj je p1 dejanska poteza
            if je_popout:
                self.platno.delete(Gui.TAG_FIGURA)
                self.narisi_polozaj(self.igra.polozaj)
            else:
                if igralec == IGRALEC_R:
                    self.narisi_R(p1)
                elif igralec == IGRALEC_Y:
                    self.narisi_Y(p1)

            # Sedaj pa preverimo, kako se bo igra nadaljevala
            if zmagovalec == NI_KONEC:
                # Igre še ni konec
                self.narisi_platno_menu()
                if self.igra.na_potezi == IGRALEC_R:
                    #self.napis.set('Na potezi je RDEČI!')
                    self.igralec_r.igraj()
                elif self.igra.na_potezi == IGRALEC_Y:
                    #self.napis.set('Na potezi je RUMENI!')
                    self.igralec_y.igraj()
            else:
                # Igra se je končala
                self.koncaj_igro(zmagovalec, stirka)
    
    def prekini_igralce(self):
        '''Sporoči igralcem, da morajo nehati razmišljati.'''
        if self.igralec_r:
            self.igralec_r.prekini()
        if self.igralec_y:
            self.igralec_y.prekini()

    def spremeni_velikost(self, event):
        '''Ta funkcija nam prilagaja velikost polja igralnega območja
            glede na velikost celotnega okna.'''
        self.platno.delete('all')
        (w,h) = (event.width, event.height)
        self.VELIKOST_POLJA = min(w / 8, h / 7)
        self.VELIKOST_GAP = self.VELIKOST_POLJA / 20
        self.platno.config(width=w-0.9*MIN_SIRINA, height=h-200)
        self.narisi_okvir()
        self.narisi_polozaj(self.igra.polozaj)
        if self.igra.na_potezi is None:
            (zmagovalec, stirka) = self.igra.stanje_igre()
            self.koncaj_igro(zmagovalec, stirka)

    def uredi_ime(self, ime):
        text = ime.get()
        dolzina = 7 - min(2, max(text.lower().count('w'), min(1, text.lower().count('m'))))
        if len(text) > dolzina:
            ime.set(text[:dolzina])

    def zacni_igro(self, nova=False):
        '''Zacne novo igro. Torej zaenkrat le pobriše vse dosedanje poteze.'''
        self.prekini_igralce()
        
        # Preverimo, če želimo novo igro, v tem primeru rezultat
        # nastavimo na 0-0
        if nova:
            self.rezultat = [0, 0]

        # Dodamo igralce
        self.igralec_r = self.tip_igralca[self.tip_rdeci.get()]()
        self.igralec_y = self.tip_igralca[self.tip_rumeni.get()]()

        # Pobrišemo vse figure iz igralne površine        
        self.platno.delete(Gui.TAG_FIGURA)

        # Ustvarimo novo igro
        self.igra = self.tip_igre[self.tip.get()]()

        if isinstance(self.igra, five_logika):
            self.narisi_crtice()

        # Dodamo spremenljive elemente v platno_menu
        self.narisi_platno_menu()
        
        # Preverimo, kdo je na potezi
        if self.igra.na_potezi == IGRALEC_R:
            self.igralec_r.igraj()
        elif self.igra.na_potezi == IGRALEC_Y:
            self.igralec_y.igraj()

    def zapri_okno(self, master):
        '''Ta metoda se pokliče, ko uporabnik zapre aplikacijo.'''
        # TODO
        # Igralce najprej ustavimo
        self.prekini_igralce()

        # Zapremo okno
        master.destroy()


######################################################################
## Glavni program

# Glavnemu oknu rečemo "root" (koren), ker so grafični elementi
# organizirani v drevo, glavno okno pa je koren tega drevesa

# Ta pogojni stavek preveri, ali smo datoteko pognali kot glavni program in v tem primeru
# izvede kodo. (Načeloma bi lahko datoteko naložili z "import" iz kakšne druge in v tem
# primeru ne bi želeli pognati glavne kode. To je standardni idiom v Pythonu.)

if __name__ == '__main__':
    # Naredimo glavno okno in nastavimo ime
    root = tkinter.Tk()
    root.title('Stiri v vrsto')
    root.minsize(int(MIN_SIRINA), MIN_VISINA)
    root.geometry('{0}x{1}'.format(int(0.9*MIN_SIRINA + 8*ZVP),
                                   int(7*ZVP)))

    # Naredimo objekt razreda Gui in ga spravimo v spremenljivko,
    # sicer bo Python mislil, da je objekt neuporabljen in ga bo pobrisal
    # iz pomnilnika.
    aplikacija = Gui(root)

    # Kontrolo prepustimo glavnemu oknu. Funkcija mainloop neha
    # delovati, ko okno zapremo.
    root.mainloop()
