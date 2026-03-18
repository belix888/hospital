from __future__ import annotations

from django.http import HttpResponse
from rest_framework import status, viewsets
from rest_framework.response import Response

from reports.models import ReportJob, ReportKind, ReportStatus
from reports.serializers import CreateReportSerializer, ReportJobSerializer
from reports.services.excel import export_all_doctors_month, export_doctor_month
from scheduling.permissions import IsStaffOrDoctor
from scheduling.models import Appointment, AppointmentStatus


class ReportJobViewSet(viewsets.ModelViewSet):
    queryset = ReportJob.objects.all().order_by("-created_at")
    serializer_class = ReportJobSerializer
    permission_classes = [IsStaffOrDoctor]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_staff or u.is_superuser:
            return qs
        return qs.filter(requested_by=u)

    def create(self, request, *args, **kwargs):
        s = CreateReportSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        kind = s.validated_data["kind"]
        year = s.validated_data["year"]
        month = s.validated_data["month"]

        u = request.user
        params = {"year": year, "month": month}

        if kind == ReportKind.DOCTOR_MONTH:
            if not hasattr(u, "doctor_profile"):
                return Response({"detail": "Doctor profile required"}, status=status.HTTP_400_BAD_REQUEST)
            params["doctor_id"] = u.doctor_profile.id
        elif kind == ReportKind.ALL_DOCTORS_MONTH:
            if not (u.is_staff or u.is_superuser):
                return Response({"detail": "Staff only"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"detail": "Unknown kind"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate synchronously and return a downloadable file.
        appt_qs = (
            Appointment.objects.select_related("doctor", "patient", "room")
            .filter(
                status=AppointmentStatus.SCHEDULED,
                appointment_date__gte=f"{year}-{month:02d}-01",
                appointment_date__lt=f"{year + (1 if month == 12 else 0)}-{(1 if month == 12 else month + 1):02d}-01",
            )
            .order_by("appointment_date", "appointment_time", "doctor__name")
        )

        if kind == ReportKind.DOCTOR_MONTH:
            doctor = u.doctor_profile
            appts = appt_qs.filter(doctor=doctor)
            content = export_doctor_month(
                doctor_name=doctor.name,
                specialization=doctor.specialization,
                year=year,
                month=month,
                appointments=appts,
            )
            filename = f"appointments_{doctor.name.replace(' ', '_')}_{year}_{month:02d}.xlsx"
        else:
            content = export_all_doctors_month(year=year, month=month, appointments=appt_qs)
            filename = f"all_appointments_{year}_{month:02d}.xlsx"

        resp = HttpResponse(
            content,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        resp["Content-Disposition"] = f'attachment; filename="{filename}"'
        return resp

