from datetime import datetime

from valuous.self.tool import ToolResponse


def clock_t() -> ToolResponse:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data = {"current_time": current_time}
    return {"data": data, "affordances": []}
