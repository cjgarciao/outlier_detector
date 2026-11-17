from __future__ import annotations

import logging

from statistics import mean
from statistics import median
from statistics import stdev

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    CONF_ENTITIES,
    CONF_METHOD,
    CONF_THRESHOLD,
    CONF_HYSTERESIS,
    METHOD_ABSOLUTE,
    METHOD_PERCENTAGE,
    METHOD_SIGMA,
    METHOD_MAD,
    METHOD_IMBALANCE_PERCENT,
)

_LOGGER = logging.getLogger(__name__)


def calculate_mad(
    values: list[float],
) -> tuple[float, float]:
    """
    Returns:
        median,
        MAD
    """

    median_value = median(values)

    deviations = [
        abs(v - median_value)
        for v in values
    ]

    mad = median(deviations)

    return median_value, mad


class OutlierDetectorCoordinator(
    DataUpdateCoordinator,
):
    """Shared coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config: dict,
    ) -> None:

        super().__init__(
            hass,
            logger=_LOGGER,
            name="outlier_detector",
        )

        self._config = config
        self._previous_state = False

    async def _async_update_data(self) -> dict:

        entities = self._config[CONF_ENTITIES]

        method = self._config[CONF_METHOD]

        threshold = float(
            self._config[CONF_THRESHOLD]
        )
        hysteresis = float(
            self._config.get(
                CONF_HYSTERESIS,
                0.0,
            )
        )

        samples = []
        units = set()

        #
        # Collect valid values
        #

        for entity_id in entities:

            state = self.hass.states.get(
                entity_id
            )

            if state is None:
                continue

            if state.state in (
                "unknown",
                "unavailable",
                "",
                None,
            ):
                continue

            try:
                value = float(state.state)
            except (
                ValueError,
                TypeError,
            ):
                continue

            unit = state.attributes.get(
                "unit_of_measurement"
            )

            if unit:
                units.add(unit)

            samples.append(
                {
                    "entity_id": entity_id,
                    "value": value,
                    "unit": unit,
                }
            )

        #
        # Need at least two values
        #

        if len(samples) < 2:

            return {
                "valid": False,
                "reason": "not_enough_values",
                "state": False,
                "sample_size": len(samples),
                "outliers": [],
            }

        #
        # All units must match
        #

        if len(units) > 1:

            return {
                "valid": False,
                "reason": "mixed_units",
                "state": False,
                "sample_size": len(samples),
                "units": sorted(list(units)),
                "outliers": [],
            }

        values = [
            sample["value"]
            for sample in samples
        ]

        avg = mean(values)

        median_value, mad = (
            calculate_mad(values)
        )

        try:
            stddev = (
                stdev(values)
                if len(values) >= 2
                else 0.0
            )
        except Exception:
            stddev = 0.0

        imbalance = (
            max(values) - min(values)
        )

        #imbalance_percent = imbalance/ avg * 100
        imbalance_percent = (
                imbalance / abs(avg) * 100
                if avg != 0
                else 0.0
        )
        detected_outliers = []

        max_score = 0.0
        #
        # ABSOLUTE
        #

        if method == METHOD_ABSOLUTE:

            for sample in samples:

                deviation = abs(
                    sample["value"]
                    - avg
                )

                max_score = max(
                    max_score,
                    deviation,
                )
                
                if deviation > threshold:

                    detected_outliers.append(
                        {
                            "entity_id":
                                sample[
                                    "entity_id"
                                ],
                            "value":
                                sample[
                                    "value"
                                ],
                            "deviation":
                                round(
                                    deviation,
                                    3,
                                ),
                        }
                    )

        #
        # PERCENTAGE
        #

        elif method == METHOD_PERCENTAGE:

            if avg != 0:

                for sample in samples:

                    deviation_percent = (
                        abs(
                            sample["value"]
                            - avg
                        )
                        / abs(avg)
                    ) * 100.0

                    max_score = max(
                        max_score,
                        deviation_percent,
                    )
                    if (
                        deviation_percent
                        > threshold
                    ):

                        detected_outliers.append(
                            {
                                "entity_id":
                                    sample[
                                        "entity_id"
                                    ],
                                "value":
                                    sample[
                                        "value"
                                    ],
                                "deviation_percent":
                                    round(
                                        deviation_percent,
                                        2,
                                    ),
                            }
                        )

        #
        # SIGMA
        #
        # At least 3 samples required
        #

        elif method == METHOD_SIGMA:

            if len(samples) < 3:

                return {
                    "valid": False,
                    "reason": "not_enough_samples",
                    "state": False,
                    "sample_size": len(samples),
                    "outliers": [],
                }

            if stddev > 0:

                for sample in samples:

                    sigma_distance = (
                        abs(
                            sample["value"]
                            - avg
                        )
                        / stddev
                    )
                    max_score = max(
                        max_score,
                        sigma_distance,
                    )
                    if (
                        sigma_distance
                        > threshold
                    ):

                        detected_outliers.append(
                            {
                                "entity_id":
                                    sample[
                                        "entity_id"
                                    ],
                                "value":
                                    sample[
                                        "value"
                                    ],
                                "sigma_distance":
                                    round(
                                        sigma_distance,
                                        2,
                                    ),
                            }
                        )

        #
        # MAD
        #
        # Uses Modified Z-Score:
        #
        # 0.6745 * |x - median| / MAD
        #
        # Typical threshold:
        # 3.5
        #
        elif method == METHOD_MAD:
            if len(samples) < 3:
                return {
                    "valid": False,
                    "reason": "not_enough_samples",
                    "state": False,
                    "sample_size": len(samples),
                    "outliers": [],
                }
            if mad > 0:
                for sample in samples:
                    modified_z = (
                        0.6745
                        * abs(
                            sample["value"]
                            - median_value
                        )
                        / mad
                    )
                    max_score = max(max_score, modified_z,)
                    if (modified_z > threshold):
                        detected_outliers.append(
                            {
                                "entity_id":
                                    sample[
                                        "entity_id"
                                    ],
                                "value":
                                    sample[
                                        "value"
                                    ],
                                "mad_score":
                                    round(
                                        modified_z,
                                        2,
                                    ),
                            }
                        )

            else:
                for sample in samples:
                    if (sample["value"] != median_value):
                        max_score = float("inf")
                        detected_outliers.append(
                            {
                                "entity_id": sample["entity_id"],
                                "value": sample["value"],
                                "mad_score": float("inf"),
                            }
                        )

        elif method == METHOD_IMBALANCE_PERCENT:           
            max_score = imbalance_percent
            if imbalance_percent > threshold:
                max_entity = max(
                    samples,
                    key=lambda x: x["value"],
                )
                min_entity = min(
                    samples,
                    key=lambda x: x["value"],
                )
                detected_outliers.append(
                    {
                        "max_entity": max_entity["entity_id"],
                        "max_value":  max_entity["value"],
                        "min_entity": min_entity["entity_id"],
                        "min_value":  min_entity["value"],
                        "imbalance":  round( imbalance, 2,),
                        "imbalance_percent": round(imbalance_percent, 2,),
                    }
                )

        #
        # Diagnostics
        #
        outlier_entities = []
        for item in detected_outliers:
            if "entity_id" in item:
                outlier_entities.append(
                    item["entity_id"]
                )
            if "max_entity" in item:
                outlier_entities.extend(
                    [
                        item["max_entity"],
                        item["min_entity"],
                    ]
                )
        #
        # Global hysteresis
        #
        activation_threshold = threshold
        release_threshold = max(0.0,threshold - hysteresis,)
        #new_state = self._previous_state
        new_state = getattr(self, "_previous_state", False,)

        if not new_state:
            #
            # OFF -> ON
            #
            if max_score >= activation_threshold:
                new_state = True
        else:
            #
            # ON -> OFF
            #
            if max_score <= release_threshold:
                new_state = False
        self._previous_state = new_state

        return {
            "valid": True,
            "state": new_state,
            "method": method,
            "threshold": threshold,
            "unit": next(iter(units), None,),
            "sample_size": len(samples),
            #
            # Statistics
            #
            "mean": round(avg, 3, ),
            "median": round(median_value, 3,),
            "stddev": round(stddev,3,),
            "mad": round(mad, 3, ),
            "imbalance": round(imbalance, 2,),
            "imbalance_percent": round(imbalance_percent, 2,),            
            #
            # Outliers
            #
            "outliers": detected_outliers,
            "outlier_count": len(detected_outliers),
            "outlier_entities": outlier_entities,
            "max_score": (max_score if max_score == float("inf")
                    else round(max_score, 2) ),
        }