"""Battery Charge and Range Support for the Nissan Leaf."""
from __future__ import annotations

import logging

from pycarwings2.pycarwings2 import Leaf
from voluptuous.validators import Number

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.icon import icon_for_battery_level
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.util.distance import LENGTH_KILOMETERS, LENGTH_MILES
from homeassistant.util.unit_system import IMPERIAL_SYSTEM, METRIC_SYSTEM

from . import LeafEntity
from .const import (
    DATA_BATTERY,
    DATA_CHARGING,
    DATA_LEAF,
    DATA_RANGE_AC,
    DATA_RANGE_AC_OFF,
)

_LOGGER = logging.getLogger(__name__)

ICON_RANGE = "mdi:speedometer"


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Sensors setup."""
    if discovery_info is None:
        return

    devices: list[LeafEntity] = []
    for vin, datastore in hass.data[DATA_LEAF].items():
        _LOGGER.debug("Adding sensors for vin=%s", vin)
        devices.append(LeafBatterySensor(datastore))
        devices.append(LeafRangeSensor(datastore, True))
        devices.append(LeafRangeSensor(datastore, False))

    add_devices(devices, True)


class LeafBatterySensor(LeafEntity, SensorEntity):
    """Nissan Leaf Battery Sensor."""

    def __init__(self, car: Leaf) -> None:
        """Set up battery sensor."""
        super().__init__(car)
        self._attr_unique_id = f"{self.car.leaf.vin.lower()}_soc"

    @property
    def name(self) -> str:
        """Sensor Name."""
        return f"{self.car.leaf.nickname} Charge"

    @property
    def device_class(self) -> str:
        """Return the device class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def native_value(self) -> Number | None:
        """Battery state percentage."""
        if self.car.data[DATA_BATTERY] is None:
            return None
        return round(self.car.data[DATA_BATTERY])

    @property
    def native_unit_of_measurement(self) -> str:
        """Battery state measured in percentage."""
        return PERCENTAGE

    @property
    def icon(self) -> str:
        """Battery state icon handling."""
        chargestate = self.car.data[DATA_CHARGING]
        return icon_for_battery_level(battery_level=self.state, charging=chargestate)


class LeafRangeSensor(LeafEntity, SensorEntity):
    """Nissan Leaf Range Sensor."""

    def __init__(self, car: Leaf, ac_on: bool) -> None:
        """Set up range sensor. Store if AC on."""
        self._ac_on = ac_on
        super().__init__(car)
        if ac_on:
            self._attr_unique_id = f"{self.car.leaf.vin.lower()}_range_ac"
        else:
            self._attr_unique_id = f"{self.car.leaf.vin.lower()}_range"

    @property
    def name(self) -> str:
        """Update sensor name depending on AC."""
        if self._ac_on is True:
            return f"{self.car.leaf.nickname} Range (AC)"
        return f"{self.car.leaf.nickname} Range"

    def log_registration(self) -> None:
        """Log registration."""
        _LOGGER.debug(
            "Registered LeafRangeSensor integration with Home Assistant for VIN %s",
            self.car.leaf.vin,
        )

    @property
    def native_value(self) -> float | None:
        """Battery range in miles or kms."""
        if self._ac_on:
            ret = self.car.data[DATA_RANGE_AC]
        else:
            ret = self.car.data[DATA_RANGE_AC_OFF]

        if ret is None:
            return None

        if not self.car.hass.config.units.is_metric or self.car.force_miles:
            ret = IMPERIAL_SYSTEM.length(ret, METRIC_SYSTEM.length_unit)

        return round(ret)

    @property
    def native_unit_of_measurement(self) -> str:
        """Battery range unit."""
        if not self.car.hass.config.units.is_metric or self.car.force_miles:
            return LENGTH_MILES
        return LENGTH_KILOMETERS

    @property
    def icon(self) -> str:
        """Nice icon for range."""
        return ICON_RANGE
