.. _examples:

========
Examples
========

The following are examples of how to integrate ``django-helcim`` into
a service requiring payment processing. These are not intended to be
comprehensive, but should highlight the major functionality.

More robust examples can be found within the sandbox sites. Details of
these can be can be found on the :ref:`Sandbox page <sandbox>`.

You can also find explicit details of supported functionality and
allowable options for all the ``django-helcim`` functions and classes
on the :ref:`package documentation pages <helcim>`.

.. note::

    These instructions make a distinction between making direct
    calls to the Helcim Commerce API versus using Helcim.js.
    Within this documentation, "Helcim API" refers to direct calls,
    where as "Helcim.js" will refere to calls via Helcim.js.

----------------------
Basic Helcim API Calls
----------------------

You will most likely integrate ``django-helcim`` into your application
during a POST request to submit payment information. There is typically
a significant amount of handling to properly collect payment
information and ensure a secure user experience; this example will
focus exclusively on how you would integrate with ``django-helcim`` and
not touch on the finer considerations of implementing a service that
requires payment processing.

To streamline collection of payment information, you will probably
utilize a Django form class.

.. code-block:: python

    # forms.py

    from django import forms

    class PaymentForm(forms.Form):
        cc_name = forms.CharField(max_length=128)
        cc_number = forms.CharField(max_length=16)
        cc_expiry = forms.CharField(max_length=4)
        cc_cvv = forms.CharField(max_length=4)
        amount = forms.DecimalField(decimal_places=2)

Next you will need some view to receive the form POST request and
integrate with ``django-helcim``.

.. code-block:: python

    # views.py
    form django.views.generic.edit import FormView

    from helcim.exceptions import ProcessingError, PaymentError
    from helcim.gateway import Purchase

    from .forms import PaymentForm

    class PaymentView(FormView):
        form_class = PaymentForm
        template_name = 'example_app/example_template.html'

        def post(self, request, *args, **kwargs):
            form = self.form_class(request.POST)

            if form.is_valid():
                # Prepare data for API submission with a django-helcim
                # gateway class
                purchase = Purchase(
                    save_token=True,
                    django_user=self.request.user,
                    cc_name=form.cleaned_data['cc_name'],
                    cc_number=form.cleaned_data['cc_number'],
                    cc_expiry=form.cleaned_data['cc_expiry'],
                    cc_cvv=form.cleaned_data['cc_cvv'],
                    amount=form.cleaned_data['amount'],
                )

                # Attempt to make the API calls
                try:
                    transaction, token = purchase.process()
                except ValueError as error:
                    # Add handling for ValuError
                    pass
                except ProcessingError as error:
                    # Add handling for ProcessingError
                    # These would usually be server-side errors and
                    # not suitable for end user display
                    pass
                except PaymentError as error
                    # Add handling for PaymentError
                    # These are some error that has caused payment to
                    # fail (e.g. expired card, incorrect card number)
                    pass

                # Add any final handling before redirecting user
                return self.form_valid()

            # Some error has occured during validation
            return self.form_invalid()

.. note::

    This is a generic form and form view implementation; you will need
    to customize to your specific use case.

Gateways
========

``django-helcim`` provides a variety of ``gateway`` classes to help
streamline Helcim API calls. These classes represent the types of
calls you can make to the API. Currently you can do the following:

* ``Purchase()``: a purchase or sale API call
* ``Preauthorize()``: a preauthorization API call
* ``Capture()``: a capture API call
* ``Refund()``: a refund API call
* ``Verification()``: a verification or card tokenization API call

These gateways will allow you a consistent way to make API calls in
a Python-based manner and not worry about data conversions and API
authentication. Data will undergo some basic validation to ensure
there are no type or format errors, but will not undergo any validation
to ensure the call succeeds (e.g. you will not be notified that the
credit card is expired or that you are missing details that the
Helcim API requires).

---------------
Helcim.js Calls
---------------

Helcim.js provides a way to reduce your risk and security requirements
when it comes to managing credit card data. In short, Helcim.js
will intercept any payment calls to your server and instead direct
them to the Helcim API server for processing directly. You will then
receive an API response to your call.

This is a significantly different workflow than a normal Helcim API
call, so ``django-helcim`` provides an additional ``gateway`` class
to assist with these workflows.

You will likely still require some standard way to collect payment
information (e.g. a Django form or coding the form manually in a
Django template). This is not covered extensively in this example as
this is more a requirement of Helcim.js than ``django-helcim``. If you
need assistance with this, it is recommended you view the Developer
Documentation on the Helcim website.

To assist with Helcim.js implementation, ``django-helcim`` provides
a mixin that lets you declare Helcim.js configuration details within
your Django settings and then add them to a template via the context
variable.

.. code-block:: python

    # settings.py

    DJANGO_HELCIM_CONFIG = {
        'purchase': {
            'url': 'https://myhelcim.com/js/version2.js',
            'token': 'abdefg',
        },
        'preauthorization': {
            'url':  'https://myhelcim.com/js/version2.js',
            'token': 'hijklmnop',
        }
    }

.. code-block:: python

    # views.py
    form django.views.generic.edit import FormView

    from helcim.mixins import HelcimJSMixin

    from .forms import PaymentForm

    class HelcimJSPaymentView(HelcimJSMixin, FormView):
        form_class = PaymentForm
        template_name = 'example_app/example_template.html'

.. code-block:: html

    <!-- example_template.html -->
    <!-- SCRIPT -->
    <script type="text/javascript" src="{{ helcim_js.purchase.url }}"></script>

    <!-- FORM -->
    <form name="helcimForm" id="helcimForm" action="" method="POST">
        <input type="hidden" id="token" value="{{ helcim_js.purchase.token }}">
    </form>

Once you have made Helcim.js call, you will receive the response for
handling. You will need to handle both possible errors from the call
(e.g. expired credit card) and success calls. ``django-helcim``
provides a helper class to manage these responses and create the
relevant ``django-helcim`` model instances.

.. code-block:: python

    # views.py
    form django.views.generic.edit import FormView

    from helcim.gateway import HelcimJSResponse

    from .forms import PaymentForm

    class PaymentView(FormView):
        # FormView used to allow a Django form to be used to help
        # with templating; it is not actually required for handling
        # the Helcim.js response
        form_class = PaymentForm
        template_name = 'example_app/example_template.html'

        def post(self, request, *args, **kwargs):
            response = HelcimJSResponse(
                response=request.POST,
                save_token=True,
                django_user=request.user,
            )

            # If response is valid, can save details and redirect
            if response.is_valid():
                transaction, token = response.record_purchase()

                # form_valid() used to trigger a success URL redirect
                return self.form_valid()

            # Invalid form submission/payment - render payment details
            # again. Could manage various error responses here for a
            # better user experience
            form = self.get_form()

            return self.form_invalid(form)

The ``HelcimJSResponse`` class has three methods that can be used to
provide the action supported by Helcim.js. Currently these are:

* ``record_purchase()``: a purchase or sale call
* ``record_preauthorization()``: a preauthorization API call
* ``record_verification()``: a verification or card tokenization API call
