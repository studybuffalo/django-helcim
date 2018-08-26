import requests
import xmltodict


def post(url, post_data):
    """
    Make a POST request to the provided URL and return response
    as dictionary

    url: URL to post to
    post_data: dictionary of data to include with POST request
    """

    # Setup the POST header
    post_headers = {'content-type': 'text/plain; charset=utf-8'}

    # Make the POST request
    response = requests.post(url, post_data, headers=post_headers)

    # Error handling

    # Return the response
    return xmltodict.parse(response)

def purchase():
    """
    Makes a purchase request

    Will need to work out handling new card vs. token vs. customer code
    """

    pass

def refund():
    """
    Makes a refund request
    """

    pass

def verify():
    """
    Makes a verification request
    """

    pass

def preauthorize():
    """
    Makes a pre-authorization request
    """

    pass

def capture():
    """
    Makes a capture request (to complete a preauthorization)
    """

    pass
