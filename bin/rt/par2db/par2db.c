#include "par2db.h"
#include "header.h"

int GPS_COOR = 0;
FILE *fplcmd;

int Verbose = 0;
int DINTV = 1;
int DCINT = 5;
int Log = 0;
int DCFlag = 1;

char *Pfile = "pkt.pf";

extern Source *new_source();
extern Db_buffer *new_buf();

int main (argc, argv)
int             argc;
char          **argv;
{

    extern char    *optarg;
    extern int      optind;
    double          pkttime;
    double          after = 0.0;
    int             err=0, c;
    int             rdorb;
    int             npkt = 30,
		    nselect,
                    pktid;
    char	   *after_str=0 ;
    char           *orbname = 0;
    char           *match = ".*[HS][SP]";          
    char           *database;
    char           *packet=0;
    char            srcname[ORBSRCNAME_SIZE];
    char   	   acomp[64];
    char           *s, lcmdfile[64];
    Dbptr           db;
    Save_params     par;
    int             dump=0, nbytes, bufsize = 0;
    Arr            *Parms ;
    Arr            *sources ;
    Source	   *asource;
    int 	   i, apar;
    PktChannel 	   *achan ;
    Db_buffer 	   *buffer ;
    static Packet  *Pkt=0 ;
    
    
    Program_Name = argv[0];
    elog_init (argc, argv);
    elog_notify ( 0, "%s Version Version 1.6 10/28/96\n", Program_Name ) ; 

    par.segsiz = 86400.0;
    par.wfname = 0;
    strcpy (par.datatype, "s4");

    while ((c = getopt (argc, argv, "d:gm:i:p:s:vx")) != -1)
	switch (c) {

	case 'c':
	    DINTV = 5;
	    break;

	case 'x':
	    dump = 1;
	    break;

	case 'g':
	    GPS_COOR = 1;
	    break;

	case 'O':
	    DCFlag = 0;
	    break;

	case 'm':
	    match = optarg;
	    break;

	case 'p':
	    Pfile = strdup(optarg);
	    break;

	case 'd':
	    strncpy (par.datatype, optarg, 3);
	    break;

	case 'i':
	    DINTV = atoi(optarg);
	    DCINT = ( DINTV/5 )*5;
	    DINTV = DCINT;
	    break;

	case 's':
	    npkt = atoi(optarg);
	    break;

	case 'v':
	    Log=1;
	    break;

	case '?':
	    err++;
	}

    if (err || argc - optind < 2 || argc - optind > 4)
	usage ();

    orbname = argv[optind++];
    if ((rdorb = orbopen (orbname, "r")) < 0)
	die (0, "Can't open ring buffer '%s'\n", orbname);

    database = argv[optind++];
    if (dbopen_database (database, "r+", &db) < 0)
	die (0, "Can't open output database %s\n", database);
    if (db.table < 0) {
	db = dblookup (db, 0, "wfdisc", 0, 0);
	if (db.table < 0)
	    die (0, "Can't open output table '%s'\n", database);
    }
    par.db = db ;
    par.datacode = trdatacode (par.datatype);

    sprintf( lcmdfile, "%s.LCMD\0", database);
    if( ( fplcmd = fopen( lcmdfile, "a+")) == NULL )
       die( 1, "can't open '%s' for LAST COMMAND rerords.\n", lcmdfile);
    
    if (match) {
	if ((nselect = orbselect (rdorb, match)) < 0)
	    die (1, "orbselect '%s' failed\n", match);
    }

    Pkt = newpkt();
    Parms = newarr (0);
    sources = newarr (0);

    if (argc - optind >= 1) {
	after_str = argv[optind++] ; 
	if (!strcmp (after_str, "now") == 0) {
	    after = str2epoch (after_str);
	} else {
	    if (orbget (rdorb, ORBCURRENT,
		    &pktid, srcname, &after, &packet, &nbytes, &bufsize)) 
		die(0,"orbget to get current server time fails\n") ; 
	}
	if ((pktid = orbafter (rdorb, after-0.001)) < 0) 
	    die (1, "orbafter to %s failed\n", strtime (after));
	else
	    printf ("starting pktid is #%d\n", pktid);

    } else {
	after = get_last_dbtimes (db);
	if ((pktid = orbafter (rdorb, after)) < 0) {
	    die (1, "orbafter to %s failed\n", strtime (after));
	} else
	    printf ("starting pktid is #%d\n", pktid);
    }

    err = 0;
    while(1) {

	if (orbreap (rdorb, &pktid, srcname, &pkttime, &packet, &nbytes, &bufsize)) {
	    err++; 
            complain( 0, "orbreap failed.\n" );
            if( err > 900 )  {
                   orbclose( rdorb );
		   if( (rdorb = orbopen( orbname, "r")) < 0)
		       die( 0, "Can't open ORB\n");
		   if( match )
		       if ((nselect = orbselect ( rdorb, match)) < 1 )
		           die (1, "orbselect '%s' failed\n", match); 
		   if (orbseek (rdorb, ORBCURRENT ) < 0 ) 
		       die(0,"orbseek to ORBCURRENT failed .\n") ; 
		    
    	    }
	} else  {
	     err = 0;
	
             if( strncmp( srcname, "/db", 3) == 0 ||
	         strncmp( srcname, "/pf", 3) == 0 ||
	         strncmp( srcname, "/dcdas", 6) == 0 )  
	         continue;

	     if ((asource = (Source *) getarr (sources, srcname)) == 0) {
	         asource = new_source (npkt);
	         setarr (sources, srcname, asource);
	     }

             switch (orbsort (asource->apipe, &pktid, &pkttime, srcname, 
                          &packet, &nbytes, &bufsize)) {
     
	         case 0:
		     bufsize = 0;
		     break;
	         case 2:
	         case 3:
		     complain ( 0, "orbsort error at %lf for %s\n", 
		         pkttime, srcname) ; 
		     break ;
     
	         default:
     
                     if( pkttime - asource->last  >= DINTV )  {
	                   asource->last = pkttime;
	                   setarr (sources, srcname, asource);
                     }  else continue;
     
                     if( dump)  {
		         hexdump( stdout, packet, nbytes );
		         fflush(stdout);
		     } 
	             if( Log)  {
	                  fprintf( stderr, "%s %lf\n", srcname, pkttime );
		          fflush(stderr);
	             }
	        
		     switch ( unstuffpar (packet, pkttime, &Pkt, srcname )) {
	                 case 1:
                            
                            for (apar = 0; apar < Pkt->nchannels; apar++) {
	                       achan = (PktChannel *) gettbl (Pkt->chan, apar);
	                       sprintf( &acomp[0], "%s_%s_%s\0", 
			                achan->net, achan->sta, achan->chan);
	                       if( Log)  {
			          fprintf( stderr, "%s %lf\n", acomp, pkttime );
			          fflush(stderr);
			       }
			       if( (buffer = (Db_buffer *) getarr( Parms, acomp )) != 0 )
	                            record (achan, buffer) ;
	                       else {
	                            buffer = new_buf( achan, &par);
	                            setarr( Parms, acomp, buffer );
	                       }
	                     }
	                     break;
     
	                  default:
	                     break;
                      }
                      break;
	      }
         } 
    }
}


