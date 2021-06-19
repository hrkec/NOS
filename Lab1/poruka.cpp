#include <cstdio>
#include <cstring>
#include "poruka.h"

// Stvara novi red poruka s ključem key ili vraca identifikator reda poruka ako vec postoji red s tim ključem
int createMessageQueue(key_t key) {
    int res;
    if ((res = msgget(key, 0666 | IPC_CREAT)) == -1) {
        printf("Ne mogu stvoriti red poruka!");
    }
    return res;
}

// Obriši red poruka id
void deleteMessageQueue(int id) {
    if (msgctl(id, IPC_RMID, NULL) == -1) {
        printf("Ne mogu obrisati red poruka!");
    }
}

// Stvara novu poruku tipa type s tekstom text
message createMessage(char *text, int type) {
    message msg;
    strcpy(msg.data, text);
    msg.type = type;
    return msg;
}

// Šalje poruku msg u red poruka id
int sendMessage(message msg, int id) {
    // msgsnd vraća -1 u slučaju pogreške u slanju poruke
    if (msgsnd(id, (struct msgbf *)&msg, strlen(msg.data) + 1, 0) == -1) {
        printf("Ne mogu poslati poruku!");
        return -1;
    }
    return 0;
}

// Prima poruku tipa type iz reda poruka id u strukturu podataka msg
int receiveMessage(message *msg, int id, int type) {
    // msgrcv vraća -1 u slučaju pogreške u čitanju poruke
    if (msgrcv(id, (struct msgbuf *)msg, sizeof(*msg) - sizeof(long), type, 0) == -1) {
        printf("Ne mogu primiti poruku!");
        return -1;
    }
    return 0;
}

// Prima poruku tipa type iz reda poruka id u strkturu podataka msg bez čekanja (neblokirajuće čitanje)
int receiveMessageNoWait(message *msg, int id, int type) {
    if (msgrcv(id, (struct msgbuf *)msg, sizeof(*msg) - sizeof(long), type, IPC_NOWAIT) == -1) {
        return -1;
    }
    return 0;
}
