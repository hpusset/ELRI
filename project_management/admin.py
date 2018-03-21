from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from project_management.filters import PublicationStatusFilter, DeliveredFilter, ToBeDeliveredFilter
from project_management.forms import IntermediateDeliverableSelectForm, IntermediateDeliverableRejectForm
from project_management.models import ManagementObject
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

csrf_protect_m = method_decorator(csrf_protect)


@admin.register(ManagementObject)
class ManagementObjectAdmin(admin.ModelAdmin):
    # class Media:
    #     js = ("admin/js/management_actions.js",)
    list_display = ('resource', 'id', 'partner_responsible', 'to_be_delivered_to_EC', 'delivered_to_EC',
                    'is_processed_version', 'is_rejected', 'publication_status', 'to_be_delivered_odp',
                    'delivered_odp',)
    list_filter = (PublicationStatusFilter, 'partner_responsible', DeliveredFilter,
                   ToBeDeliveredFilter, 'is_processed_version', 'rejected', 'to_be_delivered_odp', 'delivered_odp',)

    fieldsets = (
        ('EC Project', {
            'fields': (
                'related_resource', 'partner_responsible', 'delivered_to_EC', 'to_be_delivered_to_EC',
                'is_processed_version', 'rejected',
                'rejection_reason',)
        }),
        ('EU Open Data Portal', {
            'fields': ('to_be_delivered_odp', 'delivered_odp'),
        }),
    )

    readonly_fields = ('related_resource', 'is_processed_version', 'partner_responsible')

    actions = ('to_be_delivered_to_ec', 'delivered_to_ec', 'reject', 'restore_rejected', 'to_be_delivered_to_odp',
               'delivered_to_odp')

    # Set \"To be Delivered\"
    # form = ManagementObjectForm

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or \
               request.user.groups.filter(name='elrcReviewers').exists()

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or \
               request.user.groups.filter(name='elrcReviewers').exists()

    @staticmethod
    def related_resource(obj):
        return mark_safe(u'<span style="font-size:1.2em; font-weight:bold">%s</span>' % obj.resource)

    def is_rejected(self, obj):
        return "YES" if obj.rejected else "NO"

    is_rejected.short_description = "Rejected"

    def publication_status(self, obj):
        return obj.resource.storage_object.get_publication_status_display()

    publication_status.short_description = "Publication Status"

    # ACTIONS
    @csrf_protect_m
    def to_be_delivered_to_ec(self, request, queryset):
        # first check if the selected resources are eligible (not rejected or already delivered)
        # for this action before intermediate page
        if request.POST.get("action") == "to_be_delivered_to_ec":
            action_eligible = True
            for item in queryset:
                if item.rejected:
                    action_eligible = False
                    messages.add_message(request, messages.ERROR,
                                         "ERROR: You cannot specify a deliverable on rejected resource \"{}\".".format(
                                             item))
                elif item.delivered_to_EC:
                    messages.add_message(request, messages.WARNING,
                                         "Specify a \"to be\" deliverable on delivered resource \"{}\".".format(
                                             item))
            if not action_eligible:
                messages.add_message(request, messages.WARNING, "Please correct all errors and try again.")
                return

        if 'cancel' in request.POST:
            messages.add_message(request, messages.SUCCESS, "Cancelled setting deliverable.")
            return

        if 'to_be_delivered_to_ec' in request.POST:
            form = IntermediateDeliverableSelectForm(request.POST)
            if form.is_valid():
                deliverable = form.cleaned_data['deliverable']
                for item in queryset:
                    item.to_be_delivered_to_EC = deliverable
                    item.save()
                self.message_user(request, "Deliverable %s added to selected resources" % deliverable)
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = IntermediateDeliverableSelectForm(
                initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
            'selected_resources': queryset,
            'form': form,
            'path': request.get_full_path(),
            'action': 'to_be_delivered_to_ec'
        }

        return render_to_response('project_management/set_deliverable.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    to_be_delivered_to_ec.short_description = "Mark Selected Resources as \"To be Delivered to EC\""

    @csrf_protect_m
    def delivered_to_ec(self, request, queryset):
        # first check if the selected resources are eligible (not rejected) for this action before intermediate page
        if request.POST.get("action") == "delivered_to_ec":
            action_eligible = True
            for item in queryset:
                if item.rejected:
                    action_eligible = False
                    messages.add_message(request, messages.ERROR,
                                         "ERROR: You cannot specify a deliverable on rejected resource \"{}\".".format(
                                             item))
            if not action_eligible:
                messages.add_message(request, messages.WARNING, "Please correct all errors and try again.")
                return

        if 'cancel' in request.POST:
            self.message_user(request, 'Cancelled setting deliverable.')
            return

        if 'delivered_to_ec' in request.POST:
            form = IntermediateDeliverableSelectForm(request.POST)

            if form.is_valid():
                deliverable = form.cleaned_data['deliverable']
                for item in queryset:
                    item.delivered_to_EC = deliverable
                    item.save()
                self.message_user(request, "Deliverable %s added to selected resources" % deliverable)
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = IntermediateDeliverableSelectForm(
                initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
            'selected_resources': queryset,
            'form': form,
            'path': request.get_full_path(),
            'action': 'delivered_to_ec'
        }
        return render_to_response('project_management/set_deliverable.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    delivered_to_ec.short_description = "Mark Selected Resources as \"Delivered to EC\""

    @csrf_protect_m
    def reject(self, request, queryset):
        # first check if the selected resources are eligible (not rejected) for this action before intermediate page
        if request.POST.get("action") == "reject":
            action_eligible = True
            for item in queryset:
                # if item.delivered_to_EC:
                #     action_eligible = False
                #     messages.add_message(request, messages.ERROR,
                #                          "ERROR: You cannot reject the delivered resource \"{}\".".format(item))
                if item.rejected:
                    action_eligible = False
                    messages.add_message(request, messages.ERROR,
                                         "ERROR: Resource \"{}\" is already rejected due "
                                         "to the following reason: {}.".format(item, item.rejection_reason))
            if not action_eligible:
                messages.add_message(request, messages.WARNING, "Please correct all errors and try again.")
                return

        if 'cancel' in request.POST:
            self.message_user(request, 'Cancelled setting deliverable.')
            return

        if 'reject' in request.POST:
            form = IntermediateDeliverableRejectForm(request.POST)
            final_to_reject = list()

            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                for item in queryset:
                    if not item.rejected:
                        final_to_reject.append(item)
                    item.rejection_reason = rejection_reason
                    item.rejected = True
                    item.save()
                self.message_user(request, "The selected resources have been rejected")
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = IntermediateDeliverableRejectForm(
                initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})

        dictionary = {
            'selected_resources': queryset,
            'form': form,
            'path': request.get_full_path(),
            'action': 'reject'
        }
        return render_to_response('project_management/reject.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    reject.short_description = "Reject Selected Resources"

    @csrf_protect_m
    def restore_rejected(self, request, queryset):
        for obj in queryset:
            if obj.rejected:
                obj.rejected = False
                obj.save()

    restore_rejected.short_description = "Restore Selected Rejected Resources"

    def get_actions(self, request):
        result = super(ManagementObjectAdmin, self).get_actions(request)

        if 'delete_selected' in result:
            del result['delete_selected']

        return result

    # ACTIONS
    @csrf_protect_m
    def to_be_delivered_to_odp(self, request, queryset):
        if self.has_change_permission(request, queryset):
            successful = 0
            for obj in queryset:
                if not obj.to_be_delivered_odp:
                    obj.to_be_delivered_odp = True
                    obj.save()
                    successful += 1
            if successful > 0:
                messages.info(request,
                              'Successfully marked {} resources as \"To be delivered to ODP\".'.format(successful))
            else:
                messages.warning(request, 'No resources have been marked as \"To be delivered to ODP\"')
        else:
            messages.error(request, 'You do not have the permission to '
                                    'perform this action for all selected resources.')

    to_be_delivered_to_odp.short_description = "Mark Selected Resources as \"To be Delivered to ODP\""

    @csrf_protect_m
    def delivered_to_odp(self, request, queryset):
        if self.has_change_permission(request, queryset):
            successful = 0
            for obj in queryset:
                if not obj.to_be_delivered_odp and not obj.delivered_odp:
                    obj.to_be_delivered_odp = True
                    obj.delivered_odp = True
                    obj.save()
                    successful += 1
                elif obj.to_be_delivered_odp and not obj.delivered_odp:
                    obj.delivered_odp = True
                    obj.save()
                    successful += 1
            if successful > 0:
                messages.info(request,
                              'Successfully marked {} resources as \"Delivered to ODP\".'.format(successful))
            else:
                messages.warning(request, 'No resources have been marked as \"Delivered to ODP\"')
        else:
            messages.error(request, 'You do not have the permission to '
                                    'perform this action for all selected resources.')

    delivered_to_odp.short_description = "Mark Selected Resources as \"Delivered to ODP\""

    def save_model(self, request, obj, form, change):
        validation = self.validate_form(obj, form)
        is_valid = validation[0]
        message = validation[1]
        warning = None
        try:
            warning = validation[2]
        except IndexError:
            pass
        if is_valid:
            if warning:
                messages.warning(request, message)
            super(ManagementObjectAdmin, self).save_model(request, obj, form, change)
        else:
            messages.set_level(request, messages.ERROR)
            messages.error(request, message)

    @staticmethod
    def validate_form(obj, form):
        """
        Validates the management object form to be saved.
        1. If object is delivered, it cannot be rejected or set to be delivered (disabled)
        2. If object is rejected, no action on deliverables can be performed until it is restored
        3. We cannot reject a resource without specifying the rejection reason
        :type obj: management object to check
        :param form: the form to be validated
        :param obj:
        :return: tuple: (boolean, message)
        """
        # 1. If object is delivered, it cannot be rejected or set to be delivered (disable that)
        # if obj.delivered_to_EC:
        #     # if form.cleaned_data.get('rejected'):
        #     #     return False, "You cannot reject the delivered resource \"{}\".".format(obj)
        #     if form.cleaned_data.get('to_be_delivered_to_EC'):
        #         return True, "Do you need to specify a \"to be\" deliverable on delivered resource \"{}\"?".format(
        #             obj), "Warning"

        # 2. If object is rejected, no action on deliverables can be performed until it is restored
        # if form.cleaned_data.get('rejected') and (
        #             form.cleaned_data.get('delivered') or form.cleaned_data.get('to_be_delivered_to_EC')):
        #     return False, "You cannot specify a deliverable on rejected resource \"{}\".".format(obj)

        # 3. We cannot reject a resource without specifying the rejection reason
        if form.cleaned_data.get('rejected') and (not form.cleaned_data.get('rejection_reason')):
            return False, "You cannot reject resource \"{}\" without providing a rejection reason.".format(obj)

        return True, ""
