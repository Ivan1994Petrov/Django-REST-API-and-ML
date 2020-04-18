from django.db import transaction

from rest_framework import viewsets
from rest_framework import mixins

from apps.endpoints.models import \
    Endpoint, \
    MLAlgorithm, \
    MLAlgorithmStatus, \
    MLRequest
from apps.endpoints.serialize import \
    EndpointSerialize, \
    MLAlgorithmSerialize, \
    MLAlgorithmStatusSerialize, \
    MLRequestSerialize

class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = EndpointSerialize
    queryset = Endpoint.objects.all()


class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    serializer_class = MLAlgorithmSerialize
    queryset = MLAlgorithm.objects.all()


def deactivate_other_status(instance):
    old_statuses = MLAlgorithmStatus.objects.filder(parent_mlalgorithm = instance.parent_mlalgorithm,
                                                    created_at_lt=instance.created_at,
                                                    active=True)
    for i in range(len(old_statuses)):
        old_statuses[i].active = False

    MLAlgorithmStatus.objects.bulk_update(old_statuses, ['active'])


class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    serializer_class = MLAlgorithmStatusSerialize
    queryset = MLAlgorithmStatus.objects.all()

    def perform_create(self, serialize):
        try:
            with transaction.atomic():
                instance = serialize.save(active=True)
                deactivate_other_status(instance)

        except Exception as e:
            raise APIExeptions(str(e))


class MLRequestViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    serializer_class = MLRequestSerialize
    queryset = MLRequest.objects.all()
