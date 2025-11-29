from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer

class LoginView(APIView):
    """
    Login endpoint for:
    - Hospital Doctor
    - Normal User 
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        

        # --- Hospital Doctor Login ---
        hospital_doc = tbl_hospital_doctor_register.objects.filter(email=email, password=password).first()
        if hospital_doc:
            if hospital_doc.status != 'approved':
                return Response(
                    {'message': 'Hospital doctor account not approved yet. Please wait for admin approval.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response({
                'id': hospital_doc.id,
                'name': hospital_doc.name,
                'email': hospital_doc.email,
                'phone': hospital_doc.hospital_phone,
                'role': hospital_doc.role,
                'password': hospital_doc.password,
            }, status=status.HTTP_200_OK)

        # --- Normal User Login ---
        user = Register.objects.filter(email=email, password=password).first()
        if user:
            return Response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'password': user.password,
                'phone':user.phone,
                'role': user.role
            }, status=status.HTTP_200_OK)

        # --- Invalid Credentials ---
        return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


#  Hospital Doctor ViewSet
class HospitalDoctorRegisterViewSet(viewsets.ModelViewSet):
    queryset = tbl_hospital_doctor_register.objects.all()
    serializer_class = HospitalDoctorRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    

import google.generativeai as genai
import os
from dotenv import load_dotenv
from django.conf import settings

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY not found in .env file")

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Create Gemini model instance
model = genai.GenerativeModel('gemini-2.5-flash')

# ✅ PCOD-related keywords
PCOD_KEYWORDS = [
    "pcod", "pcos", "ovarian cysts", "hormonal imbalance", "irregular periods",
    "missed periods", "menstrual irregularities", "infertility", "fertility",
    "ovulation", "testosterone", "estrogen", "progesterone", "acne", "hair loss",
    "weight gain", "obesity", "insulin resistance", "sugar levels", "metformin",
    "diet", "exercise", "stress", "thyroid", "ultrasound", "fertility issues",
    "menstrual cycle", "periods", "ovaries", "pelvic pain", "cramps", "treatment",
    "lifestyle", "symptoms", "diagnosis", "medication", "medicine", "remedies",
    "doctor", "consultation", "counselling", "blood test", "scan", "reproductive health"
]

# Greeting keywords
GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]

# ✅ Chatbot API for PCOD conversations
class ChatbotAPIView(APIView):
    def post(self, request):
        user_message = request.data.get("message", "").lower().strip()

        if not user_message:
            return Response({
                "type": "error",
                "reply": "Message is empty."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Greeting responses
        if any(greet in user_message for greet in GREETINGS):
            return Response({
                "type": "greeting",
                "reply": "Hello! 😊 I'm your PCOD health assistant. You can ask me anything about PCOD symptoms, treatment, diet, or lifestyle tips."
            })

        # Check if message is PCOD-related
        if not any(keyword in user_message for keyword in PCOD_KEYWORDS):
            return Response({
                "type": "not_related",
                "reply": "I can only help with PCOD-related topics such as symptoms, causes, treatments, and lifestyle advice."
            })

        try:
            # Generate PCOD-specific answer
            response = model.generate_content(
                f"You are a women's health assistant focused on PCOD. "
                f"Provide accurate, friendly, and supportive answers about PCOD — including symptoms, treatment, fertility, "
                f"diet, and emotional health. Avoid unrelated topics. User asked: {user_message}"
            )

            return Response({
                "type": "pcod_info",
                "reply": response.text
            })

        except Exception as e:
            return Response({
                "type": "error",
                "reply": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Register, PredictionResult
from .serializers import PredictionSerializer
from .ml_assets.ml_utils import *


class PCODPredictionAPI(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        try:
            user_id = request.data.get("user_id")
            user = Register.objects.get(id=user_id)

            # User lifestyle inputs
            user_input = {
                "Age": float(request.data.get("age")),
                "Weight": float(request.data.get("weight")),
                "Height": float(request.data.get("height")),
                "BMI": float(request.data.get("bmi")),
                "Fast_Food_Consumption": float(request.data.get("fast_food")),
                "Blood_Group": encode_blood_group(request.data.get("blood_group")),
                "Pulse_Rate": float(request.data.get("pulse")),
                "Cycle_Regularity": float(request.data.get("cycle")),
                "Hair_Growth": float(request.data.get("hair")),
                "Acne": float(request.data.get("acne")),
                "Mood_Swings": float(request.data.get("mood")),
                "Skin_Darkening": float(request.data.get("skin"))
            }

            # Save PDF file temporarily
            pdf_file = request.FILES["pdf"]
            saved_obj = PredictionResult.objects.create(
                user=user,
                pdf_file=pdf_file
            )

            pdf_path = saved_obj.pdf_file.path

            # Extract medical values
            pdf_values = extract_medical_values(pdf_path)

            # Prepare the combined dataset
            df = prepare_final_df(user_input, pdf_values)

            # Predict
            df_scaled = scaler.transform(df)
            pred = model.predict(df_scaled)

            mapping = {0: "Likely", 1: "Unlikely", 2: "Highly Risk"}
            result_label = mapping[int(pred[0])]

            # Save result in DB
            saved_obj.result = result_label
            saved_obj.extracted_data = pdf_values
            saved_obj.save()

            return Response({
                "user": user.name,
                "result": result_label,
                "values": pdf_values
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)












#Doctor


@api_view(['GET'])
def view_hospital_doctor_profile(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = HospitalDoctorRegisterSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)




class HospitalDoctorProfileViewSet(viewsets.ViewSet):
    """
    A ViewSet for updating hospital doctor profiles (partial or full updates).
    """

    def partial_update(self, request, pk=None):
        try:
            doctor = tbl_hospital_doctor_register.objects.get(pk=pk)
        except tbl_hospital_doctor_register.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HospitalDoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework import viewsets
from .models import HospitalDoctorTimeSlotGroup
from .serializers import HospitalDoctorTimeSlotGroupSerializer

class HospitalDoctorTimeSlotGroupViewSet(viewsets.ModelViewSet):
    queryset = HospitalDoctorTimeSlotGroup.objects.all().order_by('-date')
    serializer_class = HospitalDoctorTimeSlotGroupSerializer







# ✅ View all available hospital doctor time slots
@api_view(['GET'])
def view_hospital_doctor_timeslots(request, doctor_id):
    """
    Get all time slot groups for a hospital doctor with booking info.
    """
    try:
        groups = HospitalDoctorTimeSlotGroup.objects.filter(doctor_id=doctor_id).order_by('date')

        if not groups.exists():
            return Response({"message": "No time slots found for this doctor."}, status=status.HTTP_404_NOT_FOUND)

        result = []
        for group in groups:
            # ✅ Already booked times for that date
            booked_times = list(
                HospitalBooking.objects.filter(
                    doctor_id=doctor_id,
                    date=group.date
                ).values_list('time', flat=True)
            )

            # Normalize booked times (e.g. "10:00:00" → "10:00")
            booked_times = [t[:5] for t in booked_times]

            result.append({
                "id": group.id,
                "doctor": group.doctor.id,
                "doctor_name": group.doctor.name,
                "date": group.date,
                "start_time": group.start_time.strftime("%H:%M:%S"),
                "end_time": group.end_time.strftime("%H:%M:%S"),
                "timeslots": [
                    {"time": t, "is_booked": t in booked_times}
                    for t in group.timeslots
                ],
            })

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







@api_view(['POST'])
def update_hospital_doctor_availability(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    available = request.data.get('available')

    if available is None:
        return Response({"error": "Availability value required (true/false)"}, status=status.HTTP_400_BAD_REQUEST)

    # Convert to boolean
    if isinstance(available, str):
        available = available.lower() in ['true', '1', 'yes']

    doctor.available = available
    doctor.save()

    return Response({
        "message": "Availability updated successfully",
        "doctor_id": doctor.id,
        "available": doctor.available
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def view_nearby_hospital_doctors(request, user_id):
    """
    Get all approved and available hospital doctors 
    who are in the same place as the user.
    """
    try:
        user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user.place:
        return Response({"error": "User place not available"}, status=400)

    # ✅ Only approved & available doctors in the same place
    doctors = tbl_hospital_doctor_register.objects.filter(
        status='approved', available=True, place__iexact=user.place
    )

    if not doctors.exists():
        return Response({"message": "No nearby hospital doctors found in your area."}, status=200)

    nearby_doctors = []
    for doctor in doctors:
        nearby_doctors.append({
            "id": doctor.id,
            "name": doctor.name,
            "qualification": doctor.qualification,
            "specialization": doctor.specialization,
            "experience": doctor.experience,
            "phone": doctor.hospital_phone,
            "hospital_name": doctor.hospital_name,
            "hospital_address": doctor.hospital_address,
            "place": doctor.place,
            "available": doctor.available,
            "image": doctor.image.url if doctor.image else None,
            "status": doctor.status,
        })

    return Response({"nearby_hospital_doctors": nearby_doctors})





# 🧠 User Adds Feedback
@api_view(['POST'])
def add_hospital_doctor_feedback(request):
    user_id = request.data.get('user')
    doctor_id = request.data.get('doctor')
    rating = request.data.get('rating')
    comments = request.data.get('comments', '')

    try:
        user = Register.objects.get(id=user_id)
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist):
        return Response({'error': 'Invalid user or doctor ID'}, status=status.HTTP_404_NOT_FOUND)

    feedback = HospitalDoctorFeedback.objects.create(
        user=user, doctor=doctor, rating=rating, comments=comments
    )
    serializer = HospitalDoctorFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 🧠 Doctor Views Feedback
@api_view(['GET'])
def view_hospital_doctor_feedback(request, doctor_id):
    feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id).order_by('-created_at')
    serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HospitalDoctorFeedback
from .serializers import HospitalDoctorFeedbackSerializer


class GetDoctorFeedbackAPI(APIView):
    def get(self, request, doctor_id):
        try:
            feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id)

            if not feedbacks.exists():
                return Response({"message": "No feedback found for this doctor."}, status=404)

            serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)
