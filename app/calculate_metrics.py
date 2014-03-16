import time, sys

def go(db,agency,mode_number_as_txt):

    print "Starting calculate_metrics.py."
    print agency.replace('_',' ')+" - M"+mode_number_as_txt

    drop_tables = """
    -- . drop_tables
    DROP TABLE IF EXISTS    rev_hr_mi_by_date,
                            trip_stops,
                            trip_stop_geoms,
                            trip_shape_geoms,
                            veh_miles_by_trip,
                            veh_hours_by_trip,
                            veh_miles_by_svc,
                            veh_hours_by_svc,
                            ntd_out,
                            stop_summary,
                            out_stop;
    """


    qry_first_last_stops = """
        CREATE TABLE trip_stops AS
        SELECT  e.trip_id, 
                first_stop_id, 
                last_stop_id
        FROM (
                SELECT a.trip_id, b.stop_id as first_stop_id
                FROM (
                        SELECT  trip_id, 
                                min(stop_sequence) AS min_stop_seq
                        FROM    stop_times
                        GROUP BY trip_id) a
                JOIN    stop_times b
                ON (    a.trip_id=b.trip_id AND
                        a.min_stop_seq=b.stop_sequence)) e
        JOIN (
                SELECT c.trip_id, d.stop_id as last_stop_id
                FROM (
                        SELECT  trip_id, 
                                max(stop_sequence) AS max_stop_seq
                        FROM    stop_times
                        GROUP BY trip_id) c
                JOIN    stop_times d
                ON (    c.trip_id=d.trip_id AND
                        c.max_stop_seq=d.stop_sequence)) f
        ON (    e.trip_id=f.trip_id),
        (SELECT trip_id FROM trip_data WHERE agency_name='%s') z
        WHERE e.trip_id in (z.trip_id); """ %agency

    qry_first_last_geoms ="""
        CREATE  TABLE trip_stop_geoms AS
        SELECT  first_geom.trip_id, 
                first_stop_id, 
                first_stop_geom, 
                last_stop_id, 
                last_stop_geom
        FROM (
                SELECT trip_id, first_stop_id, stop_geom as first_stop_geom
                FROM geo_stops
                INNER JOIN trip_stops
                ON(trip_stops.first_stop_id=geo_stops.stop_id)) first_geom
        JOIN (
                SELECT trip_id, last_stop_id, stop_geom as last_stop_geom
                FROM geo_stops
                INNER JOIN trip_stops
                ON(trip_stops.last_stop_id=geo_stops.stop_id)) last_geom
        ON (first_geom.trip_id=last_geom.trip_id),
        (SELECT trip_id FROM trip_data WHERE agency_name='%s') z
        WHERE first_geom.trip_id in (z.trip_id);
        """ %agency

    qry_trip_route_geoms = """
        CREATE TABLE trip_shape_geoms AS
        SELECT 	trip_id, 
                trips.shape_id, 
                line_geom
        FROM trips, geo_lines
        WHERE geo_lines.shape_id=trips.shape_id;
    """

    qry_veh_miles_by_trip = """
        CREATE TABLE veh_miles_by_trip AS 
        SELECT  trip_stop_geoms.trip_id, 
                (ST_Line_Locate_Point(line_geom,last_stop_geom) 
                - ST_Line_Locate_Point(line_geom,first_stop_geom)) 
                * ST_Length(ST_Transform(line_geom,900913))  --In Meters
                * 0.000621371 as veh_miles --to Miles
        FROM trip_stop_geoms, trip_shape_geoms
        WHERE trip_stop_geoms.trip_id=trip_shape_geoms.trip_id;
    """

    qry_veh_miles_by_svc = """
        CREATE TABLE veh_miles_by_svc AS
        SELECT  service_id,
                round(sum(veh_miles)::numeric,2) as veh_mi_per_svc_day
        FROM    veh_miles_by_trip,
                trips,
                routes
        WHERE   veh_miles_by_trip.trip_id=trips.trip_id AND
                trips.route_id=routes.route_id AND
                route_type='%s'
        GROUP BY service_id
        ORDER BY service_id;

    """ %mode_number_as_txt

    qry_veh_hrs = """
        CREATE TABLE veh_hours_by_trip AS
        SELECT 	c.trip_id,
                round((last_arrive_sec-first_depart_sec)::numeric/3600,2)
                    AS veh_hours
        FROM (
                SELECT 	trip_stops.trip_id, 
                        MIN(d_sec_past_mid) AS first_depart_sec 
                FROM 	trip_stops, 
                        new_stop_times a
                WHERE 	trip_stops.first_stop_id=a.stop_id AND
                         trip_stops.trip_id=a.trip_id
                GROUP BY	trip_stops.trip_id) c
        JOIN (
                SELECT 	trip_stops.trip_id, 
                        MAX(a_sec_past_mid) AS last_arrive_sec
                FROM 	trip_stops, 
                        new_stop_times b
                WHERE 	trip_stops.last_stop_id=b.stop_id AND
                        trip_stops.trip_id=b.trip_id
                GROUP BY	trip_stops.trip_id) d
        ON c.trip_id=d.trip_id;

    """

    qry_veh_hrs_by_svc = """
        CREATE TABLE veh_hours_by_svc AS
        SELECT  service_id,
                round(sum(veh_hours)::numeric,2) as veh_hrs_per_svc_day
        FROM    veh_hours_by_trip,
                trips,
                routes
        WHERE   veh_hours_by_trip.trip_id=trips.trip_id AND
                trips.route_id=routes.route_id AND
                route_type='%s'
        GROUP BY service_id
        ORDER BY service_id;
    """ %mode_number_as_txt


    qry_hrs_mi_by_day = """
    CREATE TABLE rev_hr_mi_by_date AS 
    SELECT 	dategen, 
            SUM(veh_hrs_per_svc_day) as daily_veh_hrs,
            SUM(veh_mi_per_svc_day) as daily_veh_mi
    FROM 	dates_service_ids a,
            veh_hours_by_svc b,
            veh_miles_by_svc c
    WHERE	a.service_id=b.service_id AND
            a.service_id=c.service_id
    GROUP BY dategen
    ORDER BY dategen;
    """

    qry_hrs_by_day = """
    CREATE TABLE rev_hr_mi_by_date AS 
    SELECT 	dategen, 
            SUM(veh_hrs_per_svc_day) as daily_veh_hrs
    FROM 	dates_service_ids a,
            veh_hours_by_svc b
    WHERE	a.service_id=b.service_id
    GROUP BY dategen
    ORDER BY dategen;
    """

    qry_ntd_out = """
    CREATE TABLE ntd_out AS
            SELECT 	agency_name,
                    agency_id,
                    annual_veh_hrs,
                    annual_veh_mi
            FROM agency,(
                    SELECT 	ROUND(SUM(b.daily_veh_hrs)*52,1) AS annual_veh_hrs,
                            ROUND(SUM(b.daily_veh_mi)*52,1) AS annual_veh_mi
                    FROM (

                            SELECT 	dayofweek, 
                                    AVG(daily_veh_hrs) as daily_veh_hrs, 
                                    AVG(daily_veh_mi) as daily_veh_mi
                            FROM (
                                    SELECT 	to_date(dategen::text,'YYYYMMDD'),
                                            EXTRACT(dow FROM to_date(dategen::text,'YYYYMMDD')) as dayofweek, 
                                            daily_veh_hrs, 
                                            daily_veh_mi
                                    FROM 	rev_hr_mi_by_date) b
                            GROUP BY dayofweek) b) c;
    """
    stop_summary = """
        CREATE TABLE stop_summary AS
        -- Note, takes max of routes identified for either dir at any svc_id.
        SELECT  stop_id, 
            count(distinct route_id) as numRoutes,
            array_to_string(array_agg(distinct route_id),',') AS route_ids_served,
            array_to_string(array_agg(distinct route_short_name),',') AS route_short_names_served,
            array_to_string(array_agg(distinct route_long_name),',') AS route_long_names_served
        FROM   stop_times a
            JOIN (
                SELECT route_id, trip_id
                FROM trips) con
            USING (trip_id)
            JOIN (
                SELECT route_id, route_long_name, route_short_name
                FROM routes) d
            USING (route_id) 
            JOIN (
                SELECT stop_id, agency_name 
                FROM stop_data 
                WHERE agency_name = '%s') e
        USING (stop_id)
        GROUP BY stop_id
        ORDER BY stop_id;

    """ %agency

    out_stop ="""
        CREATE TABLE out_stop AS
        SELECT  stop_geom as the_geom,
            stop_id,
            stops.stop_lat,
            stops.stop_lon,
            stops.stop_name,
            stop_desc,
            numroutes,
            route_ids_served,
            route_short_names_served,
            route_long_names_served
        FROM    stop_summary JOIN
            stops USING (stop_id) JOIN
            geo_stops USING (stop_id);
    """    
    queries = [drop_tables, qry_first_last_stops, qry_first_last_geoms,qry_trip_route_geoms,qry_veh_miles_by_trip,qry_veh_miles_by_svc,qry_veh_hrs,qry_veh_hrs_by_svc, stop_summary, out_stop]

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

    try:
        cur = db.cursor()
        cur.execute(qry_hrs_mi_by_day)
        db.commit()
        print "  Executed query - qry_hrs_mi_by_day."
    except:
        print " !ERROR: Failed query - 'query_hrs_mi_by_day - attempting just hrs."
        try:

            cur = db.cursor()
            cur.execute(qry_hrs_by_day)
            db.commit()
            print "  Executed query - qry_hrs_by_day. Not reporting miles."
        except:
            print " !ERROR: Failed query - 'query_hrs_by_day. Output will fail."
            
    try:
        cur = db.cursor()
        cur.execute(qry_ntd_out)
        db.commit()
        print "  Executed query - NTD Output."
    except:
        print " !ERROR: Failed query - NTD Output."

    print "  Completed NTD Metrics queries in ", int(time.time()-local_start)," seconds."
