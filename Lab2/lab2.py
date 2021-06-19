from tkinter import filedialog

from Crypto.Cipher import AES, DES3, PKCS1_OAEP
from Crypto.PublicKey import RSA

from Crypto.Hash import SHA512, SHA256
from Crypto.Signature import PKCS1_v1_5

from tkinter import *

root = Tk()
root.title("NOS Lab2")

# Varijable za spremanje vrste (de)kriptiranja
r = IntVar()
sym_crypt = StringVar(None, "DES")
sym_decrypt = StringVar(None, "DES")
mode_crypt = StringVar(None, "CBC")
mode_decrypt = StringVar(None, "CBC")
digest_crypt = StringVar(None, "SHA256")
digest_decrypt = StringVar(None, "SHA256")
w = Canvas(root)
decryptedMessage = None


# Funkcija za odabir simetričnog ključa kriptiranja
# Ime datoteke s ključem se sprema u root.filename i ispisuje na label
def otvori_kljuc(canvas):
    global label

    root.filename = filedialog.askopenfile(initialdir=".", initialfile="./key24.pem", title="Odaberi ključ kriptiranja",
                                           filetypes=(("pem files", "key*.pem"), ("all files", "*.*")))
    label = Label(canvas, text=root.filename.name).grid(row=4, column=2, columnspan=3)

# Funkcija za odabir datoteke digitalnog potpisa
# Ime datoteke s digitalnim potpisom se sprema u root.signaturename i ispisuje na labelSignature
def odaberi_potpis(canvas):
    global labelSignature

    root.signature = filedialog.askopenfile(initialdir=".", initialfile="./signature.bin",
                                           title="Odaberi datoteku digitalnog potpisa",
                                           filetypes=(("bin files", "signature*.bin"), ("all files", "*.*")))
    labelSignature = Label(canvas, text=root.signature.name).grid(row=8, column=2, columnspan=3)


# Funkcija za odabir omotnice
# Ime datoteke s omotnicom se sprema u root.envelopename i ispisuje na label
def odaberi_omotnicu(canvas):
    global label

    root.envelopename = filedialog.askopenfile(initialdir=".", initialfile="./envelope.bin",
                                               title="Odaberi digitalnu omotnicu",
                                               filetypes=(("bin files", "envelope*.bin"), ("all files", "*.*")))
    label = Label(canvas, text=root.envelopename.name).grid(row=4, column=2, columnspan=3)


# Funkcija za odabir privatnog RSA kljuca posiljatelja (private1_*.pem) prilikom potpisivanja
# Ime datoteke s ključem se sprema u root.rsasname i ispisuje na labelSRSA
def odaberi_privatni_rsa_posiljatelja(canvas):
    global labelSRSA
    root.rsasname = filedialog.askopenfile(initialdir=".", initialfile="./private1_2048.pem",
                                           title="Odaberi privatni ključ",
                                           filetypes=(("pem files", "private1*.pem"), ("all files", "*.*")))
    labelSRSA = Label(canvas, text=root.rsasname.name).grid(row=7, column=2, columnspan=3)


# Funkcija za odabir privatnog RSA kljuca primatelja (private2_*.pem) prilikom dekriptiranja primljene poruke
# Ime datoteke s ključem se sprema u root.rsasname2 i ispisuje na labelSRSA2
def odaberi_privatni_rsa_primatelja(canvas):
    global labelSRSA2
    root.rsasname2 = filedialog.askopenfile(initialdir=".", initialfile="./private2_2048.pem",
                                            title="Odaberi privatni ključ",
                                            filetypes=(("pem files", "private2*.pem"), ("all files", "*.*")))
    labelSRSA2 = Label(canvas, text=root.rsasname2.name).grid(row=4, column=2, columnspan=3)


# Funkcija za odabir javnog RSA kljuca posiljatelja (public1_*.pem) prilikom dekriptiranja primljenog sažetka
# Ime datoteke s ključem se sprema u root.rsapname i ispisuje na labelPRSA
def odaberi_javni_rsa_posiljatelja(canvas):
    global labelPRSA
    root.rsapname = filedialog.askopenfile(initialdir=".", initialfile="./public1_2048.pem",
                                           title="Odaberi javni ključ pošiljatelja",
                                           filetypes=(("pem files", "public1*.pem"), ("all files", "*.*")))
    labelPRSA = Label(canvas, text=root.rsapname.name).grid(row=9, column=2, columnspan=3)


# Funkcija za odabir javnog RSA kljuca primatelja (public2_*.pem) prilikom kriptiranja simetričnog ključa
# Ime datoteke s ključem se sprema u root.rsapname2 i ispisuje na labelPRSA2
def odaberi_javni_rsa_primatelja(canvas):
    global labelPRSA2
    root.rsapname2 = filedialog.askopenfile(initialdir=".", initialfile="./public2_2048.pem",
                                            title="Odaberi javni ključ primatelja",
                                            filetypes=(("pem files", "public2*.pem"), ("all files", "*.*")))
    labelPRSA2 = Label(canvas, text=root.rsapname2.name).grid(row=5, column=2, columnspan=3)


# Funkcija za kriptiranje poruke i stvaranje digitalne omotnice
# Argument funkcije message je poruka za kriptiranje, upisana u text box
def kriptiraj(message):
    print("Kriptira se: ", message, " kljucem ", root.filename.name, " sustavom ", sym_crypt.get(), " modom ", mode_crypt.get())
    # KRIPTIRANJE PORUKE
    # DES kriptiranje
    if sym_crypt.get() == "DES":
        length = 8 - (len(message) % 8)                                # nadopuna na 8 bajtova
        message += chr(length) * length

        message_b = message.encode()

        iv_file = open("ivDES.bin", "rb")                               # učitaj inicijalizacijski vektor iz datoteke 'ivDES.bin'
        iv = iv_file.read()
        iv_file.close()

        keyK = root.filename.read().encode()                            # učitaj simetrični ključ za kriptiranje iz datoteke root.filename
        if mode_crypt.get() == "CBC":                                   # CBC način kriptiranja
            cipher = DES3.new(keyK, DES3.MODE_CBC, iv)

        else:                                                           # CFB način kriptiranja
            cipher = DES3.new(keyK, DES3.MODE_CFB, iv)

        encryptedMessage = cipher.encrypt(message_b)                    # kriptiraj poruku odabranim načinom

    # AES kriptiranje
    else:
        length = 16 - (len(message) % 16)                               # nadopuna na 16 bajtova
        message += chr(length) * length
        message_b = message.encode()

        iv_file = open("ivAES.bin", "rb")                               # učitaj inicijalizacijski vektor iz datoteke 'ivAES.bin'
        iv = iv_file.read()
        iv_file.close()
        keyK = root.filename.read().encode()                            # učitaj simetrični ključ za kriptiranje iz datoteke root.filename

        if mode_crypt.get() == "CBC":                                   # CBC način kriptiranja
            cipher = AES.new(keyK, AES.MODE_CBC, iv)

        else:                                                           # CFB način kriptiranja
            cipher = AES.new(keyK, AES.MODE_CFB, iv)

        encryptedMessage = cipher.encrypt(message_b)                    # kriptiraj poruku odabranim načinom

    # KRIPTIRANJE SIMETRIČNOG KLJUČA
    keyPB = RSA.importKey(open(root.rsapname2.name).read())             # učitaj javni ključ primatelja poruke
    encryptor = PKCS1_OAEP.new(keyPB)                                   # inicijalizacija encryptora za kriptiranje ključem keyPB
    encryptedKey = encryptor.encrypt(keyK)                              # kriptiraj ključ keyK (kojim se kriptirala poruka) javnim ključem primatelja keyPB

    envelope = [encryptedMessage, encryptedKey]
    file2 = open("envelope.bin", "wb")                                  # otvori binarnu datoteku envelope.bin za upis digitalne omotnice
    duljinaPoruke = len(encryptedMessage)
    file2.write(duljinaPoruke.to_bytes(5, byteorder='big'))             # zapiši duljinu poruke
    file2.write(envelope[0])                                            # zapiši kriptiranu poruku
    file2.write(envelope[1])                                            # zapiši kriptirani ključ
    file2.close()

    label2 = Label(root, text="Generirana digitalna omotnica u datoteku envelope.bin!").pack()  # ispiši obavijest da je generirana omotnica


# Funkcija za generiranje digitalnog potpisa
# Argument funkcije je poruka koja se potpisuje
def potpis(message):
    key = RSA.importKey(open(root.rsasname.name).read())                # učitaj (svoj) privatni ključ pošiljatelja
    if digest_crypt.get() == "SHA256":                                  # SHA3-256
        h = SHA256.new()
    else:                                                               # SHA3-512 hash
        h = SHA512.new()
    message_b = message.encode()
    h.update(message_b)                                                 # izračunaj sažetak (hash) poruke koristeći odabranu funkciju izračunavanja

    signature = PKCS1_v1_5.new(key).sign(h)                               # generiraj digitalni potpis koristeći izračunati sažetak
    file3 = open("signature.bin", "wb")
    file3.write(signature)                                              # spremi digitalni potpis u binarnu datoteku 'signature.bin'
    file3.close()
    label2 = Label(root, text="Generiran digitalni potpis u datoteku signature.bin!").pack()     # ispiši obavijest da je generiran potpis


# Funkcija za otvaranje i provjeru digitalne omotnice
# Argumenti funkcije su lokacija digitalne omotnice i canvas za ispis obavijesti
def dekriptiraj(envelope, w):
    file4 = open(envelope.name, 'rb')                                   # otvori digitalnu omotnicu
    velPoruke = file4.read(5)
    velPoruke = int.from_bytes(velPoruke, byteorder='big')              # pročitaj veličinu poruke

    encryptedMessage = file4.read(velPoruke)                            # pročitaj kriptiranu poruku iz omotnice
    encryptedKey = file4.read()                                         # pročitaj kriptirani ključ iz omotnice

    keySA = RSA.importKey(open(root.rsasname2.name).read())             # učitaj (svoj) privatni ključ primatelja
    decryptor = PKCS1_OAEP.new(keySA)                                   # inicijalizacija decryptora koristeći učitani ključ keySA
    decryptedKey = decryptor.decrypt(encryptedKey)                      # dekriptiraj kriptirani ključ

    if sym_decrypt.get() == "DES":                                      # DES dekripcija
        iv_file = open("ivDES.bin", "rb")                               # učitaj inicijalizacijski vektor
        iv = iv_file.read()
        iv_file.close()
        if mode_decrypt.get() == "CBC":                                 # CBC način
            decipher = DES3.new(decryptedKey, DES3.MODE_CBC, iv)
        else:                                                           # CFB način
            decipher = DES3.new(decryptedKey, DES3.MODE_CFB, iv)

    else:                                                               # AES dekripcija
        iv_file = open("ivAES.bin", "rb")                               # učitaj inicijalizacijski vektor
        iv = iv_file.read()
        iv_file.close()
        if mode_decrypt.get() == "CBC":                                 # CBC način
            decipher = AES.new(decryptedKey, AES.MODE_CBC, iv)
        else:                                                           # CFB način
            decipher = AES.new(decryptedKey, AES.MODE_CFB, iv)

    decryptedMessage = decipher.decrypt(encryptedMessage)               # dekriptiraj kriptiranu poruku
    decryptedMessage = decryptedMessage[:-decryptedMessage[-1]]         # brisanje nadopune
    result = Label(w, text="Primljena poruka: " + decryptedMessage.decode())    # ispiši primljenu (dekriptiranu) poruku
    result.grid(row=6, column=1, rowspan=2, columnspan=5)

    decryptedFile = open("message.bin", "wb")
    decryptedFile.write(decryptedMessage)                               # upiši dekriptiranu poruku u 'message.bin'


# Funkcija za izradu digitalnog pečata - izrada digitalne omotnice i digitalnog potpisa
def izrada_pecata():
    global w
    w.destroy()
    w = Canvas(root)
    w.pack()

    w4 = Canvas(w, height=40)
    w4.pack()
    e = Entry(w4, width=40)                                             # text box za upis poruke
    e.pack()
    e.delete(0, END)
    e.insert(0, "Upisi poruku za kriptiranje i potpis!")

    w2 = Canvas(w, height=30)
    w2.pack()
    w2.create_text(200, 10, text="Odaberi simetrični kriptosustav i način kriptiranja")

    w3 = Canvas(w)
    w3.pack()

    aes = Radiobutton(w3, text="AES", variable=sym_crypt, value="AES")      # gumbovi za odabir simetričnog kriptosustava
    des3 = Radiobutton(w3, text="3-DES", variable=sym_crypt, value="DES")

    mode_crypt_ecb = Radiobutton(w3, text="CFB", variable=mode_crypt, value="CFB")  # gumbovi za odabir načina kriptiranja
    mode_crypt_cbc = Radiobutton(w3, text="CBC", variable=mode_crypt, value="CBC")

    w5 = Canvas(w, height=20)
    w5.pack()
    w5.create_text(200, 10, text="Odaberi funkciju za izračunavanje sažetka poruke")

    w6 = Canvas(w)
    w6.pack()

    digest256 = Radiobutton(w6, text="SHA3-256", variable=digest_crypt, value="SHA256") # gumbovi za odabir funkcije za izračun sažetka
    digest512 = Radiobutton(w6, text="SHA3-512", variable=digest_crypt, value="SHA512")

    aes.grid(row=1, column=1)
    des3.grid(row=2, column=1)

    mode_crypt_ecb.grid(row=1, column=3)
    mode_crypt_cbc.grid(row=2, column=3)

    digest256.grid(row=1, column=1)
    digest512.grid(row=1, column=2)

    root.filename = open('./key24.pem')
    kljuc_gumb = Button(w3, text="Odaberi simetrični ključ", command=lambda: otvori_kljuc(w3))  # gumb za odabir simetričnog ključa za kriptiranje
    kljuc_gumb.grid(row=4, column=1)
    label = Label(w3, text=root.filename.name).grid(row=4, column=2, columnspan=3)              # ispis lokacije odabranog ključa

    root.rsapname2 = open('./public2_2048.pem')
    kljuc_gumb_primatelj = Button(w3, text="Odaberi javni ključ primatelja",                    # gumb za odabir javnog ključa primatelja
                                  command=lambda: odaberi_javni_rsa_primatelja(w3))
    kljuc_gumb_primatelj.grid(row=5, column=1)
    labelPRSA2 = Label(w3, text=root.rsapname2.name).grid(row=5, column=2, columnspan=3)        # ispis lokacije odabranog javnog ključa primatelja

    kriptiraj_gumb = Button(w3, text="Generiraj omotnicu", command=lambda: kriptiraj(e.get()))  # gumb za pokretanje generiranja digitalne omotnice
    kriptiraj_gumb.grid(row=6, column=1, columnspan=5)

    root.rsasname = open('./private1_2048.pem')
    rsa_gumb = Button(w3, text="Odaberi svoj privatni ključ", command=lambda: odaberi_privatni_rsa_posiljatelja(w3))    # gumb za odabir privatnog ključa pošiljatelja
    rsa_gumb.grid(row=7, column=1)
    labelSRSA = Label(w3, text=root.rsasname.name).grid(row=7, column=2, columnspan=3)          # ispis lokacije odabranog privatnog ključa pošiljatelja

    potpis_gumb = Button(w6, text="Generiraj potpis", command=lambda: potpis(e.get()))          # gumb za pokretanje generiranja digitalnog potpisa
    potpis_gumb.grid(row=2, column=1, columnspan=2)


# Funkcija za provjeru digitalnog potpisa
def provjera_potpisa(w):
    decryptedFile = open("message.bin", "rb")                           # učitaj dekriptiranu primljenu poruku
    decryptedMessage = decryptedFile.read()                             # pročitaj poruku
    if digest_decrypt.get() == "SHA256":
        h = SHA256.new()
    else:
        h = SHA512.new()
    h.update(decryptedMessage)                                          # Izračunaj sažetak primljene poruke

    # Dekriptiraj kriptirani hash
    key2 = RSA.importKey(open(root.rsapname.name).read())               # učitaj javni ključ pošiljatelja poruke
    file5 = open("signature.bin", "rb")                                 # učitaj digitalni potpis
    signature = file5.read()
    verifier = PKCS1_v1_5.new(key2)

    if verifier.verify(h, signature):                                                                # provjeri digitalni potpis
        labeeel = Label(w, text="Digitalni potpis je valjan!").grid(row=2, column=1, columnspan=2)      # ispiši obavijest da je digitalni potpis valjan
    else:
        labeeel = Label(w, text="Digitalni potpis nije valjan!").grid(row=2, column=1, columnspan=2)    # ispiši obavijest da digitalni potpis nije valjan

    file5.close()

def provjera_pecata():
    global w
    w.destroy()
    w = Canvas(root)
    w.pack()

    w4 = Canvas(w, height=40)
    w4.pack()
    root.envelopename = open('./envelope.bin')
    omotnica_gumb = Button(w4, text="Odaberi omotnicu", command=lambda: odaberi_omotnicu(w4))   # gumb za odabir digitalne omotnice
    omotnica_gumb.grid(row=4, column=1)
    label = Label(w4, text=root.envelopename.name).grid(row=4, column=2, columnspan=3)

    w2 = Canvas(w, height=30)
    w2.pack()
    w2.create_text(200, 10, text="Odaberi simetrični kriptosustav i način kriptiranja")

    w3 = Canvas(w)
    w3.pack()

    aes = Radiobutton(w3, text="AES", variable=sym_decrypt, value="AES")                        # gumbovi za odabir simetričnog kriptosustava
    des3 = Radiobutton(w3, text="3-DES", variable=sym_decrypt, value="DES")

    mode_decrypt_ecb = Radiobutton(w3, text="CFB", variable=mode_decrypt, value="CFB")          # gumbovi za odabir načina kriptiranja
    mode_decrypt_cbc = Radiobutton(w3, text="CBC", variable=mode_decrypt, value="CBC")

    w5 = Canvas(w, height=20)
    w5.pack()
    w5.create_text(200, 10, text="Odaberi funkciju za izračunavanje sažetka poruke")

    w6 = Canvas(w)
    w6.pack()

    digest256 = Radiobutton(w6, text="SHA3-256", variable=digest_decrypt, value="SHA256")       # gumbovi za odabir funkcije za izračun sažetka poruke
    digest512 = Radiobutton(w6, text="SHA3-512", variable=digest_decrypt, value="SHA512")

    aes.grid(row=1, column=1)
    des3.grid(row=2, column=1)

    mode_decrypt_ecb.grid(row=1, column=3)
    mode_decrypt_cbc.grid(row=2, column=3)

    digest256.grid(row=1, column=1)
    digest512.grid(row=1, column=2)

    root.rsasname2 = open('./private2_2048.pem')
    rsa_gumb2 = Button(w3, text="Odaberi svoj privatni ključ", command=lambda: odaberi_privatni_rsa_primatelja(w3))     # gumb za odabir privatnog ključa primatelja
    rsa_gumb2.grid(row=4, column=1)
    labelPRSA2 = Label(w3, text=root.rsasname2.name).grid(row=4, column=2, columnspan=3)

    root.filename = open('./envelope.bin')
    kljuc_gumb = Button(w3, text="Otvori omotnicu", command=lambda: dekriptiraj(root.filename, w3))             # gumb za pokretanje funkcije za otvaranje i provjeru digitalne omotnice
    kljuc_gumb.grid(row=5, column=1, columnspan=3)

    root.signature = open('./signature.bin')
    potpis_gumb = Button(w3, text="Odaberi digitalni potpis", command=lambda: odaberi_potpis(w3))               # gumb za odabir datoteke digitalnog potpisa
    potpis_gumb.grid(row=8, column=1)
    labelSignature = Label(w3, text=root.signature.name).grid(row=8, column=2, columnspan=3)

    root.rsapname = open('./public1_2048.pem')
    rsa_gumb = Button(w3, text="Odaberi javni ključ pošiljatelja", command=lambda: odaberi_javni_rsa_posiljatelja(w3))  # gumb za odabir javnog ključa pošiljatelja
    rsa_gumb.grid(row=9, column=1)
    labelPRSA = Label(w3, text=root.rsapname.name).grid(row=9, column=2, columnspan=3)

    w7 = Canvas(w, height=20)
    w7.pack()

    potpis_gumb = Button(w6, text="Provjeri potpis", command=lambda: provjera_potpisa(w7))                      # gumb za pokretanje funkcije za provjeru digitalnog potpisa
    potpis_gumb.grid(row=6, column=1, columnspan=2)


canvas = Canvas(root, width=400, height=300, bg="white")
canvas.pack()

frame = Frame(root)
frame.pack()

izrada = Radiobutton(canvas, text="Izrada pečata", variable=r, value=1, command=izrada_pecata)
izrada.grid(row=1, column=1)
provjera = Radiobutton(canvas, text="Provjera pečata", variable=r, value=2, command=provjera_pecata)
provjera.grid(row=1, column=2)

mainloop()