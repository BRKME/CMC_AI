"""
OpenAI Integration для CMC AI - Alpha Take для текстовых новостей
Version: 2.1.0 - Institutional Grade Prompt (with AI hashtags)
Генерирует Alpha Take, Context Tag и Hashtags для новостей CoinMarketCap AI

ОБНОВЛЕНО В v2.1.0:
- ОТКАТ: AI снова генерирует хэштеги (как было в v1.0)
- Оставлен новый institutional-grade промпт
- Запрещены эмодзи в Alpha Take и Context Tag
- Хэштеги генерируются AI с fallback на предопределенные

ОБНОВЛЕНО В v2.0.0:
- Новый institutional-grade промпт
- Улучшенные Context Tag категории
- Строгий профессиональный тон
"""

import os
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)

# OpenAI API Key
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Инициализация клиента
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        logger.info("✓ OpenAI client initialized for CMC AI v2.1")
    except Exception as e:
        logger.error(f"✗ Failed to initialize OpenAI client: {e}")
        client = None
else:
    logger.warning("⚠️ OPENAI_API_KEY not found - Alpha Take generation disabled")


# MASTER PROMPT для CMC AI новостей - INSTITUTIONAL GRADE v2.1
CMC_NEWS_MASTER_PROMPT = """ROLE
You are an institutional-grade crypto research assistant.
Your task is to transform raw crypto news, data, screenshots, or narratives into clear, emotionally neutral market intelligence suitable for professional investors.

You do not give trading advice. You do not issue explicit price predictions unless clearly data-driven and probabilistic. You focus on market regimes, positioning, flows, incentives, and narratives.

Tone: concise, analytical, signal-focused
Audience: US-based, market-literate crypto investors
Writing style: buy-side / sell-side research note (not journalism)

HARD RULES FOR ALPHA TAKE & CONTEXT TAG
* ❌ No emojis in Alpha Take or Context Tag
* ❌ No calls to action
* ❌ No "bullish / bearish" language
* ❌ No execution or strategy wording
* ❌ No hype, storytelling, or motivational tone

OUTPUT FORMAT (MANDATORY)

ALPHA_TAKE: [2–4 short sentences maximum. Dense, non-repetitive. Zero restatement of obvious facts. Focus on second-order effects: incentives, participant behavior, liquidity dynamics, crowding/dispersion, regime stability vs fragility. Interpretive not predictive. Descriptive not prescriptive. About behavior and structure, not outcomes.]

CONTEXT_TAG: [ONE line only. ONE category only. 2–4 words. No emojis. No directional bias.]

HASHTAGS: [Generate 3-5 relevant, contextual hashtags based on the current market state and content. Use professional vocabulary. Format: #Tag1 #Tag2 #Tag3]

THREE TYPES OF ALPHA TAKE
You MUST select exactly one per analysis:

1️⃣ Alpha Take — Flow & Positioning
Use when content includes:
* ETF inflows / outflows
* Open interest, liquidations
* Funding rates, leverage
* Bitcoin dominance
* On-chain positioning

Primary focus:
* Risk appetite shifts
* De-risking vs re-leveraging
* Capital concentration or dispersion
* Asymmetry building or unwinding

2️⃣ Alpha Take — Narrative & Attention
Use when content includes:
* KOL or social momentum
* Sector narratives (AI, DeFi, L2, infra)
* Story-driven repricing
* Media-driven attention

Primary focus:
* Where attention is rotating
* Narrative crowding vs early-stage themes
* Consensus formation, fatigue, or fragmentation

3️⃣ Alpha Take — Structural / Macro
Use when content includes:
* Regulation
* Macro or policy developments
* Market structure changes
* Adoption or infrastructure shifts

Primary focus:
* Regime changes
* Long-duration implications
* Constraints, frictions, tail risks

CONTEXT TAG CATEGORIES
Select ONE category only:

🧩 Risk Regime (macro liquidity & risk appetite)
Examples:
* Fragile risk-on
* Risk-off environment
* Liquidity-driven regime
* High uncertainty phase

📈 Market Regime (price behavior & structure)
Examples:
* Volatile range
* Compression phase
* Trend transition phase
* Momentum exhaustion

⏳ Time Horizon (dominant timeframe implied)
Examples:
* Near-term volatility
* Short-term cautious
* Medium-term constructive
* Long-duration shift

🧠 Positioning Bias (crowding & exposure)
Examples:
* Defensive positioning
* Light exposure
* Crowded longs
* De-risked market

DECISION TREE — CONTEXT TAG
* References flows, leverage, liquidity? → Risk Regime / Positioning Bias
* Describes volatility or structure? → Market Regime
* Emphasizes duration, not price? → Time Horizon
* Core insight is crowding/exposure? → Positioning Bias

⚠️ Never mix categories
⚠️ Avoid mechanical repetition across posts

HASHTAGS GUIDELINES
* Generate 3-5 hashtags relevant to the content
* Use professional, market-focused vocabulary
* Avoid generic tags like #Crypto #Bitcoin unless specifically relevant
* Examples: #BTCFlows #InstitutionalDemand #MacroRisk #DeFiRotation #AltcoinSeason
* Format: #CamelCase for multi-word tags

QUALITY CHECK (INTERNAL)
Before finalizing, verify:
* Does this reduce noise?
* Does it surface structure, not summary?
* Would a hedge fund analyst find it useful?

If yes → publish
If no → refine

EXAMPLE OUTPUT

Input: "Bitcoin ETF flows show sustained positive inflows after weeks of outflows. Meanwhile, altcoins remain suppressed with dominance near 60%."

ALPHA_TAKE: Renewed institutional flows suggest selective re-entry rather than broad risk appetite. Historically, this pattern precedes either sustainable risk-on regime if macro holds, or false start if BTC fails to establish clear trend. Meaningful rotation into alts would require both stable BTC price action and improved derivatives activity signaling broader confidence.

CONTEXT_TAG: Selective risk-on

HASHTAGS: #BTCFlows #InstitutionalDemand #SelectiveRisk

Remember:
* NO emojis in Alpha Take or Context Tag
* Hashtags are ALLOWED and should be generated
* Focus on interpretation, not description
* Professional institutional tone
"""


def get_ai_alpha_take(news_text, question_context=""):
    """
    Получает Alpha Take от OpenAI для текстовой новости
    
    v2.1: AI генерирует хэштеги (возврат функциональности v1.0)
    
    Args:
        news_text: Текст новости/анализа от CMC AI
        question_context: Контекст вопроса (опционально)
        
    Returns:
        dict: {
            "alpha_take": "...",
            "context_tag": "...",
            "hashtags": "..." or None
        }
        или None если ошибка
    """
    if not client:
        logger.warning("OpenAI client not initialized - skipping Alpha Take generation")
        return None
    
    try:
        # Формируем полный контекст
        full_input = news_text
        if question_context:
            full_input = f"Question Context: {question_context}\n\nNews/Analysis:\n{news_text}"
        
        logger.info(f"🤖 Requesting Alpha Take from OpenAI (v2.1 institutional)...")
        logger.info(f"   Input length: {len(full_input)} chars")
        
        # Вызываем OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Быстрая и недорогая модель
            messages=[
                {
                    "role": "system",
                    "content": CMC_NEWS_MASTER_PROMPT
                },
                {
                    "role": "user",
                    "content": full_input
                }
            ],
            max_tokens=350,  # Alpha Take + Context Tag + Hashtags
            temperature=0.7
        )
        
        # Парсим ответ
        content = response.choices[0].message.content.strip()
        logger.info(f"  ✓ OpenAI response received")
        
        # Извлекаем компоненты
        alpha_take = None
        context_tag = None
        hashtags = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('ALPHA_TAKE:'):
                alpha_take = line.replace('ALPHA_TAKE:', '').strip()
            elif line.startswith('CONTEXT_TAG:'):
                context_tag = line.replace('CONTEXT_TAG:', '').strip()
            elif line.startswith('HASHTAGS:'):
                hashtags = line.replace('HASHTAGS:', '').strip()
        
        # Валидация
        if not alpha_take:
            logger.warning(f"Could not parse Alpha Take from response")
            logger.warning(f"  Response: {content[:200]}...")
            # Fallback: используем весь ответ
            alpha_take = content
        
        logger.info(f"  ✓ Alpha Take: {alpha_take[:100]}...")
        if context_tag:
            logger.info(f"  ✓ Context Tag: {context_tag}")
        if hashtags:
            logger.info(f"  ✓ AI Hashtags: {hashtags}")
        
        return {
            "alpha_take": alpha_take,
            "context_tag": context_tag,
            "hashtags": hashtags  # v2.1: AI генерирует хэштеги
        }
        
    except Exception as e:
        logger.error(f"Error getting Alpha Take: {e}")
        import traceback
        traceback.print_exc()
        return None


def enhance_caption_with_alpha_take(title, text, hashtags_fallback, ai_result):
    """
    Добавляет Alpha Take к caption для Telegram
    
    v2.1: Использует AI хэштеги если есть, иначе fallback
    
    Format:
    <title>
    
    <original_text_summary>
    
    Alpha Take
    <alpha_take>
    
    Context: <context_tag>
    
    <hashtags>
    
    Args:
        title: Заголовок поста
        text: Оригинальный текст (TLDR)
        hashtags_fallback: Хештеги fallback (если AI не сгенерировал)
        ai_result: Результат от get_ai_alpha_take()
        
    Returns:
        str: Enhanced caption с Alpha Take
    """
    if not ai_result:
        # Без AI - старый формат
        return f"<b>{title}</b>\n\n{text}\n\n{hashtags_fallback}"
    
    alpha_take = ai_result.get('alpha_take', '')
    context_tag = ai_result.get('context_tag', '')
    hashtags_ai = ai_result.get('hashtags', '')
    
    # v2.1: Используем AI хэштеги если есть, иначе fallback
    hashtags = hashtags_ai if hashtags_ai else hashtags_fallback
    
    # Сокращаем оригинальный текст если добавляем Alpha Take
    # Чтобы уместиться в Telegram лимиты
    max_original_text = 800  # Оставляем место для Alpha Take
    if len(text) > max_original_text:
        text = text[:max_original_text-3] + "..."
    
    # Формируем enhanced caption
    caption = f"<b>{title}</b>\n\n"
    
    # Оригинальный контент (сокращенный)
    caption += f"{text}\n\n"
    
    # Alpha Take секция
    caption += f"<b>Alpha Take</b>\n"
    caption += f"{alpha_take}\n\n"
    
    # Context Tag если есть
    if context_tag:
        caption += f"<i>Context: {context_tag}</i>\n\n"
    
    # Хештеги (AI или fallback)
    caption += f"{hashtags}"
    
    # Проверка на длину Telegram
    if len(caption) > 4000:
        logger.warning(f"⚠️ Caption слишком длинный ({len(caption)}), сокращаю оригинальный текст")
        # Агрессивное сокращение
        max_original_text = 400
        text = text[:max_original_text-3] + "..."
        
        caption = f"<b>{title}</b>\n\n"
        caption += f"{text}\n\n"
        caption += f"<b>Alpha Take</b>\n"
        caption += f"{alpha_take}\n\n"
        if context_tag:
            caption += f"<i>Context: {context_tag}</i>\n\n"
        caption += f"{hashtags}"
    
    return caption


def enhance_twitter_with_alpha_take(title, alpha_take, context_tag, hashtags):
    """
    Создаёт Twitter контент с Alpha Take
    
    v2.1: hashtags могут быть AI-generated или fallback
    
    Args:
        title: Заголовок
        alpha_take: Alpha Take текст
        context_tag: Context Tag
        hashtags: Хештеги (AI-generated или fallback)
        
    Returns:
        str: Twitter-formatted текст (single tweet)
    """
    # Twitter лимит
    max_length = 270
    
    # Формат: Title + Alpha Take (сокращенный) + Context + Hashtags
    
    # Резервируем место
    reserved = len(title) + len(hashtags) + 20  # +20 для форматирования
    if context_tag:
        reserved += len(f"Context: {context_tag}") + 4
    
    available_for_alpha = max_length - reserved
    
    # Сокращаем Alpha Take если нужно
    if len(alpha_take) > available_for_alpha:
        # Берем первые предложения
        sentences = alpha_take.split('. ')
        short_alpha = sentences[0] + "."
        
        if len(short_alpha) > available_for_alpha:
            short_alpha = alpha_take[:available_for_alpha-3] + "..."
    else:
        short_alpha = alpha_take
    
    # Собираем твит
    tweet = f"{title}\n\n{short_alpha}"
    
    if context_tag:
        tweet += f"\n\nContext: {context_tag}"
    
    tweet += f"\n\n{hashtags}"
    
    # Финальная проверка
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    return tweet
