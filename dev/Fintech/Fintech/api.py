from Fintech.models import Report, File
from Fintech.users import is_site_manager
from rest_framework import routers, serializers, generics
from django.db.models import Q


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = File
        fields = ('id','title', 'upload_date', 'is_encrypted', 'upload')

class ReportSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Report
        fields = ('id','title','timestamp', 'company_name', 'company_ceo', 'company_phone', 'company_location', 'company_country',
                  'sector', 'industry', 'current_projects', 'is_private')


class ReportList(generics.ListAPIView):
    serializer_class = ReportSerializer

    def get_queryset(self):
        user = self.request.user;

        if is_site_manager(user):
            return Report.objects.all()
        #List of permissions for each group that the user belongs to
        groupPermissions = [g.reportpermissions_set.all() for g in user.groups.all()]
        return Report.objects.filter(Q(is_private=False) 
            | Q(permissions__in=user.reportpermissions_set.all()) 
            | Q(permissions__in=[item for sublist in groupPermissions for item in sublist]))


class ReportFiles(generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        report = self.kwargs['reportID']
        return File.objects.filter(report__pk=report)