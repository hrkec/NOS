#include <cstdio>
#include <cstdlib>
#include <unistd.h>
#include <ctime>
#include "poruka.h"
#include "konstante.h"

int main(int argc, char** argv){
    srand(time(0));
    int k = atoi(argv[1]);         // k je identifikator posjetitelja, zadaje se kao argument naredbene linije
                                        // pri stvaranju novog procesa posjetitelja poziv naredbe fork()
//    printf("Stvoren posjetitelj %d\n", k);
    message msg;                        // Poruka koja se prima / šalje
    int msgid;                          // id reda poruka
    key_t key = getuid();               // ključ za stvaranje reda poruka
    msgid = createMessageQueue(key);    // stvori red poruka s ključem ključ (tj. dohvati identifikator reda poruka), spremi identifikator reda u msgid
    char id[1];
    id[0] = k + '0';                    // char zapis broja k (indeks procesa)

    for(int i = 0; i < 3; i++){         // 3 vožnje za svakog posjetitelja
        int sleeping_time = rand() % (2000 - 100 + 1) + 100;    // spavaj sleeping_time milisekundi
        usleep(sleeping_time * 1000);   // prima nanosekunde ( * 1000 )

        printf("Posjetitelj %d se želi voziti!\n", k);
        msg = createMessage(id, ZELIM);         // stvori poruku da se posjetitelj želi voziti
        sendMessage(msg, msgid);                // pošalji poruku u red poruka

        // cekaj odgovor SJEDI
        receiveMessage(&msg, msgid, SJEDI);
        printf("Sjeo posjetitelj %d na vrtuljak.\n", k);

        // cekaj odgovor USTANI
        receiveMessage(&msg, msgid, USTANI);
        printf("Sišao posjetitelj %d s vrtuljka.\n", k);
    }

    // Nakon 3 vožnje, stvori poruku da je posjetitelj završio
    msg = createMessage(id, ZAVRSIO);
    sendMessage(msg, msgid);            // pošalji poruku u red poruka

    printf("\nPosjetitelj %d je ZAVRŠIO!\n\n", k);      // kraj procesa posjetitelj
}