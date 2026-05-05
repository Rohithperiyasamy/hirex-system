"""
Hirex — HR Management Views
Interview scheduling, dashboard, PDF report generation
"""

from django.shortcuts import get_object_or_404, render
import pandas as pd
from django.http import JsonResponse, HttpResponse
from .models import interviewSchedule
from Authentication.models import Hr
import secrets, datetime, json
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.timezone import now
from django.conf import settings

import fitz
from io import BytesIO

from django.views.decorators.http import require_POST

@require_POST
def delete_interview(request, id):
    hr_email = request.session.get('hr_email')
    if not hr_email:
        return redirect('/auth/login/')
    
    interview = get_object_or_404(interviewSchedule, id=id, Assigned_hr=hr_email)
    interview.delete()
    return redirect('/hr/dashboard/')


# ── SCHEDULING HELPER ────────────────────────────────────────────
def schedule_next_interview():
    today = now().date()
    start = today + datetime.timedelta(days=7)
    last  = interviewSchedule.objects.order_by("-interviewDate", "-interviewTime").first()

    if last and last.interviewDate >= start:
        current_date = last.interviewDate
        current_time = last.interviewTime
    else:
        current_date = start
        current_time = datetime.time(9, 0)

    if interviewSchedule.objects.filter(interviewDate=current_date, interviewTime=current_time).count() >= 3:
        current_time = (datetime.datetime.combine(today, current_time) + datetime.timedelta(hours=1)).time()
        if current_time >= datetime.time(21, 0):
            current_date += datetime.timedelta(days=1)
            current_time  = datetime.time(9, 0)

    return current_date, current_time


def send_interview_email(name, email, token, interview_date, interview_time, notes=''):
    platform = getattr(settings, 'PLATFORM_NAME', 'Hirex')
    company  = getattr(settings, 'COMPANY_NAME', 'Hirex Technologies Pvt Ltd')
    support  = getattr(settings, 'SUPPORT_EMAIL', 'support@hirex.ai')

    # FIXED: Always use verified EMAIL_HOST_USER as sender
    if not settings.EMAIL_HOST_USER:
        print("[Hirex Email] ERROR: EMAIL_HOST_USER is not set in .env!")
        return False
    from_email = 'Hirex <rohithperiyasamy74@gmail.com>'
    subject = f'[{platform}] Interview Invitation — Technical Assessment'
    message = (
        f"Dear {name},\n\n"
        f"Congratulations! You have been shortlisted for a Technical Interview "
        f"on the {platform} AI Platform.\n\n"
        f"📅 Interview Details:\n"
        f"   Date : {interview_date}\n"
        f"   Time : {interview_time}\n"
        f"   Mode : Online — AI-Powered Assessment\n"
        f"   Link : http://127.0.0.1:8000/join/?access={token}\n\n"
    )
    if notes:
        message += f"📝 Special Instructions:\n{notes}\n\n"
    message += (
        f"✅ Preparation Tips:\n"
        f"   1. Ensure a stable internet connection and a functional webcam & microphone.\n"
        f"   2. Use a quiet, well-lit space.\n"
        f"   3. Review the job role requirements before the interview.\n\n"
        f"⚠️  Important: Join at the scheduled time using the link above.\n"
        f"   For support contact: {support}\n\n"
        f"Good luck!\n\n"
        f"Best Regards,\n"
        f"HR Team\n"
        f"{company}\n"
    )

    try:
        send_mail(subject, message, from_email, [email])
        print(f"[Hirex Email] Successfully sent to {email}")
        return True
    except Exception as e:
        print(f"[Hirex Email] Failed to send to {email}: {e}")
        return False


# ── DASHBOARD ─────────────────────────────────────────────────────
def dashboard(request):
    if request.GET.get('logout') == '1':
        request.session.flush()
        return redirect('/auth/login/')

    hr_email = request.session.get('hr_email')
    if not hr_email:
        return redirect('/auth/login/')

    hr_obj = Hr.objects.filter(email=hr_email).first()
    email_errors = []

    if request.method == 'POST' and request.FILES.get('file'):
        excel_file = request.FILES['file']
        try:
            df = pd.read_excel(excel_file)
            for _, row in df.iterrows():
                token = secrets.token_hex(16)[:32]
                iv_date, iv_time = schedule_next_interview()
                interviewSchedule.objects.create(
                    name=row['Name'], email=row['Email'],
                    jobRole=row['Job_Role'], experience=row['Experience'],
                    resume=row['Resume_Link'],
                    interviewDate=iv_date, interviewTime=iv_time,
                    token=token, Assigned_hr=hr_email,
                )
                success = send_interview_email(row['Name'], row['Email'], token, iv_date, iv_time)
                if not success:
                    email_errors.append(row['Email'])
        except Exception as e:
            return render(request, 'dashboard.html', {'hrObj': hr_obj, 'error': str(e)})

    query      = request.GET.get('q', '')
    candidates = interviewSchedule.objects.filter(Assigned_hr=hr_email)
    if query:
        candidates = candidates.filter(
            Q(name__icontains=query) | Q(email__icontains=query) | Q(jobRole__icontains=query)
        )

    return render(request, 'dashboard.html', {
        'hrObj':         hr_obj,
        'allcandidates': candidates,
        'email_errors':  email_errors,
    })


# ── RESULT REPORT ─────────────────────────────────────────────────
def Result_report(request, id):
    c = get_object_or_404(interviewSchedule, id=id)

    iot_violations = []
    if c.iot_violations:
        try:
            iot_violations = json.loads(c.iot_violations)
        except Exception:
            iot_violations = []

    context = {
        'name':                c.name,
        'email':               c.email,
        'jobRole':             c.jobRole,
        'experience':          c.experience,
        'resume':              c.resume,
        'strengths':           [s.strip() for s in (c.strengths or '').split('\n') if s.strip()],
        'weaknesses':          [w.strip() for w in (c.weaknesses or '').split('\n') if w.strip()],
        'accuracy':            c.accuracy,
        'communication':       c.communication,
        'technical_depth':     c.technical_depth,
        'good_fit':            c.good_fit,
        'evaluation_complete': c.evaluation_complete,
        'cheatingScore':       c.cheatingScore,
        'iot_violations':      iot_violations,
        'interviewDate':       c.interviewDate,
        'interviewTime':       c.interviewTime,
        'createdAt':           c.createdAt,
    }
    return render(request, 'ResultReport.html', context)


# ── MANUAL SCHEDULE ───────────────────────────────────────────────
def manual_schedule(request):
    hr_email = request.session.get('hr_email')
    if not hr_email:
        return redirect('/auth/login/')

    hr_obj = Hr.objects.filter(email=hr_email).first()

    if request.method == 'POST':
        try:
            name        = request.POST.get('name')
            email       = request.POST.get('email')
            job_role    = request.POST.get('jobRole')
            experience  = request.POST.get('experience')
            resume      = request.POST.get('resume')
            iv_date_str = request.POST.get('interviewDate')
            iv_time_str = request.POST.get('interviewTime')
            notes       = request.POST.get('notes', '')
            use_auto    = request.POST.get('useAutoSchedule') == 'on'

            if not all([name, email, job_role, experience, resume]):
                return JsonResponse({'success': False, 'message': 'All required fields must be filled.'})

            token = secrets.token_hex(16)[:32]

            if use_auto or not iv_date_str or not iv_time_str:
                iv_date, iv_time = schedule_next_interview()
            else:
                iv_date = datetime.datetime.strptime(iv_date_str, '%Y-%m-%d').date()
                iv_time = datetime.datetime.strptime(iv_time_str, '%H:%M').time()

            interviewSchedule.objects.create(
                name=name, email=email, jobRole=job_role,
                experience=float(experience), resume=resume,
                interviewDate=iv_date, interviewTime=iv_time,
                token=token, Assigned_hr=hr_email,
            )

            email_sent = send_interview_email(name, email, token, iv_date, iv_time, notes)

            return JsonResponse({
                'success':        True,
                'message':        'Interview scheduled and email sent.' if email_sent else 'Interview scheduled but email failed — check EMAIL settings in .env.',
                'interview_date': str(iv_date),
                'interview_time': str(iv_time),
                'token':          token,
            })
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'})

    return render(request, 'manual_schedule.html', {'hrObj': hr_obj})


# ── HIRING SUGGESTIONS ────────────────────────────────────────────
def safe_lower(s):
    return s.lower() if isinstance(s, str) else ''


def hiring_suggestions(request):
    hr_email   = request.session.get('hr_email')
    candidates = interviewSchedule.objects.filter(Assigned_hr=hr_email, evaluation_complete=True)
    results    = []

    for c in candidates:
        try:
            accuracy = float((c.accuracy or '0').replace('%', '').strip())
        except (ValueError, TypeError):
            accuracy = 0.0

        is_good_fit = safe_lower(c.good_fit)      == 'yes'
        no_cheating = safe_lower(c.cheatingScore)  != 'cheating'

        if accuracy > 80 and is_good_fit and no_cheating:
            status = 'Strong Candidate'
        elif safe_lower(c.cheatingScore) == 'cheating':
            status = 'Integrity Concern'
        elif accuracy > 60:
            status = 'Average Candidate'
        else:
            status = 'Needs Review'

        results.append({
            'name':          c.name,
            'jobRole':       c.jobRole,
            'accuracy':      accuracy,
            'status':        status,
            'cheatingScore': c.cheatingScore,
            'good_fit':      c.good_fit,
        })

    return render(request, 'HiringSuggestionsSam.html', {'candidates': results, 'count': len(results)})


# ── PDF REPORT (PyMuPDF) ──────────────────────────────────────────
def download_report_pdf(request, id):
    c        = get_object_or_404(interviewSchedule, id=id)
    platform = getattr(settings, 'PLATFORM_NAME', 'Hirex')
    company  = getattr(settings, 'COMPANY_NAME', 'Hirex Technologies Pvt Ltd')

    iot_list = []
    if c.iot_violations:
        try:
            iot_list = json.loads(c.iot_violations)
        except Exception:
            iot_list = []

    doc  = fitz.open()
    page = doc.new_page(width=595, height=842)

    NAVY  = (0.05, 0.11, 0.17)
    CYAN  = (0.00, 0.67, 0.76)
    WHITE = (1, 1, 1)
    LGRAY = (0.94, 0.96, 0.98)
    DGRAY = (0.30, 0.36, 0.42)
    GREEN = (0.0, 0.78, 0.33)
    AMBER = (1.0, 0.70, 0.0)

    M = 45
    y = 0

    def text(x, ty, content, size=11, color=NAVY, bold=False):
        fontname = "helv" if not bold else "hebo"
        page.insert_text((x, ty), content, fontsize=size, color=color, fontname=fontname)

    def section_header(ty, title, color=NAVY):
        page.draw_rect(fitz.Rect(M, ty, 595 - M, ty + 22), color=None, fill=color)
        page.insert_text((M + 8, ty + 15), title, fontsize=11, color=WHITE, fontname="hebo")
        return ty + 30

    page.draw_rect(fitz.Rect(0, 0, 595, 80), color=None, fill=NAVY)
    page.insert_text((M, 35), platform, fontsize=28, color=WHITE, fontname="hebo")
    page.insert_text((M, 58), "Interview Evaluation Report", fontsize=13, color=CYAN, fontname="helv")
    page.draw_rect(fitz.Rect(0, 80, 595, 83), color=None, fill=CYAN)
    y = 100

    y = section_header(y, "CANDIDATE INFORMATION", NAVY)
    info_rows = [
        ("Name",           c.name),
        ("Email",          c.email),
        ("Position",       c.jobRole),
        ("Experience",     f"{c.experience} years"),
        ("Interview Date", str(c.interviewDate)),
        ("Interview Time", str(c.interviewTime)),
    ]
    for i, (label, val) in enumerate(info_rows):
        row_y = y + i * 20
        if i % 2 == 0:
            page.draw_rect(fitz.Rect(M, row_y, 595 - M, row_y + 20), color=None, fill=LGRAY)
        text(M + 6,   row_y + 14, label + ":", size=10, color=DGRAY, bold=True)
        text(M + 130, row_y + 14, val,          size=10, color=NAVY)
    y += len(info_rows) * 20 + 14

    status_txt   = "COMPLETED" if c.evaluation_complete else "PENDING"
    status_color = GREEN if c.evaluation_complete else AMBER
    page.draw_rect(fitz.Rect(M, y, M + 140, y + 22), color=None, fill=status_color)
    page.insert_text((M + 8, y + 15), f"Status: {status_txt}", fontsize=10, color=WHITE, fontname="hebo")
    y += 36

    if c.evaluation_complete:
        y = section_header(y, "PERFORMANCE METRICS", (0.08, 0.18, 0.30))
        metrics = [
            ("Accuracy",        c.accuracy        or "N/A"),
            ("Communication",   c.communication   or "N/A"),
            ("Technical Depth", c.technical_depth or "N/A"),
            ("Cultural Fit",    c.good_fit        or "N/A"),
            ("Integrity Score", c.cheatingScore   or "N/A"),
        ]
        for i, (label, val) in enumerate(metrics):
            row_y = y + i * 20
            if i % 2 == 0:
                page.draw_rect(fitz.Rect(M, row_y, 595 - M, row_y + 20), color=None, fill=LGRAY)
            text(M + 6,   row_y + 14, label + ":", size=10, color=DGRAY, bold=True)
            text(M + 160, row_y + 14, val,          size=10, color=NAVY)
        y += len(metrics) * 20 + 14

        if c.strengths:
            y = section_header(y, "STRENGTHS", (0.0, 0.49, 0.20))
            for line in [s.strip() for s in c.strengths.split('\n') if s.strip()]:
                text(M + 10, y + 12, f"✓  {line}", size=10, color=(0.0, 0.39, 0.16))
                y += 18
            y += 6

        if c.weaknesses:
            y = section_header(y, "AREAS FOR IMPROVEMENT", (0.55, 0.13, 0.13))
            for line in [w.strip() for w in c.weaknesses.split('\n') if w.strip()]:
                text(M + 10, y + 12, f"→  {line}", size=10, color=(0.50, 0.10, 0.10))
                y += 18
            y += 6

        if iot_list:
            y = section_header(y, f"IOT PROCTORING EVENTS ({len(iot_list)} violation(s))", (0.60, 0.35, 0.0))
            for v in iot_list[:8]:
                line = f"  [{v.get('timestamp','')[:19]}]  {v.get('violation_type','unknown')}"
                text(M + 6, y + 12, line, size=9, color=DGRAY)
                y += 16
            y += 6

    page.draw_rect(fitz.Rect(0, 810, 595, 842), color=None, fill=NAVY)
    page.insert_text((M, 830), f"Confidential — {platform} AI Interview Platform  |  {company}", fontsize=8, color=LGRAY, fontname="helv")
    page.insert_text((480, 830), datetime.datetime.now().strftime("%Y-%m-%d"), fontsize=8, color=LGRAY, fontname="helv")

    buf = BytesIO()
    doc.save(buf)
    doc.close()
    buf.seek(0)

    response = HttpResponse(buf.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Hirex_Report_{c.name}_{c.id}.pdf"'
    return response