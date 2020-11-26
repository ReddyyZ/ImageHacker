from fractions import Fraction
import piexif

class Converter(object):
    def __init__(self):
        pass

    def get_coordinates(self,geotags):
        if not geotags:
            raise ValueError("GPSInfo blank")

        lat = self.degress_to_decimal(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
        lon = self.degress_to_decimal(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

        return {"Latitude": lat,"Longitude": lon,"Altitude": geotags["GPSAltitude"] if "GPSAltitude" in geotags else "Blank"}
    
    def coordinates_to_degress(self, lat, lng, altitude):
        lat_deg = self.to_degress(lat, ["S", "N"])
        lng_deg = self.to_degress(lng, ["W", "E"])

        exiv_lat = (self.change_to_rational(lat_deg[0]), self.change_to_rational(lat_deg[1]), self.change_to_rational(lat_deg[2]))
        exiv_lng = (self.change_to_rational(lng_deg[0]), self.change_to_rational(lng_deg[1]), self.change_to_rational(lng_deg[2]))

        gps_ifd = {
            piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),
            piexif.GPSIFD.GPSAltitudeRef: 1,
            piexif.GPSIFD.GPSAltitude: self.change_to_rational(round(altitude)),
            piexif.GPSIFD.GPSLatitudeRef: lat_deg[3],
            piexif.GPSIFD.GPSLatitude: exiv_lat,
            piexif.GPSIFD.GPSLongitudeRef: lng_deg[3],
            piexif.GPSIFD.GPSLongitude: exiv_lng,
        }

        return (exiv_lat, exiv_lng, gps_ifd)

    def to_degress(self,value, loc):
        if value < 0:
            loc_value = loc[0]
        elif value > 0:
            loc_value = loc[1]
        else:
            loc_value = ""
        abs_value = abs(value)
        deg =  int(abs_value)
        t1 = (abs_value-deg)*60
        minutes = int(t1)
        seconds = round((t1 - minutes)* 60, 5)
        return (deg, minutes, seconds, loc_value)


    def change_to_rational(self,number):
        f = Fraction(str(number))
        return (f.numerator, f.denominator)

    def degress_to_decimal(self, dms, ref:list):
        # degrees = dms[0][0] / dms[0][1]
        # minutes = dms[1][0] / dms[1][1] / 60.0
        # seconds = dms[2][0] / dms[2][1] / 3600.0

        degrees = dms[0]
        minutes = dms[1] / 60.0
        seconds = dms[2] / 3600.0

        if ref in ['S', 'W']:
            degrees = -degrees
            minutes = -minutes
            seconds = -seconds

        return round(degrees + minutes + seconds, 5)