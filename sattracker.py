
import sys
import time
import datetime
from math import *

import ephem

class Tracker():

    def __init__(self, satellite, groundstation=("59.4000", "24.8170", "0")):
        self.groundstation = ephem.Observer()
        self.groundstation.lat = groundstation[0]
        self.groundstation.lon = groundstation[1]
        self.groundstation.elevation = int(groundstation[2])

        self.satellite = ephem.readtle(satellite["name"], satellite["tle1"], satellite["tle2"])

    def set_epoch(self, epoch=time.time()):
        ''' sets epoch when parameters are observed '''

        self.epoch = epoch
        self.groundstation.date = datetime.datetime.utcfromtimestamp(epoch)
        self.satellite.compute(self.groundstation)

    def azimuth(self):
        ''' returns satellite azimuth in degrees '''
        return degrees(self.satellite.az)

    def elevation(self):
        ''' returns satellite elevation in degrees '''
        return degrees(self.satellite.alt)

    def latitude(self):
        ''' returns satellite latitude in degrees '''
        return degrees(self.satellite.sublat)

    def longitude(self):
        ''' returns satellite longitude in degrees '''
        return degrees(self.satellite.sublong)

    def range(self):
        ''' returns satellite range in meters '''
        return self.satellite.range

    def doppler(self, frequency_hz=437505000):
        ''' returns doppler shift in hertz '''
        return -self.satellite.range_velocity / 299792458. * frequency_hz

    def ecef_coordinates(self):
        ''' returns satellite earth centered cartesian coordinates
            https://en.wikipedia.org/wiki/ECEF
        '''
        x, y, z = self._aer2ecef(self.azimuth(), self.elevation(), self.range(), float(self.groundstation.lat), float(self.groundstation.lon), self.groundstation.elevation)
        return x, y, z

    def _aer2ecef(self, azimuthDeg, elevationDeg, slantRange, obs_lat, obs_long, obs_alt):

        #site ecef in meters
        sitex, sitey, sitez = llh2ecef(obs_lat,obs_long,obs_alt)

        #some needed calculations
        slat = sin(radians(obs_lat))
        slon = sin(radians(obs_long))
        clat = cos(radians(obs_lat))
        clon = cos(radians(obs_long))

        azRad = radians(azimuthDeg)
        elRad = radians(elevationDeg)

        # az,el,range to sez convertion
        south  = -slantRange * cos(elRad) * cos(azRad)
        east   =  slantRange * cos(elRad) * sin(azRad)
        zenith =  slantRange * sin(elRad)

        x = ( slat * clon * south) + (-slon * east) + (clat * clon * zenith) + sitex
        y = ( slat * slon * south) + ( clon * east) + (clat * slon * zenith) + sitey
        z = (-clat *        south) + ( slat * zenith) + sitez

        return x, y, z
        
    def next_pass_table(self, num_points = 10):
        self.set_epoch()
        next_pass_data = self.groundstation.next_pass(self.satellite)
        
        rise_timestamp = ephem._convert_to_seconds_and_microseconds(next_pass_data[0])[0]
        set_timestamp = ephem._convert_to_seconds_and_microseconds(next_pass_data[4])[0]
        duration = set_timestamp -rise_timestamp
        time_step = int(duration/num_points)
        
        azimuth = []
        elevation = []
        
        for i in range(num_points):
            self.groundstation.date = datetime.datetime.utcfromtimestamp(ephem._convert_to_seconds_and_microseconds(next_pass_data[0])[0] + i*time_step)
            self.satellite.compute(self.groundstation)
            azimuth.append(self.azimuth())
            elevation.append(self.elevation())

        self.set_epoch()
        self.satellite.compute(self.groundstation)

        return azimuth, elevation
		
