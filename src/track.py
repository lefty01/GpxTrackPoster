# Copyright 2016-2017 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

import datetime
import gpxpy
import json
import os


class Track:
    def __init__(self):
        self.file_names = []
        self.polylines = []
        self.bounds = {}
        self.start_time = None
        self.end_time = None
        self.length = 0
        self.special = False

    def load_gpx(self, file_name):
        self.file_names = [os.path.basename(file_name)]
        with open(file_name, 'r') as file:
            gpx = gpxpy.parse(file)
            tb = gpx.get_time_bounds()
            b = gpx.get_bounds()
            self.start_time = tb[0]
            self.end_time = tb[1]
            self.bounds['min_lat'] = b.min_latitude
            self.bounds['max_lat'] = b.max_latitude
            self.bounds['min_lon'] = b.min_longitude
            self.bounds['max_lon'] = b.max_longitude
            if self.start_time is None:
                raise Exception("Track has no start time.")
            if self.end_time is None:
                raise Exception("Track has no end time.")
            self.length = gpx.length_2d()
            if self.length == 0:
                raise Exception("Track is empty.")
            gpx.simplify()
            for t in gpx.tracks:
                for s in t.segments:
                    line = [(p.latitude, p.longitude) for p in s.points]
                    self.polylines.append(line)

    def append(self, other):
        self.end_time = other.end_time
        self.polylines.extend(other.polylines)
        self.length += other.length
        self.file_names.extend(other.file_names)
        self.special = self.special or other.special

    # FIXME: load/store track bounds in cache

    def load_cache(self, cache_file_name):
        with open(cache_file_name) as data_file:
            data = json.load(data_file)
            self.start_time = datetime.datetime.strptime(data["start"], "%Y-%m-%d %H:%M:%S")
            self.end_time = datetime.datetime.strptime(data["end"], "%Y-%m-%d %H:%M:%S")
            self.length = float(data["length"])
            self.polylines = []
            for data_line in data["segments"]:
                self.polylines.append([(float(d["lat"]), float(d["lng"])) for d in data_line])

    def store_cache(self, cache_file_name):
        dir_name = os.path.dirname(cache_file_name)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        with open(cache_file_name, 'w') as json_file:
            lines_data = []
            for line in self.polylines:
                lines_data.append([{"lat": lat, "lng": lng} for (lat, lng) in line])
            json.dump({"start": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                       "end": self.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                       "length": self.length,
                       "min_lat": self.bounds['min_lat'],
                       "max_lat": self.bounds['max_lat'],
                       "min_lon": self.bounds['min_lon'],
                       "max_lon": self.bounds['max_lon'],
                       "segments": lines_data},
                      json_file)
