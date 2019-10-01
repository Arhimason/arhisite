from bot_handler.core.command import Command


@Command('a', block='defaults', description='Check bot')
def alive(CurrentUse):
    vars = [
        'Кто если не я, врубись, никто другой',
        'ДАЯМАШИНА',
        'Угум',
        'ES OFCORRS',
        'Ты это мне?',
        'Неважно',
        'Я не спрашивал',
        'Было',
        'Da, I am alive blin!!1',
        'Честь имею',
        'Я живой, а ты?',
        'вам бан'
    ]

    return '{}\n Current worker restarted {} ago'
