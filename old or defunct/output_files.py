import psycopg2
import sys
import string

def go(in_dbname, in_username, in_password, out_folder_path, gtfs_name, mode_number_as_txt, start_date_YYYYMMDD):
    "Export key tables from route, stop_route, stop and active_trips into a specified folder that has universal access"
    print "Starting export."
    print "M"+mode_number_as_txt
    #Clean off the last backslash of filepath
    if out_folder_path[-1] == "\\":
        out_folder_path=out_folder_path[:-1]
        
    
    out1 = "COPY (SELECT * FROM out_route) TO '"+out_folder_path+"\\"+in_dbname+"_route.csv' WITH CSV HEADER"
    out2 = "COPY (SELECT * FROM out_stop_route) TO '"+out_folder_path+"\\"+in_dbname+"_stop_route.csv' WITH CSV HEADER"
    out3 = "COPY (SELECT * FROM out_stop) TO '"+out_folder_path+"\\"+in_dbname+"_stop.csv' WITH CSV HEADER"
    out4 = "COPY (SELECT * FROM out_active_trips_agg) TO '"+out_folder_path+"\\"+in_dbname+"_active_trips.csv' WITH CSV HEADER"
    out5 = "COPY (SELECT * FROM out_all_trips_per_day) TO '"+out_folder_path+"\\"+in_dbname+"_all_trips_per_day.csv' WITH CSV HEADER"
    out6 = "COPY (SELECT * FROM out_active_trips_bytod) TO '"+out_folder_path+"\\"+in_dbname+"_all_trips_per_timeofday.csv' WITH CSV HEADER"

    out7a = """
        COPY (
            SELECT *
            FROM (
                SELECT  *,
                        '%s'::varchar AS feed_date
                FROM    rev_hr_mi_by_date) a
            WHERE dategen::int >= feed_date::int)
        TO '""" %start_date_YYYYMMDD
    
    out7 = out7a+out_folder_path+"\\"+gtfs_name[:(len(gtfs_name)-13)]+"_M"+mode_number_as_txt+"_rev_hr_mi_by_date_"+start_date_YYYYMMDD+".csv' WITH CSV HEADER"

    out_ntd = "COPY (SELECT * FROM ntd_out) TO '"+out_folder_path+"\\ntd_out_M"+mode_number_as_txt+"_"+gtfs_name[:(len(gtfs_name)-13)]+".csv' WITH CSV HEADER"
	
    db = psycopg2.connect(database=in_dbname, user=in_username, password=in_password)
    cur = db.cursor()
    try:
        cur.execute(out7)
        cur.execute(out_ntd)
        print "  Generated output file in "+out_folder_path
    except:
        print " !ERROR: Did not generate output file."

    print "  Completed export."
    
    
    db.commit()
    db.close()
