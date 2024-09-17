import os

import backtracepython as backtrace


def open_file(name):
    open(name).read()


current_location = os.path.dirname(os.path.abspath(__file__))
backtrace.initialize(
    endpoint=os.getenv(
        "BACKTRACE_SUBMISSION_URL",
        "https://submit.backtrace.io/your-universe/token/json",
    ),
    attributes={
        "application": "example-app",
        "application.version": "1.0.0",
        "version": "1.0.0",
    },
    attachments=[
        os.path.join(current_location, "test.txt"),
        os.path.join(current_location, "not-existing-file"),
    ],
    debug_backtrace=True,
)


def main():

    # send an exception from the try/catch block
    try:
        open_file("not existing file")
    except:
        backtrace.send_last_exception()

    # send a message
    backtrace.send_report("test message")

    # generate and send unhandled exception
    open_file("not existing file")


if __name__ == "__main__":
    main()
