from __future__ import annotations

from rest_framework import serializers

from reports.models import ReportJob


class ReportJobSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = ReportJob
        fields = ["id", "kind", "status", "params", "file_url", "error", "created_at", "finished_at"]

    def get_file_url(self, obj: ReportJob):
        request = self.context.get("request")
        if not obj.file:
            return None
        url = obj.file.url
        if request:
            return request.build_absolute_uri(url)
        return url


class CreateReportSerializer(serializers.Serializer):
    kind = serializers.ChoiceField(choices=["doctor_month", "all_doctors_month"])
    year = serializers.IntegerField(min_value=2000, max_value=2100)
    month = serializers.IntegerField(min_value=1, max_value=12)

