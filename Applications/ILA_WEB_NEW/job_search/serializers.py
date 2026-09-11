from rest_framework import serializers
from .models import PartnerCompany, JobListing, CandidateResume, JobMatch


class PartnerCompanySerializer(serializers.ModelSerializer):
    active_jobs_count = serializers.IntegerField(source="jobs.count", read_only=True)

    class Meta:
        model = PartnerCompany
        fields = "__all__"


class JobListingSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_logo = serializers.CharField(source="company.logo", read_only=True)

    class Meta:
        model = JobListing
        fields = "__all__"


class CandidateResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateResume
        fields = "__all__"


class JobMatchSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source="candidate.candidate_name", read_only=True)
    candidate_email = serializers.CharField(source="candidate.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    company_name = serializers.CharField(source="job.company.name", read_only=True)

    class Meta:
        model = JobMatch
        fields = "__all__"
