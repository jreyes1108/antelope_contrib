#include <stdlib.h>
#include "db.h"
#include "stock.h"
#include "db2sql.h"
#include "dbmon.h"

int
main( int argc, char **argv )
{
	char	*dbname = "/opt/antelope/data/db/demo/demo";
	Dbptr	db;
	Tbl	*sqlcommands = (Tbl *) NULL;
	char	*sync;
	int	flags = 0;
	
	Program_Name = argv[0];

	dbopen( dbname, "r", &db );

	db = dblookup( db, "", "origin", "", "" );

	db.record = 0;

	db2sqlinsert( db, &sqlcommands, dbmon_compute_row_sync, flags );

	sync = dbmon_compute_row_sync( db );

	db2sqldelete( db, sync, &sqlcommands, flags );		

	free( sync );

	debugtbl( stdout, "Conversion results:\n", sqlcommands );

	freetbl( sqlcommands, free );

	return 0;
}
