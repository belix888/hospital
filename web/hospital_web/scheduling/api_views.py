from __future__ import annotations

from datetime import datetime

from django.utils.timezone import now as tz_now
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from clinic.models import Doctor
from scheduling.models import Appointment
from scheduling.permissions import IsStaffOrDoctor
from scheduling.serializers import AppointmentSerializer
from scheduling.services.booking import create_appointment, extend_appointment, finish_appointment_now, get_available_rooms
from scheduling.services.monitoring import build_room_monitoring_view


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related("doctor", "patient", "room").all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsStaffOrDoctor]

    def get_queryset(self):
        qs = super().get_queryset()
        u = self.request.user
        if u.is_staff or u.is_superuser:
            return qs
        if hasattr(u, "doctor_profile"):
            return qs.filter(doctor=u.doctor_profile)
        return qs.none()

    def create(self, request, *args, **kwargs):
        u = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vd = serializer.validated_data
        try:
            doctor: Doctor
            if u.is_staff or u.is_superuser:
                doctor = vd.get("doctor")
                if not doctor:
                    return Response({"detail": "doctor_id is required for staff"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                doctor = u.doctor_profile
            appt = create_appointment(
                doctor=doctor,
                patient=vd["patient"],
                room=vd["room"],
                appointment_date=vd["appointment_date"],
                appointment_time=vd["appointment_time"],
                duration_minutes=vd["duration_minutes"],
                notes=vd.get("notes", ""),
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        out = self.get_serializer(instance=appt)
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def extend(self, request, pk=None):
        # staff can extend any; doctors can extend only own (enforced by get_object)
        extra = int(request.data.get("extra_minutes", 0))
        try:
            self.get_object()
            appt = extend_appointment(appointment_id=int(pk), extra_minutes=extra)
        except (ValueError, Appointment.DoesNotExist) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(instance=appt).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        try:
            self.get_object()
            appt = finish_appointment_now(appointment_id=int(pk))
        except (ValueError, Appointment.DoesNotExist) as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(instance=appt).data, status=status.HTTP_200_OK)


class RoomMonitorView(APIView):
    permission_classes = [IsStaffOrDoctor]

    def get(self, request):
        date_str = request.GET.get("date") or datetime.now().strftime("%Y-%m-%d")
        vm = build_room_monitoring_view(date_str=date_str)
        # serialize minimal response
        return Response(
            {
                "date": vm["date_str"],
                "now": tz_now().isoformat(),
                "rooms": [
                    {
                        "room_id": l.room_id,
                        "room_name": l.room_name,
                        "is_busy_now": l.is_busy_now,
                        "busy_until": l.busy_until,
                        "current_doctor_name": l.current_doctor_name,
                        "upcoming_time": l.upcoming_time,
                        "upcoming_doctor_name": l.upcoming_doctor_name,
                    }
                    for l in vm["lines"]
                ],
            },
            status=status.HTTP_200_OK,
        )


class AvailableRoomsView(APIView):
    permission_classes = [IsStaffOrDoctor]

    def get(self, request):
        try:
            d = request.GET.get("date") or ""
            t = request.GET.get("time") or ""
            duration = int(request.GET.get("duration_minutes") or 60)
            if not d or not t:
                raise ValueError("date and time are required")
            appointment_date = datetime.strptime(d, "%Y-%m-%d").date()
            appointment_time = datetime.strptime(t, "%H:%M").time()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        rooms = get_available_rooms(appointment_date=appointment_date, appointment_time=appointment_time, duration_minutes=duration)
        return Response(
            [{"id": r.id, "name": r.name} for r in rooms],
            status=status.HTTP_200_OK,
        )

