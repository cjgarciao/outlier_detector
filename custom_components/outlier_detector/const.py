DOMAIN = "outlier_detector"

PLATFORMS = [
    "binary_sensor",
    "sensor",
]

CONF_NAME = "name"
CONF_ENTITIES = "entities"
CONF_METHOD = "method"
CONF_THRESHOLD = "threshold"
CONF_HYSTERESIS = "hysteresis"


METHOD_ABSOLUTE = "absolute"
METHOD_PERCENTAGE = "percentage"
METHOD_SIGMA = "sigma"
METHOD_MAD = "mad"
METHOD_IMBALANCE_PERCENT = "imbalance_percent"


METHODS = [
    METHOD_ABSOLUTE,
    METHOD_PERCENTAGE,
    METHOD_SIGMA,
    METHOD_MAD,
    METHOD_IMBALANCE_PERCENT,
]

DEFAULT_NAME = "Outlier Detector"

#
# Recommended defaults
#
# absolute: engineering units
# percentage: %
# sigma: standard deviations
# mad: modified z-score
#

DEFAULT_METHOD = METHOD_MAD

DEFAULT_THRESHOLDS = {
    METHOD_ABSOLUTE: 3.0,
    METHOD_PERCENTAGE: 20.0,
    METHOD_SIGMA: 2.0,
    METHOD_MAD: 3.5,
    METHOD_IMBALANCE_PERCENT: 20.0,
}

DEFAULT_THRESHOLD = DEFAULT_THRESHOLDS[
    DEFAULT_METHOD
]

DEFAULT_HYSTERESIS = 0.0

METHOD_OPTIONS = [
    {
        "value": METHOD_MAD,
        "label": "MAD"
    },
    {
        "value": METHOD_SIGMA,
        "label": "Sigma"
    },
    {
        "value": METHOD_PERCENTAGE,
        "label": "Percentage"
    },
    {
        "value": METHOD_ABSOLUTE,
        "label": "Absolute"
    },
    {
        "value": METHOD_IMBALANCE_PERCENT,
        "label": "Room Imbalance Percent",
    },
]