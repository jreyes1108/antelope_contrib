#!/usr/bin/env python

# {{{ HEADERS
#
# @author:   Rob Newman <rlnewman@ucsd.edu>, (+1) 858 822 1333
# @expanded: Juan Reyes <reyes@ucsd.edu>, (+1) 858 822 2989
# @created:  2010-08-11
# @modified: 2010-08-17
#
# @usage:
#   Create:
#      element = dbcentral(path,nickname)               # Default mode
#      element = dbcentral(path,nickname,False)         # Don't output times for tables, just a list
#      element = dbcentral(path,nickname,True,True)     # Enable Debug mode. Verbose output
#   Access:
#      print element                                    # Nice print of values
#      element.type                                     # return string value for mode [dbcentral,masquerade]
#      element.path                                     # return string value for path
#      element.nickname                                 # return string value for nickname
#      element.include_times                            # return string value for boolean of include_times 'True,False'
#      element.list()                                   # return list of databases opend by dbcentral
#      element.load()                                   # open pointers to databases and store them in memory
#      element.list_pointers()                          # return list of databases pointers opend to use in a loop
#      element(epoch)                                   # return full path for database matching the epoch time
#      element.pointer(epoch)                           # return db pointer for database matching the epoch time
#                                                       # NOTE: to return pointers you need to use load() first...
#
#   Note:
#       dbcentral will load the database and test for the existence of the 'clusters' table first. If missing 
#       the class will assume that the intention of the user is to load a regular database and use the class
#       functionality to store the pointer. This will trigger the self.type value to be "masquerade". Regular
#       dbcentral tables will load normally and set self.type to "dbcentral". 

# }}} HEADERS

import sys
import os

# Load datascope functions
sys.path.append( os.environ['ANTELOPE'] + '/data/python/antelope/' )
import datascope as datascope
import stock as stock


class dbcentral:

    def __init__(self, path, nickname=None, include_times=True, debug=False):
        # {{{ __init__
        self.type = False
        self.path = os.path.abspath(path)
        self.nickname = nickname
        self.include_times = include_times
        self.debug = debug
        self.loaded = False

        # Create dictionary to hold all the values
        self.local_namelist = {}
        self.pointers = {}

        # Load the values from the db.
        self._get_list()


        # }}} __init__

    def __str__(self):
#{{{
        """
        end-user/application display of content using print() or log.msg()
        """
        text = '\nDBCENTRAL (path:%s, nickname:%s):' % (self.path,self.nickname)

        if self.include_times:
            for value in self.local_namelist.keys():
                text += "\n\t%s: (%s)" % (value,self.local_namelist[value])

        else:
            for value in self.local_namelist.keys():
                text += "\n\t%s" % value

        return text
#}}}

    def __call__(self, time):
#{{{
        """
        method to intercepts data requests.
        """
        if not time:
            time = now()

        for element in self.local_namelist:
            if self.local_namelist[element][0] < time and time < self.local_namelist[element][1]:
                return element

        print "\n\nClass dbcentral(): No match for (%s)\n\n" % time
        return False
#}}}

    def __dell__(self):
        #{{{ cleanup vars
        """
        method to intercepts data requests.
        """
        for element in self.pointers:
            datascope.db.close( element )
            
        self.local_namelist = {}
        self.pointers = {}
        self.loaded = False

        #}}}

    def list_pointers(self):
        #{{{ return pointer for db related to a time
        """
        method to return ALL pointers to the dbs
        """
        if not self.loaded:
            print "\n\nClass dbcentral(): Need to call load() method first!!!!\n\n" % time
            return []

        temp = []
        for element in self.pointers:
                temp = temp + [self.pointers[element]]

        return temp
        #}}}

    def pointer(self, time):
        #{{{ return pointer for db related to a time
        """
        method to return pointers to the dbs
        """
        if not self.loaded:
            print "\n\nClass dbcentral(): Need to call load() method first!!!!\n\n" % time
            return []

        for element in self.local_namelist:
            if self.local_namelist[element][0] < time and time < self.local_namelist[element][1]:
                return self.pointers[element]

        print "\n\nClass dbcentral(): No match for (%s)\n\n" % time
        return False
        #}}}

    def load(self):
        #{{{ method load() will opend all pointers to the dbs
        """
        method for opennig all the dbs and store the pointers
        """
        self.loaded = True

        for element in self.local_namelist:
            try:

                self.pointers[element] = datascope.dbopen( element )

            except Exception,e:

                self.pointers[element] = False
                print "\n\nClass dbcentral(): Cannot open database %s (%s)\n\n" % (element,e)

        #}}}

    def _problem(self, log):
        #{{{ Nice print of errors
        """
        method to print problems and raise exceptions
        """
        print "\n\nCLASS dbcentral:"
        print "\tERROR:\n\t\t%s" % log
        print "\tINFO:"
        print "\t\tpath:%s" % self.path
        print "\t\tnickname:%s" % self.nickname
        print "\t\tinclude_times:%s\n" % self.include_times

        #}}}

    def _get_list(self):
        # {{{ private function to load data

        try:

            db = datascope.dbopen(self.path,'r')

        except Exception,e:

            self._problem("Cannot open cluster database. (%s)" % e)
            return False


        try:

            db.lookup('','clusters','','')

        except Exception,e:

            self._problem("Cannot look up 'clusters' table in database. (%s)" % e)
            return False


        try:

            db.query(datascope.dbTABLE_PRESENT)

        except:

            self._problem("Not a dbcentral database. Openning single database.")
            self.type = 'masquerade'
            self.local_namelist[self.path] = (-10000000000.0,10000000000.0)
            return 

        else:

            self.type = 'dbcentral'
            
            if self.nickname is None:
                self._problem("Need nickname for dbcentral clustername regex.")
                return Flase


        try:

            db.lookup('','clusters','','dbNULL')
            null_time,null_endtime = db.getv('time','endtime')

        except Exception,e:

            self._problem("Cannot look up null values in clusters table. (%s)" % e)
            return False


        expr = "clustername =='%s'" % self.nickname


        try:

            db.subset(expr)

        except Exception,e:

            self._problem("Cannot subset on clustername. %s" % e)
            return False


        db.sort(['time'])
        nclusters = db.nrecs()

        if nclusters < 1:

            self._problem("No matches for nickname.")

        if self.debug:
            print "*debug*: Records=%s" % nclusters

        for i in range(nclusters):

            db[3]=i

            dbname_template = db.extfile()

            if self.debug:
                print "*debug*: dbname_template=%s" % dbname_template

            try:

                self.volumes,self.net,time,endtime = db.getv("volumes","net","time","endtime")

            except Exception,e:

                self._problem("Problems with db.getv('volumes','net','time','endtime'). (%s)\n" % e)
                return False

            if self.debug:
                print "*debug*: volumes=%s" % self.volumes
                print "*debug*: net=%s" % self.net
                print "*debug*: time=%s" % time
                print "*debug*: endtime=%s" % endtime

            if endtime == null_endtime:
                #{{{ endtime

                # This will be problematic with realtime systems
                endtime = stock.now()
                if self.debug:
                    print "*debug*: endtime=%s" % endtime

                # }}} endtime

            if self.volumes == 'single':
                # {{{ single

                if self.debug:
                    print "*debug*: Single... dbname=%s" % dbname_template

                self.local_namelist[dbname_template] = (time,endtime)

                # }}} single

            elif self.volumes == 'year':
                # {{{ year

                start_year = int(stock.epoch2str(time,"%Y"))
                end_year   = int(stock.epoch2str(endtime,"%Y"))

                for y in range(start_year,end_year+1):

                    voltime    = stock.str2epoch("1/1/%s 00:00:00" % y)
                    volendtime = stock.str2epoch("12/31/%s 23:59:59" % y)
                    dbname     = stock.epoch2str(voltime,dbname_template)

                    if self.debug:
                        print "*debug*: TEST... year=%s dbname=%s" % (y,dbname)

                    if os.path.isfile(dbname):

                        self.local_namelist[dbname] = (voltime,volendtime);

                # }}} year

            elif self.volumes == 'month':
                # {{{ month

                start_month = int(stock.epoch2str(time,"%L"))
                start_year  = int(stock.epoch2str(time,"%Y"))
                end_month   = int(stock.epoch2str(endtime,"%L"))
                end_year    = int(stock.epoch2str(endtime,"%Y"))

                vol_month   = start_month
                vol_year    = start_year

                # Iterator
                i = 0

                while vol_year < end_year or ( vol_year == end_year and vol_month <= end_month ):

                    voltime           = stock.str2epoch("%d/1/%d" % (vol_month,vol_year) )

                    if vol_month < 12:
                        temp_vol_endmonth = vol_month + 1
                        temp_vol_endyear  = vol_year
                    else:
                        temp_vol_endmonth = 1
                        temp_vol_endyear  = vol_year + 1

                    volendtime = stock.str2epoch("%d/1/%d" % (temp_vol_endmonth,temp_vol_endyear) ) - 1
                    dbname     = stock.epoch2str(int(voltime), dbname_template)

                    if self.debug:
                        print "*debug*: TEST... time=%s dbname=%s" % (voltime,dbname)

                    if os.path.isfile(dbname):

                        self.local_namelist[dbname] = (voltime,volendtime)

                    if vol_month < 12:
                        vol_month = vol_month + 1
                    else:
                        vol_year = vol_year + 1
                        vol_month = 1

                    i = i + 1

                # }}} month

            elif self.volumes == 'day':
                # {{{ day

                start_day = int(stock.yearday(time))
                end_day   = int(stock.yearday(endtime))

                vol_day   = start_day

                # Iterator
                i = 0

                while vol_day <= end_day:

                    voltime    = stock.epoch(vol_day)
                    volendtime = voltime + 86399 # one second less than a full day
                    dbname     = stock.epoch2str(voltime, dbname_template)
                    
                    if self.debug:
                        print "*debug*: TEST... time=%s dbname=%s" % (voltime,dbname)

                    if os.path.isfile(dbname):

                        self.local_namelist[dbname] = (voltime,volendtime)

                    vol_day = stock.yearday((stock.epoch(vol_day)+86400))

                    i += 1

                # }}} day

            else:

                return "Volumes type '%s' in cluster database not understood" % volumes

        if self.debug:
            print "*debug*: DBS=%s" % self.local_namelist.keys()


        # }}} 

    def list(self):
        #{{{ return values to the user

        if self.include_times:
            return self.local_namelist

        else:
            return self.local_namelist.keys()

        #}}}

# 
# For debugging...
#
if __name__ == '__main__':
#{{{ Tests for class dbcentral
    #
    # This will run if the file is called directly.
    # If the file is imported then the test is ignored.
    #

    time =  1081924400.00000

    print 'Constructor call:'
    #
    # There is no dbcentral database on contrib or demo so you nee to set this to yours
    #
    dbcntl = dbcentral('/Users/reyes/dbcentral/dbcentral','anza',True)
    #dbcntl = dbcentral('/opt/antelope/data/db/demo/demo')

    print 'Function load():'
    dbcntl.load()

    print 'Access class properties:'
    print '\tdbcntl = dbcentral("%s","%s","%s")' % (dbcntl.path,dbcntl.nickname,dbcntl.include_times)
    print '\tdbcntl.type => %s\n' % dbcntl.type
    print 'Print object:'
    print '\t%s\n' % dbcntl
    print 'List function:'
    print '\tlist() => %s\n' % dbcntl.list()
    print 'List_pointers function:'
    print '\tlist_pointers() => %s\n' % dbcntl.list_pointers()

    print 'Regular function call (using time):'
    print '\tdbcntl(%s) => %s\n' % (time,dbcntl(time))
    print 'Pointer function (using time):'
    print '\tdbcntl.pointer(%s) => %s' % (time,dbcntl.pointer(time))

#}}}
