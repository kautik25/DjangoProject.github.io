from django.shortcuts import get_object_or_404
"""
from .models import Transaction
from paypal.standard.ipn.signals import valid_ipn_received, invalid_ipn_received
from django.dispatch import receiver

@receiver(valid_ipn_received)
def payment_notification_valid(sender, **kwargs):
    print("valid_ipn_received")
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        transaction = get_object_or_404(Transaction, transaction_id=int(ipn.invoice))
        print("mc_gross", ipn.mc_gross)

        if transaction.amount == ipn.mc_gross:
            # mark the transaction as completed
            transaction.is_complete = True
            transaction.save()

@receiver(invalid_ipn_received)
def payment_notification_invalid(sender, **kwargs):
    print("invalid_ipn_received")
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        transaction = get_object_or_404(Transaction, transaction_id=int(ipn.invoice))
        print("mc_gross", ipn.mc_gross)

        if transaction.amount == ipn.mc_gross:
            # mark the transaction as completed
            transaction.is_complete = True
            transaction.save()
"""