from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    tg_user_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    username = models.CharField(max_length=30, unique=True)
    language_code = models.CharField(max_length=10, blank=True)
    is_premium = models.BooleanField(default=False)
    allows_write_to_pm = models.BooleanField(default=False)
    who_invited = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    auth_hash = models.CharField(max_length=1000, blank=True)

    # ton fields 
    wallet_address = models.CharField(max_length=66, blank=True)
    app_name = models.CharField(max_length=100, blank=True)

    has_paid = models.BooleanField(default=False)

    ton_balance = models.FloatField(default=0)
    goy_balance = models.FloatField(default=0)
    
    # analytics fields
    registred_at = models.DateTimeField(auto_now_add=True)

    @property
    def refferals(self):
        return User.objects.filter(who_invited=self)

    def __str__(self):
        return self.username
    
    class Meta:
        indexes = [
            models.Index(fields=['tg_user_id'])
        ]