from rest_framework import serializers
from .models import *

from rest_framework import serializers
from .models import Register

class RegisterSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Register
        fields = '__all__'


    


from rest_framework import serializers
from .models import *

from rest_framework import serializers
from .models import Register

class RegisterSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Register
        fields = '__all__'
# serializers.py
from rest_framework import serializers

class DoctorLoginSerializer(serializers.Serializer):
    doctor_id = serializers.CharField(max_length=100)
    email = serializers.EmailField()

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100, write_only=True)

class DoctorSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = tbl_doctor
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        
        # Convert images to /media/ paths
        if instance.id_proof:
            rep['id_proof'] = f"/media/{instance.id_proof}"  # /media/id_proofs/idcard.jpg
        if instance.doctor_image:
            rep['doctor_image'] = f"/media/{instance.doctor_image}"  # /media/doctor_images/d1.jpeg
        
        return rep




from rest_framework import serializers
from .models import PredictionResult

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PredictionResult
        fields = "__all__"
        read_only_fields = ("result", "extracted_data", "created_at")
