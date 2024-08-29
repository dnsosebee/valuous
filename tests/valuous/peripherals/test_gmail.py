
import asyncio

import pytest

from valuous.peripherals import gmail


@pytest.mark.asyncio
async def test_gmail():

    unread_messages = gmail.get_unread_inbox()
    test_messages = [m for m in unread_messages if "valuous+test" in m.sender]
    for m in test_messages:
        m.mark_as_read()

    # Send a message from one to two
    first_test_message = gmail.SendMessageArgs(
        to="Valuous Test Inbox 2 <valuous+test2@gmail.com>",
        sender="Valuous Test Inbox 1 <valuous+test1@gmail.com>",
        subject="Test email 1",
        msg_html="<p>Hi,<br />How are you?</p>",
        msg_plain="Hi,\nHow are you?",
        signature=False  # use my account signature
    )
    gmail.send_message(first_test_message)
    await asyncio.sleep(5)

    unread_messages = gmail.get_unread_inbox()
    test_messages = [m for m in unread_messages if "valuous+test" in m.sender]
    assert len(test_messages) == 1

    unread_message = test_messages[0]
    assert unread_message.subject == "Test email 1"
    assert unread_message.html == "<body><p>Hi,<br/>How are you?</p></body>"
    assert unread_message.plain == "Hi,\nHow are you?"
    assert unread_message.sender == "Valuous Test Inbox 1 <valuous+test1@gmail.com>"
    unread_message.mark_as_read()

    reply = gmail.send_reply(
        original_email=unread_message,
        reply_text="I'm good, thanks!",
        reply_sender="Valuous Test Inbox 2 <valuous+test2@gmail.com>"
    )
    gmail.send_message(reply)
    await asyncio.sleep(5)

    unread_messages = gmail.get_unread_inbox()
    test_messages = [m for m in unread_messages if "valuous+test" in m.sender]
    assert len(test_messages) == 1

    unread_message = test_messages[0]
    assert unread_message.subject == "Re: Test email 1"
    assert unread_message.html is not None
    assert unread_message.plain is not None
    assert "<body><p>I\'m good, thanks!</p>\n<p>On " in unread_message.html
    assert """, Valuous Test Inbox 1 <valuous> wrote:</valuous></p>\n<blockquote style="border-left: 1px solid #ccc; margin: 0 0 0 .8ex; padding-left: 1ex;">\n<p>Hi,<br/>How are you?</p>\n</blockquote>\n</body>""" in unread_message.html
    assert "I'm good, thanks!\n\nOn " in unread_message.plain
    assert ", Valuous Test Inbox 1 <valuous+test1@gmail.com> wrote:\n> Hi,\n> How are you?" in unread_message.plain
    assert unread_message.sender == "Valuous Test Inbox 2 <valuous+test2@gmail.com>"
    unread_message.mark_as_read()

    # await asyncio.sleep(5)
    # unread_messages = gmail.get_unread_inbox()
    # assert len(unread_messages) == 0
