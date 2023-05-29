from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from website.serializer import *
from django.http import JsonResponse
from .permissions import *
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from .pagination import CustomPageNumberPagination
import django_filters.rest_framework
from PIL import Image
from django.db.models import Q
import io
from django.core.files.storage import default_storage
# Create your views here.


def send_mail(user, token, pk):
    # import pdb;pdb.set_trace()
    email = EmailMessage(
        subject="verify email",
        body=f"Hi verify your account by click this LINK \n \n  http://127.0.0.1:8000/verify/{token}/{pk}",
        to=[user],
    )
    email.send()


def verify(request, token, pk):
    # import pdb;pdb.set_trace()
    # breakpoint()
    user = Employees_table.objects.get(email=pk)
    user.is_active = True
    user.save()
    return HttpResponse("<h1>you have registerd succesfully </h1>")



# 
class Company_management(viewsets.ViewSet):
    queryset = Companies_table.objects.all()
    # pagination_class = CustomPageNumberPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["company_name","company_id"]
    permission_classes = [IsAdminUser_ForAdmin]
    
    def create(self,request):

        serializer = Company_Serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success":"Company added successfully"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        # import pdb;pdb.set_trace()
        company = Companies_table.objects.get(company_id=pk)
        serializer = Company_Serializer(company, data=request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request):
        user = Companies_table.objects.all()
        queryset = self.filter_queryset(user)
        paginator = CustomPageNumberPagination()
        objects = paginator.paginate_queryset(queryset, request)
        serializer = Company_Serializer(objects, many=True)
        return Response(serializer.data)

    '''http://127.0.0.1:8000/company/?comany_name=Radh'''

    def filter_queryset(self, queryset):
        
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        
        return queryset

    def retrieve(self, request, pk=None):
        try:
            user = Companies_table.objects.get(company_id=pk)
        except Companies_table.DoesNotExist:
            return Response(
                {"msg": "There is no User With this ID"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = Company_Serializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        try:
            Companies_table.objects.get(company_id=pk).delete()
        except Companies_table.DoesNotExist:
            return Response(
                {"msg": "NO data Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"msg": "Deleted Success"}, status=status.HTTP_200_OK)



"""REgister Employee"""
def image_resize(img):
    thumbnail_image = img
    if thumbnail_image.mode == 'RGBA':
        thumbnail_image = thumbnail_image.convert('RGB')
    thumbnail_image = Image.open(thumbnail_image)
    thumbnail_image = thumbnail_image.resize((100, 100))
    thumbnail_image_io = io.BytesIO()
    thumbnail_image.save(thumbnail_image_io, format='JPEG')
    thumbnail_image_io.seek(0)
    thumbnail_content = ContentFile(thumbnail_image_io.read())
    return thumbnail_content

class Register_ViewAPI(viewsets.ViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request):

        serializer = RegisterSerializer(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # import pdb;pdb.set_trace()
        pk = Employees_table.objects.get(email=request.data["email"])
        refresh = RefreshToken.for_user(pk)
        send_mail(serializer.data["email"], refresh.access_token, pk)
        context = {}
        context = dict(request.data)
        response_data = {
            "UserName": context["username"],
            "Email": context["email"],
            "Token Access": str(refresh.access_token),
            "Token Refresh": str(refresh),
        }
        return Response(data=response_data, status=status.HTTP_201_CREATED)

class View_Employee(viewsets.ViewSet):
    queryset = Companies_table.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ["first_name","email"]
    permission_classes = [IsAdminUser_ForAdmin]

    def list(self, request):
        user = Employees_table.objects.all()
        queryset = self.filter_queryset(user)
        paginator = CustomPageNumberPagination()
        objects = paginator.paginate_queryset(queryset, request)
        serializer = View_employee(objects,many=True)
        return Response(serializer.data)

    '''http://127.0.0.1:8000/company/?comany_name=Radh'''

    def filter_queryset(self, queryset):
        
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        
        return queryset


class ProfileImage_View(viewsets.ViewSet):
    
    permission_classes = [
        IsAuthenticated,
    ]
    parser_classes = [JSONParser, FormParser, MultiPartParser]
    
    def update(self, request, pk=None):

        usr = Employees_table.objects.get(id=pk)
        serializer = Update_emp_info(instance= usr, data=request.data,context={'request': request})

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        
    def destroy(self, request, pk=None):
        try:
            Employees_table.objects.get(username=request.user.username).delete()
        except Employees_table.DoesNotExist:
            return Response(
                {"msg": "NO data Found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"msg": "Image Deleted Success"}, status=status.HTTP_200_OK)



# class Employee_management(viewsets.ViewSet):
#     queryset = Employees_table.objects.all()
#     # pagination_class = CustomPageNumberPagination
#     filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
#     filterset_fields = ["name",'email']
#     permission_classes = [IsAdminUser_ForAdmin]

#     def list(self, request):
#         user = Companies_table.objects.all()
#         queryset = self.filter_queryset(user)
#         paginator = CustomPageNumberPagination()
#         objects = paginator.paginate_queryset(queryset, request)
#         serializer = List_emp_Serializer(objects, many=True)
#         return Response(serializer.data)

#     def filter_queryset(self, queryset):
#         for backend in list(self.filter_backends):
#             queryset = backend().filter_queryset(self.request, queryset, self)
#         return queryset







