from django.shortcuts import render

# Create your views here.
# Create your views here.
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import tbl_doctor, Register
from .serializers import DoctorLoginSerializer, UserLoginSerializer


class LoginView(APIView):
    def post(self, request):
        role = request.data.get('role')

        # Doctor Login
        if role == 'doctor':
            serializer = DoctorLoginSerializer(data=request.data)
            if serializer.is_valid():
                doctor_id = serializer.validated_data['doctor_id']
                email = serializer.validated_data['email']

                try:
                    doctor = tbl_doctor.objects.get(doctor_id=doctor_id, email=email)
                    if doctor.status != 'approved':
                        return Response(
                            {'message': 'Doctor account not approved yet.'},
                            status=status.HTTP_403_FORBIDDEN
                        )

                    return Response({
                        'id': doctor.id,
                        'name': doctor.name,
                        'email': doctor.email,
                        'doctor_id': doctor.doctor_id,
                        'role': doctor.role,
                        'status': doctor.status
                    }, status=status.HTTP_200_OK)

                except tbl_doctor.DoesNotExist:
                    return Response({'message': 'Invalid Doctor ID or Email.'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # User Login
        elif role == 'user':
            serializer = UserLoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']

                try:
                    user = Register.objects.get(email=email, password=password)
                    return Response({
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'phone': user.phone,
                        'role': user.role
                    }, status=status.HTTP_200_OK)

                except Register.DoesNotExist:
                    return Response({'message': 'Invalid Email or Password.'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response({'message': 'Please specify a valid role (doctor/user).'},
                            status=status.HTTP_400_BAD_REQUEST)


class DoctorRegisterViewSet(viewsets.ModelViewSet):
    queryset = tbl_doctor.objects.all()
    serializer_class = RegisterSerializer



    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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
