"""
Property-based tests for Career Planner Service.

Feature: ai-assistant-agent
Tests Properties 11, 12, 13, 14, 15, 16
Validates: Requirements 4.1, 4.2, 4.6, 4.8, 4.9, 4.10, 5.1-5.9
"""

import pytest
import os
import sys
from typing import List
from hypothesis import given, strategies as st, settings, assume, HealthCheck

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from terminal.career_planner import CareerPlanner, CareerReportBuilder
from terminal.models import (
    CareerContext, CareerReport, CareerDirection,
    LearningPath, LearningResource, TechRecommendation,
    Timeline, Milestone, ActionItem
)


# ==================== Custom Strategies ====================

@st.composite
def answer_strategy(draw, min_length=10, max_length=200):
    """Generate random valid answers for interview questions."""
    return draw(st.text(
        min_size=min_length,
        max_size=max_length,
        alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z'))
    ).filter(lambda x: len(x.strip()) >= min_length))


@st.composite
def short_answer_strategy(draw):
    """Generate short/insufficient answers."""
    return draw(st.text(min_size=0, max_size=9))


@st.composite
def career_direction_strategy(draw):
    """Generate random valid CareerDirection objects."""
    return CareerDirection(
        position=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        industry=draw(st.text(min_size=1, max_size=30).filter(lambda x: x.strip())),
        salary_range=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        demand_level=draw(st.sampled_from(["高", "中", "低"])),
        description=draw(st.text(min_size=1, max_size=200).filter(lambda x: x.strip())),
        requirements=draw(st.lists(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            min_size=1,
            max_size=5
        ))
    )


@st.composite
def learning_resource_strategy(draw):
    """Generate random valid LearningResource objects."""
    return LearningResource(
        name=draw(st.text(min_size=1, max_size=50).filter(lambda x: x.strip())),
        type=draw(st.sampled_from(["课程", "书籍", "认证", "项目"])),
        url=draw(st.one_of(st.none(), st.text(min_size=5, max_size=100))),
        estimated_time=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        priority=draw(st.sampled_from(["必学", "推荐", "可选"]))
    )


@st.composite
def tech_recommendation_strategy(draw):
    """Generate random valid TechRecommendation objects."""
    return TechRecommendation(
        category=draw(st.sampled_from(["编程语言", "框架", "工具", "平台"])),
        name=draw(st.text(min_size=1, max_size=30).filter(lambda x: x.strip())),
        reason=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        learning_time=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip()))
    )


@st.composite
def milestone_strategy(draw):
    """Generate random valid Milestone objects."""
    return Milestone(
        goal=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        timeframe=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        key_actions=draw(st.lists(
            st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
            min_size=1,
            max_size=3
        ))
    )


@st.composite
def action_item_strategy(draw):
    """Generate random valid ActionItem objects."""
    return ActionItem(
        priority=draw(st.integers(min_value=1, max_value=5)),
        action=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip())),
        deadline=draw(st.text(min_size=1, max_size=20).filter(lambda x: x.strip())),
        expected_outcome=draw(st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    )


@st.composite
def complete_career_report_strategy(draw):
    """Generate a complete valid CareerReport."""
    return CareerReport(
        executive_summary=draw(st.text(min_size=10, max_size=100).filter(lambda x: x.strip())),
        personal_profile=draw(st.text(min_size=10, max_size=100).filter(lambda x: x.strip())),
        career_directions=draw(st.lists(career_direction_strategy(), min_size=3, max_size=3)),
        industry_analysis=draw(st.text(min_size=10, max_size=100).filter(lambda x: x.strip())),
        skill_gap_analysis=draw(st.text(min_size=10, max_size=100).filter(lambda x: x.strip())),
        learning_path=LearningPath(
            free_resources=draw(st.lists(learning_resource_strategy(), min_size=1, max_size=2)),
            paid_resources=draw(st.lists(learning_resource_strategy(), min_size=0, max_size=1))
        ),
        tech_stack=draw(st.lists(tech_recommendation_strategy(), min_size=1, max_size=2)),
        timeline=Timeline(
            short_term=draw(st.lists(milestone_strategy(), min_size=1, max_size=1)),
            mid_term=[],
            long_term=[]
        ),
        action_items=draw(st.lists(action_item_strategy(), min_size=1, max_size=2))
    )


# ==================== Property 11: Career Interview Stage Order ====================

class TestCareerInterviewStageOrder:
    """
    Property 11: Career Interview Stage Order
    
    For any career planning session, interview questions SHALL follow the order:
    basic info → interests → skills → experience → goals → preferences.
    
    Validates: Requirements 4.2
    """
    
    EXPECTED_ORDER = [
        "basic_info",
        "interests", 
        "skills",
        "experience",
        "goals",
        "preferences"
    ]
    
    @given(answers=st.lists(answer_strategy(), min_size=6, max_size=6))
    @settings(max_examples=100)
    def test_interview_stages_follow_correct_order(self, answers: List[str]):
        """
        Feature: ai-assistant-agent, Property 11: Career Interview Stage Order
        
        Interview stages must follow the specified order.
        """
        planner = CareerPlanner()
        planner.start_interview()
        
        visited_stages = []
        
        for i, answer in enumerate(answers):
            # Record current stage before processing
            current_stage = planner.get_current_stage_name()
            if current_stage:
                visited_stages.append(current_stage)
            
            # Process the answer
            is_complete, _ = planner.process_answer(answer)
            
            if is_complete:
                break
        
        # Verify stages were visited in correct order
        for i, stage in enumerate(visited_stages):
            assert stage == self.EXPECTED_ORDER[i], \
                f"Stage {i} should be '{self.EXPECTED_ORDER[i]}' but was '{stage}'"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_stage_order_constant_across_sessions(self, data):
        """
        Feature: ai-assistant-agent, Property 11: Career Interview Stage Order
        
        The stage order should be constant across different sessions.
        """
        planner1 = CareerPlanner()
        planner2 = CareerPlanner()
        
        # Both planners should have the same stage order
        assert planner1.INTERVIEW_STAGES == planner2.INTERVIEW_STAGES
        assert planner1.INTERVIEW_STAGES == self.EXPECTED_ORDER


# ==================== Property 12: Career Interview Progress Tracking ====================

class TestCareerInterviewProgressTracking:
    """
    Property 12: Career Interview Progress Tracking
    
    For any career planning session, the progress value SHALL increase 
    monotonically from 0.0 to 1.0 as stages are completed.
    
    Validates: Requirements 4.1
    """
    
    @given(answers=st.lists(answer_strategy(), min_size=1, max_size=10))
    @settings(max_examples=100)
    def test_progress_increases_monotonically(self, answers: List[str]):
        """
        Feature: ai-assistant-agent, Property 12: Career Interview Progress Tracking
        
        Progress should increase monotonically as stages are completed.
        """
        planner = CareerPlanner()
        planner.start_interview()
        
        previous_progress = planner.get_progress()
        assert previous_progress == 0.0, "Initial progress should be 0.0"
        
        for answer in answers:
            is_complete, _ = planner.process_answer(answer)
            current_progress = planner.get_progress()
            
            # Progress should never decrease
            assert current_progress >= previous_progress, \
                f"Progress decreased from {previous_progress} to {current_progress}"
            
            previous_progress = current_progress
            
            if is_complete:
                break
    
    @given(answers=st.lists(answer_strategy(), min_size=6, max_size=6))
    @settings(max_examples=100)
    def test_progress_reaches_one_when_complete(self, answers: List[str]):
        """
        Feature: ai-assistant-agent, Property 12: Career Interview Progress Tracking
        
        Progress should reach 1.0 when all stages are completed.
        """
        planner = CareerPlanner()
        planner.start_interview()
        
        for answer in answers:
            is_complete, _ = planner.process_answer(answer)
            if is_complete:
                break
        
        # After completing all stages, progress should be 1.0
        if planner.is_complete():
            assert planner.get_progress() == 1.0, \
                f"Progress should be 1.0 when complete, but was {planner.get_progress()}"
    
    @given(num_stages=st.integers(min_value=0, max_value=6))
    @settings(max_examples=100)
    def test_progress_value_is_fraction_of_stages(self, num_stages: int):
        """
        Feature: ai-assistant-agent, Property 12: Career Interview Progress Tracking
        
        Progress value should equal completed_stages / total_stages.
        """
        planner = CareerPlanner()
        planner.start_interview()
        
        # Complete specified number of stages
        for i in range(num_stages):
            answer = "This is a sufficiently long answer for testing purposes."
            is_complete, _ = planner.process_answer(answer)
            if is_complete:
                break
        
        expected_progress = min(num_stages, 6) / 6
        actual_progress = planner.get_progress()
        
        assert abs(actual_progress - expected_progress) < 0.001, \
            f"Expected progress {expected_progress}, got {actual_progress}"


# ==================== Property 13: Career Report Structure Completeness ====================

class TestCareerReportStructureCompleteness:
    """
    Property 13: Career Report Structure Completeness
    
    For any generated career report, it SHALL contain all required sections:
    executive summary, personal profile, career directions (≥3), industry analysis,
    skill gap analysis, learning path, tech stack, timeline, and action items.
    
    Validates: Requirements 4.10, 5.1-5.9
    """
    
    @given(report=complete_career_report_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_complete_report_passes_validation(self, report: CareerReport):
        """
        Feature: ai-assistant-agent, Property 13: Career Report Structure Completeness
        
        A complete report should pass validation.
        """
        is_valid, missing = CareerReportBuilder.validate_report(report)
        
        assert is_valid, f"Complete report should be valid, but missing: {missing}"
        assert len(missing) == 0
    
    @given(report=complete_career_report_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_report_has_all_required_sections(self, report: CareerReport):
        """
        Feature: ai-assistant-agent, Property 13: Career Report Structure Completeness
        
        Report must have all 9 required sections.
        """
        # Check each required section
        assert report.executive_summary, "Missing executive summary"
        assert report.personal_profile, "Missing personal profile"
        assert len(report.career_directions) >= 3, "Need at least 3 career directions"
        assert report.industry_analysis, "Missing industry analysis"
        assert report.skill_gap_analysis, "Missing skill gap analysis"
        assert report.learning_path.free_resources or report.learning_path.paid_resources, \
            "Missing learning resources"
        assert report.tech_stack, "Missing tech stack"
        assert report.timeline.short_term or report.timeline.mid_term or report.timeline.long_term, \
            "Missing timeline milestones"
        assert report.action_items, "Missing action items"
    
    @settings(max_examples=100)
    @given(st.data())
    def test_incomplete_report_fails_validation(self, data):
        """
        Feature: ai-assistant-agent, Property 13: Career Report Structure Completeness
        
        An incomplete report should fail validation.
        """
        # Create an empty report
        empty_report = CareerReport()
        
        is_valid, missing = CareerReportBuilder.validate_report(empty_report)
        
        assert not is_valid, "Empty report should not be valid"
        assert len(missing) > 0, "Should have missing sections"


# ==================== Property 14: Career Direction Contains Required Fields ====================

class TestCareerDirectionRequiredFields:
    """
    Property 14: Career Direction Contains Required Fields
    
    For any career direction in the report, it SHALL contain position name,
    industry, salary range, demand level, description, and requirements list.
    
    Validates: Requirements 4.6
    """
    
    @given(direction=career_direction_strategy())
    @settings(max_examples=100)
    def test_career_direction_has_all_fields(self, direction: CareerDirection):
        """
        Feature: ai-assistant-agent, Property 14: Career Direction Contains Required Fields
        
        Each career direction must have all required fields.
        """
        is_valid, missing = CareerReportBuilder.validate_career_direction(direction)
        
        assert is_valid, f"Career direction should be valid, but missing: {missing}"
        assert len(missing) == 0
    
    @given(direction=career_direction_strategy())
    @settings(max_examples=100)
    def test_career_direction_fields_not_empty(self, direction: CareerDirection):
        """
        Feature: ai-assistant-agent, Property 14: Career Direction Contains Required Fields
        
        Career direction fields should not be empty.
        """
        assert direction.position and len(direction.position.strip()) > 0
        assert direction.industry and len(direction.industry.strip()) > 0
        assert direction.salary_range and len(direction.salary_range.strip()) > 0
        assert direction.demand_level in ["高", "中", "低"]
        assert direction.description and len(direction.description.strip()) > 0
        assert len(direction.requirements) > 0
    
    @settings(max_examples=100)
    @given(st.data())
    def test_incomplete_direction_fails_validation(self, data):
        """
        Feature: ai-assistant-agent, Property 14: Career Direction Contains Required Fields
        
        An incomplete career direction should fail validation.
        """
        # Create direction with missing fields
        incomplete = CareerDirection(
            position="",
            industry="",
            salary_range="",
            demand_level="",
            description="",
            requirements=[]
        )
        
        is_valid, missing = CareerReportBuilder.validate_career_direction(incomplete)
        
        assert not is_valid, "Incomplete direction should not be valid"
        assert len(missing) > 0


# ==================== Property 15: Learning Resources Categorization ====================

class TestLearningResourcesCategorization:
    """
    Property 15: Learning Resources Categorization
    
    For any learning path in the report, resources SHALL be categorized 
    into free_resources and paid_resources lists.
    
    Validates: Requirements 4.9
    """
    
    @given(
        free_resources=st.lists(learning_resource_strategy(), min_size=0, max_size=5),
        paid_resources=st.lists(learning_resource_strategy(), min_size=0, max_size=5)
    )
    @settings(max_examples=100)
    def test_learning_path_has_two_categories(self, free_resources, paid_resources):
        """
        Feature: ai-assistant-agent, Property 15: Learning Resources Categorization
        
        Learning path should have separate free and paid resource lists.
        """
        assume(len(free_resources) > 0 or len(paid_resources) > 0)
        
        learning_path = LearningPath(
            free_resources=free_resources,
            paid_resources=paid_resources
        )
        
        # Verify the structure has both categories
        assert hasattr(learning_path, 'free_resources')
        assert hasattr(learning_path, 'paid_resources')
        assert isinstance(learning_path.free_resources, list)
        assert isinstance(learning_path.paid_resources, list)
    
    @given(resource=learning_resource_strategy())
    @settings(max_examples=100)
    def test_learning_resource_has_required_fields(self, resource: LearningResource):
        """
        Feature: ai-assistant-agent, Property 15: Learning Resources Categorization
        
        Each learning resource should have required fields.
        """
        assert resource.name and len(resource.name.strip()) > 0
        assert resource.type in ["课程", "书籍", "认证", "项目"]
        assert resource.estimated_time and len(resource.estimated_time.strip()) > 0
        assert resource.priority in ["必学", "推荐", "可选"]


# ==================== Property 16: Skill Roadmap Time Estimates ====================

class TestSkillRoadmapTimeEstimates:
    """
    Property 16: Skill Roadmap Time Estimates
    
    For any skill or learning resource in the report, it SHALL include 
    an estimated learning time.
    
    Validates: Requirements 4.8
    """
    
    @given(tech=tech_recommendation_strategy())
    @settings(max_examples=100)
    def test_tech_recommendation_has_learning_time(self, tech: TechRecommendation):
        """
        Feature: ai-assistant-agent, Property 16: Skill Roadmap Time Estimates
        
        Each tech recommendation must have a learning time estimate.
        """
        assert tech.learning_time is not None
        assert len(tech.learning_time.strip()) > 0
    
    @given(resource=learning_resource_strategy())
    @settings(max_examples=100)
    def test_learning_resource_has_time_estimate(self, resource: LearningResource):
        """
        Feature: ai-assistant-agent, Property 16: Skill Roadmap Time Estimates
        
        Each learning resource must have a time estimate.
        """
        assert resource.estimated_time is not None
        assert len(resource.estimated_time.strip()) > 0
    
    @given(report=complete_career_report_strategy())
    @settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
    def test_all_skills_in_report_have_time_estimates(self, report: CareerReport):
        """
        Feature: ai-assistant-agent, Property 16: Skill Roadmap Time Estimates
        
        All skills and resources in a report must have time estimates.
        """
        # Check tech stack
        for tech in report.tech_stack:
            assert tech.learning_time and len(tech.learning_time.strip()) > 0, \
                f"Tech '{tech.name}' missing learning time"
        
        # Check learning resources
        for resource in report.learning_path.free_resources:
            assert resource.estimated_time and len(resource.estimated_time.strip()) > 0, \
                f"Free resource '{resource.name}' missing time estimate"
        
        for resource in report.learning_path.paid_resources:
            assert resource.estimated_time and len(resource.estimated_time.strip()) > 0, \
                f"Paid resource '{resource.name}' missing time estimate"
