from rest_framework import serializers
from .models import *
import datetime
import re
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import os
from website.tasks import pic_thumbnail

def tot_years(date):
    date_of_birth = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    today_date = datetime.datetime.now().date()
    date_diff = today_date - date_of_birth
    total_years = date_diff.days // 365

    return total_years


def generate_thumbnail(image):
    
    img = Image.open(image)
    thumbnail_size = (100, 100)
    img.thumbnail(thumbnail_size)
    thumbnail = Image.new('RGB', thumbnail_size)
    thumbnail.paste(img)
    return thumbnail

class Company_Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = Companies_table
        fields = "__all__"
    
    def validate(self, attrs):
        
        if (
            not re.search(
                "^(\+91[\-\s]?)?[0]?(91)?[789]\d{9}$", str(attrs["company_phone"]))
            or attrs["company_phone"] == ""
        ):
            raise serializers.ValidationError(
                {"phone": "phone fields should be in 10 digits or in proper format."}
            )
            
        if len(attrs['company_address']) < 30:
            raise serializers.ValidationError(
                {"Address": "Add full address"}
            )          
              
        return super().validate(attrs)


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Employees_table
        fields = (
            "fk_company_id",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
            "profile_pic",
            "profile_pic_thumbnail",
            "password",
            "password2"
        )
        extra_kwargs = {
            "password":{'write_only':True}
            }
    
    def validate(self, attrs):
             
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
            
        date_difference = tot_years(attrs["date_of_birth"])
        
        if datetime.datetime.strptime(attrs["date_of_birth"], "%Y-%m-%d").date() >= datetime.datetime.now().date() or date_difference < 18:
            raise serializers.ValidationError(
                {"Date_of_birth": "Date is invalid, you are under 18"}
            )
        try:
            with Image.open(attrs['profile_pic']) as img:
                if img.format not in ['JPEG', 'PNG','jpg','png']:
                    raise serializers.ValidationError("Only JPEG, PNG images are allowed.")
                
            with Image.open(attrs['profile_pic_thumbnail']) as img:
                if img.format not in ['JPEG', 'PNG','jpg','png']:
                    raise serializers.ValidationError("Only JPEG, PNG images are allowed.")
        except:
            
            raise serializers.ValidationError("Invalid image file.")

        return attrs


    def create(self, validated_data):
        request = self.context.get('request')
        # import pdb;pdb.set_trace()
        try:
            profile_pic = validated_data['profile_pic']
            profile_pic_thumbnail = validated_data['profile_pic_thumbnail']
            profile_pic_name = f"{request.data.get('username')}.jpg"
            profile_pic_path = default_storage.save(f"profile_pics/{profile_pic_name}", profile_pic)

            validated_data['profile_pic'] = profile_pic_path


            
            if profile_pic_thumbnail:
                # Call the Celery task to resize the profile picture thumbnail
                resized_profile_pic_thumbnail = pic_thumbnail(profile_pic_thumbnail)
                
                profile_pic_thumbnail_name = f"{request.data.get('username')}_thumb.jpg"
                profile_pic_thumbnail_path = default_storage.path(f"profile_thumbnails/{profile_pic_thumbnail_name}")
                resized_profile_pic_thumbnail.save(profile_pic_thumbnail_path, 'JPEG')
                validated_data['profile_pic_thumbnail'] = profile_pic_thumbnail_path
                



        except:
            raise serializers.ValidationError({" Unsuccess: somthing is wrong "})

        try:       
            company_id = int(request.data.get('fk_company_id'))
            company_table = Companies_table.objects.get(company_id = company_id)
            company_table.company_total_employees += 1
            company_table.save()
        except:
            raise serializers.ValidationError({"False Information : Mentioned company id is not a valid"})
        
        return Employees_table.objects.create_user(**validated_data)

class View_employee(serializers.ModelSerializer):
    class Meta:

        model = Employees_table
        fields = (
            "fk_company_id",
            "email",
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
            "profile_pic",
            "profile_pic_thumbnail"
        )
        
    def validate(self, attrs):
        return super().validate(attrs)

class Update_emp_info(serializers.Serializer):
  
    username = serializers.CharField(write_only = True,required = False)
    first_name = serializers.CharField(write_only = True,required = False)
    last_name = serializers.CharField(write_only = True,required = False)
    date_of_birth = serializers.CharField(write_only = True,required = False)
    profile_pic = serializers.ImageField(write_only = True,required = False)
    profile_pic_thumbnail = serializers.ImageField(write_only = True,required = False)

            
    def validate_profile_pic(self, value):
        # Remove the old profile picture file
        if value and self.instance.profile_pic:
            if os.path.isfile(self.instance.profile_pic.path):
                os.remove(self.instance.profile_pic.path)
        
        return value

    def validate_profile_pic_thumbnail(self, value):
        
        # Remove the old profile picture thumbnail file
        if value and self.instance.profile_pic_thumbnail:
            if os.path.isfile(self.instance.profile_pic_thumbnail.path):
                os.remove(self.instance.profile_pic_thumbnail.path)
        
        return value

    def update(self, instance, validated_data):

        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)

        request = self.context.get('request') 

        profile_pic = validated_data.get('profile_pic')
        
        if profile_pic:

            profile_pic_name = f"{instance.username}.jpg"
            profile_pic_path = default_storage.save(f"profile_pics/{profile_pic_name}", profile_pic)
            validated_data['profile_pic'] = profile_pic_path

        profile_pic_thumbnail = validated_data.get('profile_pic_thumbnail')
        
        if profile_pic_thumbnail:
            
            profile_pic_thumbnail_image = Image.open(profile_pic_thumbnail)
            resized_profile_pic_thumbnail = profile_pic_thumbnail_image.resize((100, 100))
            resized_profile_pic_thumbnail = resized_profile_pic_thumbnail.convert('RGB')
            profile_pic_thumbnail_name = f"{request.data.get('username')}_thumb.jpg"  # Replace with your desired filename logic
            profile_pic_thumbnail_path = default_storage.path(f"profile_thumbnails/{profile_pic_thumbnail_name}")
            resized_profile_pic_thumbnail.save(profile_pic_thumbnail_path, 'JPEG')

            validated_data['profile_pic_thumbnail'] = profile_pic_thumbnail_path
        instance.save()
        return instance