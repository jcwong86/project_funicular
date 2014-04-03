def go(db):
    "Drops all the tables created in this program."

    qry_cleanup=    """
        DROP TABLE IF EXISTS 
        agency,
        calendar,
        calendar_dates,
        fare_attributes,
        fare_rules,
        feed_info,
        frequencies,
        routes,
        shapes,
        stop_times,
        stops,
        transfers,
        trips,
        geo_shapes,
        geo_lines,
        geo_stops,
        new_stop_times,
        trip_data,
        stop_data,
        dates_service_ids,
        veh_hours_by_trip,
        veh_hours_by_svc,
        trip_stops,
        trip_stop_geoms,
        trip_shape_geoms,
        veh_miles_by_trip,
        veh_miles_by_svc,
        stop_summary,
        out_stop,
        out_route,
        rev_hr_mi_by_date,
        ntd_out,
        q_geo_lines,
        q_shape_lookup,
        trip_stats,
        trip_lengths,
        route_stats,
        route_stats_sat,
        route_stats_sun,
        route_stats_wkdy,
        route_stats_gen CASCADE;"""


    try:
        cur = db.cursor()
        cur.execute(qry_cleanup)
        db.commit()
        print "  Database cleaned up."
    except Exception, e:
        print " !ERROR: Failed to drop tables. Cleanup failed."
        print e
        
