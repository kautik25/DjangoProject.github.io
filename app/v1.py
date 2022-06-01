from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.models import Group, User
from django.db.models import Q, F
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.contrib import messages
from app.form import (
    UserRegistrationForm,
    UserForm,
    UserProfileForm,
    UserResetPwdForm,
    BankCreateForm,
    BankUpdateForm,
    CardCreateForm,
    CardUpdateForm,
    SearchUserForm,
    SendMoneyForm,
    RequestMoneyForm,
    CompletePaymentForm,
)

from .models import (
    Profile,
    Account,
    Bank,
    Card,
    Transaction,
    PaymentMethod,
)
class Index(View):
    def get(self, request):
        return render(request, 'index.html')


class UserLogin(LoginView):
    def get_success_url(self):
        return reverse_lazy("index")


class UserLogout(LogoutView):
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse_lazy('user_login'))


class UserRegistration(CreateView):
    form_class = UserRegistrationForm
    model = User
    template_name = 'app/user_registration_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = form.save()
        password = form.cleaned_data['password']

        user.set_password(password)
        user.save()

        group = Group.objects.get(name='normal_user')
        user.groups.add(group)

        # Create User Profile model
        Profile.objects.create(user=user, birthday=form.clean_birthday(), address=form.clean_address())
        payment = PaymentMethod.objects.create(user=user, method_type='account')
        Account.objects.create(payment=payment)

        return HttpResponseRedirect(reverse_lazy('user_login'))


class UserResetPwd(UpdateView, PermissionRequiredMixin):
    form_class = UserResetPwdForm
    model = User
    template_name = 'app/user_reset_pwd_form.html'
    success_url = 'user_login'
    permission_required = 'app.change_user'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user

        password = form.cleaned_data['password']
        instance.user.set_password(password)
        instance.save()

        return HttpResponseRedirect(reverse_lazy('user_login'))


class UserProfile(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'app/user_profile_form.html'
    permission_required = 'app.view_profile'


class UserProfileUpdate(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    model = User
    form_class = UserForm
    template_name = 'app/user_profile_update.html'
    permission_required = 'app.change_profile'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(UserProfileUpdate, self).get_context_data(**kwargs)
        user = self.object
        profile = user.profile
        context['profile_form'] = UserProfileForm(instance=profile)
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.save()

        user_profile, create = Profile.objects.update_or_create(user=instance.user)
        user_profile.birthday = self.request.POST['birthday']
        user_profile.address = self.request.POST['address']

        user_profile.save()

        return HttpResponseRedirect(reverse_lazy('profile'))


class AccountList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'app/account_list.html'
    permission_required = 'app.view_account'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['nbar'] = 'account'
        context['account'] = Account.objects.filter(payment__user=user)
        return context


class AccountTransfer(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.change_account'

    def get(self, request, pk):
        account = get_object_or_404(
            Account,
            pk=pk,
        )
        return render(request, 'app/account_transfer_confirm.html', {'account': account, 'nbar': 'account'})

    def post(self, request, pk):
        Account.objects.filter(id=self.kwargs.get('pk')).update(balance=0)
        return HttpResponseRedirect(reverse_lazy('account'))


class BankList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'app/bank_list.html'
    permission_required = 'app.view_bank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['nbar'] = 'bank'
        context['bank_list'] = Bank.objects.filter(payment__user=user)
        return context


class BankCreate(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    form_class = BankCreateForm
    model = Bank
    template_name = 'app/bank_create.html'
    permission_required = 'app.add_bank'

    def get_context_data(self, **kwargs):
        context = super(BankCreate, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['nbar'] = 'bank'
        return context

    def form_valid(self, form):
        bank = form.save(commit=False)
        bank.user = self.request.user
        bank.method_type = 'bank'
        bank.owner_first_name = form.cleaned_data['owner_first_name']
        bank.owner_last_name = form.cleaned_data['owner_first_name']
        bank.routing_number = form.cleaned_data['routing_number']
        bank.account_number = form.cleaned_data['account_number']

        payment = PaymentMethod.objects.create(user=bank.user, method_type=bank.method_type)
        Bank.objects.create(payment=payment,
                            owner_last_name=bank.owner_last_name,
                            owner_first_name=bank.owner_first_name,
                            routing_number=bank.routing_number,
                            account_number=bank.account_number)

        return HttpResponseRedirect(reverse_lazy('bank'))


class BankDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_bank'

    def get(self, request, pk):
        bank = get_object_or_404(
            Bank,
            pk=pk,
        )

        return render(
            request,
            'app/bank_detail.html',
            {'bank': bank, 'user': bank.payment.user, 'nbar': 'bank'}
        )


class BankUpdate(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    model = Bank
    form_class = BankUpdateForm
    template_name = 'app/bank_update.html'
    permission_required = 'app.change_bank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nbar'] = 'bank'
        return context

    def get_success_url(self):
        bank_id = self.kwargs['pk']
        return reverse_lazy('bank_detail', kwargs={'pk': bank_id})


class BankDelete(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    model = Bank
    template_name = 'app/bank_confirm_delete.html'
    permission_required = 'app.delete_bank'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nbar'] = 'bank'
        return context

    def delete(self, request, *args, **kwargs):
        bank = Bank.objects.get(id=kwargs.get('pk'))
        bank.delete()
        return HttpResponseRedirect(reverse_lazy('bank'))


class CardList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'app/card_list.html'
    permission_required = 'app.view_card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['nbar'] = 'card'
        context['card_list'] = Card.objects.filter(payment__user=user)
        return context


class CardCreate(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    form_class = CardCreateForm
    model = Card
    template_name = 'app/card_create.html'
    permission_required = 'app.add_card'

    def get_context_data(self, **kwargs):
        context = super(CardCreate, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['nbar'] = 'card'
        return context

    def form_valid(self, form):
        card = form.save(commit=False)
        card.user = self.request.user
        card.method_type = 'card'
        card.owner_first_name = form.cleaned_data['owner_first_name']
        card.owner_last_name = form.cleaned_data['owner_first_name']
        card.card_number = form.cleaned_data['card_number']
        card.card_type = form.cleaned_data['card_type']
        card.security_code = form.cleaned_data['security_code']
        card.expiration_date = form.cleaned_data['expiration_date']

        payment = PaymentMethod.objects.create(user=card.user, method_type=card.method_type)
        Card.objects.create(payment=payment,
                            owner_last_name=card.owner_last_name,
                            owner_first_name=card.owner_first_name,
                            card_number=card.card_number,
                            card_type=card.card_type,
                            security_code=card.security_code,
                            expiration_date=card.expiration_date)

        return HttpResponseRedirect(reverse_lazy('card'))


class CardDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_card'

    def get(self, request, pk):
        card = get_object_or_404(
            Card,
            pk=pk
        )

        return render(
            request,
            'app/card_detail.html',
            {'card': card, 'user': card.payment.user, 'nbar': 'card'}
        )


class CardUpdate(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    model = Card
    form_class = CardUpdateForm
    template_name = 'app/card_update.html'
    permission_required = 'app.add_card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nbar'] = 'card'
        return context

    def get_success_url(self):
        card_id = self.kwargs['pk']
        return reverse_lazy('card_detail', kwargs={'pk': card_id})


class CardDelete(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    model = Card
    template_name = 'app/card_confirm_delete.html'
    permission_required = 'app.delete_card'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nbar'] = 'card'
        return context

    def delete(self, request, *args, **kwargs):
        card = Card.objects.get(id=kwargs.get('pk'))
        card.delete()

        return HttpResponseRedirect(reverse_lazy('card'))


class ActivityList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = Transaction
    template_name = 'app/activity_list.html'
    permission_required = 'app.view_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        """
        context['pay_list'] = Transaction.objects.filter(Q(creator=user, is_complete=True, transaction_type='send') |
                                                         Q(receiver=user, is_complete=True,
                                                           transaction_type='request')).order_by('-create_date')
        context['receive_list'] = Transaction.objects.filter(Q(receiver=user, is_complete=True, transaction_type='send') |
                                                            Q(creator=user, is_complete=True,
                                                            transaction_type='request')).order_by('-create_date')
        """
        context['pay_list'] = Transaction.objects.filter(Q(creator=user, transaction_type='send') |
                                                         Q(receiver=user,
                                                           transaction_type='request')).order_by('-create_date')
        context['receive_list'] = Transaction.objects.filter(Q(receiver=user, transaction_type='send') |
                                                            Q(creator=user,
                                                            transaction_type='request')).order_by('-create_date')

        return context


class SendSearchUser(LoginRequiredMixin, ListView):
    model = User
    form_class = SearchUserForm
    template_name = 'app/send_search_user_form.html'

    def get_queryset(self):
        try:
            username = self.kwargs['search_user']
        except:
            username = ''

        if username != '':
            object_list = self.model.objects.filter(username=username)
        else:
            object_list = self.model.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        context = super(SendSearchUser, self).get_context_data(**kwargs)
        query = self.request.GET.get("search_user")
        context['user'] = self.request.user

        if query:
            queryset = (Q(username=query))
            search_user = User.objects.filter(queryset).distinct()
            if not search_user:
                messages.error(self.request, 'No user found.')
        else:
            search_user = []

        context['search_user'] = search_user
        context['nbar'] = 'send'

        return context


class SendMoney(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    form_class = SendMoneyForm
    model = Transaction
    template_name = 'app/send_money_form.html'
    permission_required = 'app.add_transaction'

    def get_context_data(self, **kwargs):
        context = super(SendMoney, self).get_context_data(**kwargs)
        creator = self.request.user
        context['receiver'] = User.objects.get(id=self.kwargs.get('pk'))
        context['sender_payment_list'] = PaymentMethod.objects.filter(user=creator)
        context['nbar'] = 'send'
        return context

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.creator = self.request.user
        transaction.receiver = User.objects.get(id=self.kwargs.get('pk'))
        transaction.transaction_type = 'send'
        #transaction.is_complete = True
        transaction.is_complete = False
        transaction.category = form.clean_category()
        transaction.amount = form.cleaned_data['amount']
        transaction.description = form.clean_description()
        transaction.payment_method = form.clean_payment_method()

        creator_payment = PaymentMethod.objects.filter(user=transaction.creator,
                                                        method_id=transaction.payment_method.method_id)
        creator_account = Account.objects.filter(payment=creator_payment[0])
        if creator_account:
            creator_account.update(balance=F('balance') - transaction.amount)

        receiver_payment = PaymentMethod.objects.filter(user=transaction.receiver, method_type='account')
        receiver_account = Account.objects.filter(payment=receiver_payment[0])
        receiver_account.update(balance=F('balance')+transaction.amount)

        transaction.save()
        self.request.session['transaction_id'] = transaction.transaction_id
        #return HttpResponseRedirect(reverse_lazy('send_success'))
        #Paypal redirect
        #return redirect(reverse(paypal_payment_process))

        #Paytm redirect
        return redirect(reverse(paytm_payment_process))

class SendSuccess(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/send_success_page.html', {'nbar': 'send'})


class RequestSearchUser(LoginRequiredMixin, ListView):
    model = User
    form_class = SearchUserForm
    template_name = 'app/request_search_user_form.html'

    def get_queryset(self):
        try:
            username = self.kwargs['search_user']
        except:
            username = ''
        if username != '':
            object_list = self.model.objects.filter(username=username)
        else:
            object_list = self.model.objects.all()
        return object_list

    def get_context_data(self, **kwargs):
        context = super(RequestSearchUser, self).get_context_data(**kwargs)
        query = self.request.GET.get("search_user")
        context['user'] = self.request.user

        if query:
            queryset = (Q(username=query))
            search_user = User.objects.filter(queryset).distinct()
            if not search_user:
                messages.error(self.request, 'No user found.')
        else:
            search_user = []

        context['search_user'] = search_user
        context['nbar'] = 'request'

        return context


class RequestMoney(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    form_class = RequestMoneyForm
    model = Transaction
    template_name = 'app/request_money_form.html'
    permission_required = 'app.add_transaction'

    def get_context_data(self, **kwargs):
        context = super(RequestMoney, self).get_context_data(**kwargs)
        creator = self.request.user
        context['receiver'] = User.objects.get(id=self.kwargs.get('pk'))
        context['request_payment_list'] = PaymentMethod.objects.filter(user=creator)
        context['nbar'] = 'request'
        return context

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.creator = self.request.user
        transaction.receiver = User.objects.get(id=self.kwargs.get('pk'))
        transaction.transaction_type = 'request'
        transaction.is_complete = False
        transaction.category = form.clean_category()
        transaction.amount = form.cleaned_data['amount']
        transaction.description = form.clean_description()
        transaction.save()

        return HttpResponseRedirect(reverse_lazy('request_success'))


class RequestSuccess(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/request_success_page.html', {'nbar': 'request'})


class IncompleteTranList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = Transaction
    template_name = 'app/incomplete_list.html'
    permission_required = 'app.view_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['tran_creator_list'] = Transaction.objects.filter(creator=user, is_complete=False)
        context['tran_receiver_list'] = Transaction.objects.filter(receiver=user, is_complete=False)
        context['nbar'] = 'incomplete'
        return context


class IncompletePayment(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_transaction'

    def get(self, request, pk):
        transaction = get_object_or_404(
            Transaction,
            pk=pk
        )

        return render(
            request,
            'app/incomplete_payment.html',
            {'tran': transaction, 'user': self.request.user, 'nbar': 'incomplete'}
        )


class IncompletePaymentConfirm(LoginRequiredMixin, UpdateView, PermissionRequiredMixin):
    model = Transaction
    form_class = CompletePaymentForm
    template_name = 'app/payment_confirm.html'
    permission_required = 'app.change_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sender = self.request.user
        context['sender_list'] = PaymentMethod.objects.filter(user=sender)
        context['tran'] =  self.kwargs['pk']
        context['nbar'] = 'incomplete'
        return context

    def form_valid(self, form):
        transaction = form.save(commit=False)
        #transaction.is_complete = True
        transaction.is_complete = False
        transaction.payment_method = form.clean_payment_method()

        sender = self.request.user
        sender_payment = PaymentMethod.objects.filter(user=sender, method_id=transaction.payment_method.method_id)
        sender_account = Account.objects.filter(payment=sender_payment[0])
        if sender_account:
            sender_account.update(balance=F('balance') - transaction.amount)

        # receiver is the person who create the request (transaction creator at this point)
        receiver_payment = PaymentMethod.objects.filter(user=transaction.creator, method_type='account')
        receiver_account = Account.objects.filter(payment=receiver_payment[0])
        receiver_account.update(balance=F('balance')+transaction.amount)

        transaction.save()
        return HttpResponseRedirect(reverse_lazy('payment_complete'))


class PaymentComplete(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'app/payment_success.html', {'nbar': 'incomplete'})


class IncompleteRequest(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_transaction'

    def get(self, request, pk):
        transaction = get_object_or_404(
            Transaction,
            pk=pk
        )

        return render(
            request,
            'app/incomplete_request.html',
            {'tran': transaction, 'user': self.request.user, 'nbar': 'incomplete'}
        )


class IncompleteRequestDelete(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    model = Transaction
    template_name = 'app/request_delete.html'
    success_url = reverse_lazy('incomplete')
    permission_required = 'app.delete_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tran'] = self.kwargs['pk']
        context['nbar'] = 'incomplete'
        return context


class StaffUserList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'staff/user_list.html'
    permission_required = 'app.view_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_list'] = User.objects.filter(is_staff=False)
        return context


class StaffUserInfo(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_user'

    def get(self, request, pk):
        user = get_object_or_404(
            User,
            pk=pk
        )

        return render(
            request,
            'staff/user_information.html',
            {'user': user}
        )


class StaffUserTran(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'staff/user_transaction_list.html'
    permission_required = 'app.view_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.kwargs['pk']
        context['tran_list'] = Transaction.objects.filter(Q(receiver=target_user) |
                                                          Q(creator=target_user)).order_by('-create_date')
        context['user'] = User.objects.get(id=self.kwargs.get('pk'))
        return context


class StaffUserTranDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_transaction'

    def get(self, request, pk, tpk):
        user = get_object_or_404(
            User,
            pk=pk
        )

        tran = get_object_or_404(
            Transaction,
            pk=tpk
        )

        return render(
            request,
            'staff/user_transaction_detail.html',
            {'user': user, 'tran': tran}
        )


class StaffUserTranDelete(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.delete_transaction'

    def get(self, request, pk, tpk):
        user = get_object_or_404(
            User,
            pk=pk
        )

        tran = get_object_or_404(
            Transaction,
            pk=tpk
        )
        return render(
            request,
            'staff/user_transaction_delete.html',
            {'user': user, 'tran': tran}
        )


    def post(self, request, pk, tpk):
        tran = Transaction.objects.get(transaction_id=tpk)

        creator_payment = PaymentMethod.objects.filter(user=tran.creator, method_type='account')
        creator_account = Account.objects.filter(payment=creator_payment[0])
        creator_account.update(balance=F('balance') + tran.amount)

        receiver_payment = PaymentMethod.objects.filter(user=tran.receiver, method_type='account')
        receiver_account = Account.objects.filter(payment=receiver_payment[0])
        receiver_account.update(balance=F('balance') - tran.amount)
        tran.delete()
        return HttpResponseRedirect(reverse_lazy('staff_user_tran', kwargs={'pk': pk}))


class StaffUserPayment(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = User
    template_name = 'staff/user_payment_list.html'
    permission_required = ('app.view_account', 'app.view_bank', 'app.view_card')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.kwargs['pk']

        context['account'] = Account.objects.filter(payment__user=user)
        context['bank_list'] = Bank.objects.filter(payment__user=user)
        context['card_list'] = Card.objects.filter(payment__user=user)
        context['user'] = User.objects.get(id=self.kwargs.get('pk'))
        return context


class StaffUserBankDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = ('app.view_bank')
    def get(self, request, pk, bpk):
        user = get_object_or_404(
            User,
            pk=pk
        )

        bank = get_object_or_404(
            Bank,
            pk=bpk
        )

        return render(
            request,
            'staff/user_bank_detail.html',
            {'user': user, 'bank': bank}
        )


class StaffUserCardDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_card'

    def get(self, request, pk, cpk):
        user = get_object_or_404(
            User,
            pk=pk
        )

        card = get_object_or_404(
            Card,
            pk=cpk
        )

        return render(
            request,
            'staff/user_card_detail.html',
            {'user': user, 'card': card}
        )


class StaffTransactionList(LoginRequiredMixin, ListView, PermissionRequiredMixin):
    model = Transaction
    template_name = 'staff/transaction_list.html'
    permission_required = 'app.view_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tran_list'] = Transaction.objects.all()
        return context


class StaffTranDetail(LoginRequiredMixin, View, PermissionRequiredMixin):
    permission_required = 'app.view_transaction'

    def get(self, request, pk):
        tran = get_object_or_404(
            Transaction,
            pk=pk
        )

        return render(
            request,
            'staff/transaction_detail.html',
            {'tran': tran}
        )


class StaffTranDelete(LoginRequiredMixin, DeleteView, PermissionRequiredMixin):
    model = Transaction
    template_name = 'staff/transaction_delete.html'
    permission_required = 'app.delete_transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tran'] = self.kwargs['pk']
        return context

    def delete(self, request, *args, **kwargs):
        tran = Transaction.objects.get(transaction_id=kwargs.get('pk'))

        creator_payment = PaymentMethod.objects.filter(user=tran.creator, method_type='account')
        creator_account = Account.objects.filter(payment=creator_payment[0])
        creator_account.update(balance=F('balance') + tran.amount)

        receiver_payment = PaymentMethod.objects.filter(user=tran.receiver, method_type='account')
        receiver_account = Account.objects.filter(payment=receiver_payment[0])
        receiver_account.update(balance=F('balance') - tran.amount)

        tran.delete()
        return HttpResponseRedirect(reverse_lazy('staff_transaction'))

"""
#DCAVENUE views
#from importd import d
from django.dispatch import receiver
from django.urls import reverse, get_mod_func
from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from .utils import generate_order_id, enc_request, dec_response
from app import POST_URL

@d("/start/", name="dcavenue-start")
def start(request):
    order_id = request.REQUEST.get("Order_Id")
    if not order_id:
        order_id = generate_order_id()
    enc_request_data = enc_request(request, order_id=order_id)
    request.session["dcavenue_order_id"] = order_id

    return HttpResponse(
        
            #<html>
            #    <head><title>Redirecting...</title></head>
            #    <body>
            #        <form method="post" name="redirect" action="%s">
            #            <input type="hidden" name="encRequest" value="%s">
            #            <input type="hidden" name="Merchant_Id" value="%s">
            #        </form>
            #    </body>
            #    <script language='javascript'>
            #        document.redirect.submit();
            #    </script>
            #</html>
            % (POST_URL, enc_request_data, settings.DCAVENUE["MERCHANT_ID"])
    )


@csrf_exempt
@d("/callback/", name="dcavenue-callback")
def callback(request):
    enc_response = request.REQUEST["encResponse"]
    if not enc_response:
        raise Http404("No encResponse")

    data = dec_response(request, enc_response)

    if not data:
        raise Http404("Checksum Failed")

    order_id = request.session["dcavenue_order_id"]

    if order_id:
        del request.session["dcavenue_order_id"]
    else:
        raise Http404("No order id in session")

    if order_id != data["Order_Id"]:
        raise Http404("Invalid orderid")

    cb_module, cb_method = get_mod_func(
        settings.DCAVENUE.get("CALLBACK", "paybills.app.utils.default_callback")
    )
    cb = getattr(__import__(cb_module, {}, {}, ['']), cb_method)

    return cb(request, data)
"""
"""
#django-payments view functions
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from payments import get_payment_model, RedirectNeeded

def payment_details(request, payment_id):
    payment = get_object_or_404(get_payment_model(), id=payment_id)
    try:
        form = payment.get_form(data=request.POST or None)
    except RedirectNeeded as redirect_to:
        return redirect(str(redirect_to))
    return TemplateResponse(request, 'payment.html',
                            {'form': form, 'payment': payment})
"""

#django-paypal views
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentsForm
from django.shortcuts import redirect
from django.urls import reverse

@csrf_exempt
def paypal_payment_done(request):
    """
    Activated when payment is successful
    """
    return render(request, 'app/paypal_done.html')

@csrf_exempt
def paypal_payment_canceled(request):
    """
    Activated when payment is canceled
    """
    return render(request, 'app/paypal_canceled.html')

def paypal_payment_process(request):
    """
    Activated when user clicks on pay button
    """
    transaction_id = request.session.get('transaction_id')
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    host = request.get_host()
    print(settings.PAYPAL_RECEIVER_EMAIL)

    paypal_dict = {
        'business' : str(settings.PAYPAL_RECEIVER_EMAIL),
        'amount' : transaction.amount,
        'item_name': transaction.description,
        'invoice': str(transaction.transaction_id),
        'currency_code' : 'USD',
        'notify_url' : 'http://{}{}'.format(host, reverse('paypal-ipn')),
        'return_url' : 'http://{}{}'.format(host, reverse(paypal_payment_done)),
        #'return_url' : 'http://{}{}'.format(host, reverse('paypal_done')),
        'cancel_return' : 'http://{}{}'.format(host, reverse(paypal_payment_canceled)),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'app/paypal_process.html', {'form':form, 'transaction':transaction})

from . import PaytmChecksum

def paytm_payment_process(request):
    transaction_id = request.session.get('transaction_id')
    transaction = get_object_or_404(Transaction, transaction_id=transaction_id)
    host = request.get_host()

    merchant_key = settings.PAYTM_SECRET_KEY
    print('http://{}{}'.format(host, reverse('paytm_callback')))

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.transaction_id)),
        ('CUST_ID', str(transaction.creator.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        #('CALLBACK_URL', 'http://127.0.0.1:8000/paytm_callback/'),
        ('CALLBACK_URL', 'http://{}{}'.format(host, reverse('paytm_callback'))),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = PaytmChecksum.generateSignature(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    print('paytm_params', paytm_params)
    return render(request, 'app/paytm_redirect.html', context=paytm_params)

@csrf_exempt
def paytm_callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = PaytmChecksum.verifySignature(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'app/paytm_callback.html', context=received_data)
        return render(request, 'app/paytm_callback.html', context=received_data)
