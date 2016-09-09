from django.contrib.admin import widgets
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.html import format_html
from django.utils.text import Truncator


class ForeignKeyRawIdHiddenWidget(widgets.ForeignKeyRawIdWidget):
    input_type = 'hidden'

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.model._default_manager.using(self.db).get(**{key: value})
        except (ValueError, self.rel.model.DoesNotExist):
            return ''

        label = '&nbsp;<strong>{}</strong>'
        text = Truncator(obj).words(14, truncate='...')
        # try:
        #     change_url = reverse(
        #         '%s:%s_%s_change' % (
        #             self.admin_site.name,
        #             obj._meta.app_label,
        #             obj._meta.object_name.lower(),
        #         ),
        #         args=(obj.pk,)
        #     )
        # except NoReverseMatch:
        #     pass  # Admin not registered for target model.
        # else:
        #     text = format_html('<a href="{}">{}</a>', change_url, text)

        return format_html(label, text)