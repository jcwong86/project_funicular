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

import import_gtfs, output_files, calculate_metrics, prep_tables, get_modes, \
    get_agencies, date_svc_id_select, route_out, stops_out, cleanup
import time, math, psycopg2, os, urlparse, boto
from datetime import datetime, timedelta
from sys import argv
from shutil import make_archive, rmtree
from config import OUTPUT_PATH, S3_BUCKET

def go(gtfs_url, short_agency_name_no_spaces, output_folder):
    local_start=time.time()
    print "----------------------------------"
    print "Running GTFS Reader for "+gtfs_url

    # db = psycopg2.connect(host=in_dbhost, database=in_dbname,
    #     user=in_username, password=in_password)

    urlparse.uses_netloc.append("postgres")
    db_url = urlparse.urlparse(os.environ["DATABASE_URL"])
    
    db = psycopg2.connect(
        database=db_url.path[1:],
        user=db_url.username,
        password=db_url.password,
        host=db_url.hostname,
        port=db_url.port)

    if import_gtfs.go(gtfs_url, db):
        prep_tables.go(db)
        route_out.go(db)
        stops_out.go(db)
        
        modenums = get_modes.go(db)
        request_dir = os.path.normcase(OUTPUT_PATH +'/' + output_folder + '/')
        os.mkdir(request_dir)
        for mode in modenums:
            output_files.go(db_url.hostname, db_url.path[1:], db_url.username,
                db_url.password, mode, 'stop', short_agency_name_no_spaces,
                output_folder)
            output_files.go(db_url.hostname, db_url.path[1:], db_url.username,
                db_url.password, mode, 'route', short_agency_name_no_spaces,
                output_folder)
        zipOut = archive(request_dir)
        download_link = move_to_S3(zipOut)
        print "GTFS Reader completed."
    else:
        print "!!ERROR: Import problem - program terminated."
    cleanup.go(db)
    if time.time()-local_start < 60:
        print "Total runtime < 1 min."
    else:
        print "Total runtime: "+ str(math.trunc((time.time()-local_start)/60)) + \
            " min " +str(round((time.time()-local_start)%60)) +" sec."
    print "----------------------------------"
    db.close()
    return download_link

def archive(directory):
    make_archive(directory, 'zip', directory)
    rmtree(directory)
    return(directory[:-1] + '.zip')

def move_to_S3(file):
    s3_key = boto.connect_s3().get_bucket(S3_BUCKET, validate = False).new_key(os.path.basename(file))
    s3_key.set_contents_from_filename(file)
    os.remove(file)
    return s3_key.generate_url(expires_in = 259200)

if __name__ == "__main__":
    go(argv[1], argv[2], argv[3])
