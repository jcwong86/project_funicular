import date_svc_id_select
import time

def go(db):
    "Generates a table of unique route geometries and characteristics for use in shapefile creation."
    date_svc_id_select.go(db)
    print "Begin route calculations."


    qry_cleanup = """
    DROP TABLE IF EXISTS
    q_geo_lines,
    q_shape_lookup,
    trip_stats,
    trip_lengths,
    out_route,
    route_stats_sat,
    route_stats_sun,
    route_stats_wkdy,
    route_stats_gen;

    """

    qry_unique_lines = """
    
    CREATE TABLE q_geo_lines(
    line_geom GEOMETRY,
    q_shape_id SERIAL);"""

    qry_update_unique_lines = """
    INSERT INTO q_geo_lines 
    (SELECT DISTINCT line_geom 
    FROM geo_lines);
    """

    qry_unique_lines_lookup = """
    CREATE TABLE q_shape_lookup AS (
    SELECT
        shape_id,
        q_shape_id
    FROM
        geo_lines JOIN q_geo_lines USING (line_geom));
    
    ALTER TABLE dates_service_ids ADD dow INTEGER;
    """

    qry_dow = """
    UPDATE dates_service_ids
    SET dow = EXTRACT (dow FROM to_date(dategen::varchar,'YYYYMMDD'));"""

    qry_trip_stats = """
    CREATE TABLE trip_stats AS
    SELECT  
        trip_id,
        service_id,
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id,
        first_departure,
        last_arrival,
        trip_duration_min,
        num_stops
    FROM
        trips 
        JOIN q_shape_lookup USING (shape_id) 
        JOIN routes USING (route_id) 
        JOIN (
            SELECT
                trip_id,
                min(d_sec_past_mid) AS first_departure,
                max(a_sec_past_mid) AS last_arrival,
                (max(a_sec_past_mid)-min(d_sec_past_mid))/60::float AS trip_duration_min,
                count(DISTINCT stop_id) AS num_stops
            FROM
                new_stop_times 
            GROUP BY
                trip_id 
            ORDER BY
                trip_id ASC) a USING (trip_id);"""

    qry_trip_lengths="""
    CREATE TABLE trip_lengths AS
    SELECT  trip_id,
        ST_LENGTH(line_geom,true)*0.000621371 AS trip_length_mi
    FROM
        trips JOIN geo_lines USING (shape_id);
    """

    qry_route_stats_gen="""
    CREATE TABLE route_stats_gen AS
    SELECT
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id,
        MAX(trip_duration_min) as MAXTRIPDUR,
        MIN(trip_duration_min) as MINTRIPDUR,
        AVG(num_stops) as TYPNSTOPS,
        AVG(trip_length_mi) as TYPTRIPLEN
    FROM
        trip_stats JOIN trip_lengths USING (trip_id)
    GROUP BY
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id
    ORDER BY route_id, route_short_name, direction_id;
    """

    qry_route_stats_sat="""
    CREATE TABLE route_stats_sat AS
    SELECT
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id,
        MIN(first_departure) AS FRSTTRIPSA,
        MAX(last_arrival) AS LASTTRIPSA,
        COUNT(trip_id) AS NTRIPS_SA
    FROM
        trip_stats
    WHERE   
        trip_id IN(
            SELECT 
                trip_id
            FROM 
                trips
            WHERE   
                service_id IN(
                    SELECT 
                        DISTINCT service_id
                    FROM
                        dates_service_ids
                    WHERE
                        dategen IN (SELECT MIN(dategen) FROM dates_service_ids WHERE dow='6')))
    GROUP BY
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id;
    """
    qry_route_stats_sun="""
    CREATE TABLE route_stats_sun AS
    SELECT
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id,
        MIN(first_departure) AS FRSTTRIPSU,
        MAX(last_arrival) AS LASTTRIPSU,
        COUNT(trip_id) AS NTRIPS_SU
    FROM
        trip_stats
    WHERE   
        trip_id IN(
            SELECT 
                trip_id
            FROM 
                trips
            WHERE   
                service_id IN(
                    SELECT 
                        DISTINCT service_id
                    FROM
                        dates_service_ids
                    WHERE
                        dategen IN (SELECT MIN(dategen) FROM dates_service_ids WHERE dow='0')))
    GROUP BY
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id;
    """
    
    qry_route_stats_wkdy="""
    CREATE TABLE route_stats_wkdy AS
    SELECT
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id,
        MIN(first_departure) AS FRSTTRIPWK,
        MAX(last_arrival) AS LASTTRIPWK,
        COUNT(trip_id) AS NTRIPS_WK
    FROM
        trip_stats
    WHERE   
        trip_id IN(
            SELECT 
                trip_id
            FROM 
                trips
            WHERE   
                service_id IN(
                    SELECT 
                        DISTINCT service_id
                    FROM
                        dates_service_ids
                    WHERE
                        dategen IN (SELECT MIN(dategen) FROM dates_service_ids WHERE dow='2')))
    GROUP BY
        route_id,
        route_short_name,
        route_long_name,
        trip_headsign,
        direction_id,
        q_shape_id;"""
    
    qry_route_stats="""
    CREATE TABLE out_route AS
    SELECT 
        line_geom,
        route_id,
        route_type,
        route_stats_gen.route_short_name as rt_sname,
        route_stats_gen.route_long_name as rt_lname,
        trip_headsign as t_headsign,
        direction_id as dir_id,
        q_shape_id,
        maxtripdur,
        mintripdur,
        typnstops,
        typtriplen,
        frsttripsa,
        lasttripsa,
        ntrips_sa,
        frsttripsu,
        lasttripsu,
        ntrips_su,
        frsttripwk,
        lasttripwk,
        ntrips_wk
    FROM 
        route_stats_gen
        JOIN route_stats_sat USING(route_id, route_short_name, route_long_name, trip_headsign, direction_id, q_shape_id)
        JOIN route_stats_sun USING(route_id, route_short_name, route_long_name, trip_headsign, direction_id, q_shape_id)    
        JOIN route_stats_wkdy USING(route_id, route_short_name, route_long_name, trip_headsign, direction_id, q_shape_id)
        JOIN q_geo_lines USING (q_shape_id)
        JOIN routes USING (route_id);"""
    
    queries = [qry_cleanup,qry_unique_lines,qry_update_unique_lines,qry_unique_lines_lookup,qry_dow,qry_trip_stats,qry_trip_lengths,qry_route_stats_gen,qry_route_stats_sat,qry_route_stats_sun,qry_route_stats_wkdy,qry_route_stats]

    local_start=time.time()
    for query in queries:    
        try:
            cur = db.cursor()
            cur.execute(query)
            db.commit()
            print "  Query executed."
        except Exception, e:
            print " !ERROR: Failed a query - See description below."
            print e
            print " !Stopping script. Reset the db connection to continue using it. db.reset()"
            break
    print "  Completed route_outs queries in ", int(time.time()-local_start)," seconds."

            