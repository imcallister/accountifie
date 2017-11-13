from datetime import datetime
from decimal import Decimal

from django.db.models import Model as djangoModel
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from . import exceptions


class AllChoices(object):
    def __contains__(self, value):
        return True


class AlwaysValidValidator(object):
    def validate(self, val):
        return True


class BaseField(object):
    def __init__(self, kwargs):
        self.transform = kwargs.pop('transform', lambda val:val)


class Field(BaseField):
    position = 0

    def __init__(self, **kwargs):
        super(Field, self).__init__(kwargs)
        self.null = kwargs.pop("null", False)
        self.default = kwargs.pop("default", None)
        if self.default and not self.null:
            raise exceptions.FieldError("You cannot provide a default without setting the field as nullable")
        if 'row_num' in kwargs:
            self.position = kwargs.pop('row_num')
        else:
            self.position = Field.position
            Field.position += 1
        if 'match' in kwargs:
            self.match = kwargs.pop('match')
        self.validator = kwargs.pop('validator', AlwaysValidValidator)
        if 'multiple' in kwargs:
            self.has_multiple = kwargs.pop('multiple')
        self.prepare = kwargs.pop('prepare', lambda val:val)
        if 'keys' in kwargs and isinstance(self, ComposedKeyField):
            self.keys = kwargs.pop('keys')
        self.choices = kwargs.pop('choices', AllChoices())
        if len(kwargs) > 0:
            raise ValueError("Arguments %s unexpected" % list(kwargs.keys()))

    def get_transform_method(self, instance):
        """ Look for transform_<field_name>, else look for the transform parameter, else identity method """
        transform_method = "transform_" + getattr(self, "fieldname", self.field_name)
        transform = getattr(instance, transform_method, self.transform)
        return transform

    def get_prep_value(self, value, instance=None):
        try:
            value = self.prepare(value)
            transform = self.get_transform_method(instance)
            value = transform(value)

            if not value and self.null:
                value = self.default
            else:
                value = self.to_python(value)
            if value not in self.choices:
                if not self.null:
                    raise exceptions.ChoiceError("Value \'%s\' does not belong to %s" % (value, self.choices))
                value = None
            if not self.validator().validate(value):
                raise exceptions.FieldError(self.validator.validation_message)
            return value
        except exceptions.ChoiceError:
            raise
        except exceptions.FieldError:
            raise
        except ValueError:
            self.raise_type_error(value)

    def raise_type_error(self, value):
        raise ValueError("Value \'%s\' in columns %d does not match the expected type %s" %
                             (value, self.position + 1, self.__class__.field_name))


class IntegerField(Field):
    field_name = "Integer"

    def to_python(self, value):
        return int(value)


class BooleanField(Field):
    field_name = "Boolean"

    def default_is_true_method(self, value):
        return value.lower() == "true"

    def __init__(self, *args, **kwargs):
        if 'is_true' in kwargs:
            self.is_true_method = kwargs.pop('is_true')
        else:
            self.is_true_method = self.default_is_true_method
        super(BooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return self.is_true_method(value)


class CharField(Field):
    field_name = "String"

    def to_python(self, value):
        return value


class DateField(Field):
    field_name = "Date"

    def __init__(self, *args, **kwargs):
        if 'format' in kwargs:
            self.format = kwargs.pop('format')
        else:
            self.format = "%d/%m/%Y"
        super(DateField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return datetime.strptime(value, self.format)


class DecimalField(Field):
    field_name = "A Decimal number"

    def to_python(self, value):
        return Decimal(value)


class FloatField(Field):
    field_name = "A float number"

    def to_python(self, value):
        return float(value)


class IgnoredField(Field):
    field_name = "Ignore the value"


class DjangoModelField(Field):
    field_name = "not defined"

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', 'pk')
        if len(args) < 1:
            raise ValueError("You should provide a Model as the first argument.")
        self.model = args[0]
        try:
            if not issubclass(self.model, djangoModel):
                raise TypeError("The first argument should be a django model class.")
        except TypeError:
            raise TypeError("The first argument should be a django model class.")
        super(DjangoModelField, self).__init__(**kwargs)

    def to_python(self, value):
        try:
            return self.model.objects.get(**{self.pk: value})
        except ObjectDoesNotExist:
            raise exceptions.ForeignKeyFieldError("No match found for %s, %s:%s" % (self.model.__name__, self.pk, value), self.model.__name__, value)
        except MultipleObjectsReturned:
            raise exceptions.ForeignKeyFieldError("Multiple match found for %s" % self.model.__name__, self.model.__name__, value)


class ComposedKeyField(DjangoModelField):
    def to_python(self, value):
        try:
            return self.model.objects.get(**value)
        except ObjectDoesNotExist:
            raise exceptions.ForeignKeyFieldError("No match found for %s" % self.model.__name__, self.model.__name__, value)
