"""The MirAIe climate platform."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    PRECISION_WHOLE,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from miraie_ac import (
    Device as MirAIeDevice,
)
from miraie_ac import (
    FanMode,
    PowerMode,
    PresetMode,
    SwingMode,
)
from miraie_ac import (
    HVACMode as MHVACMode,
)

from .const import (
    SWING_BOTTOM,
    SWING_LOWER_MIDDLE,
    SWING_MIDDLE,
    SWING_ON,
    SWING_TOP,
    SWING_UPPER_MIDDLE,
)
from .entity import MirAIeEntity, platform_async_setup_entry


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the MirAIe Climate Hub."""
    await platform_async_setup_entry(hass, entry, async_add_entities, MirAIeClimate)


class MirAIeClimate(MirAIeEntity, ClimateEntity):
    """Representation of a MirAIe Climate."""

    def __init__(self, device: MirAIeDevice) -> None:
        """Initialize the MirAIe climate entity."""
        super().__init__(device)

        self._attr_icon = "mdi:air-conditioner"
        self._attr_translation_key = "miraie_climate"
        self._attr_hvac_modes = [
            HVACMode.AUTO,
            HVACMode.COOL,
            HVACMode.OFF,
            HVACMode.DRY,
            HVACMode.FAN_ONLY,
        ]
        self._attr_preset_modes = [pm.value for pm in PresetMode]
        self._attr_fan_mode = FanMode.AUTO.value
        self._attr_fan_modes = [
            FanMode.AUTO.value,
            FanMode.QUIET.value,
            FanMode.LOW.value,
            FanMode.MEDIUM.value,
            FanMode.HIGH.value,
        ]
        self._attr_swing_modes = [
            SWING_ON,
            SWING_TOP,
            SWING_UPPER_MIDDLE,
            SWING_MIDDLE,
            SWING_LOWER_MIDDLE,
            SWING_BOTTOM,
        ]
        self._attr_max_temp = 30.0
        self._attr_min_temp = 16.0
        self._attr_target_temperature_step = 1
        self._enable_turn_on_off_backwards_compatibility = False
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.PRESET_MODE
            | ClimateEntityFeature.SWING_MODE
            | ClimateEntityFeature.TURN_OFF
            | ClimateEntityFeature.TURN_ON
        )
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS
        self._attr_precision = PRECISION_WHOLE

    @property
    def name(self) -> str:
        """Return the display name."""
        return self.device.friendly_name

    @property
    def hvac_mode(self) -> HVACMode | str | None:
        """Get HVAC mode."""
        power_mode = self.device.status.power_mode

        if power_mode == PowerMode.OFF:
            return HVACMode.OFF.value

        mode = self.device.status.hvac_mode

        if mode == MHVACMode.FAN:
            return HVACMode.FAN_ONLY.value

        return mode.value

    @property
    def current_temperature(self) -> float | None:
        """Get current temperature."""
        return self.device.status.room_temperature

    @property
    def target_temperature(self) -> float | None:
        """Get target temperature."""
        return self.device.status.temperature

    @property
    def preset_mode(self) -> str | None:
        """Get preset mode."""
        return self.device.status.preset_mode.value

    @property
    def fan_mode(self) -> str | None:
        """Get fan mode."""
        return self.device.status.fan_mode.value

    @property
    def swing_mode(self) -> str | None:
        """Set swing mode."""
        mode = self.device.status.swing_mode.value

        mode_mapping = {
            0: SWING_ON,
            1: SWING_TOP,
            2: SWING_UPPER_MIDDLE,
            3: SWING_MIDDLE,
            4: SWING_LOWER_MIDDLE,
            5: SWING_BOTTOM,
        }

        return mode_mapping.get(mode, SWING_ON)

    async def async_turn_off(self) -> None:
        """Turn off."""
        await self.device.turn_off()

    async def async_turn_on(self) -> None:
        """Turn on."""
        await self.device.turn_on()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature."""
        await self.device.set_temperature(kwargs["temperature"])

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.device.turn_off()
        else:
            if self.device.status.power_mode == PowerMode.OFF:
                await self.device.turn_on()

            if hvac_mode == HVACMode.FAN_ONLY:
                await self.device.set_hvac_mode(MHVACMode.FAN)
            else:
                await self.device.set_hvac_mode(MHVACMode(hvac_mode.value))

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        await self.device.set_fan_mode(FanMode(fan_mode))

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set swing mode."""
        swing_modes = [
            SWING_ON,
            SWING_TOP,
            SWING_UPPER_MIDDLE,
            SWING_MIDDLE,
            SWING_LOWER_MIDDLE,
            SWING_BOTTOM,
        ]
        await self.device.set_swing_mode(SwingMode(swing_modes.index(swing_mode)))

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode."""
        await self.device.set_preset_mode(PresetMode(preset_mode))
