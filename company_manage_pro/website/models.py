from django.db import models
from django.contrib.auth.hashers import make_password,check_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

"""
Take below data tables with mentioned fields (you may add more fields as you require)
Companies table: id (primary key) company_name (required)
-Employees table: id (primary key), first_name (required), 
last_name (required), company_id (foreign key to Company's primary key),
profile_pic, profile_pic_thumbnail(100x100 size of thumb mage), 
email_address"""

class Companies_table(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=400, blank=False)
    company_type = models.CharField(max_length=400, blank=False)
    company_owner = models.CharField(max_length=250, blank=False)
    company_address = models.CharField(max_length=400, blank=False)
    company_phone = models.CharField(max_length=100,blank=False,unique=True)
    company_total_employees = models.IntegerField(blank=True,default=0)
    
    def __str__(self):
        return str(self.company_id)
    
class MyUserManager(BaseUserManager):
    
    def create_user(self,fk_company_id,email,username,first_name,date_of_birth,profile_pic,profile_pic_thumbnail,last_name,password = None,password2 =None):
        if not fk_company_id:
            raise ValueError("The 'fk_company_id' field is required for regular users.")
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            password=password,
        )
        user.fk_company_id = fk_company_id
        user.first_name=first_name
        user.last_name=last_name
        user.date_of_birth = date_of_birth
        user.profile_pic = profile_pic
        user.profile_pic_thumbnail = profile_pic_thumbnail
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_superuser(self,email,username,password=None):

        user = self.model(
            email= self.normalize_email(email),
            username= username,
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using = self._db)
        return user


class Employees_table(AbstractBaseUser):
    
    
    fk_company_id = models.ForeignKey(Companies_table,to_field='company_id',related_name='employees_id',on_delete=models.CASCADE,blank=True,null=True)
    email = models.EmailField(max_length=90,verbose_name='email',unique=True)
    username = models.CharField(max_length=255, unique=True, db_index=True)
    first_name = models.CharField(max_length=90,verbose_name='first name')
    last_name =models.CharField(max_length=90,verbose_name='last name')
    date_of_birth   =   models.CharField(max_length=350,blank= True)
    profile_pic     = models.ImageField(upload_to='profile_pics')    
    profile_pic_thumbnail = models.ImageField(upload_to='profile_thumbnails')
    is_active =models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff =models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    objects= MyUserManager() 
    
    def __str__(self):
        return self.email

