"""Support for Z-Wave controls using the select platform."""
from __future__ import annotations

from typing import Dict, cast

from zwave_js_server.client import Client as ZwaveClient
from zwave_js_server.const import TARGET_VALUE_PROPERTY, CommandClass
from zwave_js_server.const.command_class.sound_switch import ToneID

from homeassistant.components.select import DOMAIN as SELECT_DOMAIN, SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DATA_CLIENT, DOMAIN
from .discovery import ZwaveDiscoveryInfo
from .entity import ZWaveBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Z-Wave Select entity from Config Entry."""
    client: ZwaveClient = hass.data[DOMAIN][config_entry.entry_id][DATA_CLIENT]

    @callback
    def async_add_select(info: ZwaveDiscoveryInfo) -> None:
        """Add Z-Wave select entity."""
        entities: list[ZWaveBaseEntity] = []
        if info.platform_hint == "Default tone":
            entities.append(ZwaveDefaultToneSelectEntity(config_entry, client, info))
        elif info.platform_hint == "multilevel_switch":
            entities.append(
                ZwaveMultilevelSwitchSelectEntity(config_entry, client, info)
            )
        else:
            entities.append(ZwaveSelectEntity(config_entry, client, info))
        async_add_entities(entities)

    config_entry.async_on_unload(
        async_dispatcher_connect(
            hass,
            f"{DOMAIN}_{config_entry.entry_id}_add_{SELECT_DOMAIN}",
            async_add_select,
        )
    )


class ZwaveSelectEntity(ZWaveBaseEntity, SelectEntity):
    """Representation of a Z-Wave select entity."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, config_entry: ConfigEntry, client: ZwaveClient, info: ZwaveDiscoveryInfo
    ) -> None:
        """Initialize a ZwaveSelectEntity entity."""
        super().__init__(config_entry, client, info)

        # Entity class attributes
        self._attr_name = self.generate_name(include_value_name=True)
        self._attr_options = list(self.info.primary_value.metadata.states.values())

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        if self.info.primary_value.value is None:
            return None
        return str(
            self.info.primary_value.metadata.states.get(
                str(self.info.primary_value.value), self.info.primary_value.value
            )
        )

    async def async_select_option(self, option: str | int) -> None:
        """Change the selected option."""
        key = next(
            key
            for key, val in self.info.primary_value.metadata.states.items()
            if val == option
        )
        await self.info.node.async_set_value(self.info.primary_value, int(key))


class ZwaveDefaultToneSelectEntity(ZWaveBaseEntity, SelectEntity):
    """Representation of a Z-Wave default tone select entity."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self, config_entry: ConfigEntry, client: ZwaveClient, info: ZwaveDiscoveryInfo
    ) -> None:
        """Initialize a ZwaveDefaultToneSelectEntity entity."""
        super().__init__(config_entry, client, info)
        self._tones_value = self.get_zwave_value(
            "toneId", command_class=CommandClass.SOUND_SWITCH
        )

        # Entity class attributes
        self._attr_name = self.generate_name(
            include_value_name=True, alternate_value_name=info.platform_hint
        )

    @property
    def options(self) -> list[str]:
        """Return a set of selectable options."""
        # We know we can assert because this value is part of the discovery schema
        assert self._tones_value
        return [
            val
            for key, val in self._tones_value.metadata.states.items()
            if int(key) not in (ToneID.DEFAULT, ToneID.OFF)
        ]

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        # We know we can assert because this value is part of the discovery schema
        assert self._tones_value
        return str(
            self._tones_value.metadata.states.get(
                str(self.info.primary_value.value), self.info.primary_value.value
            )
        )

    async def async_select_option(self, option: str | int) -> None:
        """Change the selected option."""
        # We know we can assert because this value is part of the discovery schema
        assert self._tones_value
        key = next(
            key
            for key, val in self._tones_value.metadata.states.items()
            if val == option
        )
        await self.info.node.async_set_value(self.info.primary_value, int(key))


class ZwaveMultilevelSwitchSelectEntity(ZWaveBaseEntity, SelectEntity):
    """Representation of a Z-Wave Multilevel Switch CC select entity."""

    def __init__(
        self, config_entry: ConfigEntry, client: ZwaveClient, info: ZwaveDiscoveryInfo
    ) -> None:
        """Initialize a ZwaveSelectEntity entity."""
        super().__init__(config_entry, client, info)
        self._target_value = self.get_zwave_value(TARGET_VALUE_PROPERTY)
        assert self.info.platform_data_template
        self._lookup_map = cast(
            Dict[int, str], self.info.platform_data_template.static_data
        )

        # Entity class attributes
        self._attr_options = list(self._lookup_map.values())

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        if self.info.primary_value.value is None:
            return None
        return str(
            self._lookup_map.get(
                int(self.info.primary_value.value), self.info.primary_value.value
            )
        )

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        key = next(key for key, val in self._lookup_map.items() if val == option)
        await self.info.node.async_set_value(self._target_value, int(key))
