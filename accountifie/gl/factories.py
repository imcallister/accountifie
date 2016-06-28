import factory
from .models import Company, Counterparty, Account, ExternalAccount

class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    id = 'TEST_COMPANY'
    name = 'Test Company'
    cmpy_type = 'ALO'


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account


class CounterpartyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Counterparty

    id = 'TEST_CP'
    name = 'Test Counterparty'

class ExternalAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExternalAccount
