import time
import os
import string
import psycopg2
import datetime



secPastMid = """
CREATE TABLE new_stop_times AS
SELECT  *, 
        3600*(substring(arrival_time from 1 for position(':' in arrival_time)-1)::integer) + 60*substring(arrival_time from position(':' in arrival_time)+1 for 2)::integer + substring(arrival_time from 
        char_length(arrival_time)-1 for 2)::integer AS a_sec_past_mid, 
        3600*(substring(departure_time from 1 for position(':' in departure_time)-1)::integer) + 60*substring(departure_time from position(':' in departure_time)+1 for 2)::integer + 
        substring(departure_time from char_length(departure_time)-1 for 2)::integer AS d_sec_past_mid FROM stop_times
"""     

geolines = """
    CREATE TABLE geo_lines AS
    SELECT  shape_id,
            ST_MakeLine(geom ORDER BY shape_pt_sequence) As line_geom
    FROM    geo_shapes
    GROUP BY shape_id;
    """

geostops = """
    CREATE TABLE geo_stops AS  
    SELECT  stop_id,
            stop_lat,
            stop_lon,
            stop_code,
            stop_name,
            ST_SetSRID(ST_MakePoint(stop_lon,stop_lat),4326) AS stop_geom 
    FROM stops;"""


deleteTbls = "DROP TABLE IF EXISTS new_stop_times, geo_lines, geo_stops;"
queries = [geolines,geostops,secPastMid]
        
def go(db,u,p):
    "Prepare tables for calculations and analysis by creating geometries linked to stop and route id's."
    print "Starting prep_tables.py."
    local_start = time.time()
    #Creates a synthetic date|svc_id table based on calendar/cal_date usage
    

    con = psycopg2.connect(database=db, user=u, password=p)
    cur = con.cursor()
    try:
        cur.execute(deleteTbls)
        print "  Executed query - deleteTbls"
    except:
        print " !ERROR: Failed query - deleteTbls"
    for i in queries:
        try:            
            cur.execute(i)
            print "  Executed query -", i.splitlines()[1].split()[2],""
        except Exception, e:
            print " !ERROR: Failed query - ", i.splitlines()[1].split()[2],""
            print e.pgerror
    
    con.commit()

    print "  Completed metrics queries in ", int(time.time()-local_start)," seconds."

    


