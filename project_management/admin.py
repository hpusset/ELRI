from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from project_management.filters import PublicationStatusFilter
from project_management.forms import IntermediateDeliverableSelectForm, IntermediateDeliverableRejectForm
from project_management.models import ManagementObject
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator

csrf_protect_m = method_decorator(csrf_protect)


@admin.register(ManagementObject)
class ManagementObjectAdmin(admin.ModelAdmin):
    # class Media:
    #     js = ("admin/js/management_actions.js",)

    list_display = ('resource', 'id', 'to_be_delivered', 'delivered', 'is_rejected', 'publication_status',)
    list_filter = (PublicationStatusFilter, 'delivered', 'to_be_delivered', 'rejected')
    fields = ('related_resource', 'delivered', 'to_be_delivered', 'rejected', 'rejection_reason',)
    # search_fields = ('resource',)
    readonly_fields = ('related_resource',)

    actions = ('to_be_delivered', 'delivered', 'reject', 'restore_rejected')

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
    def to_be_delivered(self, request, queryset):
        # first check if the selected resources are eligible (not rejected or already delivered)
        # for this action before intermediate page
        if request.POST.get("action") == "to_be_delivered":
            action_eligible = True
            for item in queryset:
                if item.rejected:
                    action_eligible = False
                    messages.add_message(request, messages.ERROR,
                                         "ERROR: You cannot specify a deliverable on rejected resource \"{}\".".format(
                                             item))
                elif item.delivered:
                    messages.add_message(request, messages.WARNING,
                                         "Specify a \"to be\" deliverable on delivered resource \"{}\".".format(
                                             item))
            if not action_eligible:
                messages.add_message(request, messages.WARNING, "Please correct all errors and try again.")
                return

        if 'cancel' in request.POST:
            messages.add_message(request, messages.SUCCESS, "Cancelled setting deliverable.")
            return

        if 'to_be_delivered' in request.POST:
            form = IntermediateDeliverableSelectForm(request.POST)
            if form.is_valid():
                deliverable = form.cleaned_data['deliverable']
                for item in queryset:
                    item.to_be_delivered = deliverable
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
            'action': 'to_be_delivered'
        }

        return render_to_response('project_management/set_deliverable.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    to_be_delivered.short_description = "Mark Selected Resources as \"To be Delivered\""

    @csrf_protect_m
    def delivered(self, request, queryset):
        # first check if the selected resources are eligible (not rejected) for this action before intermediate page
        if request.POST.get("action") == "delivered":
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

        if 'delivered' in request.POST:
            form = IntermediateDeliverableSelectForm(request.POST)

            if form.is_valid():
                deliverable = form.cleaned_data['deliverable']
                for item in queryset:
                    item.delivered = deliverable
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
            'action': 'delivered'
        }
        return render_to_response('project_management/set_deliverable.html',
                                  dictionary,
                                  context_instance=RequestContext(request))

    delivered.short_description = "Mark Selected Resources as \"Delivered\""

    @csrf_protect_m
    def reject(self, request, queryset):
        # first check if the selected resources are eligible (not rejected) for this action before intermediate page
        if request.POST.get("action") == "reject":
            action_eligible = True
            for item in queryset:
                if item.delivered:
                    action_eligible = False
                    messages.add_message(request, messages.ERROR,
                                         "ERROR: You cannot reject the delivered resource \"{}\".".format(item))
                elif item.rejected:
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
        1. If object is delivered, it cannot be rejected or set to be delivered
        2. If object is rejected, no action on deliverables can be performed until it is restored
        3. We cannot reject a resource without specifying the rejection reason
        :type obj: management object to check
        :param form: the form to be validated
        :param obj:
        :return: tuple: (boolean, message)
        """
        # 1. If object is delivered, it cannot be rejected or set to be delivered
        if obj.delivered:
            if form.cleaned_data.get('rejected'):
                return False, "You cannot reject the delivered resource \"{}\".".format(obj)
            elif form.cleaned_data.get('to_be_delivered'):
                return True, "Do you need to specify a \"to be\" deliverable on delivered resource \"{}\"?".format(
                    obj), "Warning"

        # 2. If object is rejected, no action on deliverables can be performed until it is restored
        elif form.cleaned_data.get('rejected') and (
                    form.cleaned_data.get('delivered') or form.cleaned_data.get('to_be_delivered')):
            return False, "You cannot specify a deliverable on rejected resource \"{}\".".format(obj)

        # 3. We cannot reject a resource without specifying the rejection reason
        elif form.cleaned_data.get('rejected') and (not form.cleaned_data.get('rejection_reason')):
            return False, "You cannot reject resource \"{}\" without providing a rejection reason.".format(obj)

        return True, ""
