from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from companies.models import Company  # Doğru import: companies uygulamasından Company modelini al
from .models import User
from companies.serializers import CompanySerializer  # Doğru import: companies uygulamasından CompanySerializer'ı al
from .serializers import UserSerializer
from .permissions import IsCompanyUserOrAdmin
from rest_framework.permissions import IsAuthenticated

class CompanyView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]
    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) == 'superadmin':
            companies = Company.objects.all()
        else:
            companies = Company.objects.filter(id=getattr(user, 'company_id', None))
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)

class UserView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]
    def get(self, request):
        user = request.user
        if getattr(user, 'role', None) == 'superadmin':
            users = User.objects.all()
        else:
            users = User.objects.filter(company=getattr(user, 'company', None))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsCompanyUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'superadmin':
            return User.objects.all()
        return User.objects.filter(company=getattr(user, 'company', None))