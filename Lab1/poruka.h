#ifndef NOS1_PORUKA_H
#define NOS1_PORUKA_H

#include <sys/msg.h>
#include <sys/types.h>
#include <sys/ipc.h>

#define LENGTH 8

// Struktura podataka poruke
typedef struct {
    long type;
    char data[LENGTH];
} message;

int createMessageQueue(key_t key);

void deleteMessageQueue(int id);

message createMessage(char *text, int type);

int sendMessage(message msg, int id);

int receiveMessage(message *msg, int id, int type);

int receiveMessageNoWait(message *msg, int id, int type);

#endif //NOS1_PORUKA_H
