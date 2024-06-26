"""The mirAIe integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from miraie_ac import MirAIeBroker, MirAIeHub

from .const import DOMAIN

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up mirAIe from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    async with MirAIeHub() as hub:
        broker = MirAIeBroker()
        await hub.init(entry.data["username"], entry.data["password"], broker)
        hass.data[DOMAIN][entry.entry_id] = hub

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
