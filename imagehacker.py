from PIL import Image as PImage
from PIL.ExifTags import TAGS, GPSTAGS
from colorama import Fore
from time import sleep
from include.converter import Converter
import piexif
import argparse
import logging
import rpycolors
import os
import textwrap
import sys

old_print = print
print = rpycolors.Console().print
clear = lambda:os.system('cls' if os.name == 'nt' else 'clear')

white   = Fore.WHITE
black   = Fore.BLACK
red     = Fore.RED
reset   = Fore.RESET
blue    = Fore.BLUE
cyan    = Fore.CYAN
yellow  = Fore.YELLOW
green   = Fore.GREEN
magenta = Fore.MAGENTA

desc = textwrap.dedent("""
                           ImageHacker - v1.0.1

            Github: https://github.com/ReddyyZ/ImageHacker
            By: ReddyyZ
    """)
def banner():
    clear()

    print(desc)
    print("[yellow][+][/yellow]Starting...")

    sleep(1)

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class Image(object):
    def __init__(self, filename:str):
        self.filename = filename
        
        logging.debug("Opening image")
        try:
            self.img  = PImage.open(self.filename)
            self.exif = piexif.load(self.img.info['exif'])
        except Exception as err:
            logging.critical("Error opening image: " + str(err))
            sys.exit(1)

    def get_geotagging(self,exif):
        '''
        Extract GPS Info and return
        '''

        logging.debug("Getting GPS Info")
        geotagging = {}
        for (idx, tag) in TAGS.items():
            if tag == 'GPSInfo':
                if idx not in exif:
                    raise ValueError("No EXIF geotagging found")

                for (key, val) in GPSTAGS.items():
                    if key in exif[idx]:
                        geotagging[val] = exif[idx][key]
        return geotagging


    def extract(self):
        '''
        Extracts exif data, decodes it, and print

        exif_ : Extracted EXIF data
        
        '''

        logging.info("Extracting image exif data")
        exif_ = self.img.getexif()

        ImageIFD    = piexif.ImageIFD
        ExifIFD     = piexif.ExifIFD

        camera      = {}
        camera_tags = [ImageIFD.Make,ImageIFD.Model,ExifIFD.Flash,ExifIFD.FlashEnergy,ExifIFD.FocalLengthIn35mmFilm,ExifIFD.FocalLength,ExifIFD.ExposureTime,ExifIFD.ISOSpeed,ExifIFD.SubjectDistance,ImageIFD.Software,ExifIFD.CameraElevationAngle,ExifIFD.CameraOwnerName,ExifIFD.ExposureMode,ExifIFD.ExposureIndex,ExifIFD.ExposureProgram,ExifIFD.ExposureBiasValue,ExifIFD.ExposureIndex]

        about       = {}
        about_tags  = [ImageIFD.Artist,ImageIFD.Copyright,ImageIFD.DateTime,ExifIFD.DateTimeDigitized,ExifIFD.DateTimeOriginal,ExifIFD.UserComment,ExifIFD.MakerNote]

        gps         = {}
        other       = {}

        try:
            for tag_id in exif_:
                tag = TAGS.get(tag_id, tag_id)
                data = exif_.get(tag_id)
                
                if isinstance(data, bytes):
                    try:
                        data = data.decode()
                    except Exception as err:
                        logging.error(f"Error decoding {tag}: "+str(err))
                        continue

                if tag_id in camera_tags or tag in camera_tags:
                    camera[tag] = data

                elif tag_id in about_tags or tag in about_tags:
                    about[tag] = data

                elif tag == "GPSInfo" or tag_id == "GPSInfo":
                    try:
                        gps_ifd = self.get_geotagging(exif_)
                        coordinates = Converter().get_coordinates(gps_ifd)

                        for i in gps_ifd:
                            gps[i] = gps_ifd[i]
                        GPS_ = True

                    except KeyError:
                        GPS_ = False
                        logging.error(f"Error getting GPS data: {red}GPSInfo blank!{reset}")

                    except Exception as err:
                        GPS_ = False
                        logging.error("Error getting GPS data: "+str(err))

                else:
                    other[tag] = data

            print(f"\n{green}[+]{reset}Camera:")
            for i in sorted(camera):
                print(f"    {i:26}: {camera[i]}")

            print(f"\n{green}[+]{reset}About:")
            for i in sorted(about):
                print(f"    {i:26}: {about[i]}")

            if GPS_:
                print(f"\n{green}[+]{reset}GPS:")
                for i in sorted(gps):
                    print(f"    {i:26}: {gps[i]}")
                for i in coordinates:
                    print(f"    {i:26}: {coordinates[i]}")

            print(f"\n{green}[+]{reset}Other:")
            for i in sorted(other):
                print(f"    {i:26}: {other[i]}")

        except Exception as err:
            logging.critical("Error extracting image data: "+str(err))

    def insert_gps(self,latitude_c,longitude_c,altitude):
        '''
        Converts coordinates to degress and return in
        gps_ifd format, that can be used to edit GPS information
        from an image.
        '''

        latitude, logintude, gps_ifd = Converter().coordinates_to_degress(latitude_c,longitude_c,altitude)
        return gps_ifd

    def insert_origin(self,author=None,date=None,Copyright=None,gps=None):
        logging.info("Inserting origin data")

        try:
            if date:
                self.exif["Exif"][piexif.ExifIFD.DateTimeOriginal]  = date
                self.exif["Exif"][piexif.ExifIFD.DateTimeDigitized] = date
                self.exif["0th"][piexif.ImageIFD.DateTime]          = date
        except Exception:
            logging.error("Error inserting date")

        try:
            if author:
                self.exif["0th"][piexif.ImageIFD.Artist] = author
        except Exception:
            logging.error("Error inserting author info")

        try:
            if Copyright:
                self.exif["0th"][piexif.ImageIFD.Copyright] = Copyright
        except Exception:
            logging.error("Error inserting copyright info")

        try:
            if gps:
                latitude, longitude, altitude = gps.split(' ')
                self.exif["GPS"] = self.insert_gps(latitude, longitude, altitude)
        except Exception:
            logging.error("Error inserting GPS data")

    def insert_camera(self,software=None,manufacturer=None,model=None):
        logging.info("Inserting camera details")

        try:
            if manufacturer:
                self.exif["0th"][piexif.ImageIFD.Make] = manufacturer

            if model:
                self.exif["0th"][piexif.ImageIFD.Model] = model

            if software:
                self.exif["0th"][piexif.ImageIFD.Software] = software
        except Exception:
            logging.error("Error inserting camera details")

    def save(self):
        logging.info("Saving file")
        try:
            exif_bytes = piexif.dump(self.exif)
            piexif.insert(exif_bytes, self.filename)
            logging.warn("File saved!")
        except Exception as err:
            logging.critical("Error saving file: " + str(err))
        

def parse_arguments():
    parser = argparse.ArgumentParser("ImageHacker",formatter_class=argparse.RawDescriptionHelpFormatter,
            # usage="python3 imagehacker.py --extract example.jpg",
            description=desc)

    parser.add_argument("filename")
    parser.add_argument("-e","--extract",help="Extract image exif data",action="count")
    parser.add_argument("-i","--insert",help="Change image exif data",action="count")
    parser.add_argument("-v","--verbose",help="Verbose",action="count")
    
    origin = parser.add_argument_group()
    origin.add_argument("--author",metavar="Name")
    origin.add_argument("--copyright")
    origin.add_argument("--date",help="Modify date (YYYY:MM:DD HH:MM:SS)", metavar='"2020:11:25 14:31:21"')
    origin.add_argument("--gps",help="Modify GPS Data (Latitude, Longitude, Altitude)", type=str, metavar='"37.090240 -95.712891 800"')

    camera = parser.add_argument_group()
    camera.add_argument("--software",metavar="Name")
    camera.add_argument("--manufacturer",metavar="Name")
    camera.add_argument("--model")

    args = parser.parse_args()

    return (args.filename, args.extract, args.insert, args.gps, args.date ,args.copyright, args.author, args.software, args.manufacturer, args.model, args.verbose)

if __name__ == "__main__":
    filename, extract, insert, gps, date, Copyright, author, software, manufacturer, model, verbose = parse_arguments()

    logging.addLevelName(logging.CRITICAL, f"{red}[!!]{reset}")
    logging.addLevelName(logging.ERROR, f"{red}[!]{reset}")
    logging.addLevelName(logging.INFO, f"{cyan}[*]{reset}")
    logging.addLevelName(logging.DEBUG, f"{magenta}[*]{reset}")
    logging.addLevelName(logging.WARN, f"{green}[+]{reset}")
    logging.basicConfig(format="%(levelname)s%(message)s", level=logging.DEBUG if verbose else logging.INFO)

    banner()

    if insert:
        img = Image(filename)

        if author or Copyright or date or gps:
            img.insert_origin(author=author,Copyright=Copyright,date=date,gps=gps)
        if software or manufacturer or model:
            img.insert_camera(software=software,manufacturer=manufacturer,model=model)
    
        img.save()

    if extract:
        Image(filename).extract()