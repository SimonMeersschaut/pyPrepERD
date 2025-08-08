#ifndef DATAFILE_H_
#define DATAFILE_H_

//#include <glib.h>
//#include "zio.h"

/* 
 * This module provides a abstraction layer for transparently reading files of
 * recorded events. If fname to 'datafile_open' is NULL, uncompressed data from
 * stdin is read.
 */

#define MAX_NADC  16     
#define ADC_SIZE sizeof(unsigned short)
#define NFBYTES 1048576  // 1 MB
#define TXTFILE "output.txt"
// #define TIMECONV 8191    TCL 15jan14
#define MAXEVENT 1000000
typedef struct {
//    ZIO_FILE *zf;
	FILE *fp;
    char *fname;
    int fmt;
    int nadc;                 // used only by old format
    unsigned char fbytes[NFBYTES];    // First NFBYTES bytes in the file
    int fbi;                  // fbytes-index
    int nfbytes;

    // The number of events, errors, timer events and rtc-events 
    // encountered so far
    int nevents;
    int nerrors;
    int ntimer;
    int nrtc;
} DataFile;

DataFile *datafile_open(const char *fname, int *nadc);
int datafile_read_event(unsigned short event[MAX_NADC], DataFile *df, int active[MAX_NADC]);
void  datafile_close(DataFile *df);

#endif // DATAFILE_H_
