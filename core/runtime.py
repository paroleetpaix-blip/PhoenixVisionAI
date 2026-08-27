"""
========================================================
PHOENIX VISION AI

Runtime Registry

Références des composants actifs du processus Phoenix.

Phoenix Security Technologies
========================================================
"""

engine = None
stream_service = None


def bind_engine(
    active_engine,
):

    global engine
    global stream_service


    engine = active_engine

    stream_service = getattr(
        active_engine,
        "stream_service",
        None,
    )


    return {
        "engine_bound":
            engine is not None,

        "stream_service_bound":
            stream_service is not None,
    }


def unbind_engine(
    active_engine=None,
):

    global engine
    global stream_service


    if (
        active_engine is not None
        and
        engine is not active_engine
    ):

        return False


    engine = None
    stream_service = None

    return True


def runtime_state():

    return {
        "engine_bound":
            engine is not None,

        "stream_service_bound":
            stream_service is not None,
    }
