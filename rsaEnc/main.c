#include <stdio.h>
#include <inttypes.h>
#include <stdlib.h>
#include "tfm.h"

#define PUB_EXP_LEN 3U
#define PRIV_EXP_LEN 128U
#define MOD_LEN 128U

void writeFile(const unsigned char *buffer, size_t size, char *path); /*functie de scriere*/
void writeFile(const unsigned char *buffer, size_t size, char *path)
{
  FILE * fp;
  size_t writeSize = 0;

  fp = fopen(path, "ab+"); /*se deschide fisierul pentru scriere in binar*/
  if (fp == NULL) /*se verifica daca fisierul este gol si se genereaza un mesaj de eroare apoi se
                     inchide si se iese din fisier*/
  {
    printf("Error: There was an Error reading the file %s \n", path);
    fclose(fp);
    exit(1);
  }

  writeSize = fwrite(buffer, sizeof(buffer[0]), size, fp); /*se verifica daca fisierul are aceeasi marime*/
  if (writeSize != size)
  {
    printf("Error: can 't write the expected size ");
    fclose(fp);
    exit(1);
  }

  fclose(fp);
}

void usage(void);
void usage(void) /*functie care ofera informatii despre datele introduse*/
{
  printf("usage(where e is for encrypt and d is for decrypt):\n");
  printf("rsa.exe e input.txt output.txt Mod.dat Exp.dat\n");
  printf("rsa.exe d input.txt output.txt Mod.dat Exp.dat\n");
}

/** \brief This function reads a file
 * 	\out buffer pointer to where the data will be stored
 * 	\in path path to the file
 */
void readFile(unsigned char *buffer, unsigned int * readSize, char *path);
void readFile(unsigned char *buffer, unsigned int * readSize, char *path) /*functia de citire*/
{
  FILE * fp;
  size_t size;

  fp = fopen(path, "rb"); /*deschide fisierul pentru citire in binar*/
  fseek(fp, 0, SEEK_END); /*duce cursorul la sfarsitul fisierului*/
  size = ftell(fp);       /*functie care afiseaza pozitia actuala a fisierului sau lungimea lui*/
  *readSize = size;
  fseek(fp, 0, SEEK_SET); /*pune cursorul la inceputul fisierului*/

  printf("\ninFile size: %d\n", size);

  if (fp == NULL) /*testeaza daca fisierul  are sau nu continut */
  {
    printf("Error: There was an Error reading the file %s \n", path);
    fclose(fp); /*inchide fisierul */
    exit(1);    /*iese din program*/
  }
  else if (fread(buffer, sizeof *buffer, size, fp) !=
           size) /*se verifica daca s a citit intreg fisierul*/
  {
    printf("Error: There was an Error reading the file %s\n", path);
    fclose(fp);
    exit(1);
  }

  fclose(fp);
}
int main(int argc, char *argv[])
{
  fp_int        expPrivBn;
  fp_int        msgBn;
  fp_int        cypBn;
  fp_int        expPubBn;
  fp_int        modBn;
  fp_int        cyphertextBn;
  char          inputFileName[128]         = {0};
  char          ModFileName[128]           = {0};
  char          ExpFileName[128]           = {0};
  char          outputFileName[128]        = {0};
  unsigned int  operation                  = 0; /* 1 for encrypt, 2 for decrypt */
  int           bytesRead                  = 0;
  unsigned char AlicePubExp[PUB_EXP_LEN]   = {0};
  unsigned char AlicePrivExp[PRIV_EXP_LEN] = {0};
  unsigned char AliceMod[MOD_LEN]          = {0};
  unsigned char message[100000]            = {0};
  unsigned char cyphertext[100000]         = {0};
  unsigned int  inputFileSize, outputFileSize, ModFileSize, ExpFileSize, fileReadSize;

  /* rsa.exe d input.txt output.txt Mod.dat Exp.dat
   * argc: number of arguments
   * argv[*]: array of strings which store the arguments */
  if (argc != 6)
  {
    usage();
    exit(1);
  }
  else
  {
    if (*argv[1] == 'e')
    {
      printf("encrypt\n");
      operation = 1;
    }
    else if (*argv[1] == 'd')
    {
      printf("decrypt\n");
      operation = 2;
    }
    else
    {
      usage();
      exit(1);
    }
    strcpy(inputFileName, argv[2]);
    inputFileSize = strlen(inputFileName);

    strcpy(outputFileName, argv[3]);
    outputFileSize = strlen(outputFileName);

    strcpy(ModFileName, argv[4]);
    ModFileSize = strlen(ModFileName);

    strcpy(ExpFileName, argv[5]);
    ExpFileSize = strlen(ExpFileName);

    printf("%s\n", inputFileName); /*se afiseaza numele fisierului de intrare */

    printf("%s\n", outputFileName); /*se afiseaza numele fisierului de iesire */

    printf("%s\n", ModFileName); /*se afiseaza numele fisierului care detine modulul cheii */

    printf("%s\n", ExpFileName); /*se afiseaza numele fisierului care contine exponetul cheii*/

    printf("inFileSize: %d outFileSize: %d\n ModFileSize: %d ExpFileSize: %d",
           inputFileSize,
           outputFileSize,
           ModFileSize,
           ExpFileSize);
  }

  fp_init(&expPrivBn);
  fp_init(&msgBn);
  fp_init(&cypBn);
  fp_init(&expPubBn);
  fp_init(&modBn);
  fp_init(&cyphertextBn);

  readFile(AliceMod, &fileReadSize, ModFileName); /**se citeste modulul lui Alice*/

  fp_read_unsigned_bin(&modBn, AliceMod, sizeof(AliceMod));

  if (operation == 1) /* encrypt */
  {
    int i;
    /* modulo = 5 bits
     * -------------------------------------------------: message.txt
     * ----- ----- ----- ----- ----- ----- ----- -----
     */
    readFile(AlicePubExp, &fileReadSize, ExpFileName); /*se citeste exponentul public a lui Alice*/
    fp_read_unsigned_bin(&expPubBn, AlicePubExp, sizeof(AlicePubExp)); /*converteste din bytearray in bignumber*/

    readFile(message, &fileReadSize, inputFileName);

    bytesRead = (int)fileReadSize;

    for (i = 0; i <= fileReadSize; i += MOD_LEN)
    {
      unsigned int toProcess;
      unsigned int lenBN;

      bytesRead -= MOD_LEN;

      if (bytesRead < 0)
      {
        toProcess = bytesRead + MOD_LEN;
      }
      else
      {
        toProcess = MOD_LEN;
      }

      /*transforma mesajul din BigNumber intr un plain message*/
      fp_read_unsigned_bin(&msgBn, &message[i], toProcess);

      fp_exptmod(&msgBn, &expPubBn, &modBn, &cyphertextBn); /*functia de criptare x^e mod n*/

      fp_to_unsigned_bin(&cyphertextBn, cyphertext);

      lenBN = fp_unsigned_bin_size(&cyphertextBn);

      /*functie care scrie mesajul criptat*/
      writeFile(cyphertext, lenBN, outputFileName);
    }
  }
  else /* decrypt */
  {
    int i;
    readFile(AlicePrivExp, &fileReadSize, ExpFileName); /*se citeste exponentul privat a lui Alice*/
    fp_read_unsigned_bin(&expPrivBn, AlicePrivExp, sizeof(AlicePrivExp)); /*converteste din bytearray in bignumber*/

    readFile(cyphertext, &fileReadSize, inputFileName);

    bytesRead = fileReadSize;

    printf("\nfilereadsize: %d bytesRead: %d\n", fileReadSize, bytesRead);

    for (i = 0; i < fileReadSize; i += MOD_LEN)
    {
      /* sterge continutul arrayului message pt a putea folosi functia strlen() */
      for(unsigned int j = 0U; j < sizeof(message); j++)
      {
        message[j] = 0U;
      }

      bytesRead -= MOD_LEN;

      fp_read_unsigned_bin(&cypBn, &cyphertext[i], MOD_LEN);

      fp_exptmod(&cypBn, &expPrivBn, &modBn, &msgBn); /*functia de decriptare (y^d mod n)*/

      fp_to_unsigned_bin(&msgBn, message); /*mesajul mare se transforma in plaintext(text simplu)*/

      writeFile(message,
                strlen((const char *)message),
                outputFileName); /*se genereaza mesajul care a fost decriptat*/
    }
  }

  return 0;
}

