#include <cstdlib>
#include <ctime>
#include <unistd.h>
#include <cstring>
#include <sys/wait.h>
#include <queue>
#include <vector>
#include <cstdio>
#include <fcntl.h>

#define MIN_FILOZOFA 3
#define MAX_FILOZOFA 10

/*
 *  Opisnici cjevovoda
 *  fd[1] je deskriptor ulazne strane cjevovoda. Pisanjem u njega stavljaju se podaci u cjevovod,
 *  a čitanje iz fd[0] (deskriptor izlazne strane cjevovoda) vadi podatke van
 */
int fd [MAX_FILOZOFA][MAX_FILOZOFA][2];

int n;  // n = broj filozofa
char received[15] = "";
char message[15] = "";

/*
    Pomocna klasa za usporedbu zahtjeva u prioritetni red
    Zahtjev je vector<int> = {i, t[i]} - sortira se uzlazno po elementu t[i], na indeksu 1
*/
class CompareClass {
public:
    bool operator() (const std::vector<int> a, const std::vector<int> b){
        return a[1] > b[1];
    }
};

/*
 *  Funkcija koju izvršava svaki proces filozof
 *  Argumenti:
 *      uid - identifikator (indeks) procesa filozofa
 *      timestamp - pocetna vrijednost lokalnog sata
 */
void filozof(int uid, int timestamp) {
    int otherId, otherTimestamp, sleepingTime;
    int currentTimestamp = timestamp;
    int newTimestamp = currentTimestamp;

    std::priority_queue<std::vector<int>, std::vector<std::vector<int> >, CompareClass> queue;   // prioritetni red za zahtjeve
    std::vector<int> request; // pomocna varijabla za zahtjev{i, t[i]}

    // inicijalizacija cjevovoda - zatvaranje strana
    for(int i = 0; i < n; i++){
        if(i != uid){
            close(fd[uid][i][0]);  // zatvori izlaznu stranu cjevovoda proces uid -> proces i
            close(fd[i][uid][1]);  // zatvori ulaznu stranu cjevovoda proces i -> proces uid
        }
    }

    printf("Filozof %d: 'Sudjelujem na konferenciji!'\n", uid);
    sleepingTime = rand() % (2000 - 100 + 1) + 100;    // spavaj sleepingTime milisekundi [100, 2000]
    usleep(sleepingTime * 1000);   // prima nanosekunde ( * 1000 )

    request = {uid, currentTimestamp};           // Zahtjev (uid,currentTimestamp)=(i,T[i])
    queue.push(request);                    // dodaj u vlastiti prioritetni red zahtjeva

    sprintf(message, "ZAHTJEV(%d,%2d)", uid, currentTimestamp);             // message = ZAHTJEV(i,T[i])
    // Šalji zahtjeve za ulazak u kritični odsječak svim ostalim procesima
    for(int i = 0; i < n; i++){
        if(i != uid){
            printf("Filozof %d: 'Šaljem filozofu %d: %s'\n", uid, i, message);
            write(fd[uid][i][1], message, strlen(message) + 1);        // Piši (šalji zahtjev) na svaki izlazni cjevovod
            usleep(1000);
        }
    }

    // Primi zahtjeve od ostalih procesa
    for(int i = 0; i < n; i++){
        if(i != uid){
            usleep(500);
            while(read(fd[i][uid][0], received, 15) == -1);       // read vraća -1 ako nema što za čitati
                                                                        // čekaj zahtjev od svakog procesa (blokirajuće)

            sscanf(received, "ZAHTJEV(%d,%d)", &otherId, &otherTimestamp);   // Učitaj i, T[i]
            printf("Filozof %d čita: 'ZAHTJEV(%d,%d)'\n", uid, otherId, otherTimestamp);

            // Uskladi svoj logički sat pravilima globalnog logičkog sata
            if(newTimestamp > otherTimestamp){
                newTimestamp += 1;
            } else {
                newTimestamp = otherTimestamp + 1;
            }

            // Stavi ZAHTJEV u svoj prioritetni red čekanja
            request = {otherId, otherTimestamp};
            queue.push(request);

            // Šalje poruku ODGOVOR
            sprintf(message, "ODGOVOR(%d,%2d)", uid, newTimestamp);        // message = ODGOVOR(i,T[i])
            printf("Filozof %d: 'Šaljem filozofu %d: %s'\n", uid, i, message);
            write(fd[uid][i][1], message, strlen(message) + 1);         // Pošalji ODGOVOR (message)
        }
    }

    // Čekaj na odgovore ostalih filozofa
    for(int i = 0; i < n; i++){
        if(i != uid){
            sleep(2);
            while(read(fd[i][uid][0], received, 15) == -1);           // čekaj odgovor svakog procesa (blokirajuće)
            sscanf(received, "ODGOVOR(%d,%d)", &otherId, &otherTimestamp);
            printf("Filozof %d čita: 'ODGOVOR(%d,%d)'\n", uid, otherId, otherTimestamp);
        }
    }

    // Ako zahtjev procesa nije na početku reda - ne može ući u kritični odsječak - čekanje na poruke IZLAZAK
    while(uid != queue.top()[0]){
        // Čekam izlazak
        for(int i = 0; i < n; i++){ // prolaz kroz sve cjevovode
            if(uid != i){
                if(read(fd[i][uid][0], received, 15) != -1){  // neblokirajuće čitanje - čeka se izlazak bilo kojeg procesa koji je bio u kritičnom odsječku
                    sscanf(received, "IZLAZAK(%d,%d)", &otherId, &otherTimestamp);
                    printf("Filozof %d čita: 'IZLAZAK(%d,%d)'\n", uid, otherId, otherTimestamp);
                    queue.pop();        // makni ZAHTJEV s početka reda
                }
            }
        }
    }

    // Ulazak u kritični odsječak
    printf("\nFilozof %d je za stolom!\n\n", uid);
    sleep(2);

    // Izlazak iz kritičnog odsječka
    queue.pop();            // makni svoj zahtjev s početka reda
    sprintf(message, "IZLAZAK(%d,%2d)", uid, currentTimestamp);  // message = IZLAZAK(i,T[i])
    for(int i = 0; i < n; i++){
        if(i != uid){
            printf("Filozof %d: 'Šaljem filozofu %d: %s'\n", uid, i, message);
            write(fd[uid][i][1], message, strlen(message) + 1); // Šalji svim procesima poruku message (IZLAZAK(i,T[i]))
        }
    }
    sleepingTime = rand() % (2000 - 100 + 1) + 100;    // spavaj sleepingTime milisekundi [100, 2000]
    usleep(sleepingTime * 1000);   // prima nanosekunde ( * 1000 )
//    printf("Filozof %d napušta konferenciju!\n", uid);  // kraj procesa
}

// Glavni program - inicijalizacija cjevovoda i stvaranje procesa filozofa
int main(int argc, char** argv){
    srand(time(NULL));
    int pid = getpid();
    int timestamp;     // lokalni sat (za argument funkciji filozof)

    // Unos broja filozofa
    printf("Unesi broj filozofa (%d - %d): ", MIN_FILOZOFA, MAX_FILOZOFA);
    scanf("%d", &n);
    while(n < MIN_FILOZOFA || n > MAX_FILOZOFA){
        printf("Pogrešan unos. Unesi broj filozofa (%d - %d): ", MIN_FILOZOFA, MAX_FILOZOFA);
        scanf("%d", &n);
    }

    // inicijalizacija cjevovoda
    for(int i = 0; i < n; i++){
        for(int j = 0; j < n; j++){
            if(i != j)
                pipe2(fd[i][j], O_NONBLOCK);        // zastavica O_NONBLOCK kreira cjevovode u neblokirajućem načinu
        }
    }

    // stvori procese filozofa
    for(int i = 0; i < n; i++){
        timestamp = rand() % 100 + 1;               // nasumična vrijednost lokalnog sata svakog filozofa
        switch(fork()){
            case -1:                                // greška
                printf("Ne mogu kreirati novi proces\n");
                exit(2);
            case 0:                                 // proces dijete
                filozof(i, timestamp);              // dijete izvodi funkciju filozof
                exit(1);
        }
    }

    if (getpid() == pid) {                          // proces roditelj
        for(int j = 0; j < n; j++)
            wait(NULL);
        printf("\n\nKonferencija je završila!\n\n");
    }

    exit(0);                                 // zatvara sve deskriptore
}

