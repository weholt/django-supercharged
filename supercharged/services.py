from dataclasses import dataclass, field
from enum import Enum, auto
from inspect import isclass
from typing import Dict, Generic, TypeVar

from django.contrib import messages
from django.shortcuts import render

T = TypeVar("T")


class ServiceProcessStatus(Enum):
    """
    Is the process complete, not started or failed.
    """

    UNPROCESSED = -1
    FAILED = 0
    OK = 1


@dataclass
class ServiceProcessResult(Generic[T]):
    """
    The result of a service process.
    """

    payload: T | None
    message: str = ""
    status: ServiceProcessStatus = ServiceProcessStatus.UNPROCESSED

    @classmethod
    def processed(cls, payload: T, message: str = ""):
        return cls(message=message, status=ServiceProcessStatus.OK, payload=payload)

    @classmethod
    def failed(cls, message: str = ""):
        return cls(message=message, status=ServiceProcessStatus.FAILED, payload=None)

    @property
    def success(self):
        return self.status == ServiceProcessStatus.OK


class ServiceException(Exception):
    """
    A generic exception raised by the service class below. Inherit and customize if needed.
    """

    class Level(Enum):
        debug = auto()
        info = auto()
        warning = auto()
        critical = auto()

    def __init__(self, title: str, message: str, level: Level = Level.info):
        super().__init__(title)
        self.title = title
        self.message = message
        self.level = level

    def __repr__(self):
        return f"[self.level] - {self.title}: {self.message}"

    def level_to_message(self, level):
        return {
            self.level.info: messages.INFO,
            self.level.debug: messages.DEBUG,
            self.level.warning: messages.WARNING,
            self.level.critical: messages.constants.ERROR,
        }[level]


class ServiceExceptionHandler:
    """ """

    def __init__(
        self,
        next_url: str = "",
        button_text: str = "",
        alternative_url: str = "",
        alternative_button_text: str = "",
        template: str = "service_message.html",
    ):
        self.next_url = next_url
        self.button_text = button_text
        self.alternative_url = alternative_url
        self.alternative_button_text = alternative_button_text
        self.template = template

    def __call__(self, function):
        def internal_function(request, *args, **kwargs):
            try:
                return function(request, *args, **kwargs)
            except ServiceException as ex:
                context = {
                    "message": ex.message,
                    "title": ex.title,
                    "level": ex.level,
                    "next_url": self.next_url,
                    "button_text": self.button_text,
                    "alternative_url": self.alternative_url,
                    "alternative_button_text": self.alternative_button_text,
                }
                return render(request, self.template, context)

        return internal_function


class ServiceProcessResultMissingException(Exception):
    pass


class ExpectedDifferentProductException(Exception):
    pass


class ExpectedProductGotNoneException(Exception):
    pass


class ExpectedNoProductException(Exception):
    pass


class ServiceCall:
    """ """

    def __init__(self, expected_product: object = None):
        self.expected_product = isclass(expected_product) or expected_product.__class__

    def __call__(self, function):
        def internal_function(request, *args, **kwargs):
            try:
                result = function(request, *args, **kwargs)

                if not isinstance(result, ServiceProcessResult):
                    raise ServiceProcessResultMissingException(
                        "A service call should produce a ServiceProcessResult"
                    )

                elif not self.expected_product and result.product is not None:
                    raise ExpectedNoProductException(
                        "This service call did not expect any product"
                    )

                elif self.expected_product and result.product is None:
                    raise ExpectedProductGotNoneException(
                        f"This service call did not produce the expected product: {self.expected_product!r}"
                    )

                elif (
                    self.expected_product
                    and result.product
                    and not isinstance(result.product, self.expected_product)
                ):
                    raise ExpectedDifferentProductException(
                        f"This service call did expect {self.expected_product!r} but got {result.product!r}"
                    )

                return result
            except ServiceException as ex:
                messages.add_message(
                    request, messages.INFO, "%s - %s" % (ex.title, ex.message)
                )

        return internal_function


class ServiceExceptionMessageHandler:
    """ """

    def __call__(self, function):
        def internal_function(request, *args, **kwargs):
            try:
                return function(request, *args, **kwargs)
            except ServiceException as ex:
                messages.add_message(
                    request, messages.INFO, "%s - %s" % (ex.title, ex.message)
                )

        return internal_function
