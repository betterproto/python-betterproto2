def test_duration() -> None:
    from tests.outputs.duration import DurationMsg

    d = {"duration": "-315576000000.999999999s"}

    assert DurationMsg.from_dict(d).to_dict() == d
    raise RuntimeError


# def test_python_todel():
#     from datetime import timedelta

#     td = timedelta(seconds=-315576000000, milliseconds=-999999999)
#     print(td.total_seconds())  # -315576000001.0

#     print(timedelta(microseconds=0, milliseconds=1).total_seconds())

#     raise RuntimeError
