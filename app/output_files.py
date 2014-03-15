import os, subprocess, zipfile

def go(dbhost, in_dbname, in_username, in_password, agency, mode, outputType):

    outPath = os.path.normcase('static/output/')
    outPrefix = agency + '_mode' + str(mode) + '_' + outputType

    shpFileArray = (
        outPrefix + '.dbf',
        outPrefix + '.prj',
        outPrefix + '.shp',
        outPrefix + '.shx')

    if outputType == 'stop':
        db_table = 'out_stop'
    # else:
        # db_table = 'out_route' -- ADD ROUTE OPTION!!!

    if os.name == 'nt':
        converter = 'pgsql2shp.exe'
    else:
        converter = 'pgsql2shp'

    try:
        subprocess.check_output([converter, '-f', os.path.join(outPath, outPrefix),
            '-h', dbhost, '-u', in_username, '-P', in_password,
            in_dbname, db_table])
        archiveFiles(outPath, outPrefix, shpFileArray)
        # modify to archive folder with name=uuid containing route and stop files!!!
        cleanUp(outPath, shpFileArray)
        print 'Export complete!'
    except:
        print 'Export failed!'

def archiveFiles(outPath, outPrefix, shpFileArray):
    with zipfile.ZipFile(os.path.join(outPath, outPrefix) + '.zip', 'w') as f:
        for file in shpFileArray:
            f.write(os.path.join(outPath, file), file)

def cleanUp(outPath, shpFileArray):
    for file in shpFileArray:
        os.remove(os.path.join(outPath, file))