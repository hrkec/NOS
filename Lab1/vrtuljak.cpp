#include <cstdio>
#include <cstdlib>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <ctime>
#include "poruka.h"
#include "konstante.h"

int main(int argc, char** argv){
    srand(time(0));
    key_t key = getuid();                           // ključ za stvaranje reda poruka
    int msgid;                                      // id reda poruka
    message msg;
    msgid = createMessageQueue(key);                // dohvati id reda poruka ako već postoji (ili stvori novi)
    msgctl(msgid, IPC_RMID, NULL);             // obriši red poruka (za svaki slučaj ako već postoji red i poruke u njemu)
    msgid = createMessageQueue(key);                // stvori red poruka

    int n = 8; // 8 posjetitelja
    // Stvaranje 8 posjetitelja
    for(int i = 1; i <= n; i++){
        // k = indeks posjetitelja
        char k = i + '0';
        switch (fork()) {
            case -1:                                // greška u stvaranju novog procesa
                printf("Ne mogu kreirati novi proces\n");
                break;
            case 0:                                 // proces dijete
                execl("./posjetitelj", "posjetitelj", &k, NULL);        // sustavski poziv - incijalizacija procesa dijete programom posjetitelj
                exit(1);
        }
    }

    int riding = 0;                                 // brojač posjetitelja koji sjede, tj koji se voze na vrtuljku
    int sleepingTime;                               // broj milisekundi za spavanje
    while(n > 0){                                   // dok postoje posjetitelji

        while(riding < 4){                          // čekaj 4 posjetitelja da zažele vožnju
            receiveMessage(&msg, msgid, ZELIM);     // čekaj poruku ŽELIM od posjetitelja
            msg = createMessage(msg.data, SJEDI);   // stvori poruku SJEDI
            sendMessage(msg, msgid);                // pošalji poruku SJEDI posjetitelju
            riding++;                               // povećaj brojač posjetitelja koji sjede
        }

        usleep(2000);
        printf("\nPokrenuo vrtuljak!\n\n");

        sleepingTime = rand() % (3000 - 1000 + 1) + 1000;    // spavaj sleepingTime milisekundi
        usleep(sleepingTime * 1000);   // prima nanosekunde ( * 1000 )

        printf("\nVrtuljak zaustavljen!\n\n");
        msg = createMessage(msg.data, USTANI);      // stvori poruku USTANI i pošalji ju 4 puta
        sendMessage(msg, msgid);
        sendMessage(msg, msgid);
        sendMessage(msg, msgid);
        sendMessage(msg, msgid);
        riding = 0;                                 // nema nikog na vrtuljku

        usleep(2000);

        while(true){
            // čitanje poruka posjetitelja da su završili s vožnjama
            // čitanje u petlji jer može biti više poruka ZAVRSIO u redu
            if(receiveMessageNoWait(&msg, msgid, ZAVRSIO) == 0){
                n--;
//                printf("\n\n N = %d\n\n", n);
            } else {                                // a ako nema poruke ZAVRSIO u redu, izlazak iz petlje čitanja
                break;
            }
        }
    }

    wait(NULL);
    deleteMessageQueue(msgid);                      // brisanje reda poruka msgid
    printf("Vrtuljak je završio s radom!\n");
    return 0;
}