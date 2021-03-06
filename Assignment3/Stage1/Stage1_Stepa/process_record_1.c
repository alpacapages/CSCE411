#include <stdio.h>
#include <stdlib.h>
#include <sys/times.h>
#include <string.h>

#include "record.h"


int main(int argc, char **argv)
{
    int i;
	int count = 0;
	char *loc;
    
    char filename[1024];
    FILE *fp = NULL;
    
    struct timeval time_start, time_end;
    
    /* start time */
    gettimeofday(&time_start, NULL);
    
    for (i = 0; i <= 1999; i++) {
        /* open the corresponding file */  
        sprintf(filename, "record_%06d.dat", i);
    
        fp = fopen(filename,"rb");
    
        if (!fp) {
            fprintf(stderr, "Cannot open %s\n", filename);
            continue;
        }
        
        /* read the record from the file */
        record_t *rp = read_record(fp);
    
        /* =========== start of data processing code ================ */
		loc = strtok(rp->location, ",");
		loc = strtok(NULL, ",");
		if(loc == NULL) {
			continue;
		}
		if(strcmp("Nebraska", loc) == 0) {
			count = count + 1;
		}
        
        /* =========== end of data processing code ================ */    
    
        /* free memory */
        free_record(rp);
    
        /* close the file */
        fclose(fp);
    }    
        
    
    /* end time */
    gettimeofday(&time_end, NULL);
    
    float totaltime = (time_end.tv_sec - time_start.tv_sec)
                    + (time_end.tv_usec - time_start.tv_usec) / 1000000.0f;
                    
         
    printf("\n\nTotal number users from Nebraska: %d users", count);    
    printf("\n\nProcess time %f seconds\n", totaltime);
    
    return 0;
}
