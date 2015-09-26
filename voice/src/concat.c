/*
 * SHITCODE MUTHAFAKA
 */

#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>
#include <stdlib.h>

#include <voice/numbers.h>
#include <voice/alphabet.h>
#include <voice/wav.h>

#define WAV_HEADER_SIZE 0x40

#define LETTER(letter) __samples_ ## letter ## _wav
#define LETTER_LEN(letter) __samples_ ## letter ## _wav_len

long get_sample(char letter, unsigned char **buf)
{
        long len = 0;

        switch (letter) {
        case 'a':
        case 'A':
                *buf = LETTER(A);
                len = LETTER_LEN(A);
                break;

        case 'b':
        case 'B':
                *buf = LETTER(B);
                len = LETTER_LEN(B);
                break;

        case 'c':
        case 'C':
                *buf = LETTER(C);
                len = LETTER_LEN(C);
                break;

        case 'd':
        case 'D':
                *buf = LETTER(D);
                len = LETTER_LEN(D);
                break;

        case 'e':
        case 'E':
                *buf = LETTER(E);
                len = LETTER_LEN(E);
                break;

        case 'f':
        case 'F':
                *buf = LETTER(F);
                len = LETTER_LEN(F);
                break;

        case 'g':
        case 'G':
                *buf = LETTER(G);
                len = LETTER_LEN(G);
                break;

        case 'h':
        case 'H':
                *buf = LETTER(H);
                len = LETTER_LEN(H);
                break;

        case 'i':
        case 'I':
                *buf = LETTER(I);
                len = LETTER_LEN(I);
                break;

        case 'j':
        case 'J':
                *buf = LETTER(J);
                len = LETTER_LEN(J);
                break;

        case 'k':
        case 'K':
                *buf = LETTER(K);
                len = LETTER_LEN(K);
                break;

        case 'l':
        case 'L':
                *buf = LETTER(L);
                len = LETTER_LEN(L);
                break;

        case 'm':
        case 'M':
                *buf = LETTER(M);
                len = LETTER_LEN(M);
                break;

        case 'n':
        case 'N':
                *buf = LETTER(N);
                len = LETTER_LEN(N);
                break;

        case 'o':
        case 'O':
                *buf = LETTER(O);
                len = LETTER_LEN(O);
                break;

        case 'p':
        case 'P':
                *buf = LETTER(P);
                len = LETTER_LEN(P);
                break;

        case 'q':
        case 'Q':
                *buf = LETTER(Q);
                len = LETTER_LEN(Q);
                break;

        case 'r':
        case 'R':
                *buf = LETTER(R);
                len = LETTER_LEN(R);
                break;

        case 's':
        case 'S':
                *buf = LETTER(S);
                len = LETTER_LEN(S);
                break;

        case 't':
        case 'T':
                *buf = LETTER(T);
                len = LETTER_LEN(T);
                break;

        case 'u':
        case 'U':
                *buf = LETTER(U);
                len = LETTER_LEN(U);
                break;

        case 'v':
        case 'V':
                *buf = LETTER(V);
                len = LETTER_LEN(V);
                break;

        case 'w':
        case 'W':
                *buf = LETTER(W);
                len = LETTER_LEN(W);
                break;

        case 'x':
        case 'X':
                *buf = LETTER(X);
                len = LETTER_LEN(X);
                break;

        case 'y':
        case 'Y':
                *buf = LETTER(Y);
                len = LETTER_LEN(Y);
                break;

        case 'z':
        case 'Z':
                *buf = LETTER(Z);
                len = LETTER_LEN(Z);
                break;

        case '0':
                *buf = LETTER(0);
                len = LETTER_LEN(0);
                break;

        case '1':
                *buf = LETTER(1);
                len = LETTER_LEN(1);
                break;

        case '2':
                *buf = LETTER(2);
                len = LETTER_LEN(2);
                break;

        case '3':
                *buf = LETTER(3);
                len = LETTER_LEN(3);
                break;

        case '4':
                *buf = LETTER(4);
                len = LETTER_LEN(4);
                break;

        case '5':
                *buf = LETTER(5);
                len = LETTER_LEN(5);
                break;

        case '6':
                *buf = LETTER(6);
                len = LETTER_LEN(6);
                break;

        case '7':
                *buf = LETTER(7);
                len = LETTER_LEN(7);
                break;

        case '8':
                *buf = LETTER(8);
                len = LETTER_LEN(8);
                break;

        case '9':
                *buf = LETTER(9);
                len = LETTER_LEN(9);
                break;

        default:
                return -EINVAL;
                break;
        }

        *buf += WAV_HEADER_SIZE;
        len -= WAV_HEADER_SIZE;

        return len;
}

long to_audio(const char* const str, unsigned char **buf)
{
        size_t size = 0;
        *buf = malloc(size);

        for (int i = 0; i < strlen(str); i++) {
                unsigned char *letter;
                long len = get_sample(str[i], &letter);
                if (len < 0)
                        continue;

                *buf = realloc(*buf, size+len);

                memcpy(*buf+size, letter, len);

                size += len;
        }

        return size;
}

long read_file(const char* const filename, unsigned char **buf)
{
        FILE *f = fopen(filename, "rb");
        if (!f) {
                return -ENOENT;
        }

        fseek(f, 0, SEEK_END);
        long fsize = ftell(f);
        rewind(f);

        *buf = malloc(fsize + 1);

        fread(*buf, fsize, 1, f);
        fclose(f);

        (*buf)[fsize] = 0;

        return fsize;
}

long string_to_voice_file(const char* const string, const char* const filename)
{
        FILE *f = fopen(filename, "wb");
        if (!f) {
                return -ENOENT;
        }

        /* write header */
        size_t write = fwrite(wav_header, 1, sizeof(wav_header), f);
        if (write <= 0) {
                return -EIO;
        }

        unsigned char *buf;

        long len = to_audio(string, &buf);

        write = fwrite(buf, 1, len, f);
        if (write <= 0) {
                return -EIO;
        }

        return len;
}

static char encoding_table[] = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                                'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
                                'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X',
                                'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f',
                                'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                                'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
                                'w', 'x', 'y', 'z', '0', '1', '2', '3',
                                '4', '5', '6', '7', '8', '9', '+', '/'};

static char *decoding_table = NULL;
static int mod_table[] = {0, 2, 1};

void build_decoding_table() {

        decoding_table = malloc(256);

        for (int i = 0; i < 64; i++)
                decoding_table[(unsigned char) encoding_table[i]] = i;
}



char *base64_encode(const unsigned char *data,
                    size_t input_length,
                    size_t *output_length) {

        *output_length = 4 * ((input_length + 2) / 3);

        char *encoded_data = malloc(*output_length);
        if (encoded_data == NULL) return NULL;

        for (int i = 0, j = 0; i < input_length;) {

                uint32_t octet_a = i < input_length ? (unsigned char)data[i++] : 0;
                uint32_t octet_b = i < input_length ? (unsigned char)data[i++] : 0;
                uint32_t octet_c = i < input_length ? (unsigned char)data[i++] : 0;

                uint32_t triple = (octet_a << 0x10) + (octet_b << 0x08) + octet_c;

                encoded_data[j++] = encoding_table[(triple >> 3 * 6) & 0x3F];
                encoded_data[j++] = encoding_table[(triple >> 2 * 6) & 0x3F];
                encoded_data[j++] = encoding_table[(triple >> 1 * 6) & 0x3F];
                encoded_data[j++] = encoding_table[(triple >> 0 * 6) & 0x3F];
        }

        for (int i = 0; i < mod_table[input_length % 3]; i++)
                encoded_data[*output_length - 1 - i] = '=';

        return encoded_data;
}


unsigned char *base64_decode(const char *data,
                             size_t input_length,
                             size_t *output_length) {

        if (decoding_table == NULL) build_decoding_table();

        if (input_length % 4 != 0) return NULL;

        *output_length = input_length / 4 * 3;
        if (data[input_length - 1] == '=') (*output_length)--;
        if (data[input_length - 2] == '=') (*output_length)--;

        unsigned char *decoded_data = malloc(*output_length);
        if (decoded_data == NULL) return NULL;

        for (int i = 0, j = 0; i < input_length;) {

                uint32_t sextet_a = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
                uint32_t sextet_b = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
                uint32_t sextet_c = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];
                uint32_t sextet_d = data[i] == '=' ? 0 & i++ : decoding_table[data[i++]];

                uint32_t triple = (sextet_a << 3 * 6)
                        + (sextet_b << 2 * 6)
                        + (sextet_c << 1 * 6)
                        + (sextet_d << 0 * 6);

                if (j < *output_length) decoded_data[j++] = (triple >> 2 * 8) & 0xFF;
                if (j < *output_length) decoded_data[j++] = (triple >> 1 * 8) & 0xFF;
                if (j < *output_length) decoded_data[j++] = (triple >> 0 * 8) & 0xFF;
        }

        return decoded_data;
}


void base64_cleanup() {
        free(decoding_table);
}

/* flag is hex : 9ec1eb4a511e622d4396aa2334c2b46fcda39366= */

int main (int argc, char** argv)
{
        printf("VOICE API\nLOGIN: ");
        fflush(stdout);

        char *login;
        scanf("%ms", &login);

        printf("PASSWORD: ");
        fflush(stdout);

        char *password;
        scanf("%ms", &password);

        printf("COMMAND [DOWNLOAD|GENERATE]: ");
        fflush(stdout);
        char *cmd;
        scanf("%ms", &cmd);

        if (!strcmp(cmd, "DOWNLOAD")) {

                char *stat = malloc(strlen(login) + strlen(password) + 0xFF);
                sprintf(stat, "stat '%s:%s/voice.wav' >>/dev/null 2>&1", login, password);

                int res = system(stat);

                if (!res) {
                        char *file = malloc(strlen(login) + strlen(password) + 0xFF);
                        sprintf(file, "%s:%s/voice.wav", login, password);

                        unsigned char *buf;
                        int len = read_file(file, &buf);

                        size_t output_len;
                        char* newbuf = base64_encode(buf, len, &output_len);

                        printf("%s", newbuf);
                        fflush(stdout);
                } else {
                        printf("NOTHING FOR YOU\n");
                        fflush(stdout);
                }

        } else if (!strcmp(cmd, "GENERATE")) {

                printf("TEXT: ");
                fflush(stdout);

                char *text;
                scanf("%ms", &text);

                printf("SUCCESS! TAKE YOU FILE LATER!\n");
                fflush(stdout);

                char *dir = malloc(strlen(login) + strlen(password) + 0xFF);
                sprintf(dir, "mkdir %s:%s >>/dev/null 2>&1", login, password);

                system(dir);

                char *file = malloc(strlen(login) + strlen(password) + 0xFF);
                sprintf(file, "%s:%s/voice.wav", login, password);

                long res = string_to_voice_file(
                        text,
                        file);

                if (res < 0) {
                        return -EIO;
                }

        } else {
                printf("NOT SUPPORTED\n");
                fflush(stdout);
                return -EINVAL;
        }


        /* too lazy to free memory */

        return 0;
}
