from bot_handler.core.command import Command


@Command('usual_message', block='defaults', description='Handle usual message(without command)', disable_parser=True)
def usual_message(CurrentUse):
    return None
