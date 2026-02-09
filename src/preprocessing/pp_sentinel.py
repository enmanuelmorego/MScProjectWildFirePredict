import ee
'''
for each image downloaded
'''
# Arguments passed in function
date = '2019-01-17'
grid_id = 26
img = 'COPERNICUS/S2_SR_HARMONIZED/20190117T111409_20190117T111410_T30UVB'

img_1 = ee.ImageCollection(img)
