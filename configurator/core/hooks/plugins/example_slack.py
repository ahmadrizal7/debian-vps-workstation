from configurator.core.hooks.events import HookContext


def slack_notification_hook(context: HookContext) -> None:
    """
    Example hook that simulates sending a Slack notification.
    """
    # Assuming ON_MODULE_ERROR or similar event usage
    if "error" in context.event.name.lower():
        error = context.data.get("error", "Unknown error")
        print(
            f"[SLACK-PLUGIN] 🔴 Alert: Module '{context.module_name}' failed during {context.event.name} with error: {error}"
        )
    else:
        print(
            f"[SLACK-PLUGIN] 🟢 Info: Module '{context.module_name}' triggered {context.event.name}."
        )
