from rest_framework.permissions import AllowAny

class CompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]