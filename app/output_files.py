import os, subprocess, zipfile, psycopg2

def go(dbhost, in_dbname, in_username, in_password, mode, outputType, agency):

    outPath = os.path.normcase('static/output/')
    outPrefix = agency + '_mode' + str(mode) + '_' + outputType

    shpFileArray = (
        outPrefix + '.dbf',
        outPrefix + '.prj',
        outPrefix + '.shp',
        outPrefix + '.shx')

    if outputType == 'stop':
        db_table = 'out_stop'
    else:
        db_table = 'out_route'

    if os.name == 'nt':
        converter = 'pgsql2shp.exe'
    else:
        converter = 'pgsql2shp'

    db=psycopg2.connect(host=dbhost, database=in_dbname, user=in_username, password=in_password)

    try:
        cur = db.cursor()
        cur.execute("DROP VIEW IF EXISTS shp_out;")
        qry="CREATE VIEW shp_out AS SELECT * FROM %s WHERE route_type='%s';" %(db_table,mode)
        print qry
        cur.execute(qry)
        db.commit()
        print "  Stop output view created for mode: " + mode
    except Exception, e:
        print " !ERROR: Output view error. Will not be able to export shpfile."
        print e
        

    try:
        subprocess.check_output([converter, '-f', os.path.join(outPath, outPrefix),
            '-h', dbhost, '-u', in_username, '-P', in_password,
            in_dbname, 'shp_out'])
        archiveFiles(outPath, outPrefix, shpFileArray)
        # modify to archive folder with name=uuid containing route and stop files!!!
        cleanUp(outPath, shpFileArray)
    except:
        print ' !Export failed main loop.'

    cur = db.cursor()
    cur.execute("DROP VIEW IF EXISTS shp_out;")
    db.commit()



def archiveFiles(outPath, outPrefix, shpFileArray):
    with zipfile.ZipFile(os.path.join(outPath, outPrefix) + '.zip', 'w') as f:
        for file in shpFileArray:
            f.write(os.path.join(outPath, file), file)
        print "  Successfully exported %s" %outPrefix

def cleanUp(outPath, shpFileArray):
    for file in shpFileArray:
        os.remove(os.path.join(outPath, file))