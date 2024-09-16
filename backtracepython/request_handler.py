import os

import requests
import simplejson as json


class BacktraceRequestHandler:
    def __init__(self, submission_url, timeout, ignore_ssl_certificate, debug):
        self.submission_url = submission_url
        self.timeout = timeout
        self.ignore_ssl_certificate = ignore_ssl_certificate
        self.debug = debug

    def send(self, report, attachments):
        payload = json.dumps(report, ignore_nan=True, bigint_as_string=True)
        self.debug_api(
            "Submitting a payload to {},\n {}\n".format(self.submission_url, payload)
        )

        files = {"upload_file": payload}

        for attachment in attachments:
            if not os.path.exists(attachment):
                continue
            try:
                files["attachment_" + os.path.basename(attachment)] = (
                    attachment,
                    open(attachment, "rb"),
                    "application/octet-stream",
                )
            except Exception as e:
                self.debug_api(
                    "Cannot add attachment {}: {}".format(attachment, str(e))
                )
                continue

        try:
            with requests.post(
                url=self.submission_url,
                files=files,
                stream=True,
                verify=not self.ignore_ssl_certificate,
                timeout=self.timeout,
            ) as response:
                if response.status_code != 200:
                    response_body = json.loads(response.text)
                    result_rx = response_body["_rxid"]
                    self.debug_api("Report available with rxId {}".format(result_rx))
                    return result_rx
                self.debug_api(
                    "Received invalid status code {}. Data: {}".format(
                        response.status_code, response.text
                    )
                )
                return None
        except Exception as e:
            self.debug_api("Received submission failure. Reason: {}".format(str(e)))
        finally:
            return None

    def debug_api(self, message):
        if not self.debug:
            return

        print(message)
