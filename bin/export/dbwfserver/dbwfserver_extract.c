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
    //
    // Just print the help section and exit the code
    //
    printf("\n\n Usage: dbwfserver_extract [-h] [-b] [-c] [-p page] [-n max_traces] [-m max_points] [-f filter] [-s subset] database time endtime\n");
    printf("\t\t-h                  Print this help and exit.\n");
    printf("\t\t-c                  Calibrate traces.\n");
    printf("\t\t-b                  Export coverage bars only, no data.\n");
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

char *
stradd( char * s1, char * s2 )
{

    /* creates a new string by concatenating two strings s1 and s2 together.
    * Unlike strcat, does not alter the original string.  Returns a
    * freshly-allocated char* that must be freed by the caller. */
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
    int     calibrate=0, errflg=0, maxtr=0, last_page=0, bars=0, maxpoints=0;
    int     c=0, i=0, n=0, page=0, bin=1, bufd=0;
    long    result=0, first_trace=0, last_trace=0, nsamp=0, nrecords=0, nrecs=0;
    float   *data=NULL, period=0, *max=NULL, *min=NULL;
    float   inf=0, ninf=0;
    double  time=0, endtime=0, samprate=0, start=0, stop=0, total_points=0;
    char    old_sta[16]="", segtype[16]="", sta[16]="", chan[16]="", temp[600]="";
    char    *database=NULL, *dbname=NULL, *subset=NULL, *filter=NULL;
    Dbptr   tr, dbwf, dbsite;
    Tbl     *fields;
    Hook    *hook=0;

    //
    // Get Inf and -Inf
    //
    inf = an_infinity();
    ninf = -inf;
    max = &ninf;
    min = &inf;

    elog_init( argc, argv);
    elog_set( ELOG_DELIVER, 0 ,"stdout");
    //elog_tag( ELOG_TAG, "%P %a@lncdfDa" );


    //
    // Get all command-line options
    //
    while ((c = getopt (argc, argv, "bhdcf:s:m:n:p:")) != -1) {
        switch (c) {

        case 'b':
            bars = 1;
            break;

        case 'h':
            help() ;
            break;

        case 'c':
            calibrate = 1;
            break;

        case 'f':
            filter =  strdup( optarg );
            break;

        case 's':
            subset = strdup( optarg );
            break;

        case 'm':
            maxpoints = atoi( optarg );
            break;

        case 'n':
            maxtr = atoi( optarg );
            break;

        case 'p':
            page = atoi( optarg );
            break;

        default:
            errflg++;
            break;
        }
    }

    if ( errflg ) help();

    //
    // VERIFY FLAGS
    //
    if ( page && ! maxtr ) {
        printf ("{\"ERROR\":\"Need -n MAXTRACES if using -p PAGE flag!\"}\n" ) ;
        exit( 1 );
    }

    //
    // GET COMMAND-LINE ARGS
    //
    if ( argc-optind != 3 ) help();
    database = argv[optind++] ;
    start = atof( argv[optind++] );
    stop = atof( argv[optind++] );

    //
    // TEST DBS
    //
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
    // SUBSET SITECHAN TABLE
    //
    if ( subset != NULL ) 
        sprintf( temp, "%s && ondate <= %s && (offdate >= %s || offdate == -1)", subset,epoch2str(stop,"%Y%j"),epoch2str(start,"%Y%j") );
    else 
        sprintf( temp, "ondate <= %s && (offdate >= %s || offdate == -1)", epoch2str(stop,"%Y%j"),epoch2str(start,"%Y%j") );


    dbsite = dbsubset ( dbsite, temp, 0 ) ; 

    // TEST 
    //printf ("{\"TEST\":\" records after subset %s\"}\n", temp ) ;
    //exit(1);

    //
    // UNIQUE SORT SITECHAN TABLE
    //
    fields = strtbl("sta","chan",0) ;
    dbsite = dbsort ( dbsite, fields, dbSORT_UNIQUE,"" ) ; 
    dbquery ( dbsite, dbRECORD_COUNT, &nrecords ) ; 
    if (! nrecords) {
        printf ("{\"ERROR\":\"No records after subset %s\"}\n", temp ) ;
        exit( 1 );
    }

    // TEST 
    //printf ("{\"TEST\":\" %ld records after subset %s\"}\n", nrecords, temp ) ;
    //exit(1);

    //
    // SUBSET WFDISC TABLE
    //
    if ( subset != NULL ) 
        sprintf( temp, "%s && endtime > %f && time < %f", subset,start,stop );
    else
        sprintf( temp, "endtime > %f && time < %f", start,stop );
    dbwf = dbsubset(dbwf, temp, 0);
    dbquery ( dbwf, dbRECORD_COUNT, &nrecs ) ; 
    //printf("\n\twfdisc: %s \n", temp);
    //printf("\n\nwfdisc: %ld\n\n", nrecs);
    if (! nrecs) {
        printf ("{\"ERROR\":\"No records after subset %s\"}\n", temp ) ;
        exit( 1 );
    }

    // 
    // VERIFY NUMBER OF TRACES AND PAGES
    //
    first_trace = 0;
    last_trace = nrecords;

    if ( bars == 1 ) {
        // ONLY for coverage bars...
        page = 1;
        last_page = 1;
    }
    else {
        // ONLY for wf traces...
        // compare to flags
        if ( ! page  ) page = 1;
        if ( ! maxtr  ) maxtr = nrecords;

        // set last_page
        last_page =  nrecords / maxtr; 
        if ( ( nrecords % maxtr ) > 1 ) last_page++;

        // set first and last traces values
        if ( maxtr ) {

            first_trace = ( (page - 1) * maxtr );
            last_trace = first_trace + maxtr ;

            if ( first_trace > nrecords ) {
                printf ("{\"ERROR\":\"No more records. last_page:%i page:%i\"}\n", last_page, page ) ;
                exit( 1 );
            } 
        }

    }
    if ( last_trace > nrecords ) last_trace = nrecords;

    //
    // START BUILDING JSON OBJECT
    //
    printf ("{\"page\":%i,\"last_page\":%i,",page,last_page) ;
    printf ("\"time\":%0.0f,\"endtime\":%0.0f,",start*1000,stop*1000) ;

    if ( filter && bars == 0) 
        printf ( "\"filter\":\"%s\",",filter) ; 
    else 
        printf ( "\"filter\":\"false\",") ; 

    if ( calibrate && bars == 0) 
        printf ( "\"calib\":\"true\",") ; 
    else 
        printf ( "\"calib\":\"false\",") ; 



    for ( i = first_trace; i < last_trace; i++ )
    {

        dbsite.record = i;
        dbgetv( dbsite, NULL, "sta", &sta, "chan", &chan, 0 );

        //
        // JSON SYNTAX
        //
        if ( strcmp(old_sta,sta) != 0 ) {
            if ( strcmp(old_sta,"") != 0 ) {
                // IF THIS IS NOT THE FIRST CLOSE PREV BRACKET
                printf("},");
            }
            // TRACK LAST STATION
            sprintf( old_sta, "%s", sta );
            // NEW STATION AND NEW CHANNEL
            printf("\"%s\":{\"%s\":{", sta,chan);
        }
        else {
            // NEW CHANNEL FOR SAME STATION
            printf(",\"%s\":{", chan);
        }

        if ( bars == 1 ) {
            //
            // COVERAGE BARS
            //

            printf ( "\"format\":\"bins\"," ) ; 
            printf ( "\"type\":\"coverage\"," ) ; 
            printf ( "\"data\":[" ) ; 

            // To search from the beginning (including the 
            // first record) set the record number < 0
            dbwf.record = -1;

            sprintf( temp, "sta == '%s' && chan == '%s'", sta,chan );

            for ( ;; ) {

                result = dbfind(dbwf, temp, 0, &hook);


                //printf("\n\t%ld %s \n", result, temp);

                if (result >= 0) {

                    dbwf.record = result ;
                    dbgetv(dbwf,0,"time",&time,"endtime",&endtime,NULL) ; 

                    printf( ",[%0.0f,%0.0f]", time*1000 , endtime*1000 ) ; 

                } 
                else { break; }

            }

            printf ( "]" ) ; 

            // Clean memory
            free_hook(&hook);

            printf ( "}" ) ; 

        }
        else {

            // Try to catch any elog msgs from the trloads
            printf ( "\"ERROR\":\"" ) ; 

            // 
            // Load data into trace object
            //
            tr = dbinvalid() ;
            tr = trloadchan( dbwf, start, stop, sta, chan );

            dbquery ( tr, dbRECORD_COUNT, &nrecs ) ; 
            if (! nrecs) {
                printf ( "\"}" ) ; 
                continue;
            }

            // Calibrate trace object if needed
            if ( calibrate ) trapply_calib( tr );

            // filter trace object if needed
            if ( filter ) trfilter( tr, filter );

            tr.record = 0; 

            dbgetv(tr,0,"nsamp",&nsamp,"samprate",&samprate,"segtype",&segtype,NULL) ; 

            total_points = samprate * ( stop - start ); 

            // Try to catch any elog msgs from the trloads
            printf ( "\"," ) ; 

            period = 1/samprate;

            printf ( "\"type\":\"wf\"," ) ;
            printf ( "\"samprate\":%f,",samprate ) ;
            printf ( "\"segtype\":\"%s\",",segtype ) ;


            //
            // Calculate if we need to bin the data
            //
            if ( maxpoints && total_points > maxpoints ) {
                bin = total_points / maxpoints;
                if ( fmod( total_points , maxpoints ) > 1 ) bin++;
                printf ( "\"format\":\"bins\"," ) ; 
            } 
            else {
                printf ( "\"format\":\"lines\"," ) ; 
            }

            printf ( "\"data\":[null" ) ; 

            for ( tr.record = 0 ; tr.record < nrecs ; tr.record++ ) { 

                dbgetv(tr,0,"time",&time,"nsamp",&nsamp,"data",&data,NULL) ; 

                if ( ! nsamp ) continue; 

                for ( n=0 ; n<nsamp ; n++ ) { 

                    time += period;

                    //
                    // Bin data if we need to...
                    //
                    if ( bin > 1 ){

                        bufd++;
                        if ( data[n] < *min) min = &data[n];
                        if ( data[n] > *max) max = &data[n];

                    }

                    if ( bin > 1 && bufd < bin && n < nsamp-1 ) continue;

                    if ( bin > 1 ) {
                        // The time is of the last element in the bin
                        if ( isinf(*min) ) min = 0;
                        if ( isinf(*max) ) max = 0;
                        printf( ",[%0.0f,%0.1f,%0.1f]", time*1000 , *min, *max ) ; 
                    }
                    else {
                        if ( isinf(data[n]) ) data[n] = 0;
                        printf( ",[%0.0f,%0.1f]", time*1000 , data[n] ) ; 
                    }

                    max = &ninf;
                    min = &inf;
                    bufd = 0;
                }

                printf( ",null" );

            }

            printf ( "]}" ) ; 

        }

    }
    printf ( "}}\n" ) ; 

    return 0;
}
