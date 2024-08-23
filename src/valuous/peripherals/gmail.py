
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from valuous.peripherals.simplegmail import Gmail
from valuous.peripherals.simplegmail.message import Message
from valuous.self.tool import ToolResponse

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


def open_unread_t() -> ToolResponse:
    inbox = get_unread_inbox()
    data = {"unread_messages": [{"subject": m.subject, "snippet": m.snippet, "id": m.id}
            for m in inbox]}
    affordances = [view_message_t, init_mail_t] if len(data) > 0 else [
        init_mail_t]
    return {
        "data": data,
        "affordances": affordances
    }


class ViewMessageArgs(BaseModel):
    id: str


def view_message_t(args: ViewMessageArgs) -> ToolResponse:
    inbox = get_unread_inbox()
    message = next((m for m in inbox if m.id == args.id), None)
    message.mark_as_read()
    data = {"message": message}
    affordances = [init_mail_t]
    return {"data": data, "affordances": affordances}

# We may want to remove for simplicity!


def init_mail_t() -> ToolResponse:
    data = {}
    affordances = [open_unread_t]
    return {"data": data, "affordances": affordances}


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


class SendReplyArgs(BaseModel):
    original_email: Message
    reply_text: str
    reply_sender: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


def send_reply_t(args: SendReplyArgs) -> SendMessageArgs:
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

    send_message_args = SendMessageArgs(
        to=args.original_email.sender,
        sender=args.reply_sender,
        subject=_reply_subject(args.original_email.subject),
        msg_html=html_body,
        msg_plain=plain_body,
        signature=False
    )

    send_message(send_message_args)

    response = init_mail_t()
    response["redirect"] = {
        "tool": open_unread_t,
        "args": None
    }
    return response
