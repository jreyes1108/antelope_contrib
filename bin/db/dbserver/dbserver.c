#include <stdio.h>
#include "db.h"
#include "stock.h"

/* This code is taken directly from the dbprocess(3) manpage's
   'try.c' example program.
*/

int main(int argc, char **argv) {

    extern char *optarg;
    extern int optind;
    int c, errflg = 0 ;
    Dbptr db;
    char *database ;
    int verbose = 0 ;
    Pf *pf = 0 ;
    Tbl *input, *list ;

    Program_Name = argv[0];

    if ( argc != 2 )
	die ( 0, "Usage: %s database\n", Program_Name ) ;

    database = argv[1];
    if ( dbopen(database, "r", &db ) != 0)
	die (0, "Couldn't open database %s\n", database ) ;

    if (pfin(stdin, &pf) != 0)
	die(0, "Can't read parameter file\n");

    input = pfget_tbl (pf, "input" ) ;
    db = dbprocess ( db, input, 0 ) ;
    list = pfget_tbl ( pf, "fields" ) ;
    dbselect (db, list, stdout ) ;

    /* we'll want the option of returning either 'dbselect'-style output,
       or db2xml output, or (now this is fancy), a Ptolemy expression that
       will evaluate to an array of RecordTokens. */

    return 0;
}