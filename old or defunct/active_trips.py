import psycopg2
import psycopg2.extras
import time
import sys


def count_active_trips(in_dbname, in_username, in_password):
	"Creates a table, active_trips, out of this database."    

	qry_setup_table = "DROP TABLE IF EXISTS active_trips; CREATE TABLE active_trips (trip_id text, time int, active int);"
	qry_trip_start_end = "SELECT trip_id, MIN(d_sec_past_mid)/60 AS first_depart, MAX(a_sec_past_mid)/60 AS last_arrive FROM new_stop_times GROUP BY trip_id"

	print "\nStarting trip counting (10-min bins) for "+in_dbname
	db = psycopg2.connect(database = in_dbname,user = in_username,password = in_password)
	trip_start_end = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
	trip_start_end.execute(qry_trip_start_end)
	table_writer = db.cursor()
	table_writer.execute(qry_setup_table)
	n=0    
	for trip in trip_start_end:
		trip_id=trip['trip_id']
		trip_start=trip['first_depart']
		trip_end=trip['last_arrive']
		i=0
		while True:
			time = i*10
			active=0			
			if ((trip_start < time) & (trip_end > time)):
				#If this time period is after the start of the trip AND before the end of the trip then write a 1
				active=1
			qry_write_active = "INSERT INTO active_trips VALUES ('"+trip_id+"', "+str(time)+", "+str(active)+");"
			table_writer.execute(qry_write_active)
			i+=1 #While loop breaker
			if i>156: #go till 2am
				break
		n+=1
		if n%100 == 0: 
			sys.stdout.write('.')
		db.commit()
	table_writer.execute
	db.close()   


    
def aggregate_active_trips(in_dbname, in_username, in_password):
    "Creates a table to aggregate the active_trips by route"
  
    qry_agg = "DROP TABLE IF EXISTS out_active_trips_agg; CREATE TABLE out_active_trips_agg AS SELECT route_id, dow, time, sum(active) as sum_active FROM new_trips, active_trips WHERE new_trips.trip_id=active_trips.trip_id GROUP BY route_id, dow, time;"
    qry_agg_dow = "DROP TABLE IF EXISTS out_active_trips_bytod; CREATE TABLE out_active_trips_bytod AS SELECT dow, time, sum(active) as sum_active FROM new_trips, active_trips WHERE new_trips.trip_id=active_trips.trip_id GROUP BY dow, time;"
    db = psycopg2.connect(database = in_dbname,user = in_username,password = in_password)
    table_writer = db.cursor()
    table_writer.execute(qry_agg)
    table_writer.execute(qry_agg_dow)
    db.commit()
    db.close()
    
    
def go(in_dbname, in_username, in_password):

    begin=time.time()
    
    count_active_trips(in_dbname, in_username, in_password)
    end=time.time()
    print "\nCompleted counting "+in_dbname+" in "+str(int(end-begin))+" sec."   

    aggregate_active_trips(in_dbname, in_username, in_password)
    end=time.time()
    print "\nCompleted aggregation "+in_dbname+" in "+str(int(end-begin))+" sec."   

