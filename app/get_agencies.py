def go(db):
    "Returns an array of the agencies stored as text that exist in each feed."

    check_agencies = """
        SELECT DISTINCT replace(agency_name, ' ','_') as agency_name
        FROM agency;
        """

    try:
        cur = db.cursor()
        cur.execute(check_agencies)
        data = cur.fetchall()
        agencies=[]
        for i in data:
            agencies.append(i[0])
        db.commit()
        print "  Checked agencies. Will run for: " + str(agencies)
        return agencies
    except Exception, e:
        print " !ERROR: Failed to check agencies. May cause errors."
        print e
        return None
        
