#!/usr/bin/env python3

from sattracker import Tracker
import time

tle =  { "name": "AO-73", "tle1": "1 39444U 13066AE  23098.85474643  .00005635  00000-0  63454-3 0  9997", "tle2": "2 39444  97.6663  65.5012 0055001 139.7657 220.7649 14.85915619505932"}
qth = ("50.0", "8.0", "500")

tracker = Tracker(satellite=tle, groundstation=qth)


print(tracker.next_pass_table(30))
