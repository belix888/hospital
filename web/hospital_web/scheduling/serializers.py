from rest_framework import serializers

from clinic.models import Doctor, Patient, Room
from scheduling.models import Appointment


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "is_available"]


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "specialization", "phone", "email", "is_active"]


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ["id", "name", "phone", "birth_date"]


class AppointmentSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source="doctor",
        write_only=True,
        required=False,
        allow_null=True,
    )
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), source="patient", write_only=True)
    room_id = serializers.PrimaryKeyRelatedField(queryset=Room.objects.all(), source="room", write_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor",
            "patient",
            "room",
            "doctor_id",
            "patient_id",
            "room_id",
            "appointment_date",
            "appointment_time",
            "duration_minutes",
            "status",
            "notes",
            "created_at",
        ]

