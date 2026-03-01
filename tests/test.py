import requests

def fetch_leetcode_problem(titleSlug):
    query = """
    query getQuestionDetail($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        difficulty
        content
        topicTags {
          name
        }
        codeSnippets {
          lang
          code
        }
        sampleTestCase
      }
    }
    """
    
    url = "https://leetcode.com/graphql"
    response = requests.post(
        url,
        json={"query": query, "variables": {"titleSlug": titleSlug}}
    )
    return response.json()

# Example
problem = fetch_leetcode_problem("two-sum")
print(problem)