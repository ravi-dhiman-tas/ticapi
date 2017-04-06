from rest_framework import exceptions
from rest_framework.permissions import AllowAny
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger import renderers

import urlparse
import coreapi
from rest_framework.schemas import SchemaGenerator
from openapi_codec.utils import get_location
from openapi_codec import encode


def _custom_get_responses(link):
    if not link.action in link._api_docs:
        return {}
    else:
        if not 'responses' in link._api_docs[link.action]:
            return {}
        else:
            return link._api_docs[link.action]['responses']


def _custom_get_parameters(link, encoding):
    """
    Generates Swagger Parameter Item object.
    """
    if not link.action in link._api_docs:
        api_docs_fields = []
    else:
        api_docs_fields = link._api_docs[link.action]['fields']

    parameters = []
    for field in api_docs_fields:
        parameter = {
            'name': field['name'],
            'required': field['required'] if 'required' in field else False,
            'in': field['paramType'] if 'paramType' in field else 'formData',
            'description': field['description'],
            'type': field['type'] or 'string',
        }
        parameters.append(parameter)

    for field in link.fields:
        location = get_location(link, field)
        parameter = {
            'name': field.name,
            'required': field.required,
            'in': location,
            'description': field.description,
            'type': field.type or 'string',
        }
        parameters.append(parameter)

    return parameters


#encode._get_responses = _custom_get_responses
encode._get_parameters = _custom_get_parameters


class CustomSchemaGenerator(SchemaGenerator):

    def get_link(self, path, method, view):
        """
        Return a `coreapi.Link` instance for the given endpoint.
        """

        fields = self.get_path_fields(path, method, view)
        fields += self.get_serializer_fields(path, method, view)
        fields += self.get_pagination_fields(path, method, view)
        fields += self.get_filter_fields(path, method, view)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, view)
        else:
            encoding = None

        description = self.get_description(path, method, view)

        if self.url and path.startswith('/'):
            path = path[1:]

        data_link = coreapi.Link(
            url=urlparse.urljoin(self.url, path),
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=description
        )

        data_link._api_docs = self.get_api_docs(path, method, view)

        return data_link

    def get_api_docs(self, path, method, view):
        return view.api_docs if hasattr(view, 'api_docs') else {}


def get_swagger_view(title=None, url=None):
    """
    Returns schema view which renders Swagger/OpenAPI.
    """

    class SwaggerSchemaView(APIView):
        _ignore_model_permissions = True
        exclude_from_schema = True
        permission_classes = [AllowAny]
        renderer_classes = [
            CoreJSONRenderer,
            renderers.OpenAPIRenderer,
            renderers.SwaggerUIRenderer
        ]

        def get(self, request):
            generator = CustomSchemaGenerator(title=title, url=url)  # this is altered line
            schema = generator.get_schema(request=request)
            if not schema:
                raise exceptions.ValidationError(
                    'The schema generator did not return a schema   Document'
                )
            return Response(schema)

    return SwaggerSchemaView.as_view()
