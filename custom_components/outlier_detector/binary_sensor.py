from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import (
    ConfigEntry,
)
from homeassistant.core import (
    HomeAssistant,
)
from homeassistant.helpers.device_registry import (
    DeviceInfo,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    CONF_NAME,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """
    Set up binary sensor platform.
    """

    coordinator = hass.data[
        DOMAIN
    ][
        entry.entry_id
    ][
        "coordinator"
    ]

    async_add_entities(
        [
            OutlierBinarySensor(
                coordinator,
                entry,
            )
        ]
    )


class OutlierBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):
    """
    Binary sensor indicating whether any
    configured entity is considered an outlier.
    """

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
    ) -> None:

        super().__init__(coordinator)

        self._entry = entry

        config = {
            **entry.data,
            **entry.options,
        }

        self._detector_name = config[
            CONF_NAME
        ]

        self._attr_unique_id = (
            f"{entry.entry_id}_binary"
        )

        self._attr_translation_key = "anomaly"

    @property
    def device_info(
        self,
    ) -> DeviceInfo:

        return DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    self._entry.entry_id,
                )
            },
            name=self._detector_name,
            manufacturer="Custom",
            model="Outlier Detector",
            sw_version="1.1",
        )

    @property
    def available(
        self,
    ) -> bool:

        return (
            self.coordinator.data
            is not None
        )

    @property
    def is_on(
        self,
    ) -> bool:

        data = self.coordinator.data

        if not data:
            return False

        return data.get(
            "state",
            False,
        )

    @property
    def icon(
        self,
    ) -> str:

        if self.is_on:
            return "mdi:alert-circle"

        return "mdi:check-circle"

    @property
    def extra_state_attributes(
        self,
    ) -> dict:

        data = self.coordinator.data

        if not data:
            return {}

        attributes = {
            "valid":
                data.get(
                    "valid"
                ),
            "method":
                data.get(
                    "method"
                ),
            "threshold":
                data.get(
                    "threshold"
                ),
            "unit":
                data.get(
                    "unit"
                ),
            "sample_size":
                data.get(
                    "sample_size"
                ),
            "mean":
                data.get(
                    "mean"
                ),
            "median":
                data.get(
                    "median"
                ),
            "stddev":
                data.get(
                    "stddev"
                ),
            "mad":
                data.get(
                    "mad"
                ),
            "imbalance":
                data.get(
                    "imbalance"
                ),
            "imbalance_percent":
                data.get(
                    "imbalance_percent"
                ),
            "outlier_count":
                data.get(
                    "outlier_count"
                ),
            "outlier_entities":
                data.get(
                    "outlier_entities",
                    [],
                ),
            "max_score":
                data.get(
                    "max_score"
                ),
            "outliers":
                data.get(
                    "outliers",
                    [],
                ),
            "hysteresis":
                data.get(
                    "hysteresis"
                ),

            "activation_threshold":
                data.get(
                    "activation_threshold"
                ),

            "release_threshold":
                data.get(
                    "release_threshold"
                ),                
        }

        if not data.get(
            "valid",
            True,
        ):

            attributes["reason"] = (
                data.get(
                    "reason"
                )
            )

            if "units" in data:

                attributes[
                    "units"
                ] = data[
                    "units"
                ]

        return attributes