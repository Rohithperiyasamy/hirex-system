from django.db import models


class interviewSchedule(models.Model):
    name          = models.CharField(max_length=200)
    email         = models.CharField(max_length=200)
    jobRole       = models.CharField(max_length=200)
    experience    = models.CharField(max_length=200)
    resume        = models.TextField()
    Assigned_hr   = models.TextField(blank=True, null=True)

    # Evaluation results
    strengths       = models.TextField(blank=True, null=True)
    weaknesses      = models.TextField(blank=True, null=True)
    accuracy        = models.CharField(max_length=10, blank=True, null=True)
    communication   = models.CharField(max_length=10, blank=True, null=True)
    technical_depth = models.CharField(max_length=10, blank=True, null=True)
    good_fit        = models.CharField(max_length=5,  blank=True, null=True)
    evaluation_complete = models.BooleanField(default=False)

    # Schedule
    interviewDate = models.DateField()
    interviewTime = models.TimeField()
    token         = models.CharField(max_length=200, unique=True)
    createdAt     = models.DateTimeField(auto_now_add=True)

    # Proctoring
    cheatingScore = models.CharField(max_length=20, blank=True, null=True)

    # IoT proctoring violations (JSON stored as text)
    iot_violations = models.TextField(blank=True, null=True,
                                      help_text="JSON list of IoT violation events from Raspberry Pi camera")

    def __str__(self):
        return f"{self.name} — {self.jobRole} ({self.interviewDate})"
