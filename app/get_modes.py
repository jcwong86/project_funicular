import csv, psycopg2

def go(db,u,p, agency):
    "Returns an array of the mode numbers stored as text that exist in each feed."

    check_modes = """
        SELECT DISTINCT route_type as mode_num
        FROM routes, agency
        WHERE agency.agency_id=routes.agency_id AND
            replace(agency_name,' ','_') = '%s'
        ORDER BY mode_num ASC;
    """ %agency

    try:
        con = psycopg2.connect(database=db, user=u, password=p)
        cur = con.cursor()
        cur.execute(check_modes)
        data = cur.fetchall()
        modes=[]
        for i in data:
            modes.append(i[0])
        con.commit()
        print "  Checked modes. Will run for: " + str(modes)
        return modes
    except:
        print " !ERROR: Failed to check modes. Running all modes."
        modes=['0','1','2','3']
        return modes
        
