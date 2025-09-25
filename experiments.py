#!/usr/bin/env python3
"""
Experimental comparison of planning algorithms
"""

import time
import json
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from environment import GridEnvironment
from planners.uninformed import BFSPlanner, UniformCostPlanner
from planners.informed import AStarPlanner
from planners.local_search import HillCl