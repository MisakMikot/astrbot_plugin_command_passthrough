from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, register
from astrbot.core.star.filter.event_message_type import EventMessageType


@register(
    "astrbot_plugin_command_passthrough",
    "sunashiro",
    "一个简单插件，使特定前缀的命令绕过AI大模型调用，但仍会传递到gscore等下游插件处理。",
    "0.0.1",
    "https://github.com/MisakMikot/astrbot_plugin_command_passthrough",
)
class CommandPassthrough(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.prefixes = tuple(
            prefix.strip()
            for prefix in getattr(self.config, "prefixes", [])
            if isinstance(prefix, str) and prefix.strip()
        )

    def _is_passthrough_message(self, event: AstrMessageEvent) -> bool:
        if not self.prefixes:
            return False

        message_str = getattr(event, "message_str", "")
        if not message_str:
            return False

        raw_text = message_str.lstrip()
        return raw_text.startswith(self.prefixes)

    @filter.event_message_type(EventMessageType.ALL)
    async def on_all_message(self, event: AstrMessageEvent):
        if self._is_passthrough_message(event):
            logger.info(
                f"[CommandPassthrough] 消息 '{event.message_str}' 命中前缀配置，已停止事件传播以绕过AI调用"
            )
            event.stop_event()

    async def terminate(self):
        logger.info("[CommandPassthrough] 插件已卸载")
