from django.db import models
from django.contrib.auth.models import User

class RazerUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="razer_users",)
    email = models.CharField(max_length=255,unique=True)  
    password = models.CharField(max_length=255)
    secret_key= models.CharField(max_length=255,null=True,blank=True) 
    regionNumber=models.IntegerField(null=True,blank=True) 

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email}-{self.password} (linked to {self.user.username})"
    

class UserFileHistory(models.Model):
    razer_user = models.ForeignKey("RazerUser", on_delete=models.CASCADE, related_name="file_history")
    file = models.FileField(upload_to="user_files/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File for {self.razer_user.email} at {self.created_at}"

    def get_download_url(self):
        return self.file.url  # This will be accessible via MEDIA_URL
