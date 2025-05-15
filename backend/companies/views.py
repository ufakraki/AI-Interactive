# backend/companies/views.py
from rest_framework import viewsets, permissions  # permissions'ı import ettik
from .models import Company
from .serializers import CompanySerializer
from core.permissions import IsCompanyUserOrAdmin
from rest_framework.permissions import IsAuthenticated

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated, IsCompanyUserOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', None) == 'superadmin':
            return Company.objects.all()
        return Company.objects.filter(id=getattr(user, 'company_id', None))