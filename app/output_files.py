import psycopg2
import sys
import string

def go(in_dbname, in_username, in_password, out_folder_path, gtfs_name, mode_number_as_txt):
    "Export key tables from route, stop_route, stop and active_trips into a specified folder that has universal access"
    print "Starting export for M"+mode_number_as_txt
    #Clean off the last backslash of filepath
    if out_folder_path[-1] == "\\":
        out_folder_path=out_folder_path[:-1]
        
    
    out_stop = "COPY (SELECT * FROM out_stop) TO '"+out_folder_path+"\\"+gtfs_name[:-4]+"_stop.csv' WITH CSV HEADER"
    
    db = psycopg2.connect(database=in_dbname, user=in_username, password=in_password)
    cur = db.cursor()
    try:
        cur.execute(out_stop)
        print "  Generated output file in "+out_folder_path
    except:
        print " !ERROR: Did not generate output file."
        print out_stop
    print "  Completed export."
    
    
    db.commit()
    db.close()
