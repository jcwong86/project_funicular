import psycopg2

def check_calendar_exists(db,u,p):
    "Checks if there is a calendar table associated with this feed. Returns True if table exists."
    print "Checking calendar files."
    qry_calendar = """
        SELECT *
        FROM information_schema.tables
        WHERE table_name='calendar';
    """


    try:
        con = psycopg2.connect(database=db, user=u, password=p)
        cur = con.cursor()
        cur.execute(qry_calendar)
        out = bool(cur.rowcount)
        con.commit()

        if out:
            con = psycopg2.connect(database=db, user=u, password=p)
            cur = con.cursor()
            cur.execute("SELECT sum(monday::int)::int FROM calendar")
            sum_mon=cur.fetchone()
            if sum_mon[0]<1:
                return False            
            con.commit()
        return out
    except:
        print " !ERROR: Cannot determine if calendar exists."
        return False

def check_calendar_dates_exists(db,u,p):
    "Checks if there is a calendar_dates table associated with this feed. Returns True if table exists."

    qry_calendar = """
        SELECT *
        FROM information_schema.tables
        WHERE table_name='calendar_dates';
    """


    try:
        con = psycopg2.connect(database=db, user=u, password=p)
        cur = con.cursor()
        cur.execute(qry_calendar)
        out = bool(cur.rowcount)
        con.commit()
        return out
    except:
        print " !ERROR: Cannot determine if calendar_dates exists."
        return False

qry_dates_svc_id_calendar_dates = """
     -- For those that only use calendar_dates
    CREATE TABLE dates_service_ids AS
    SELECT 	service_id, 
            calendar_dates.date as dategen
    FROM 	calendar_dates, (
            SELECT to_char(to_date('20100101','YYYYMMDD')+s.a,'YYYYMMDD') as dategen
            FROM generate_series(0,2000,1) as s(a)) b
    WHERE 	calendar_dates.date=b.dategen AND
            exception_type='1'
    """

qry_dates_svc_id_calendar_and_calendar_dates = """
     -- For those that use calendar and calendar_dates properly
    CREATE TABLE dates_service_ids AS
        SELECT 	dategen::numeric, 
		service_id
        FROM(   SELECT 	dategen, 
			extract(dow FROM to_date(dategen,'YYYYMMDD')) as dategen_dow
                FROM (
			SELECT dategen
			FROM(	SELECT	to_char(to_date('20100101','YYYYMMDD')+s.a,'YYYYMMDD') AS dategen
				FROM 	generate_series(0,2000,1) as s(a)) b
				ORDER BY dategen) yr_dates,
				(SELECT min(to_date(start_date,'YYYYMMDD')) AS svc_start
				FROM	calendar) as min,
				(SELECT max(to_date(end_date,'YYYYMMDD')) AS svc_end
				FROM	calendar) as max				
			WHERE 	to_date(dategen,'YYYYMMDD') >= min.svc_start AND
				to_date(dategen,'YYYYMMDD') <= max.svc_end) d,
                (
                SELECT service_id, start_date, end_date, dow
                FROM	(
                        SELECT 	calendar.*, a.b as dow 
                        FROM calendar, generate_series(0,6) as a(b)) c
                WHERE	(sunday='1' AND dow=0) OR
                        (monday='1' AND dow=1) OR
                        (tuesday='1' AND dow=2) OR
                        (wednesday='1' AND dow=3) OR
                        (thursday='1' AND dow=4) OR
                        (friday='1' AND dow=5) OR
                        (saturday='1' AND dow=6)
                ORDER BY service_id, dow) calendar_transposed
        WHERE 	start_date<=dategen AND
                end_date>=dategen AND
                dategen_dow=dow
	EXCEPT (SELECT 	to_char(to_date(calendar_dates.date,'YYYYMMDD'),'YYYYMMDD')::numeric AS dategen, 
			calendar_dates.service_id
		FROM calendar_dates
		WHERE exception_type='2')
	UNION(	SELECT 	to_char(to_date(calendar_dates.date,'YYYYMMDD'),'YYYYMMDD')::numeric AS dategen, 
			calendar_dates.service_id
		FROM calendar_dates
		WHERE exception_type='1')
	ORDER BY dategen, service_id;
"""


qry_dates_svc_id_calendar = """
     -- For those that use calendar and calendar_dates properly
    CREATE TABLE dates_service_ids AS
        SELECT 	dategen::numeric, 
		service_id
        FROM(   SELECT 	dategen, 
			extract(dow FROM to_date(dategen,'YYYYMMDD')) as dategen_dow
                FROM (
			SELECT dategen
			FROM(	SELECT	to_char(to_date('20120101','YYYYMMDD')+s.a,'YYYYMMDD') AS dategen
				FROM 	generate_series(0,1200,1) as s(a)) b
				ORDER BY dategen) yr_dates,
				(SELECT min(to_date(start_date,'YYYYMMDD')) AS svc_start
				FROM	calendar) as min,
				(SELECT max(to_date(end_date,'YYYYMMDD')) AS svc_end
				FROM	calendar) as max				
			WHERE 	to_date(dategen,'YYYYMMDD') >= min.svc_start AND
				to_date(dategen,'YYYYMMDD') <= max.svc_end) d,
                (
                SELECT service_id, start_date, end_date, dow
                FROM	(
                        SELECT 	calendar.*, a.b as dow 
                        FROM calendar, generate_series(0,6) as a(b)) c
                WHERE	(sunday='1' AND dow=0) OR
                        (monday='1' AND dow=1) OR
                        (tuesday='1' AND dow=2) OR
                        (wednesday='1' AND dow=3) OR
                        (thursday='1' AND dow=4) OR
                        (friday='1' AND dow=5) OR
                        (saturday='1' AND dow=6)
                ORDER BY service_id, dow) calendar_transposed
        WHERE 	start_date<=dategen AND
                end_date>=dategen AND
                dategen_dow=dow
	ORDER BY dategen, service_id;
"""

qry_drop_tables = "DROP TABLE IF EXISTS dates_service_ids;"

def go(db,u,p):
    "Creates service_id and date table based on appropriate use of calendar and calendar_date files."

    calendar = check_calendar_exists(db,u,p)
    calendar_dates = check_calendar_dates_exists(db,u,p)
    print "  Calendar:" + str(calendar)
    print "  Calendar_date:" + str(calendar_dates)

    if calendar and calendar_dates:
        try:
            con = psycopg2.connect(database=db, user=u, password=p)
            cur = con.cursor()
            print "  Executing qry_dates_svc_id_calendar_and_calendar_dates"
            cur.execute(qry_drop_tables)
            cur.execute(qry_dates_svc_id_calendar_and_calendar_dates)
            con.commit()
        except:
            print " !ERROR: Cannot calculate dates and service ids. Only calendar table exists."
     
    elif calendar and not calendar_dates:
        try:
            con = psycopg2.connect(database=db, user=u, password=p)
            cur = con.cursor()
            print "  Executing qry_dates_svc_id_calendar"
            cur.execute(qry_drop_tables)
            cur.execute(qry_dates_svc_id_calendar)
            con.commit()
        except:
            print " !ERROR: Cannot calculate dates and service ids. Only calendar table exists."
            
    elif not calendar and calendar_dates:
        try:
            con = psycopg2.connect(database=db, user=u, password=p)
            cur = con.cursor()
            cur.execute(qry_drop_tables)            
            print "  Executing qry_dates_svc_id_calendar_dates"
            cur.execute(qry_dates_svc_id_calendar_dates)
            con.commit()
        except:
            print " !ERROR: Cannot calculate dates and service ids. Only calendar table exists."
    
     

        
