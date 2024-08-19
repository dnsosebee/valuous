from valuous.peripherals import telegram


def test_get_bot():
    bot = telegram.get_bot()
    assert bot is not None


def test_get_updates():
    bot = telegram.get_bot()
    updates = telegram.get_updates(bot)
    print(updates)
    assert updates is not None
