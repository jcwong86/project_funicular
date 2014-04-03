def go(db):
    "Returns an array of the mode numbers stored as text that exist in each feed."

    check_modes = """
        SELECT DISTINCT route_type as mode_num
        FROM routes
        ORDER BY mode_num ASC;
    """ 

    try:
        cur = db.cursor()
        cur.execute(check_modes)
        data = cur.fetchall()
        modes=[]
        for i in data:
            modes.append(i[0])
        db.commit()
        print "  Checked modes. Will run for: " + str(modes)
        return modes
    except:
        print " !ERROR: Failed to check modes. Running all modes."
        modes=['0','1','2','3','4','5','6','7']
        return modes
        
