from django.db import models
from django.contrib.auth.models import User

BANK_CHOICES = [
    ("Malayan Banking Berhad", "Malayan Banking Berhad"),
    ("CIMB Group Holdings", "CIMB Group Holdings"),
    ("Public Bank Berhad", "Public Bank Berhad"),
    ("RHB Bank", "RHB Bank"),
    ("Hong Leong Bank", "Hong Leong Bank"),
    ("AmBank", "AmBank"),
    ("UOB Malaysia", "UOB Malaysia"),
    ("Bank Rakyat", "Bank Rakyat"),
    ("OCBC Bank Malaysia", "OCBC Bank Malaysia"),
    ("HSBC Bank Malaysia", "HSBC Bank Malaysia"),
    ("Bank Islam Malaysia", "Bank Islam Malaysia"),
    ("Affin Bank", "Affin Bank"),
    ("Alliance Bank Malaysia Berhad", "Alliance Bank Malaysia Berhad"),
    ("Standard Chartered Bank Malaysia", "Standard Chartered Bank Malaysia"),
    ("MBSB Bank Berhad", "MBSB Bank Berhad"),
    ("Citibank Malaysia", "Citibank Malaysia"),
    ("Bank Simpanan Nasional (BSN)", "Bank Simpanan Nasional (BSN)"),
    ("Bank Muamalat Malaysia Berhad", "Bank Muamalat Malaysia Berhad"),
    ("Agrobank", "Agrobank"),
    ("Al-Rajhi Malaysia", "Al-Rajhi Malaysia"),
    ("Co-op Bank Pertama", "Co-op Bank Pertama"),
    ("MBSB Bank", "MBSB Bank")
    ]

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    bank_name = models.CharField(max_length=100, choices=BANK_CHOICES)
    account_number = models.CharField(max_length=18)
    phone_number = models.CharField(max_length=12, null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name}'