import gdal
import scipy
import scipy.ndimage
from scipy.interpolate import griddata
import numpy as np
import ogr
import matplotlib.pyplot as plt
import os
import geopandas as gpd

def outfileName(infile,outname):
    dirname = os.path.dirname(infile)
    basename = os.path.basename(infile)
    final = dirname+'/'+ basename[:-4]+outname
    return final


def makeTreeTif(infile):
#Input a lidar data tif file and output a binary raster layer with tress as 1 and all else as 0
    outfile = outfileName(infile,"_treetif.tif")
    print outfile
    ds = gdal.Open(infile)
    #Assign variables to information needed tp create output
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    rows = arr.shape[0]
    cols = arr.shape[1]
    geotrans = ds.GetGeoTransform()
    proj = ds.GetProjection()
    
    #Create an array of the input raster
    myarray = np.array(band.ReadAsArray())
    #Create a binary array where buildings(>=50) = 1
    buildingsBinary = np.where(myarray>=50, 1, 0)
    #Dilate buildings binary array
    buildingsBinary_dilation = scipy.ndimage.morphology.binary_dilation(buildingsBinary)
    #Create a binary array were ground(<=) = 1
    groundBinary = np.where(myarray<=5, 1, 0)
    #Add ground binary and building binary to create non tree binary array 
    nonTreeBinary = np.add(buildingsBinary_dilation,groundBinary)
    #Dilate non tree binary array
    nonTreeBinary_dilation = scipy.ndimage.morphology.binary_dilation(nonTreeBinary)
    #Close gaps in dilated non tree binary array to remove isolated 1 values
    nonTreeBinary_dilation_opening =scipy.ndimage.binary_opening(nonTreeBinary_dilation, structure=np.ones((6,6))).astype(np.int)
    #Create binary array where trees = 1
    treeBinary = np.where(nonTreeBinary_dilation_opening==1, 0, 1)
    #Dilate  binary tree array
    treeBinary_dilation = scipy.ndimage.morphology.binary_dilation(treeBinary)
    #Close gaps in dilated tree binary array to remove isolated 1 values
    treeBinary_dilation_opening = scipy.ndimage.binary_opening(treeBinary_dilation, structure=np.ones((5,5))).astype(np.int)
    
    #Assign variables for output file info, name, filetype
    dstfile = outfile
    driver = gdal.GetDriverByName('GTiff')
    #Create new tiff file, write array to tiff file
    dataset = driver.Create(dstfile,cols,rows,1,gdal.GDT_Float32)
    dataset.GetRasterBand(1).WriteArray(treeBinary_dilation_opening)
    #Set spatial reference and projection of output file to same as input file
    dataset.SetGeoTransform(geotrans)
    dataset.SetProjection(proj)
    dataset.FlushCache()
    dataset = None
    return outfile
    

def makePolygon(infile):
    outfile = outfileName(infile,"_treeshp.shp")
    print outfile
    #input tif file
    ds = gdal.Open(infile)
    tree_band = ds.GetRasterBand(1)
    polylayer = "PolygonTest"
    drv = ogr.GetDriverByName("ESRI Shapefile")
    dst_ds = drv.CreateDataSource(outfile)
    dst_layer = dst_ds.CreateLayer(polylayer, srs=None)
    #Create New Field in output shapefile to assign value to
    newField = ogr.FieldDefn('Value', ogr.OFTInteger)
    dst_layer.CreateField(newField)
    gdal.Polygonize(tree_band, None, dst_layer, 0, [], callback=None)
    return outfile


def dissolvePolygon(infile):
    outfile = outfileName(infile,"_treediss.shp")
    tree_layer = gpd.read_file(infile)
    tree_subset = tree_layer[['Shape','Value']]
    #dissolve polygons by Value
    dissolved_tree_subset = tree_subset.dissolve(by='Value')
    dissolved_tree_subset.plot()
    head = dissolved_tree_subset.head()
    dissolved_tree_subset.to_file(outfile)
    return outfile
    
def makeTreeLayerSHP(intiff):
    infile = makeTreeTif(intiff)
    inshp = makePolygon(infile)
    outshp = dissolvePolygon(inshp)


    
makeTreeLayerSHP('H:/Lidar/NH/213_range_z.tif')
  
