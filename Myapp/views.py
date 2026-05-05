"""
Hirex — Myapp Views
Interview engine, proctoring, IoT endpoint, feedback
"""

from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json, base64, cv2, numpy as np
from datetime import datetime, timedelta

from Hr.models import interviewSchedule
from .utils import generate, pdf_ocr, evaluation
from .models import Feedback

# ── Module-level interview state (per worker process) ────────────
_interview_state = {}   # key = token → {name, role, level, job_description, participant_info}
previous_transcripts = []   # kept for backward compat (single-user dev)
proctoring_counts    = {}   # token → {zero, one, multiple}


# ── HELPERS ──────────────────────────────────────────────────────
def check_interview_schedule(interview_schedule):
    """Return 0=past, 1=now (within window), 2=future."""
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    iv_date = interview_schedule.interviewDate
    iv_time = interview_schedule.interviewTime

    if iv_date < current_date:
        return 0
    if iv_date == current_date:
        end_time = (datetime.combine(current_date, iv_time) + timedelta(hours=1)).time()
        if iv_time <= current_time <= end_time:
            return 1
        if current_time > end_time:
            return 0
        return 2
    return 2


# ── VIEWS ─────────────────────────────────────────────────────────
def home(request):
    return render(request, 'homepage.html')


def join(request):
    meetid = request.GET.get('access')
    if not meetid:
        return render(request, '404.html')
    try:
        detail = interviewSchedule.objects.get(token=meetid)

        if detail.evaluation_complete:
            return render(request, 'interview-already-completed.html', {'interviewDetail': detail})

        status = check_interview_schedule(detail)
        if status == 1:
            request.session.set_expiry(5400)
            request.session['session_interviewee_name']  = detail.name
            request.session['session_interviewee_email'] = detail.email
            request.session['session_interviewee_token'] = detail.token

            # Preload interview state keyed by token
            token = detail.token
            participant_info = pdf_ocr(detail.resume)[:1000]

            _interview_state[token] = {
                'name':              detail.name,
                'role':              detail.jobRole,
                'level':             detail.experience,
                'participant_info':  participant_info,
                'job_description': (
                    f"Role: {detail.jobRole}\n"
                    f"Experience level: {detail.experience} years\n"
                    "Evaluate the candidate on their technical knowledge, "
                    "problem-solving skills, communication, and role suitability."
                ),
            }
            return render(request, 'joinold.html', {'interviewDetail': detail})
        else:
            return render(request, 'wrong-date-time-interview.html',
                          {'status': status, 'interviewDetail': detail})

    except interviewSchedule.DoesNotExist:
        return render(request, '404.html')


def interview(request):
    session_name  = request.session.get('session_interviewee_name')
    session_email = request.session.get('session_interviewee_email')
    session_token = request.session.get('session_interviewee_token')
    if not session_name or not session_email:
        return render(request, '404.html')
    interview_obj = get_object_or_404(interviewSchedule, token=session_token)
    return render(request, 'interview.html', {
        'interview':         interview_obj,
        'interviewee_email': session_email,
        'interviewee_token': session_token,
    })


@csrf_exempt
def tool(request):
    """Receive a candidate transcript chunk and return the next AI question."""
    if request.method != 'POST':
        return JsonResponse({'status': 'fail', 'message': 'Invalid request'}, status=400)

    data       = json.loads(request.body)
    transcript = data.get('transcript', '')
    token      = request.session.get('session_interviewee_token', '')

    # Load interview state for this token
    state = _interview_state.get(token, {})
    name             = state.get('name', '')
    job_description  = state.get('job_description', '')
    participant_info = state.get('participant_info', '')
    level            = state.get('level', '')
    role             = state.get('role', '')

    # Per-session transcript history
    prev_transcripts = request.session.get('transcripts', [])
    should_end       = len(prev_transcripts) >= 10

    ai_reply = generate(name, job_description, participant_info, level, role, prev_transcripts, transcript)

    prev_transcripts.append({'transcript': transcript, 'response': ai_reply})
    request.session['transcripts'] = prev_transcripts

    return JsonResponse({
        'status':               'success',
        'message':              'Data received',
        'transcripts':          prev_transcripts,
        'should_end_interview': should_end,
    })


def feedback(request):
    """Post-interview feedback + save evaluation results."""
    session_name  = request.session.get('session_interviewee_name')
    session_email = request.session.get('session_interviewee_email')
    session_token = request.session.get('session_interviewee_token')

    if not session_token:
        return render(request, '404.html')

    # Save proctoring result
    save_final_proctoring_result(session_token)
    proctoring_counts.pop(session_token, None)

    # Evaluate transcript
    transcripts = request.session.get('transcripts', [])
    if transcripts:
        res = evaluation({'transcripts': transcripts})
        try:
            iv = interviewSchedule.objects.filter(email=session_email, token=session_token).first()
            if iv:
                iv.strengths        = res.get('strengths')
                iv.weaknesses       = res.get('weaknesses')
                iv.accuracy         = res.get('accuracy')
                iv.communication    = res.get('communication')
                iv.technical_depth  = res.get('technical_depth')
                iv.good_fit         = res.get('good_fit')
                iv.evaluation_complete = True
                iv.save()
                print(f"[Hirex] Evaluation saved for {session_email}")
        except Exception as e:
            print(f"[Hirex] Error saving evaluation: {e}")

    if not session_name or not session_email or not session_token:
        return render(request, '404.html')

    try:
        interview_obj = interviewSchedule.objects.get(token=session_token)
    except interviewSchedule.DoesNotExist:
        return render(request, '404.html')

    if request.method == 'POST':
        feedback_text = request.POST.get('feedback_text')
        rating        = request.POST.get('rating')
        if not feedback_text or not rating:
            return JsonResponse({'success': False, 'message': 'Both feedback and rating are required.'})
        try:
            rating = int(rating)
            if not 1 <= rating <= 5:
                return JsonResponse({'success': False, 'message': 'Rating must be between 1 and 5.'})
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid rating.'})

        Feedback.objects.create(
            name=interview_obj.name,
            email=interview_obj.email,
            feedback=feedback_text,
            rating=rating,
        )
        request.session.flush()
        return JsonResponse({'success': True, 'message': 'Feedback submitted successfully!'})

    return render(request, 'feedback.html', {'interview': interview_obj})


# ── SOFTWARE PROCTORING (OpenCV) ─────────────────────────────────
@csrf_exempt
def proctoring_view(request):
    """Receive a base64 webcam frame and run face detection."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

    data       = json.loads(request.body)
    image_data = data.get('image')
    token      = data.get('token')

    if not image_data or not token:
        return JsonResponse({'status': 'error', 'message': 'Missing image or token'})

    try:
        header, encoded = image_data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        nparr     = np.frombuffer(img_bytes, np.uint8)
        img       = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return JsonResponse({'status': 'error', 'message': 'Empty image'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Image decode error: {e}'}, status=400)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray         = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces        = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    face_count   = len(faces)

    if token not in proctoring_counts:
        proctoring_counts[token] = {'zero': 0, 'one': 0, 'multiple': 0}

    if face_count == 0:
        proctoring_counts[token]['zero'] += 1
    elif face_count == 1:
        proctoring_counts[token]['one'] += 1
    else:
        proctoring_counts[token]['multiple'] += 1

    return JsonResponse({'status': 'success', 'faces': face_count})


def save_final_proctoring_result(token):
    counts = proctoring_counts.get(token)
    if not counts:
        return False
    if counts['multiple'] > 3:
        result = 'cheating'
    elif counts['zero'] > 5:
        result = 'suspicious'
    else:
        result = 'normal'
    try:
        iv = interviewSchedule.objects.get(token=token)
        iv.cheatingScore = result
        iv.save()
        return True
    except interviewSchedule.DoesNotExist:
        return False


# ── IOT PROCTORING ENDPOINT ──────────────────────────────────────
@csrf_exempt
def iot_event(request):
    """
    IoT Camera Endpoint — called by Raspberry Pi / IP camera.

    Expected JSON payload:
    {
        "secret":          "hirex-iot-secret-2025",
        "candidate_token": "<interview token>",
        "violation_type":  "face_absent | multiple_faces | unknown_person",
        "timestamp":       "2025-01-01T10:30:00",
        "snapshot":        "<base64-encoded JPEG or empty string>"
    }
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

    # Authenticate IoT device
    secret          = data.get('secret', '')
    expected_secret = getattr(settings, 'IOT_SECRET_KEY', 'hirex-iot-secret-2025')
    if secret != expected_secret:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=401)

    candidate_token = data.get('candidate_token', '')
    violation_type  = data.get('violation_type', 'unknown')
    timestamp       = data.get('timestamp', datetime.now().isoformat())
    snapshot        = data.get('snapshot', '')

    try:
        iv = interviewSchedule.objects.get(token=candidate_token)
    except interviewSchedule.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Candidate token not found'}, status=404)

    # Load existing IoT violations and append
    existing = []
    if iv.iot_violations:
        try:
            existing = json.loads(iv.iot_violations)
        except Exception:
            existing = []

    existing.append({
        'violation_type': violation_type,
        'timestamp':      timestamp,
        'has_snapshot':   bool(snapshot),
    })

    iv.iot_violations = json.dumps(existing)

    # Update cheating score based on IoT violations
    violation_counts = len([v for v in existing if v['violation_type'] in ('multiple_faces', 'unknown_person')])
    absent_counts    = len([v for v in existing if v['violation_type'] == 'face_absent'])

    if violation_counts > 3:
        iv.cheatingScore = 'cheating'
    elif absent_counts > 5 or violation_counts > 1:
        iv.cheatingScore = 'suspicious'
    else:
        iv.cheatingScore = 'normal'

    iv.save()

    print(f"[Hirex IoT] Violation '{violation_type}' logged for {iv.email} — Score: {iv.cheatingScore}")

    return JsonResponse({
        'status':           'success',
        'message':          f"Violation '{violation_type}' logged",
        'total_violations': len(existing),
        'cheating_score':   iv.cheatingScore,
    })