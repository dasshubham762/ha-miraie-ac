"""Base entity for MirAIe."""

from typing import TypeVar

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from miraie_ac import (
    Device as MirAIeDevice,
)
from miraie_ac import (
    MirAIeHub,
)

from .const import DOMAIN

_EntityT = TypeVar("_EntityT", bound="MirAIeEntity")


async def platform_async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    entity_type: _EntityT,
) -> None:
    """Set up an MirAIe platform."""
    hub: MirAIeHub = hass.data[DOMAIN][entry.entry_id]

    entities = list(map(entity_type, hub.home.devices))

    async_add_entities(entities)


class MirAIeEntity(Entity):
    """MirAIe base entity."""

    def __init__(self, device: MirAIeDevice) -> None:
        """Initialize entity."""
        self.device = device
        self._attr_unique_id = self.device.id

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.device.id)
            },
            name=self.device.friendly_name,
            manufacturer=self.device.details.brand,
            model=self.device.details.model_number,
            sw_version=self.device.details.firmware_version,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.device.status.is_online

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self.device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self.device.remove_callback(self.async_write_ha_state)
