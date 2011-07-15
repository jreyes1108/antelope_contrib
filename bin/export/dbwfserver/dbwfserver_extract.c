#include <stock.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
//#include <stdlib.h>
//#include <unistd.h>

#include "tr.h"


static void
help ()
{
    printf("\n\n Usage: dbwfserver_extract [-h] [-d] [-c] [-p page] [-n max_traces] [-m max_points] [-f filter] [-s subset] database time endtime\n");
    printf("\t\t(for debugging)\n");
    printf("\t\t-h                  Print this help.\n");
    printf("\t\t-d                  Display traces in a dbpick window at the end.\n");
    printf("\t\t(for data extraction)\n");
    printf("\t\t-c                  Calibrate traces.\n");
    printf("\t\t-p  'page'          If we have extra traces then show this page.\n");
    printf("\t\t-n  'traces'        Do not export more than this number of traces.\n");
    printf("\t\t-b  'bin_size'      Use this value to bin the data. No binning unless 'max_points' is in use and reached.\n");
    printf("\t\t-m  'max_points'    Hard limit on total return points. Try binning and return less than max_points.\n");
    printf("\t\t-f  'filter'        Use this string to filter the traces. ie 'BW 0.1 4 5.0 4'\n");
    printf("\t\t-s  'regex'         Do a subset on the database using this regex.\n");
    printf("\t\tdatabase            Full path to a database.\n");
    printf("\t\ttime                Start time for extraction.\n");
    printf("\t\tendtime             End time for extraction.\n");
    printf("\n");
    printf("\tANF-UCSD dbwfserver data extraction tool\n");
    printf("\tNO BRTT support!\n");
    printf("\treyes@ucsd.edu\n");
    exit (1);
}


/* creates a new string by concatenating two strings s1 and s2 together.
 * Unlike strcat, does not alter the original string.  Returns a
 * freshly-allocated char* that must be freed by the caller. */
char *
stradd( char * s1, char * s2 )
{
    char * ns;
    int len;

    if ( !s1 || !s2 ) return NULL;

    len = strlen( s1 ) + strlen( s2 ) + 1;
    ns = (char*) malloc ( len * sizeof(char) );
    sprintf( ns, "%s%s", s1, s2 );

    return strdup(ns);
}


int
main (int argc, char **argv)
{
    int     c, i, n, display, page, bin, bufd, first;
    int     calibrate, errflg, maxtr=0, last_page, maxpoints=0;
    long    first_trace=0, last_trace=0;
    char    *database=NULL, *dbname=NULL, *subset=NULL, *filter=NULL;
    char    old_sta[16]="";
    char    sta[16]="", chan[16]="";
    Dbptr   tr, db, dbwf, dbsite;
    long    nrecords=0, nrecs=0;
    double  start, stop;
    Tbl     *fields;
    float  *data, period, *max, *min;
    long   nsamp; 
    double time, endtime, samprate;
    char   segtype[8]="";

    while ((c = getopt (argc, argv, "hdcn:f:s:m:n:p:")) != -1) {
        switch (c) {

        case 'n':
            maxtr = atoi( optarg );
            break ; 

        case 'd':
            display = 1 ; 
            break ; 

        case 'f':
            filter =  strdup( optarg );
            break ;

        case 'm':
            maxpoints = atoi( optarg );
            break ;

        case 'p':
            page = atoi( optarg );
            break ;

        case 's':
            subset = strdup( optarg );
            break ;

        case 'c':
            calibrate = 1;
            break;

        case 'h':
            help() ;

        default:
            errflg++;
            break ;
        }
    }

    if (errflg || argc-optind != 3)
    help();

    //
    // Verify flags
    //
    if ( page && ! maxtr ) {
        printf ("{\"ERROR\":\"Need -n MAXTRACES if using -p PAGE flag!\"}\n" ) ;
        exit( 1 );
    }

    //
    // Get command line args
    //
    database = argv[optind++] ;
    start = atof( argv[optind++] );
    stop = atof( argv[optind++] );

    //
    // Load database
    //
    if ( dbopen(database, "r", &db) ) {
        printf ("{\"ERROR\":\"Can't open %s\"}\n", database ) ;
        exit( 1 );
    }


    // SITE
    //dbname = stradd( database, ".site" );
    //if ( dbopen_table(dbname, "r", &dbsite) == dbINVALID ) { 
    //    printf ("{\"ERROR\":\"Can't open %s\"}\n", dbname ) ;
    //    exit( 1 );
    //}
    //dbquery ( dbsite, dbRECORD_COUNT, &nrecords ) ; 
    //if (! nrecords) {
    //    printf ("{\"ERROR\":\"EMPTY %s\"}\n", dbname ) ;
    //    exit( 1 );
    //}
    //free(dbname);


    // SITECHAN
    dbname = stradd( database, ".sitechan" );
    if ( dbopen_table(dbname, "r", &dbsite) == dbINVALID ) { 
        printf ("{\"ERROR\":\"Can't open %s\"}\n", dbname ) ;
        exit( 1 );
    }
    dbquery ( dbsite, dbRECORD_COUNT, &nrecords ) ; 
    if (! nrecords) {
        printf ("{\"ERROR\":\"EMPTY %s\"}\n", dbname ) ;
        exit( 1 );
    }
    free(dbname);


    // WFDISC
    dbname = stradd( database, ".wfdisc" );
    if ( dbopen_table(dbname, "r", &dbwf) == dbINVALID ) { 
        printf ("{\"ERROR\":\"Can't open %s\"}\n", dbname ) ;
        exit( 1 );
    }
    dbquery ( dbwf, dbRECORD_COUNT, &nrecords ) ; 
    if (! nrecords) {
        printf ("{\"ERROR\":\"EMPTY %s\"}\n", dbname ) ;
        exit( 1 );
    }
    free(dbname);



    //
    // Join site and sitechan tables
    //
    //dbsite = dbjoin (dbsite, dbsitechan, 0, 0, 0, 0, 0);
    //dbquery ( dbsite, dbRECORD_COUNT, &nrecords ) ; 
    //if (! nrecords) {
    //    printf ("{\"ERROR\":\"No records after join of site and sitechan for %s\"}\n", database ) ;
    //    exit( 1 );
    //}

    //
    // Subset database
    //
    if ( subset ) { 
        dbsite = dbsubset ( dbsite, subset, 0 ) ; 
    }

    // Unique sort on sta and chans
    fields = strtbl("sta","chan",0) ;
    dbsite = dbsort ( dbsite, fields, dbSORT_UNIQUE,"" ) ; 

    dbquery ( dbsite, dbRECORD_COUNT, &nrecords ) ; 

    if (! nrecords) {
        printf ("{\"ERROR\":\"No records after subset %s\"}\n", subset ) ;
        exit( 1 );
    }

    first_trace = 0;
    last_trace = nrecords;
    if ( ! page  ) page = 1;
    if ( ! maxtr  ) maxtr = nrecords;

    last_page =  nrecords / maxtr; 
    if ( ( nrecords % maxtr ) > 1 ) last_page++;

    if ( maxtr ) {

        first_trace = ( (page - 1) * maxtr );
        last_trace = first_trace + maxtr ;

        if ( first_trace > nrecords ) {
            //printf ("{\"ERROR\":\"No more records. recs:%ld maxtr:%i page:%i\"}\n", nrecords, maxtr, page ) ;
            printf ("{\"ERROR\":\"No more records. last_page:%i page:%i\"}\n", last_page, page ) ;
            exit( 1 );
        }
        
        if ( last_trace > nrecords ) last_trace = nrecords;
    }

    //
    // Apply the same subset to the wfdisc table
    //
    if ( subset )
        dbwf = dbsubset ( dbwf, subset, 0 ) ; 

    //
    // We can save space if we say this only once...
    //
    printf ("{\"page\":%i,\"last_page\":%i,",page,last_page) ;
    printf ("\"time\":%f,\"endtime\":%f,",start*1000,stop*1000) ;
    if ( filter ) 
        printf ( "\"filter\":\"%s\",",filter) ; 
    else 
        printf ( "\"filter\":\"false\",") ; 

    if ( calibrate ) 
        printf ( "\"calib\":\"true\",") ; 
    else 
        printf ( "\"calib\":\"false\",") ; 



    for ( i = first_trace; i < last_trace; i++ )
    {
        dbsite.record = i;
        dbgetv( dbsite, NULL, "sta", &sta, "chan", &chan, 0 );

        if ( strcmp(old_sta,sta) != 0 ) {
            if ( strcmp(old_sta,"") != 0 ) {
                printf("},");
            }
            sprintf( old_sta, "%s", sta );
            printf("\"%s\":{\"%s\":{", sta,chan);
        }
        else {
            printf(",\"%s\":{", chan);
        }

        // 
        // Load data into trace object
        //
        tr = dbinvalid() ;
        tr = trloadchan ( dbwf, start, stop, sta, chan );

        // eliminate marked gaps from waveforms; these
        //   are gaps where no data was recorded, but special missing values
        //   were inserted instead of ending the wfdisc record 
        if ( trsplit(tr, 0, 0) ) { 
            printf ( "\"ERROR\":\"trsplit failed\"}" ) ; 
            continue;
        }

        // splice together any adjacent data segments which can be
        if ( trsplice(tr, 0, 0, 0) ) { 
            printf ( "\"ERROR\":\"trsplice failed\"}" ) ; 
            continue;
        }

        dbquery ( tr, dbRECORD_COUNT, &nrecs ) ; 
        if (! nrecs) {
            printf ( "\"ERROR\":\"No Data!\"}" ) ; 
            continue;
        }

        // Calibrate trace object if needed
        if ( calibrate ) trapply_calib( tr );

        // filter trace object if needed
        if ( filter ) trfilter( tr, filter );

        for ( tr.record = 0 ; tr.record < nrecs ; tr.record++ ) { 

            // We are missing previous sections of the WF for now... WIP
            dbgetv(tr,0,"time",&time,"endtime",&endtime,"nsamp",&nsamp,"samprate",&samprate,"segtype",&segtype,"data",&data,NULL) ; 

        }

        period = 1/samprate;
        first = 1;
        max = NULL;
        min = NULL;
        bufd = 0;
        bin = 1;

        //
        // Calculate if we need to bin the data
        //
        if ( maxpoints && nsamp > maxpoints ) {
            bin = nsamp / maxpoints;
            if ( ( nsamp % maxpoints ) > 1 ) bin++;
        }

        if ( bin == 1 )
            printf ( "\"format\":\"lines\"," ) ; 
        else
            printf ( "\"format\":\"bins\"," ) ; 

        printf ( "\"type\":\"wf\"," ) ; 
        printf ( "\"time\":%f,",time*1000 ) ; 
        printf ( "\"endtime\":%f,",endtime*1000 ) ; 
        printf ( "\"samprate\":%f,",samprate ) ; 
        printf ( "\"segtype\":\"%s\",",segtype ) ; 
        printf ( "\"data\":[" ) ; 

        for ( n=0 ; n<nsamp ; n++ ) { 
            //
            // Bin data if we need to...
            //
            if ( bin > 1 ){
                bufd++;

                if ( min == NULL || data[n] < *min) min = &data[n];
                if ( max == NULL || data[n] > *max) max = &data[n];

            }

            if ( bin > 1 && bufd < bin ) {
                time = time + period;
                continue;
            }

            if ( first == 0  ) printf( "," );

            if ( bin > 1 )
                // The time is of the last element in the bin
                printf( "[%f,%f,%f]", time*1000 , *min, *max ) ; 
            else 
                printf( "[%f,%f]", time*1000 , data[n] ) ; 

            time = time + period;
            max = NULL;
            min = NULL;
            bufd = 0;
            first = 0;

        }

        printf ( "]}" ) ; 

    }
    printf ( "}}\n" ) ; 

    //trfree( tr );

    return 0;
}
