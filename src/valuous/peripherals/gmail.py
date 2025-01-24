
from typing import List, Optional

from pydantic import BaseModel
from simplegmail import Gmail
from simplegmail.message import Message
from simplegmail.query import construct_query

_client: Gmail = Gmail(client_secret_file='secrets/gmail_client_secret.json',
                       creds_file='secrets/gmail_token.json', access_type='offline')


def _quote_message(original_message, is_html=False):
    if is_html:
        return f'''
        <blockquote style="border-left: 1px solid #ccc; margin: 0 0 0 .8ex; padding-left: 1ex;">
            {original_message}
        </blockquote>
        '''
    else:
        return "\n".join(f"> {line}" for line in original_message.split("\n"))


def _reply_subject(original_subject: str):
    if original_subject.startswith("Re: "):
        return original_subject
    else:
        return f"Re: {original_subject}"


def _plaintext_to_html(plaintext: str):
    return plaintext.replace("\n", "<br />")


def get_unread_inbox():
    return _client.get_unread_inbox()


def get_message(id: str) -> Message:
    return _client.get_messages(
        query=construct_query(
            {
                "id": id
            }
        )
    )[0]


class SendMessageArgs(BaseModel):
    to: str
    sender: str
    subject: str
    msg_plain: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    msg_html: Optional[str] = None
    attachments: Optional[List[str]] = None
    signature: bool = False


def send_message(args: SendMessageArgs):
    return _client.send_message(**args.model_dump())


def send_reply(original_email: Message, reply_text: str, reply_sender: str) -> SendMessageArgs:
    html_body = plain_body = None

    if original_email.html:
        quoted_html = _quote_message(original_email.html, is_html=True)
        html_body = f'''
        <p>{_plaintext_to_html(reply_text)}</p>
        <p>On {original_email.date}, {original_email.sender} wrote:</p>
        {quoted_html}
        '''

    if original_email.plain:
        quoted_plain = _quote_message(original_email.plain, is_html=False)
        plain_body = f"{reply_text}\n\nOn {original_email.date}, {
            original_email.sender} wrote:\n{quoted_plain}"

    return SendMessageArgs(
        to=original_email.sender,
        sender=reply_sender,
        subject=_reply_subject(original_email.subject),
        msg_html=html_body,
        msg_plain=plain_body or "",
        signature=False
    )
