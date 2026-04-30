"""SDK compatibility shim for the discriminated-union ``AgentSettings`` rework."""

from typing import Any

try:
    from pydantic import ValidationError

    from openhands.sdk.settings import (  # type: ignore[attr-defined]
        ACPAgentSettings,
        AgentSettingsConfig,
        LLMAgentSettings,
        default_agent_settings,
        export_agent_settings_schema,
    )
    from openhands.sdk.settings import (
        validate_agent_settings as _sdk_validate_agent_settings,
    )

    _HAS_DISCRIMINATED_UNION = True
    try:
        from openhands.sdk.settings import (
            OpenHandsAgentSettings as _OpenHandsAgentSettings,  # noqa: F401
        )

        _HAS_OPENHANDS_AGENT_KIND = True
    except ImportError:
        _HAS_OPENHANDS_AGENT_KIND = False

    def validate_agent_settings(data: Any):  # type: ignore[misc]
        try:
            return _sdk_validate_agent_settings(data)
        except ValidationError:
            if (
                not _HAS_OPENHANDS_AGENT_KIND
                and isinstance(data, dict)
                and data.get('agent_kind') == 'openhands'
            ):
                fallback = dict(data)
                fallback['agent_kind'] = 'llm'
                return _sdk_validate_agent_settings(fallback)
            raise
except ImportError:
    _HAS_DISCRIMINATED_UNION = False
    _HAS_OPENHANDS_AGENT_KIND = False
    from openhands.sdk.settings import AgentSettings

    LLMAgentSettings = AgentSettings  # type: ignore[misc, assignment]

    class _ACPAgentSettingsStub:
        """Sentinel — older SDK builds cannot produce ACPAgentSettings instances."""

    ACPAgentSettings = _ACPAgentSettingsStub  # type: ignore[misc, assignment]
    AgentSettingsConfig = AgentSettings  # type: ignore[misc, assignment]

    def default_agent_settings() -> AgentSettings:  # type: ignore[misc]
        return AgentSettings()

    def validate_agent_settings(data: dict[str, Any]) -> AgentSettings:  # type: ignore[misc]
        if isinstance(data, dict) and data.get('kind') == 'acp':
            raise RuntimeError(
                "Stored settings contain kind='acp' but the installed "
                'openhands-sdk does not support ACP agents. Upgrade to an '
                'SDK release that includes the discriminated-union rework '
                '(OpenHands/software-agent-sdk#2861).'
            )
        return AgentSettings.model_validate(data)

    def export_agent_settings_schema():  # type: ignore[misc]
        return AgentSettings.export_schema()


__all__ = [
    'ACPAgentSettings',
    'AgentSettingsConfig',
    'LLMAgentSettings',
    '_HAS_DISCRIMINATED_UNION',
    '_HAS_OPENHANDS_AGENT_KIND',
    'default_agent_settings',
    'export_agent_settings_schema',
    'validate_agent_settings',
]
