# -*- coding: cp1252 -*-
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


# 
# This script opens a zipped GTFS feed and imports the data into a
# spatially enabled PostgreSQL database. It does little error handling
# pertaining to feed validation; users should ensure GTFS feeds are in good
# shape using one of many tools available for validation first.
#
# Dependencies:
# This script assumes users have setup PostgreSQL, PostGIS, Python, and have
# the psycopg2 library installed for Python. It uses welcome.py
#

import zipfile
import csv
import time
import os
import string
import psycopg2
import sys
import re

## SQL to modify the tables into appropriate view

def chooseFields(inFile):
    "Returns an array of field names based on which gtfs .txt table is used."
    if(inFile=='agency.txt'): 
        a=['agency_id', 'agency_name', 'agency_url', 'agency_timezone','agency_lang','agency_phone','agency_fare_url']
    elif(inFile=='calendar.txt'): 
        a=['service_id', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'start_date', 'end_date']
    elif(inFile=='calendar_dates.txt'):  
        a=['service_id', 'date', 'exception_type']
    elif(inFile=='fare_attributes.txt'):  
        a=['fare_id', 'price', 'currency_type', 'payment_method', 'transfers', 'transfer_duration']
    elif(inFile=='fare_rules.txt'):  
        a=['fare_id', 'route_id', 'origin_id', 'destination_id', 'contains_id']
    elif(inFile=='frequencies.txt'):  
        a=['trip_id', 'start_time', 'end_time', 'headway_secs','exact_times']
    elif(inFile=='routes.txt'):  
        a=['route_id', 'agency_id', 'route_short_name', 'route_long_name', 'route_desc', 'route_type', 'route_url', 'route_color', 'route_text_color']
    elif(inFile=='shapes.txt'):  
        a=['shape_id', 'shape_pt_lat', 'shape_pt_lon', 'shape_pt_sequence', 'shape_dist_traveled']
    elif(inFile=='stop_times.txt'):  
        a=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence', 'stop_headsign', 'pickup_type', 'drop_off_type', 'shape_dist_traveled']
    elif(inFile=='stops.txt'):   
        a=['stop_id','stop_code','stop_name','stop_desc','stop_lat','stop_lon','zone_id', 'stop_url','location_type','parent_station','stop_timezone','wheelchair_boarding']
    elif(inFile=='transfers.txt'):
        a=['from_stop_id','to_stop_id','transfer_time','min_transfer_time']
    elif(inFile=='trips.txt'):
        a=['route_id', 'service_id', 'trip_id', 'trip_headsign', 'trip_short_name','direction_id', 'block_id', 'shape_id','wheelchair_accessible']
    elif(inFile=='feed_info.txt'):
        a=['feed_publisher_name','feed_publisher_url','feed_lang','feed_start_date','feed_end_date','feed_version']
    else: 
        a=[]
        print "  WARNING: Funny unrecognized table: %s" % inFile
    #print "The correct fields are: "+ str(a)
    return a

def setupTableQuery(tablename):
    "Run a query to create a table in db with name/fields according to GTFS"
    if tablename == 'agency.txt':
        b="CREATE TABLE agency (agency_id varchar,agency_name varchar,agency_url varchar,agency_timezone varchar,agency_lang varchar,agency_phone varchar,agency_fare_url varchar);"
    elif(tablename=='calendar.txt'): 
        b="CREATE TABLE calendar (service_id varchar,monday varchar,tuesday varchar,wednesday varchar,thursday varchar,friday varchar,saturday varchar,sunday varchar,start_date varchar,end_date varchar);"
    elif(tablename=='calendar_dates.txt'):  
        b="CREATE TABLE calendar_dates (service_id varchar,date varchar,exception_type varchar);"
    elif(tablename=='fare_attributes.txt'):  
        b="CREATE TABLE fare_attributes (fare_id varchar,price varchar,currency_type varchar,payment_method varchar,transfers varchar,transfer_duration varchar);"
    elif(tablename=='fare_rules.txt'):  
        b="CREATE TABLE fare_rules (fare_id varchar,route_id varchar,origin_id varchar,destination_id varchar,contains_id varchar);"
    elif(tablename=='feed_info.txt'):
        b="CREATE TABLE feed_info (feed_publisher_name varchar,feed_publisher_url varchar,feed_lang varchar,feed_start_date varchar,feed_end_date varchar,feed_version varchar);"
    elif(tablename=='frequencies.txt'):  
        b="CREATE TABLE frequencies (trip_id varchar,start_time varchar,end_time varchar,headway_secs varchar,exact_times varchar);"
    elif(tablename=='routes.txt'):  
        b="CREATE TABLE routes (route_id varchar,agency_id varchar,route_short_name varchar,route_long_name varchar,route_desc varchar,route_type varchar,route_url varchar,route_color varchar,route_text_color varchar);"
    elif(tablename=='shapes.txt'):  
        b="CREATE TABLE shapes (shape_id varchar,shape_pt_lat double precision,shape_pt_lon double precision,shape_pt_sequence integer,shape_dist_traveled double precision);"
    elif(tablename=='stop_times.txt'):  
        b="CREATE TABLE stop_times (trip_id varchar,arrival_time varchar,departure_time varchar,stop_id varchar,stop_sequence integer,stop_headsign varchar,pickup_type varchar,dropoff_type varchar,shape_dist_traveled varchar);"
    elif(tablename=='stops.txt'):   
        b="CREATE TABLE stops (stop_id varchar,stop_code varchar,stop_name varchar,stop_desc varchar,stop_lat double precision,stop_lon double precision,zone_id varchar,stop_url varchar,location_type varchar,parent_station varchar,timezone varchar,wheelchair_boarding varchar);"
    elif(tablename=='transfers.txt'):
        b="CREATE TABLE transfers (from_stop_id varchar,to_stop_id varchar,transfer_type varchar,min_transfer_time varchar);"
    elif(tablename=='trips.txt'):  
        b="CREATE TABLE trips (route_id varchar,service_id varchar,trip_id varchar,trip_headsign varchar,trip_short_name varchar,direction_id varchar,block_id varchar,shape_id varchar,wheelchair_accessible varchar);"
    elif(tablename=='feed_info.txt'):  
        b="CREATE TABLE feed_info (feed_publisher_name varchar,feed_publisher_url varchar,feed_lang varchar,feed_start_date varchar,feed_end_date varchar,feed_version varchar);"
    else: 
        b=[]
        print "  WARNING: Funny unrecognized table: %s" % tablename
    #In the future, this should be an executable query, not just print it here.
    return b

def insertData(GTFSfeed):

    #queries and array definitions
    file_structure = ['agency.txt', 'calendar.txt', 'calendar_dates.txt', 'fare_attributes.txt', 'fare_rules.txt', 'feed_stats', 'frequencies.txt', 'routes.txt',  'shapes.txt', 'stop_times.txt', 'stops.txt', 'transfers.txt',  'trips.txt', 'feed_info.txt']
    
    drop_tables="DROP TABLE IF EXISTS agency, calendar, calendar_dates, fare_attributes, fare_rules, frequencies, routes, shapes, stop_times, stops, transfers, trips, feed_info, geo_shapes, geo_stop_times, trips_per_stop, stop_level_avg_hdwy, rte_svc_span, rte_hdwy, rte_hrs_svc, rte_trips_day, geo_lines, geo_stops, trip_speeds, rte_speeds, temp1, rte_dist_bw_stops, out_stop, out_route,new_stop_times CASCADE;"
    
    drop_views="DROP VIEW IF EXISTS geojson_shapes CASCADE;"
    
    #convert departure times to seconds past midnight


    # Connect to database
    con = psycopg2.connect(database=dbname, user=username, password=password)
    cur = con.cursor()
    cur.execute(drop_tables)
    cur.execute(drop_views)
    local_start=time.time()
    feed = zipfile.ZipFile(GTFSfeed)
    
    #Create a readable zipfile object from GTFS feed
    for txtfile in feed.namelist():#Loop through the files that should be in a GTFS feed            
        printline= "\n  "+txtfile+" started at "+ str(int(time.time()-local_start))+" sec."
        sys.stdout.write(printline)
        if txtfile in file_structure:                   #If the intended file exists
            fieldnames = chooseFields(txtfile)          #Get the fieldnames that go along with text file
            setupQry = setupTableQuery(txtfile)+"\n"    #Write a SQL query that sets up a table for this txt file
            cur.execute(setupQry)
            dr = csv.DictReader(feed.open(txtfile))     #Create a Dictionary Reader from zipped textfile
                                                          #Start the SQL insert statement
            i=0
            j=0
            for fieldname in dr.fieldnames:         #make sure all headers are lowercased to match fieldnames
                
                dr.fieldnames[j] = fieldname.strip().lower()
                dr.fieldnames[j] = re.sub('[﻿]', '', dr.fieldnames[j])
                j+=1
                k=0
                l=0
            for row in dr:                              #For each line in the textfile
                k+=1
                if k%50000==0:
                    sys.stdout.write('.')
                insert_statement = 'INSERT INTO '+string.rstrip(txtfile,'.txt')+' VALUES ('
                l+=1
                for fieldname in fieldnames:            #For each intended field               
                    try:
                        row[fieldname]                    #See if it exists
                    except:
                        insert_statement += "NULL,"         #Add blank data when the field isn't included in txtfile structure
                    else:
                        if row[fieldname] == "":
                            insert_statement += "NULL,"     #Add blank data for blank/missing data
                        else:
                                                        #If everything is good, write the data into the Insert statement
                                                        #In the future, any switch statements for diff data types go here
                            a = row[fieldname].strip()
                            insert_statement += "'"+string.replace(a,"'","")+"',"
                insert_statement=string.rstrip(insert_statement,",")+");"                 #Close the Insert statement
                cur.execute(insert_statement)
    feed.close()
    con.commit()
    local_end=time.time()
    #print "\n-Checked ",dbname, " in ", int(local_end-local_start)," sec"
    
def timeToSeconds(text):
    h,m,s = map(int,text.split(":"))
    return h*60*60 + m*60 + s

def spatiallyEnable():
    "Runs queries that will spatially enable the stop_times and shapes files by adding geo_tablenames"
    #convert shape points to line geometries
    shapes1 = "CREATE TABLE geo_shapes AS SELECT shape_id, shape_pt_lat, shape_pt_lon,shape_pt_sequence FROM shapes;"
    shapes2 = "ALTER TABLE geo_shapes ADD COLUMN geom geometry(POINT,4326);"
    shapes3 = "UPDATE geo_shapes SET geom = ST_SetSRID(ST_MakePoint(shape_pt_lon,shape_pt_lat),4326);"
    shapes4 = "CREATE INDEX shapes_geom ON geo_shapes USING GIST(geom);"
    shapes5 = "CREATE VIEW geojson_shapes AS SELECT shape_id, ST_AsGeoJSON(ST_MakeLine(geom ORDER BY shape_pt_sequence)) As line_geom FROM geo_shapes GROUP BY shape_id;"

    try:
        con = psycopg2.connect(database=dbname, user=username, password=password)
        cur = con.cursor()
        cur.execute(shapes1)
        cur.execute(shapes2)
        cur.execute(shapes3)
        cur.execute(shapes4)
        cur.execute(shapes5)
        con.commit()
        print "\n  Spatially enabled tables."
    except:
        print "\n !ERROR: Spatial enabling failed!"

def go(gtfs_filename, in_dbname, in_username, in_password):
    "Import a zipped gtfs file from a folder at the same hierarchy called gtfs_data \
    and connect to a pgSQL database with specified parameters."
    
    global dbname
    global username
    global password
    global path
    global mode
    
    dbname = in_dbname
    username = in_username
    password = in_password
    path = os.path.normcase("../gtfs_feeds/" + gtfs_filename)

    print "----------------------------------"
    print "Starting import_gtfs."
    # print dbname, username, password, path
    local_start=time.time()    
    insertData(path)
    spatiallyEnable()
    print "  Completed ",gtfs_filename, " in ", int(time.time()-local_start)," seconds"
    
    return True
