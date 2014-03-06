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
       
alltripsperday = "CREATE TABLE out_all_trips_per_day AS \
    SELECT dow, count(trip_id) \
    FROM new_trips \
    GROUP BY dow;"

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

georoutes = "CREATE TABLE geojson_rte_stop_shape AS \
SELECT route_id, dow, direction_id, \
ST_AsGeoJSON(ST_MakeLine(stop_geom ORDER BY stop_sequence)) As stop_line_geom \
FROM ( \
	SELECT distinct r.route_id, r.dow, r.direction_id, stop_id, stop_geom, stop_sequence \
	FROM route_shapes r \
	JOIN new_trips t USING (shape_id) \
	JOIN new_stop_times ns using (trip_id) \
	JOIN geo_stops USING (stop_id) \
	ORDER BY r.route_id, r.dow, r.direction_id, stop_sequence ASC) a \
GROUP BY route_id, dow, direction_id;"



deleteTbls = "DROP TABLE IF EXISTS geo_stop_times, trips_per_stop, stop_level_avg_hdwy, \
rte_svc_span, rte_hdwy, rte_hrs_svc, rte_trips_day, geo_lines, geo_stops, trip_speeds, \
rte_speeds, temp1, rte_dist_bw_stops, out_stop, out_route_stop, out_stop_route, geojson_route_shapes, out_route, routes_types_serving_stops, geojson_rte_stop_shape, out_all_trips_per_day, all_trips_per_day,new_trips CASCADE;"

queries = ["geolines","routeshapes","geostops","georoutes","avghdwystops","routes_serve_stops","tripsperday","hrsofservice","avghdwyrte","svcspan","tripspeeds","routespeeds","stopdist","routes","stops","stop_routes"]
        
def go(db,u,p):
    "perform second level analysis for all route and stop-level queries"
    print "Starting Metrics."
    local_start = time.time()
    con = psycopg2.connect(database=db, user=u, password=p)
    cur = con.cursor()
    try:
        cur.execute(deleteTbls)
        print "  Executed query - deleteTbls"
    except:
        print " !ERROR: Failed query - deleteTbls"
    try:            
        cur.execute(geolines)
        print "  Executed query - geolines"
    except:
        print " !ERROR: Failed query - geolines"
    try:            
        cur.execute(geostops)
        print "  Executed query - geostops"
    except:
        print " !ERROR: Failed query - geostops"

    con.commit()

    print "  Completed metrics queries in ", int(time.time()-local_start)," seconds."

    


