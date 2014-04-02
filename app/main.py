# Copyright (c) 2013 Team Cypress: Aaron Gooze, Jack Reed, Landon Reed, James Wong
# Questions? Email James at jcwong86@gmail.com or Aaron at aaron.gooze@gmail.com.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import import_gtfs
import output_files
import calculate_metrics
import prep_tables
import get_modes
import get_agencies
import time
import math
import date_svc_id_select
import psycopg2
import route_out
import stops_out
import cleanup
from sys import argv

# for out_folder_path on a windows machine, go to "c:\\tmp\\"
def go(gtfs_url, in_dbhost, in_dbname, in_username, in_password, short_agency_name_no_spaces):
    local_start=time.time()
    print "----------------------------------"
    print "Running GTFS Reader for "+gtfs_url

    db = psycopg2.connect(host=in_dbhost, database=in_dbname,
        user=in_username, password=in_password)

    if import_gtfs.go(gtfs_url, db):
        prep_tables.go(db)
        route_out.go(db)
        stops_out.go(db)
        
        modenums = get_modes.go(db)
        for mode in modenums:
            output_files.go(in_dbhost, in_dbname, in_username,
                in_password, mode, 'stop',short_agency_name_no_spaces)
            output_files.go(in_dbhost, in_dbname, in_username,
                in_password, mode, 'route', short_agency_name_no_spaces)
        print "GTFS Reader completed."
    else:
        print "!!ERROR: Import problem - program terminated."
    cleanup.go(db)
    if time.time()-local_start < 60:
        print "Total runtime < 1 min."
    else:
        print "Total runtime: "+ str(math.trunc((time.time()-local_start)/60)) + " min " +str(round((time.time()-local_start)%60)) +" sec."
    print "----------------------------------"
    db.close()

if __name__ == "__main__":
    go(argv[1], argv[2], argv[3], argv[4], argv[5])
