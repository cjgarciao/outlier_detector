from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_NAME,
    CONF_ENTITIES,
    CONF_METHOD,
    CONF_THRESHOLD,
    DEFAULT_NAME,
    DEFAULT_METHOD,
    DEFAULT_THRESHOLD,
    METHOD_OPTIONS,
    CONF_HYSTERESIS,
    DEFAULT_HYSTERESIS,
)


class OutlierDetectorConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Outlier Detector config flow."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input=None,
    ):
        errors = {}

        if user_input is not None:

            units = set()

            for entity_id in user_input[
                CONF_ENTITIES
            ]:

                state = self.hass.states.get(
                    entity_id
                )

                if state is None:
                    continue

                unit = state.attributes.get(
                    "unit_of_measurement"
                )

                if unit:
                    units.add(unit)

            if len(units) > 1:

                errors["base"] = (
                    "mixed_units"
                )

            else:

                return self.async_create_entry(
                    title=user_input[
                        CONF_NAME
                    ],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self._schema(),
            errors=errors,
        )

    def _schema(self):

        return vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=DEFAULT_NAME,
                ): str,

                vol.Required(
                    CONF_ENTITIES,
                ): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain=["sensor"],
                        multiple=True,
                    )
                ),

                vol.Required(
                    CONF_METHOD,
                    default=DEFAULT_METHOD,
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=METHOD_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),

                vol.Required(
                    CONF_THRESHOLD,
                    default=DEFAULT_THRESHOLD,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        step=0.1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_HYSTERESIS,
                    default=DEFAULT_HYSTERESIS,
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        step=0.1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )

    @staticmethod
    def async_get_options_flow(
        config_entry,
    ):
        return OutlierOptionsFlow(
            config_entry
        )


class OutlierOptionsFlow(
    config_entries.OptionsFlow,
):
    """Options flow."""

    def __init__(
        self,
        config_entry,
    ) -> None:

        self._config_entry = (
            config_entry
        )

    async def async_step_init(
        self,
        user_input=None,
    ):

        if user_input is not None:

            units = set()

            for entity_id in user_input[
                CONF_ENTITIES
            ]:

                state = self.hass.states.get(
                    entity_id
                )

                if state is None:
                    continue

                unit = state.attributes.get(
                    "unit_of_measurement"
                )

                if unit:
                    units.add(unit)

            if len(units) > 1:

                return self.async_show_form(
                    step_id="init",
                    data_schema=self._options_schema(),
                    errors={
                        "base":
                            "mixed_units"
                    },
                )

            return self.async_create_entry(
                title="",
                data=user_input,
            )

        return self.async_show_form(
            step_id="init",
            data_schema=self._options_schema(),
        )

    def _options_schema(self):

        data = {
            **self._config_entry.data,
            **self._config_entry.options,
        }

        return vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=data.get(CONF_NAME, DEFAULT_NAME,),
                ): str,
                
                vol.Required(
                    CONF_ENTITIES,
                    default=data.get(CONF_ENTITIES, [],),
                ): selector.EntitySelector( selector.EntitySelectorConfig(
                        domain=["sensor"], multiple=True,
                    )
                ),

                vol.Required(
                    CONF_METHOD,
                    default=data.get(
                        CONF_METHOD,
                        DEFAULT_METHOD,
                    ),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=METHOD_OPTIONS,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),

                vol.Required(
                    CONF_THRESHOLD,
                    default=data.get(
                        CONF_THRESHOLD,
                        DEFAULT_THRESHOLD,
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        step=0.1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
                vol.Required(
                    CONF_HYSTERESIS,
                    default=data.get(
                        CONF_HYSTERESIS,
                        DEFAULT_HYSTERESIS,
                    ),
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=0,
                        step=0.1,
                        mode=selector.NumberSelectorMode.BOX,
                    )
                ),
            }
        )