INFO = {
        "DT": "10min",
        "KEY_STATION": "station_id",
        "VARS": {
            "t":  { "info":"temperature",    "um": "C"},
            "h":  { "info":"humidity",       "um": "."},
            "p":  { "info":"precipitation",  "um": "mm/dt"},
            "ws": {	"info":"wind speed",     "um": "m/s"},
            "wd": { "info":"wind direction", "um": "deg"}
        }
    }

DEFAULT = {
        "VARS_CHECK": ["t", "h", "p", "ws"],
        "VARS_CONS": ["ws", "wd"],
        "RANGES": {
        	"t":  [-30, 50],
        	"h":  [0, 100],
        	"p":  [0, 400],
        	"ws": [0, 75],
        	"wd": [0, 360]
            },
    	"STEPS": {
        	"t":  2,
        	"h":  10
    	},
        "WINDOW":3,
    	"VARIATIONS": {
        	"t":  [0.01, -30, 50],
        	"h":  [0.01, 0, 95],
        	"ws": [0.01, 0, 75]
    	}
    }
