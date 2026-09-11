from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import PartnerCompany, JobListing, CandidateResume, JobMatch
from .serializers import (
    PartnerCompanySerializer,
    JobListingSerializer,
    CandidateResumeSerializer,
    JobMatchSerializer,
)


class PartnerCompanyViewSet(viewsets.ModelViewSet):
    queryset = PartnerCompany.objects.annotate(active_jobs_count=Count("jobs")).all().order_by("-created_at")
    serializer_class = PartnerCompanySerializer


class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.select_related("company").all().order_by("-posted_date")
    serializer_class = JobListingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        domain = self.request.query_params.get("domain")
        country = self.request.query_params.get("country")
        blue_card = self.request.query_params.get("blue_card")
        if domain:
            qs = qs.filter(domain=domain)
        if country:
            qs = qs.filter(country=country)
        if blue_card:
            qs = qs.filter(blue_card_eligible=(blue_card.lower() == "true"))
        return qs


class CandidateResumeViewSet(viewsets.ModelViewSet):
    queryset = CandidateResume.objects.all().order_by("-uploaded_at")
    serializer_class = CandidateResumeSerializer

    @action(detail=True, methods=["get", "post"], url_path="run-job-match")
    def run_job_match(self, request, pk=None):
        """
        Dynamically calculates match scores between candidate skills and all active jobs.
        """
        candidate = self.get_object()
        active_jobs = JobListing.objects.filter(status="Active").select_related("company")
        
        matches = []
        for job in active_jobs:
            score = 30
            # Domain match
            if job.domain.lower() in candidate.field.lower() or candidate.field.lower() in job.domain.lower():
                score += 25

            # Skills overlap
            matched_skills = []
            for req_skill in job.required_skills:
                for cand_skill in candidate.primary_skills:
                    if (
                        req_skill.lower() in cand_skill.lower()
                        or cand_skill.lower() in req_skill.lower()
                    ):
                        matched_skills.append(req_skill)
                        break

            score += min(30, len(matched_skills) * 10)

            # German Level match
            if job.min_german_level == "None" or candidate.german_level >= job.min_german_level:
                score += 15

            score = min(99, max(20, score))

            matches.append({
                "job_id": job.id,
                "job_title": job.title,
                "company_name": job.company.name,
                "location": f"{job.city}, {job.country}",
                "salary_range": job.salary_range,
                "match_score": score,
                "matched_skills": list(set(matched_skills)),
                "is_high_fit": score >= 75,
            })

        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return Response({"candidate_name": candidate.candidate_name, "matches": matches})


class JobMatchViewSet(viewsets.ModelViewSet):
    queryset = JobMatch.objects.select_related("candidate", "job", "job__company").all().order_by("-matched_at")
    serializer_class = JobMatchSerializer
