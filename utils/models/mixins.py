class ObjectOwnerMixin:
    """
    Restrict access to the endpoint to the owner of the object.
    """

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(owner=self.request.user)

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PreserveInitialFieldValueMixin:
    """
    Mixin to save initial values of fields before save.

    preserved filed should be specified in _preserved_fields attribute.
    fields can be accessed as self._initial_field_name
    """

    _preserved_fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._preserved_fields = self.get_preserved_fields()
        for field in self._preserved_fields:
            setattr(self, f"_initial_{field}", getattr(self, field))

    def get_preserved_fields(self):
        return self._preserved_fields
