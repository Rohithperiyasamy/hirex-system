from django.contrib import messages
import random
from django.shortcuts import redirect, render
from .models import Interviewee, Hr
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from datetime import datetime, timedelta


def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))  # FIX 1: was 4-digit (1000–9999)


def signup(request):
    if request.method == "POST":
        request.session['signupName']     = request.POST.get('name')
        request.session['signupPhone']    = request.POST.get('phone')
        request.session['signupEmail']    = request.POST.get('email')
        request.session['signupPassword'] = request.POST.get('password')
        request.session['signupCompany']  = request.POST.get('company')

        email_to_check = request.session.get('signupEmail')

        if Hr.objects.filter(email=email_to_check).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'updatedSignup.html')
        else:
            otp = generate_otp()
            subject = '[Hirex] Your OTP Verification Code'
            message = (
                f'Your OTP code is {otp}.\n'
                f'Please use this code to verify your email address.\n'
                f'This code expires in 5 minutes.'
            )
            from django.conf import settings
            email_from     = settings.DEFAULT_FROM_EMAIL  # FIX 2: use DEFAULT_FROM_EMAIL
            signupEmail    = request.session.get('signupEmail')
            recipient_list = [signupEmail]

            try:
                send_mail(subject, message, email_from, recipient_list)
            except Exception as e:
                # FIX 3: show error to user instead of silently failing
                print(f"[Hirex] OTP email failed: {e}")
                messages.error(request, f"Failed to send OTP email. Please check email settings. Error: {e}")
                return render(request, 'updatedSignup.html')

            current_datetime   = datetime.now()
            formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
            request.session['otpGenTime'] = formatted_datetime
            request.session['signupOtp']  = otp
            return redirect('otpVerify')

    return render(request, 'updatedSignup.html', {})


def login(request):
    if request.method == "POST":
        loginEmail    = request.POST.get('email')
        loginPassword = request.POST.get('password')

        hr_user = Hr.objects.filter(email=loginEmail).first()
        if hr_user is None:
            messages.error(request, 'Email not found.')
        elif not check_password(loginPassword, hr_user.password):
            messages.error(request, 'Incorrect password.')
        else:
            request.session['hr_id']    = hr_user.id
            request.session['hr_name']  = hr_user.name
            request.session['hr_email'] = hr_user.email
            return redirect("/hr/dashboard/")

    return render(request, 'login.html', {})


def otpVerify(request):
    if request.method == "POST":
        signup_otp_a = request.POST.get('otp_a', '')
        signup_otp_b = request.POST.get('otp_b', '')
        signup_otp_c = request.POST.get('otp_c', '')
        signup_otp_d = request.POST.get('otp_d', '')

        user_signup_otp = signup_otp_a + signup_otp_b + signup_otp_c + signup_otp_d

        current_datetime = datetime.now()
        otpGenTime       = request.session.get('otpGenTime', None)

        if not otpGenTime:
            # FIX 4: handle missing session gracefully
            messages.error(request, 'Session expired. Please sign up again.')
            return redirect('signup')

        otp_datetime = datetime.strptime(otpGenTime, '%Y-%m-%d %H:%M:%S')
        difference   = current_datetime - otp_datetime
        five_minutes = timedelta(minutes=5)
        otp          = request.session.get('signupOtp', None)

        if difference > five_minutes:
            # FIX 5: was silent — now shows error and redirects
            messages.error(request, 'OTP has expired. Please sign up again.')
            return redirect('signup')

        if otp == user_signup_otp:
            signupName     = request.session.get('signupName')
            signupEmail    = request.session.get('signupEmail')
            signupPhone    = request.session.get('signupPhone')
            signupPassword = request.session.get('signupPassword')
            signupCompany  = request.session.get('signupCompany')

            hr = Hr(
                name=signupName,
                phone=signupPhone,
                email=signupEmail,
                password=make_password(signupPassword),
                company=signupCompany,
            )
            hr.save()

            del request.session['signupOtp']
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        else:
            # FIX 6: was silent — now shows error to user
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, 'otp.html', {})

    return render(request, 'otp.html', {})