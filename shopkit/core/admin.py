from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from shopkit.core.utils import get_model_from_string
from shopkit.core.settings import ORDERSTATE_CHANGE_MODEL


class PricedItemAdminMixin(object):
    """ Admin mixin for priced items. """
    def get_price(self, obj):
        price = obj.get_price()
        return price
    get_price.short_description = _('price')


class OrderStateChangeInline(admin.TabularInline):
    model = get_model_from_string(ORDERSTATE_CHANGE_MODEL)

    fields = ('date', 'state', )
    readonly_fields = ('date', 'state')

    extra = 0
    max_num = 0
    can_delete = False


class OrderItemInlineBase(admin.TabularInline):
    extra = 0

    readonly_fields = ('price', )
