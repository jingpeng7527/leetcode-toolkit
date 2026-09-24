SUBMISSION_LIST = """
query submissionList($offset: Int!, $limit: Int!, $lastKey: String) {
  submissionList(offset: $offset, limit: $limit, lastKey: $lastKey) {
    lastKey
    hasNext
    submissions { id title titleSlug statusDisplay timestamp }
  }
}
"""

PROBLEMSET = """
query problemset($skip: Int, $limit: Int) {
  problemsetQuestionList: questionList(categorySlug: "", limit: $limit, skip: $skip, filters: {}) {
    total: totalNum
    questions: data { titleSlug title difficulty questionFrontendId topicTags { name } }
  }
}
"""

STUDY_PLAN = """
query studyPlan($slug: String!) {
  studyPlanV2Detail(planSlug: $slug) {
    planSubGroups { questions { titleSlug } }
  }
}
"""

FAVORITE_LIST = """
query favorite($favoriteSlug: String!, $skip: Int, $limit: Int) {
  favoriteQuestionList(favoriteSlug: $favoriteSlug, filter: {}, skip: $skip, limit: $limit) {
    totalLength
    hasMore
    questions { titleSlug }
  }
}
"""

DAILY = """
query daily {
  activeDailyCodingChallengeQuestion {
    date
    link
    question { titleSlug title difficulty topicTags { name } }
  }
}
"""

QUESTION_DETAIL = """
query question($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    title titleSlug difficulty content topicTags { name }
  }
}
"""
