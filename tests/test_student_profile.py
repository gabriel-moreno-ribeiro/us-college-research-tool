"""
Testes para src/student_profile.py — scoring puro/determinístico.
"""

from src.student_profile import StudentProfile, compute_relevance_score


class TestStudentProfile:
    def test_interest_keywords_basic(self):
        p = StudentProfile(interests=["machine learning"])
        kw = p.interest_keywords()
        assert "machine learning" in kw
        assert "machine" in kw
        assert "learning" in kw

    def test_interest_keywords_hyphenated(self):
        p = StudentProfile(interests=["human-computer interaction"])
        kw = p.interest_keywords()
        assert "human computer interaction" in kw

    def test_interest_keywords_filters_short_words(self):
        p = StudentProfile(interests=["AI in NLP"])
        kw = p.interest_keywords()
        assert "nlp" in kw
        assert "in" not in kw  # too short (len <= 2)


class TestComputeRelevanceScore:
    def test_no_interests_returns_zero(self):
        p = StudentProfile(interests=[])
        assert compute_relevance_score("anything here", p) == 0.0

    def test_exact_phrase_match_scores_high(self):
        p = StudentProfile(interests=["human-computer interaction"])
        text = "Professor works on human computer interaction and ubiquitous computing"
        score = compute_relevance_score(text, p)
        assert score >= 0.8

    def test_synonym_match(self):
        p = StudentProfile(interests=["machine learning"])
        text = "Research focuses on deep learning and neural network architectures"
        score = compute_relevance_score(text, p)
        assert score >= 0.6

    def test_no_match_scores_zero(self):
        p = StudentProfile(interests=["quantum physics"])
        text = "Professor works on medieval literature and postmodern criticism"
        score = compute_relevance_score(text, p)
        assert score == 0.0

    def test_partial_word_match(self):
        p = StudentProfile(interests=["distributed systems"])
        text = "Works on distributed computing and cloud infrastructure"
        score = compute_relevance_score(text, p)
        assert score > 0.0

    def test_score_bounded_zero_to_one(self):
        p = StudentProfile(interests=["machine learning", "NLP", "computer vision"])
        text = "deep learning neural network natural language processing image recognition"
        score = compute_relevance_score(text, p)
        assert 0.0 <= score <= 1.0

    def test_multiple_interests_accumulate(self):
        p_single = StudentProfile(interests=["machine learning"])
        p_multi = StudentProfile(interests=["machine learning", "artificial intelligence"])
        text = "deep learning AI neural network"
        score_single = compute_relevance_score(text, p_single)
        score_multi = compute_relevance_score(text, p_multi)
        assert score_multi >= score_single
