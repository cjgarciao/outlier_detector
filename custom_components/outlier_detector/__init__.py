from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import (
    HomeAssistant,
    callback,
)
from homeassistant.helpers.event import (
    async_track_state_change_event,
)

from .const import (
    DOMAIN,
    PLATFORMS,
    CONF_ENTITIES,
)
from .coordinator import (
    OutlierDetectorCoordinator,
)


async def async_setup(
    hass: HomeAssistant,
    config: dict,
) -> bool:
    """Set up integration."""

    hass.data.setdefault(
        DOMAIN,
        {},
    )

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up config entry."""

    config = {
        **entry.data,
        **entry.options,
    }

    coordinator = (
        OutlierDetectorCoordinator(
            hass,
            config,
        )
    )

    await coordinator.async_refresh()

    @callback
    async def _handle_state_change(event):
        """Refresh coordinator when a monitored entity changes."""

        await coordinator.async_request_refresh()

    unsub = async_track_state_change_event(
        hass,
        config[CONF_ENTITIES],
        _handle_state_change,
    )

    hass.data.setdefault(
        DOMAIN,
        {},
    )

    hass.data[DOMAIN][
        entry.entry_id
    ] = {
        "coordinator": coordinator,
        "unsub": unsub,
    }

    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )

    entry.async_on_unload(
        entry.add_update_listener(
            async_reload_entry
        )
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload config entry."""

    stored = hass.data[
        DOMAIN
    ].get(
        entry.entry_id
    )

    if stored:
        stored["unsub"]()

    unload_ok = (
        await hass.config_entries.async_unload_platforms(
            entry,
            PLATFORMS,
        )
    )

    if unload_ok:
        hass.data[
            DOMAIN
        ].pop(
            entry.entry_id,
            None,
        )

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""

    await hass.config_entries.async_reload(
        entry.entry_id
    )