"""Switch entities for MirAIe platform."""

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from miraie_ac import Device as MirAIeDevice
from miraie_ac import DisplayMode

from .entity import MirAIeEntity, platform_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the MirAIe Climate Hub."""
    await platform_async_setup_entry(
        hass, entry, async_add_entities, MirAIeClimateDisplayModeSwitch
    )


class MirAIeClimateDisplayModeSwitch(MirAIeEntity, SwitchEntity):
    """Climate display mode switch entity."""

    def __init__(self, device: MirAIeDevice) -> None:
        """Initialize the climate display mode switch entity."""
        super().__init__(device)

        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def icon(self) -> str:
        """Get the icon."""
        return "mdi:monitor" if self.is_on else "mdi:monitor-off"

    @property
    def name(self) -> str:
        """Get name."""
        return self.device.friendly_name + " display mode"

    @property
    def is_on(self) -> bool:
        """Whether the device is on."""
        return self.device.status.display_mode == DisplayMode.ON

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on."""
        await self.device.set_display_mode(DisplayMode.ON)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self.device.set_display_mode(DisplayMode.OFF)
