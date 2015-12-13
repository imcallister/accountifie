import locale

from django.template import Library

from accountifie.gl.models import Company

register = Library()

@register.filter
def currency(value, arg = '', symbol = True):
    '''
    Currency formatting template filter.

    Takes a number -- integer, float, decimal -- and formats it according to
    the locale specified as the template tag argument (arg). Examples:

      * {{ value|currency }}
      * {{ value|currency:"en_US" }}
      * {{ value|currency:"pt_BR" }}
      * {{ value|currency:"pt_BR.UTF8" }}

    If the argument is omitted, the default system locale will be used.

    The third parameter, symbol, controls whether the currency symbol will be
    printed or not. Defaults to true.

    As advised by the Django documentation, this template won't raise
    exceptions caused by wrong types or invalid locale arguments. It will
    return an empty string instead.

    Be aware that currency formatting is not possible using the 'C' locale.
    This function will fall back to 'en_US.UTF8' in this case.
    '''

    saved = locale.getlocale()
    given = arg and ('.' in arg and str(arg) or (arg, 'UTF8'))

    if saved == (None, None) and given == '':
        given = 'en_US.UTF8'

    try:
        locale.setlocale(locale.LC_ALL, given)

        return locale.currency(value, symbol, True)

    except (TypeError, locale.Error):
        return ''

    finally:
        locale.setlocale(locale.LC_ALL, saved)

@register.filter
def company_color(cid):
    try:
        company = Company.objects.get(pk=cid)
        return company.color_code or '#000'
    except Company.DoesNotExist:
        return '#000'
