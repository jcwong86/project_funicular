import os, subprocess, zipfile, psycopg2

def go(dbhost, in_dbname, in_username, in_password, mode, outputType, agency):

    if mode == '0':
        mode_name = 'LTRail'
    elif mode == '1':
        mode_name = 'HVRail' 
    elif mode == '2':
        mode_name = 'CommRail'
    elif mode == '3':
        mode_name = 'Bus'
    elif mode == '4':
        mode_name = 'Ferry'
    elif mode == '5':
        mode_name = 'CableCar'
    elif mode == '6':
        mode_name = 'Gondola'
    elif mode == '7':
        mode_name = 'Funicular'
    else:
        mode_name = "unknown_mode"


    outPath = os.path.normcase('static/output/')
    outPrefix = agency + '_' + str(mode_name) + '_' + outputType

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

    check_table = """
        SELECT *
        FROM %s ;
    """ %db_table  

    try:
        cur = db.cursor()
        cur.execute("DROP VIEW IF EXISTS shp_out;")
        qry="CREATE VIEW shp_out AS SELECT * FROM %s WHERE route_type='%s';" %(db_table,mode)
        cur.execute(qry)
        db.commit()
        try:
            cur=db.cursor()
            cur.execute(check_table)
            non_empty = bool(cur.rowcount)
            db.commit()

            if non_empty:
                try:
                    subprocess.check_output([converter, '-f', os.path.join(outPath, outPrefix),
                        '-h', dbhost, '-u', in_username, '-P', in_password,
                        in_dbname, 'shp_out'])
                    archiveFiles(outPath, outPrefix, shpFileArray)
                    # modify to archive folder with name=uuid containing route and stop files!!!
                    cleanUp(outPath, shpFileArray)
                except:
                    print ' !Export failed main loop.'
            else:
                print " !The output table [%s]is empty. Will not generate shpfile." %db_table
        except Exception, f:
            print " !ERROR: Couldn't check rows in tables. Will not be able to export shpfile."
            print f
    except Exception, e:
        print " !ERROR: Output error. Will not be able to export shpfile."
        print e
        



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