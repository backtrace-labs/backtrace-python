from backtracepython.client import construct_submission_url

universe = "test"
hostname = "https://{}.sp.backtrace.io".format(universe)
token = "1234567812345678123456781234567812345678123456781234567812345678"

submit_url = "https://submit.backtrace.io/{}/{}/json".format(universe, token)


def test_direct_submission_url():
    expected_direct_submission_url = "{}/post?token={}&format=json".format(
        hostname, token
    )
    assert construct_submission_url(hostname, token) == expected_direct_submission_url


def test_submit_submission_url():
    assert construct_submission_url(submit_url, None) == submit_url


def test_submit_submission_url_when_token_available():
    assert construct_submission_url(submit_url, token) == submit_url
