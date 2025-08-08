//#include <glib.h>
#include <stdlib.h>
#include <stdio.h>
#include "datafile.h"

void printline(int printarray[MAX_NADC_LENGTH],int nadc_length,FILE *output_file);

int main(int argc, char **argv)
{
    DataFile *datafile;
    unsigned short *event;
    int i, j, nadc_length;
    int active[MAX_NADC_LENGTH];
    int printarray[MAX_NADC_LENGTH];
    FILE *output_file;
	// g_set_prgname(argv[0]);

    nadc_length = -1;
    datafile = datafile_open((argc >= 2)? argv[1]: NULL, &nadc_length);
    output_file=fopen(TXTFILE,"w");
    if(output_file==NULL)
    {
		printf("unable to create output file");
    } 

    event = malloc(MAX_NADC_LENGTH*ADC_SIZE);

    while (datafile_read_event(event, datafile, active)) {
        j = 0;
        for (i = 0; i < nadc_length; i++) {   // i fysieke ADC, j registered ADC-event in binary .lst file
    		if (active[i])  {

				printarray[i]=event[j];
           		j++;
			} 
			else{
		   		printarray[i]=0;
	       	}
        }
		
		printline(printarray,nadc_length,output_file);

    }
    datafile_close(datafile);
    fclose(output_file);
    return 0;
}
void printline(int printarray[MAX_NADC_LENGTH], int nadc_length, FILE *output_file)
// print `printarray` with length `nadc_length`, delimiter `space` to `outputfile`.
{
	int i;
	if(printarray[nadc_length-1]!=0)
	{
		for(i=0;i<nadc_length;i++)
		{
			fprintf(output_file,"%d ",printarray[i]);
		}
		fprintf(output_file,"\n",nadc_length);
	}
}
