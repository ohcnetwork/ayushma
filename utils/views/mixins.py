from rest_framework.response import Response


class PartialUpdateModelMixin:
    def perform_update(self, serializer):
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class GetSerializerClassMixin:
    def get_serializer_class(self):
        """
        A class which inherits this mixins should have variable
        `serializer_action_classes`.

        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class SampleViewSet(viewsets.ViewSet):
            serializer_class = DocumentSerializer
            serializer_action_classes = {
               "upload": UploadDocumentSerializer,
               "download": DownloadDocumentSerializer,
            }

            @action
            def upload:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.
        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


class GetPermissionClassesMixin:
    def get_permissions(self):
        """
        A class which inherits this mixins should have variable
        `permission_action_classes`.

        Look for permission classes in self.permission_action_classes, which
        should be a dict mapping action name (key) to
        permission class instances (iterable),
        i.e.:

        class SampleViewSet(viewsets.ViewSet):
            permission_classes = (IsAuthenticated,)
            permission_action_classes = {
               "upload": (IsAuthenticatedOrReadOnly(), IsAdminUser()),
               "download": (AllowAny(),),
            }

            @action
            def upload:
                ...

        If there's no entry for that action then just fallback to the regular
        get_permissions.
        """
        try:
            return self.permission_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_permissions()
