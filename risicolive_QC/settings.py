INFO = {
        "DT": "10min",
        "VARS": {
            "t":  { "info":"temperature",    "um": "C"},
            "h":  { "info":"humidity",       "um": "."},
            "p":  { "info":"precipitation",  "um": "mm/dt"},
            "ws": {	"info":"wind speed",     "um": "m/s"},
        }
    }

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
        "WINDOW":12,
    	"VARIATIONS": {
        	"t":  [0.01, -30, 50],
        	"h":  [0.01, 0, 95],
        	"ws": [0.01, 0, 75]
    	}
    }
