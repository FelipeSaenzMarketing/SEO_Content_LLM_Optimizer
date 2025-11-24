import re
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Tuple

import streamlit as st
import requests
from bs4 import BeautifulSoup


# ========= ANALYSIS LOGIC =========

@dataclass
class ContentAnalysis:
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    paragraph_count: int
    long_paragraphs: int
    heading_ratio: float
    list_ratio: float
    numbers_count: int
    url_count: int
    citation_like_count: int
    type_token_ratio: float
    repetition_score: float
    recommendations: List[str]


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r"[.!?]+\s+", text.strip())
    return [s for s in sentences if s]


def split_paragraphs(text: str) -> List[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    return paragraphs


def is_heading(line: str) -> bool:
    line = line.strip()
    if line.startswith("#"):
        return True
    if re.match(r"<h[1-6]>.*</h[1-6]>", line, re.IGNORECASE):
        return True
    if len(line.split()) <= 8 and not line.endswith("."):
        return True
    return False


def is_list_item(line: str) -> bool:
    return bool(re.match(r"^[-*•]\s+", line.strip()))


def analyze_text(text: str) -> ContentAnalysis:
    clean_text = text.strip()
    
    words = re.findall(r"\w+", clean_text, flags=re.UNICODE)
    word_count = len(words)
    unique_words = set(w.lower() for w in words)
    
    sentences = split_sentences(clean_text)
    sentence_count = len(sentences) or 1
    avg_sentence_length = word_count / sentence_count if sentence_count else 0.0
    
    paragraphs = split_paragraphs(clean_text)
    paragraph_count = len(paragraphs) or 1
    long_paragraphs = sum(1 for p in paragraphs if len(p.split()) > 120)
    
    lines = [l for l in text.split("\n") if l.strip()]
    heading_count = sum(1 for l in lines if is_heading(l))
    list_count = sum(1 for l in lines if is_list_item(l))
    
    heading_ratio = heading_count / paragraph_count if paragraph_count else 0.0
    list_ratio = list_count / paragraph_count if paragraph_count else 0.0
    
    numbers_count = len(re.findall(r"\d+", clean_text))
    url_count = len(re.findall(r"https?://\S+", clean_text))
    
    citation_like_count = 0
    citation_like_count += len(re.findall(r"\[\d+\]", clean_text))
    citation_like_count += len(re.findall(r"\(\d{4}\)", clean_text))
    citation_like_count += len(
        re.findall(r"\bseg[uú]n\b", clean_text, flags=re.IGNORECASE)
    )
    
    type_token_ratio = len(unique_words) / word_count if word_count else 0.0
    
    tokens_lower = [w.lower() for w in words]
    bigrams = list(zip(tokens_lower, tokens_lower[1:]))
    bigram_counts = Counter(bigrams)
    if bigram_counts:
        _, max_count = bigram_counts.most_common(1)[0]
        repetition_score = max_count / sentence_count if sentence_count else 0.0
    else:
        repetition_score = 0.0
    
    recommendations: List[str] = []
    
    if word_count < 500:
        recommendations.append(
            "The content is relatively short. Consider adding more context, definitions, and detailed examples."
        )
    if avg_sentence_length > 25:
        recommendations.append(
            "Average sentence length is high. Split long sentences into shorter ones to improve clarity and LLM comprehension."
        )
    if long_paragraphs > 0:
        recommendations.append(
            f"There are {long_paragraphs} very long paragraphs. Split them into smaller chunks to make parsing and scanning easier."
        )
    if heading_ratio < 0.2:
        recommendations.append(
            "Use more headings (H2/H3) to structure the content into clear, thematic sections."
        )
    if list_ratio < 0.1:
        recommendations.append(
            "Add more bullet lists to highlight steps, key points, or advantages. Structured information is easier for LLMs to reuse."
        )
    if numbers_count < 5:
        recommendations.append(
            "Very few numeric data points detected. Add numbers, dates, or percentages that can be explicitly cited."
        )
    if url_count == 0 and citation_like_count == 0:
        recommendations.append(
            "No references or sources detected. Adding links to official documentation or studies increases authority and citability."
        )
    if type_token_ratio < 0.3 and word_count > 0:
        recommendations.append(
            "Vocabulary diversity seems low. Use more specific terms and semantic variations related to the topic."
        )
    if repetition_score > 1.5:
        recommendations.append(
            "High repetition of text patterns detected. Rewrite or condense redundant parts to add more new information."
        )
    
    return ContentAnalysis(
        word_count=word_count,
        sentence_count=sentence_count,
        avg_sentence_length=avg_sentence_length,
        paragraph_count=paragraph_count,
        long_paragraphs=long_paragraphs,
        heading_ratio=heading_ratio,
        list_ratio=list_ratio,
        numbers_count=numbers_count,
        url_count=url_count,
        citation_like_count=citation_like_count,
        type_token_ratio=type_token_ratio,
        repetition_score=repetition_score,
        recommendations=recommendations
    )


def fetch_url_content(url: str, timeout: int = 15) -> Tuple[str, str]:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }
    
    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()
    
    main_candidates = []
    
    article = soup.find("article")
    if article:
        main_candidates.append(article)
    
    main_tag = soup.find("main")
    if main_tag:
        main_candidates.append(main_tag)
    
    if not main_candidates:
        main_candidates.append(soup.body or soup)
    
    best_node = max(main_candidates, key=lambda node: len(node.get_text(" ", strip=True)))
    extracted_text = best_node.get_text("\n", strip=True)
    
    lines = [line.strip() for line in extracted_text.split("\n") if line.strip()]
    extracted_text = "\n\n".join(lines)
    
    title = soup.title.string.strip() if soup.title and soup.title.string else url
    
    return title, extracted_text


def render_analysis(analysis: ContentAnalysis, original_text: str) -> None:
    data = asdict(analysis)
    
    st.subheader("📊 Metrics Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Words", analysis.word_count)
        st.metric("Sentences", analysis.sentence_count)
        st.metric("Paragraphs", analysis.paragraph_count)
    with col2:
        st.metric("Avg. Sentence Length", f"{analysis.avg_sentence_length:.1f}")
        st.metric("Very Long Paragraphs", analysis.long_paragraphs)
        st.metric("Repetition Score", f"{analysis.repetition_score:.2f}")
    with col3:
        st.metric("Numbers Detected", analysis.numbers_count)
        st.metric("URLs in Text", analysis.url_count)
        st.metric("Citation-like Patterns", analysis.citation_like_count)
    
    st.markdown("---")
    st.subheader("🧱 Structure & LLM Signals")
    col4, col5 = st.columns(2)
    with col4:
        st.write("**Headings per Paragraph (ratio)**")
        st.progress(min(1.0, analysis.heading_ratio))
        st.write(f"Value: `{analysis.heading_ratio:.2f}` (target ≥ 0.20)")
    with col5:
        st.write("**Lists per Paragraph (ratio)**")
        st.progress(min(1.0, analysis.list_ratio))
        st.write(f"Value: `{analysis.list_ratio:.2f}` (target ≥ 0.10)")
    
    st.markdown("---")
    st.subheader("🧠 Lexical Diversity")
    st.write(
        f"**Type-Token Ratio (TTR):** `{analysis.type_token_ratio:.3f}` "
        "(ratio between unique words and total words)."
    )
    
    st.markdown("---")
    st.subheader("✅ Recommendations to Improve 'Citability'")
    if analysis.recommendations:
        for rec in analysis.recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success(
            "No recommendations generated. The content already matches the basic heuristics defined."
        )
    
    with st.expander("🛠 Technical Analysis Details (JSON)"):
        st.json(data)
    
    with st.expander("📝 Raw Analyzed Text"):
        st.text_area("Content used for the analysis:", value=original_text, height=250)


def main():
    st.set_page_config(
        page_title="Content Analyzer for LLM Citability",
        page_icon="📚",
        layout="wide",
    )
    
    st.title("📚 Content Analyzer for LLM Citability")
    st.write(
        "Paste your content or provide a URL to get metrics and recommendations "
        "to make it more useful and 'citable' for large language models."
    )
    
    with st.expander("💡 How This Tool Works", expanded=False):
        st.markdown(
            """
        - **Analyzes structure**: words, sentences, paragraphs, headings, lists  
        - **Looks for 'citable' signals**: numbers, URLs, citation-like patterns  
        - **Evaluates lexical diversity**: type-token ratio and repetition patterns  
        - **Generates practical suggestions**: actionable recommendations to improve content
        """
        )
    
    st.markdown("### ✍️ Option 1: Paste Content")
    pasted_text = st.text_area(
        "Paste your article, guide, or long-form content here:",
        height=250,
        placeholder="Write or paste your text here...",
        key="pasted_text",
    )
    
    analyze_paste_button = st.button("🔍 Analyze Pasted Content")
    
    st.markdown("---")
    st.markdown("### 🌐 Option 2: Analyze a URL")
    url = st.text_input(
        "Enter a URL to crawl and analyze its main content:",
        placeholder="https://example.com/article",
        key="url_input",
    )
    
    analyze_url_button = st.button("🕷️ Crawl URL and Analyze")
    
    if analyze_paste_button:
        if not pasted_text.strip():
            st.warning("⚠️ Please paste some content to analyze.")
        else:
            with st.spinner("Analyzing pasted content... ⏳"):
                analysis = analyze_text(pasted_text)
                render_analysis(analysis, pasted_text)
    
    if analyze_url_button:
        if not url.strip():
            st.warning("⚠️ Please enter a valid URL.")
        else:
            try:
                with st.spinner("Crawling URL and analyzing content... ⏳"):
                    page_title, extracted_text = fetch_url_content(url)
                    
                    if not extracted_text.strip():
                        st.error("❌ Could not extract meaningful content from the provided URL.")
                        return
                    
                    st.info(f"✅ Content extracted from: **{page_title}**")
                    analysis = analyze_text(extracted_text)
                    render_analysis(analysis, extracted_text)
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Network/HTTP error while fetching the URL: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error while crawling or analyzing the URL: {e}")


if __name__ == "__main__":
    main()