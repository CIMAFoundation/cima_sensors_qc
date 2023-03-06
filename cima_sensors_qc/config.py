################################################################################
# Copyright 2023, Nicolò Perello, Mirko D'Andrea
################################################################################
#This file is part of cima_sensors_qc.
#
#cima_sensors_qc is free software: you can redistribute it and/or modify it under
#the terms of the GNU General Public License as published by the
#Free Software Foundation, either version 3 of the License,
#or (at your option) any later version.
#
#cima_sensors_qc is distributed in the hope that it will be useful, but WITHOUT
#ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License along with
#cima_sensors_qc. If not, see <https://www.gnu.org/licenses/>.
################################################################################

DEFAULT = {
        "VARS_CHECK": ["t", "h", "p", "ws"],
        "RANGES": {
            "t":  [-30, 50],
            "h":  [0, 100],
            "p":  [0, 400],
            "ws": [0, 75],
            },
        "STEPS": {
            "t":  2,
            "h":  10
        },
        "WINDOW": 12,
        "VARIATIONS": {
            "t":  [0.01, -30, 50],
            "h":  [0.01, 0, 100],
            "ws": [0.01, 0, 75]
        }
    }
