import requests
import xmltodict


def post(url, post_data={}):
    """Makes POST to Helcim API and provides response as dictionary.

    Args:
        url (str): URL to the Helcim API.
        post_data (dict): The parameters to pass with the POST request.

    Returns:
        dict: The API response.

    Raises:
        ValueError: TBD.

    """

    # Setup the POST header
    post_headers = {'content-type': 'text/plain; charset=utf-8'}

    # Make the POST request
    response = requests.post(url, post_data, headers=post_headers)

    # Error handling

    # Return the response
    return xmltodict.parse(response)

def purchase():
    """Makes a purchase request
    """
    # TODO: Will need to work out handling new card vs. token vs. customer code

    pass

def refund():
    """Makes a refund request
    """

    pass

def verify():
    """Makes a verification request
    """

    pass

def preauthorize():
    """Makes a pre-authorization request
    """

    pass

def capture():
    """Makes a capture request (to complete a preauthorization)
    """

    pass
