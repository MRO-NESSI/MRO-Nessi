from math import sin, cos, tan, atan, degrees, radians 

from indiclient import indiclient

class Telescope(object):
    """Class that will represent a telescope."""

    def __init__(self, host, port):
        """
        Arguments:
            host (str) -- indiclient host
            port (int) -- indiclient port
        """
        self._indi = indiclient(host, port)

    def __del__(self):
        self._indi.quit()

    @property
    def ra(self):
        ra = self._indi.get_element(
            "Telescope", "Pointing", "RA2K").get_float()
        
        return ra
    
    @ra.setter
    def ra(self, ra):
        self._indi.set_and_send_float(
            "Telescope", "Pointing", "RA2K", ra)

    @property
    def dec(self):
        dec = self._indi.get_element(
            "Telescope", "Pointing", "Dec2K").get_float()
        
        return dec

    @dec.setter
    def dec(self, dec):
        self._indi.set_and_send_float(
            "Telescope", "Pointing", "Dec2K", dec)

    @property
    def airmass(self):
        am = self._indi.get_element(
            "Telescope", "Pointing", "AM").get_float()
        
        return am

    @property
    def altitude(self):
        alt = self._indi.get_element(
            "Telescope", "Pointing", "Alt").get_float()
        
        return alt

    @property
    def azimuth(self):
        az = self._indi.get_element(
            "Telescope", "Pointing", "Az").get_float()
        
        return az

    @property
    def focus(self):
        focus = self._indi.get_element(
            "Telescope", "Pointing", "Focus").get_float()
        
        return focus

    @property
    def parallactic_angle(self):
        pa = self._indi.get_element(
            "Telescope", "Pointing", "PA").get_float()
        
        return pa

    @property
    def parallactic_angle_manual(self):
        #Need HA
        #Need Dec
        #Need lat
        #All should be in radians, to use math.py
        #teneta = cos(latrad)*sin(HArad) / (sin(latrad)*cos(decrad) - cos(latrad)*sin(decrad)*cos(HArad))
        #return atan(teneta)
        dec_rad = radians(self.dec)
        ha_rad  = radians(self.ha)
        lat_rad = radians(self.latitude)
        teneta  = cos(lat_rad) * sin(ha_rad) / (
            sin(lat_rad) * cos(dec_rad) - cos(lat_rad) * sin(dec_rad) * cos(ha_rad)
            )
        return degrees(atan(teneta))
        
    @property
    def ha(self):
        '''get hour angle.'''
        ha_degree = self._indi.get_element(
            "Telescope", "Pointing", "HA").get_float()
        
        return ha_degree

    @property
    def latitude(self):
        #A constant taken from MRO's wiki page
        return 33.976667

    @property
    def julian_date(self):
        jul = self._indi.get_element(
            "Telescope", "Pointing", "JD").get_float()
        
        return jul

    @property
    def wind_speed(self):
        ws = self._indi.get_element(
            "Environment", "Now", "WindSpeed").get_text()
        
        return ws

    @property
    def wind_gust(self):
        wg = self._indi.get_element(
            "Environment", "Now", "WindGust").get_text()
        
        return wg

    @property
    def wind_direction(self):
        wd = self._indi.get_element(
            "Environment", "Now", "WindDir").get_text()
        
        return wd

