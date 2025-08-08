#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>
#include "datafile.h"

typedef enum {FMT_OLD, FMT_NEW} FileFmt;
#define TRUE  1
#define FALSE 0

#define MIN(A,B)  (((A) < (B)) ? (A) : (B))

/*
static gint nadc_old(const DataFile *df);
static void align (DataFile *df);
static gsize nextbytes(void *buf, gsize bufsize, DataFile *df);
int nadc_new(DataFile *df);
*/
static int aligned(const unsigned char *event, unsigned int nadc);
static void skip_header(DataFile *df);

static unsigned int adcnum (unsigned short adc)
// Old data format
{
    unsigned char *h = (unsigned char *)&adc;
    return (h[1] & 0xE0) >> 5;
}


static unsigned short adcval (unsigned short adc)
// Old data format
{
    unsigned char *h = (unsigned char *)&adc;
    return (h[1] & 31) << 8 | h[0];
}


static int nextbytes(void *buf, int bufsize, DataFile *df)
// Put the next 'bufsize' bytes into buf.  Take them from df->firstbytes if
// there's any left, otherwise read from df->zf.  Return actual number of bytes
// put into buf.
{
    int n, m = 0, tot = 0;
    char *h;

    n = df->nfbytes - df->fbi;   // Bytes left in df->fbytes

    if (n > 0) {
        m = MIN(n, bufsize);
        memmove(buf, &(df->fbytes[df->fbi]), m);
        df->fbi += m;
        tot = m;
    } 

    if (bufsize - m > 0) {
        h = &((char *)buf)[m];
        tot += fread(h, 1, bufsize - m, df->fp);
		//int val1 = h[0];
		//int val2 = h[1];
    }

    return tot;
}


DataFile *datafile_open(const char *fname, int *nadc)
// Return NULL if fname is empty.  
//
// If nadc < 0, try to resolve the number of ADC:s from data 
{
    DataFile *df;

//    DEBUG_PRINT("in\n");

    df = (DataFile *) malloc (sizeof(DataFile));
    if (df == NULL) printf("Can't allocate memory");

    df->nevents = 0;
    df->ntimer = 0;
    df->nerrors = 0;
    df->nrtc = 0;

    df->fbi = 0;
    df->fmt = 1;

    df->fp = fopen(fname, "rb");

    if (fname)
        df->fname = strdup(fname);
    else
        df->fname = strdup("(stdin)");

    df->nfbytes = fread(df->fbytes, 1, NFBYTES, df->fp);
    if (df->nfbytes == 0) return NULL;

        skip_header(df);
        if (*nadc < 0) {
            // *nadc = df->nadc = nadc_new(df); //TCL 8.4.14
			*nadc = df->nadc = 2;
            fprintf(stderr, "The number of ADC:s in data is fixed to be %i\n", *nadc);
        } else
            df->nadc = *nadc;
    return df;
}


static void skip_header(DataFile *df)
{
    char word[11];
    const int wordlen = sizeof(word)-1;
    char c[2];

//    DEBUG_PRINT("in\n");
    word[wordlen] = '\0';
    if (nextbytes(word, wordlen, df) != wordlen)
        printf("Can't find beginning of listdata in file '%s'\n", df->fname);

    while (strcmp(word, "[LISTDATA]") != 0) {
        memmove(word, &word[1], wordlen-1);
//            g_print("%s\n", word);						// JoMe 2014.01.31 removed 
        if (nextbytes(&word[wordlen-1], 1, df) != 1) {
//            g_print("word = '%s'\n", word);					// JoMe 2014.01.31 removed 
            printf("Can't find beginning of listdata in file '%s'\n", 
                     df->fname);
        }
    }

    // Read final linebreak (Windows/DOS-style)
    nextbytes(c, 2, df);
/*
    DEBUG_PRINT("%i %i\n", c[0], c[1]);
    DEBUG_PRINT("out '%s'\n", word);
*/
}


static void align(DataFile *df)
{
    unsigned int i = 0;

    while (!aligned(&(df->fbytes[i]), df->nadc) 
           && i < (df->nfbytes - df->nadc)*ADC_SIZE)
        i += 2;

    if (!aligned(&(df->fbytes[i]), df->nadc)) {
      printf("Strange looking data in '%s'. "
                "Can't make any sense out of it.", df->fname);
    }
    df->fbi = i;
}


static int aligned(const unsigned char *event, unsigned int nadc)
{
    unsigned int i;
    const unsigned short *h;

    h = (unsigned short *)event;

    for (i = 0; i < nadc; i++) {
        if (adcnum(h[i]) != (i % 8))  return FALSE;
    }
    return TRUE;
}


int nactive_adc(unsigned short w, int *active, int nactive)
// Number of active ADC:s.  
{
    unsigned short i;
    int n, j;

    n = 0;
    j = 0;
    i = 1;
    for (j = 0; j < nactive; j++) {
        if (w & i) { 
            n++;
            active[j] = TRUE;
        } else
            active[j] = FALSE;
        i *= 2;
    }

    return n;
}


int nadc_new(DataFile *df)
// Returns the number of the highest ADC that is active in any event found in
// the beginning (i.e. df->fbytes) of the file.  NOTE: It is assumed that the
// ascii-header has been skipped already.
{
    unsigned int *dw;
    unsigned short hw, lw;
    int nadc = -1, i, j, n;
    int active[MAX_NADC];

//    DEBUG_PRINT("in\n");

    i = df->fbi; 
    while (i <= df->nfbytes - 4) {
        dw = (unsigned int *)&(df->fbytes[i]);
        hw = *dw >> 16;
        lw = *dw & 0xffff;
        i += 4;
        
        if (*dw == 0xffffffff || hw == 0x4000)  {
            // Sync or timer event
        } else {
            n = nactive_adc(lw, active, MAX_NADC);
            for (j = 0; j < MAX_NADC; j++)
                if (active[j] && j+1 > nadc) nadc = j+1;

            if (*dw & 0x10000000) {
                // Skip RTC-data, uses 6 bytes
                i += 6;
            }

            if (*dw & 0x80000000) {
                // Skip dummy word, 2 bytes
                i += 2;
            }

            // Skip ADC:s themselves
            i += n*ADC_SIZE;
        }
    }
    
//    DEBUG_PRINT("out\n");
    return nadc;
}

//JoMe, 2014.01.31: getest op een file, de volgende routine is inderdaad actief !!

int datafile_read_event(unsigned short event[MAX_NADC], DataFile *df, int active[MAX_NADC])
{
    unsigned int dw;
    unsigned short hw, lw, w, w3[3];
    int n;

    while (TRUE) {
//		printf("test");
        if (nextbytes(&dw, 4, df) != 4) return 0;
        hw = dw >> 16;
        lw = dw & 0xffff;

        if (dw == 0xffffffff) {
            // Sync event
        } else if (hw == 0x4000)  {
            df->ntimer++;
        } else {
            n = nactive_adc(lw, active, MAX_NADC);

            if (dw & 0x10000000) {
                // Read RTC-data.  Ignored.
                df->nrtc++;
                if (nextbytes(w3, 6, df) != 6) return 0;
            }

            if (dw & 0x80000000) {
                if (!(hw & 0x8000)) df->nerrors++;   
                // Read dummy word
                if (nextbytes(&w, 2, df) != 2) return 0;
            }

            if (nextbytes(event, ADC_SIZE*n, df) != (int)(ADC_SIZE*n))
                return 0;

            df->nevents++;
            break;
        }
    } 

    return 1;
}

void  datafile_close(DataFile *df)
{
    fprintf(stderr, "Read %i events from %s \n", df->nevents, df->fname);
    if (df->fmt == FMT_OLD)
        fprintf(stderr, "(%i errors)\n", df->nerrors);
    else if (df->fmt == FMT_NEW)
        fprintf(stderr, "(%i timer events)\n", df->ntimer);
        
    free (df->fname);
    fclose(df->fp);
    free (df);
}
//blabla
