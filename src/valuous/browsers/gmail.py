

from typing import Callable, List, Optional

from pydantic import BaseModel

from valuous.peripherals import gmail
from valuous.peripherals.simplegmail.message import Message
from valuous.self.tool import ToolResponse

valuous_sender = "Valuous <valuous@gmail.com>"


# def init_mail_t() -> ToolResponse:
#     data = {}
#     affordances = [open_unread_t]
#     return {"data": data, "affordances": affordances}

def open_unread_t() -> ToolResponse:
    inbox = gmail.get_unread_inbox()
    data = {"unread_messages": [{"subject": m.subject, "snippet": m.snippet, "id": m.id}
            for m in inbox]}
    affordances = [view_message_t] if len(data) > 0 else []
    return {
        "data": data,
        "affordances": affordances
    }


class SendMessageArgs(BaseModel):
    to: str
    msg_plain: str
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    subject: str
    msg_plain: str


def send_message_t(args: SendMessageArgs) -> ToolResponse:
    gmail.send_message(gmail.SendMessageArgs(
        **args.model_dump(), sender=valuous_sender))


class ViewMessageArgs(BaseModel):
    id: str


def view_message_t(args: ViewMessageArgs) -> ToolResponse:
    inbox = gmail.get_unread_inbox()
    message = next((m for m in inbox if m.id == args.id), None)
    message.mark_as_read()
    data = {"message": message}
    affordances = [open_unread_t, get_send_reply_t(
        original_email=message, reply_sender=valuous_sender)]
    return {"data": data, "affordances": affordances}


class SendReplyArgs(BaseModel):
    reply_text: str


def get_send_reply_t(original_email: Message, reply_sender: str) -> Callable[[SendReplyArgs], ToolResponse]:
    def send_reply_t(args: SendReplyArgs) -> ToolResponse:
        send_message_args = gmail.send_reply(
            original_email, args.reply_text, reply_sender)
        gmail.send_message(send_message_args)

        response = open_unread_t()
        response["redirect"] = {
            "tool": open_unread_t,
            "args": None
        }
        return response

    return send_reply_t
