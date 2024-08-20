
from typing import List, Optional

from pydantic import BaseModel, ConfigDict
from simplegmail import Gmail
from simplegmail.message import Message

_client: Gmail = Gmail(client_secret_file='secrets/gmail_client_secret.json',
                       creds_file='secrets/gmail_token.json', access_type='offline')


class SendMessageArgs(BaseModel):
    to: str
    sender: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    subject: str
    msg_html: str
    msg_plain: str
    attachments: Optional[List[str]] = None
    signature: bool = False


def get_unread_inbox():
    return _client.get_unread_inbox()


def send_message(args: SendMessageArgs):
    return _client.send_message(**args.model_dump())


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


class CreateEmailReplyArgs(BaseModel):
    original_email: Message
    reply_text: str
    reply_sender: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


def create_email_reply(args: CreateEmailReplyArgs) -> SendMessageArgs:
    html_body = plain_body = None

    if args.original_email.html:
        quoted_html = _quote_message(args.original_email.html, is_html=True)
        html_body = f'''
        <p>{_plaintext_to_html(args.reply_text)}</p>
        <p>On {args.original_email.date}, {args.original_email.sender} wrote:</p>
        {quoted_html}
        '''

    if args.original_email.plain:
        quoted_plain = _quote_message(args.original_email.plain, is_html=False)
        plain_body = f"{args.reply_text}\n\nOn {args.original_email.date}, {
            args.original_email.sender} wrote:\n{quoted_plain}"

    return SendMessageArgs(
        to=args.original_email.sender,
        sender=args.reply_sender,
        subject=_reply_subject(args.original_email.subject),
        msg_html=html_body,
        msg_plain=plain_body,
        signature=False
    )
