from valuous.self.trace import Trace, TraceData


def test_trace():
    t = Trace(
        data=TraceData(
            id="root",
            module_name="root",
            qualified_name="root",
            goal="root",
            args=(),
            kwargs={},
            result=None
        ),
        active=True
    )
    b = t
    b.children.append(Trace(
        data=TraceData(
            id="child",
            module_name="child",
            qualified_name="child",
            goal="child",
            args=(),
            kwargs={},
            result=None
        ),
        active=True
    ))
