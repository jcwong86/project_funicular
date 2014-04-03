import time, sys

def go(db):
    "Creates a table of stop geometries and characteristics that can be used for shapefile generation."

    print  "Begin stop calculations."
    

    drop_tables = """
    -- . drop_tables
    DROP TABLE IF EXISTS    
                            stop_summary,
                            out_stop;
    """



    stop_summary = """
        CREATE TABLE stop_summary AS
        -- Note, takes max of routes identified for either dir at any svc_id.
        SELECT  stop_id, 
            route_type,
            count(distinct route_id) as numRoutes,
            array_to_string(array_agg(distinct route_id),',') AS route_ids_served,
            array_to_string(array_agg(distinct route_short_name),',') AS route_short_names_served,
            array_to_string(array_agg(distinct route_long_name),',') AS route_long_names_served
        FROM   stop_times a
            JOIN (
                SELECT route_id, trips.trip_id, route_type
                FROM trips JOIN routes USING (route_id)) c
            USING (trip_id)
            JOIN (
                SELECT route_id, route_long_name, route_short_name
                FROM routes) d
            USING (route_id) 
        GROUP BY stop_id, route_type
        ORDER BY stop_id;

    """ 

    out_stop ="""
        CREATE TABLE out_stop AS
        SELECT  stop_geom as the_geom,
            stop_id,
            route_type,
            stops.stop_lat,
            stops.stop_lon,
            stops.stop_name as stopname,
            stop_desc as stopdesc,
            numroutes as numrts,
            route_ids_served as rserved_id,
            route_short_names_served as rserved_sh,
            route_long_names_served as rserved_lg
        FROM    stop_summary JOIN
            stops USING (stop_id) JOIN
            geo_stops USING (stop_id);
    """    
    queries = [drop_tables, stop_summary, out_stop]

    "perform second level analysis for all route and stop-level queries"
    local_start=time.time()
    for i in queries:
        try:
            cur = db.cursor()
            
            try:
                cur.execute(i)
                db.commit()
                print "  Executed query -", i.splitlines()[1].split()[2],""
            except Exception, e:
                print " !ERROR: Failed query - ", i.splitlines()[1].split()[2],""
                print e.pgerror
                print
                pass
        except:
            print " !ERROR: Connection Failed."

    print "  Completed stop_outs queries in ", int(time.time()-local_start)," seconds."
