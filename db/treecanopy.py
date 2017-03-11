import gdal
import os
import numpy as np
import matplotlib.pyplot as plt
import ogr
gdal.AllRegister()


def maketreetif(inputfile,outputfile):
    #input tif file
    ds = gdal.Open(inputfile)
    
    #Assign varibles for input file info (bands, columns, rows, spatial reference, projection) 
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    rows = arr.shape[0]
    cols = arr.shape[1]
    geotrans = ds.GetGeoTransform()
    proj = ds.GetProjection()
    
    #Create an array
    myarray = np.array(band.ReadAsArray())
    
    #Create a binary array where values >=10 are assigned 1 and others are assigned 0
    binary = np.where(myarray>=10, 1, 0)
    
    #Select values with elevation >=10 by multiplying orginal array by binary array
    clip= myarray*binary
    
    #Assign variables for output file info, name, filetype
    dstfile = outputfile
    driver = gdal.GetDriverByName('GTiff')
    
    #Create new tiff file, write array to tiff file
    dataset = driver.Create(dstfile,cols,rows,1,gdal.GDT_Float32)
    dataset.GetRasterBand(1).WriteArray(binary)
    
    #Set spatial reference and projection of output file to same as input file
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None

 
maketreetif("H:/Lidar/20150429_QL1_18TXM690687_NE_range_z_float_3857.tif","H:/Lidar/lasttest.tiff")

#Fill gaps
#finband = gdal.Open(dstfile).GetRasterBand(1)
#gdal.FillNodata(finband,None,20, 0)


#Add Field conatining binary value/ or value
#newField = ogr.FieldDefn('MYFLD', ogr.OFTInteger)
#newoutlayer.CreateField(newField)



def makepolygon(inputfile,outputfile):
    #input tif file
    ds = gdal.Open(inputfile)
    tree_band = ds.GetRasterBand(1)
    polylayer = "PolygonTest"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(outputfile)
    dst_layer = dst_ds.CreateLayer(polylayer, srs=None)
    gdal.Polygonize(tree_band, None, dst_layer, -1, [], callback=None)

makepolygon('H:/Lidar/TestRastClipfunc.tiff','H:/Lidar/LastTestshp.shp')