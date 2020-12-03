
from math import radians, sin, cos, asin, sqrt

baseLong = 23.722064
baseLat = 90.405298

radius = 6341

pointLong = 23.7279233
pointLat = 90.3972157

baseLong = radians(baseLong)
baseLat = radians(baseLat)

pointLong = radians(pointLong)
pointLat = radians(pointLat)

# dLong = baseLong - pointLong
# dLat = baseLat - pointLat

dLat = 0.00079
dLong = 0.00079

a = sin(dLat/2)**2 + cos(baseLat) * cos(pointLat) * sin(dLong/2)**2
c = 2*asin(sqrt(a))

distance = c*radius

print("dLat: ", dLat)
print("dLong: ", dLong)
print("distance: ", distance)
print(" -              - ")
