"""
OpenAI Integration для CMC AI - Alpha Take для текстовых новостей
Version: 2.3.2 - Fixed: ◼️ emoji preserved in caption
Генерирует Alpha Take, Context Tag и Hashtags для новостей CoinMarketCap AI

ОБНОВЛЕНО В v2.3.2:
- FIX: ◼️ теперь добавляется перед "Alpha Take" в caption
- AI не генерирует ◼️, мы добавляем его при форматировании
- Убраны только лишние префиксы "ALPHA TAKE — Structural / Macro"

ОБНОВЛЕНО В v2.3.1:
- FIX: Убрано дублирование Context Tag и Hashtags
- Улучшен парсинг ответа OpenAI
- Очищен промпт от лишних типов
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
        logger.info("✓ OpenAI client initialized for CMC AI v2.3.2")
    except Exception as e:
        logger.error(f"✗ Failed to initialize OpenAI client: {e}")
        client = None
else:
    logger.warning("⚠️ OPENAI_API_KEY not found - Alpha Take generation disabled")


# MASTER PROMPT для CMC AI новостей - INSTITUTIONAL GRADE v2.3.2
CMC_NEWS_MASTER_PROMPT = """MASTER PROMPT — Crypto Radar / OracAI

"Alpha Take — Institutional Market Intelligence"

ROLE

You are an institutional-grade crypto research assistant.

Your task is to transform raw crypto news, data, screenshots, indicators, or narratives into high-signal market intelligence suitable for professional investors.

You do not give trading advice.
You do not issue explicit price predictions unless strictly data-driven and probabilistic.
You focus on market regimes, positioning, flows, incentives, liquidity, and narratives — not outcomes.

Tone: concise, analytical, emotionally neutral
Audience: US-based, market-literate crypto investors
Writing style: buy-side / sell-side research note
Constraint: optimized for high-density delivery (feed / alerts / SMS)

HARD RULES (STRICT)

- No emojis in the analysis text itself
- No calls to action
- No execution or strategy language
- No hype, storytelling, or motivational tone
- No restating the headline or data inside Alpha Take
- No mechanical summary of the input
- No simplistic "this is good/bad" framing
- No prefixes like "ALPHA TAKE —" or type labels in the analysis text
- No visual symbols in the analysis text

Bullish / bearish wording is not allowed in body text.
If sentiment must be conveyed, it must be expressed structurally (positioning, flows, participation), never directionally.

OUTPUT FORMAT (MANDATORY)

Return ONLY these three lines with NO additional text, NO type labels, NO symbols in the text:

ALPHA_TAKE: [Your analysis here - 1 sentence preferred, maximum 2-3 if structure needed]
CONTEXT_TAG: [2-4 words only]
HASHTAGS: [3-5 hashtags with # symbol]

CRITICAL: Do NOT include in the analysis text:
- Type indicators ("Structural / Macro", "Flow & Positioning", "Narrative & Attention")
- "ALPHA TAKE —" prefix
- Section headers
- Visual symbols
- Any explanatory text

ALPHA TAKE — CORE DEFINITION

The Alpha Take answers one question only:

"What does this mean for market participants right now, given the broader market and news environment?"

It is:
- Interpretive, not predictive
- Descriptive, not prescriptive
- About behavior and structure, not outcomes
- Contextual — never fragmented or isolated from the wider news flow

Alpha Take must synthesize:
- the specific input (news / data / indicator), and
- the prevailing macro, liquidity, regulatory, and narrative backdrop

ALPHA TAKE — STYLE RULES

Length:
- 1 sentence preferred for sentiment dashboards, recurring indicators, positioning snapshots
- Up to 2-3 sentences max only if additional structure is essential

Writing constraints:
- Dense, precise, non-repetitive
- Zero retelling of the input
- Zero generic filler ("creates uncertainty", "could impact markets")

Alpha Take must emphasize second-order effects:
- shifts in incentives
- changes in participant behavior
- liquidity sensitivity or constraints
- crowding vs dispersion
- narrative fatigue, overlap, or fragmentation
- regime stability vs fragility

THREE TYPES OF ALPHA TAKE

Select exactly ONE type internally (but DO NOT include type name in output):

1. Flow & Positioning
Use when content includes: ETF inflows/outflows, open interest, liquidations, funding rates, leverage, Bitcoin dominance, on-chain positioning
Focus: Risk appetite shifts, de-risking vs re-leveraging, capital concentration/dispersion, asymmetry building/unwinding

2. Narrative & Attention
Use when content includes: Sector/theme narratives (L1, AI, DeFi, infra), social/media momentum, KOL-driven repricing
Focus: Where attention rotates vs where capital is not, narrative crowding vs early-stage themes, consensus formation/fatigue/fragmentation

3. Structural / Macro
Use when content includes: Regulation/policy, macro developments, market structure changes, adoption/infrastructure shifts
Focus: Regime transitions, long-duration constraints/tail risks, frictions affecting liquidity/access/participation

CONTEXT TAG — RULES

- ONE line only
- ONE category only
- 2-4 words
- No emojis
- No directional bias
- Context ≠ signal

Categories:
Risk Regime: Risk-off environment, Fragile risk-on, Liquidity-driven regime, High uncertainty phase
Market Regime: Volatile range, Compression phase, Trend transition phase, Momentum exhaustion
Time Horizon: Near-term volatility, Short-term cautious, Medium-term constructive, Long-duration shift
Positioning Bias: Defensive positioning, Light exposure, Crowded longs, De-risked market

HASHTAGS GUIDELINES

- Generate 3-5 hashtags relevant to the content
- Use professional, market-focused vocabulary
- Avoid generic tags like #Crypto #Bitcoin unless specifically relevant
- Examples: #BTCFlows #InstitutionalDemand #MacroRisk #DeFiRotation #AltcoinSeason
- Format: #CamelCase for multi-word tags

QUALITY CHECK

Before finalizing, verify:
- Does this reduce noise?
- Does it explain structure, not summary?
- Is it anchored in the broader news and regime context, not isolated?
- Would a hedge fund analyst find it immediately useful?

EXAMPLE OUTPUT

Input: "Bitcoin ETF flows show sustained positive inflows after weeks of outflows. Meanwhile, altcoins remain suppressed with dominance near 60%."

ALPHA_TAKE: Renewed institutional flows suggest selective re-entry rather than broad risk appetite, amplified by continued macro uncertainty around Fed policy and persistent regulatory overhang that constrains meaningful rotation into alts.
CONTEXT_TAG: Selective risk-on
HASHTAGS: #BTCFlows #InstitutionalDemand #SelectiveRisk

Remember:
- Return ONLY the three fields above
- NO type labels in the analysis text
- NO "ALPHA TAKE —" prefix in the analysis
- 1 sentence preferred for Alpha Take
- Professional institutional tone
"""


def get_ai_alpha_take(news_text, question_context=""):
    """
    Получает Alpha Take от OpenAI для текстовой новости
    
    v2.3.2: Clean parsing, ◼️ added during caption formatting
    
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
        
        logger.info(f"🤖 Requesting Alpha Take from OpenAI (v2.3.2)...")
        logger.info(f"   Input length: {len(full_input)} chars")
        
        # Вызываем OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
            max_tokens=250,
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
            
            # Пропускаем пустые строки
            if not line:
                continue
            
            if line.startswith('ALPHA_TAKE:'):
                # Убираем префикс
                alpha_take = line.replace('ALPHA_TAKE:', '').strip()
                
                # Убираем лишние префиксы если AI всё-таки их добавил
                # НО НЕ убираем ◼️ - его мы добавим сами при форматировании
                alpha_take = alpha_take.replace('ALPHA TAKE —', '').strip()
                alpha_take = alpha_take.replace('Structural / Macro', '').strip()
                alpha_take = alpha_take.replace('Flow & Positioning', '').strip()
                alpha_take = alpha_take.replace('Narrative & Attention', '').strip()
                
                # Убираем двойные пробелы
                while '  ' in alpha_take:
                    alpha_take = alpha_take.replace('  ', ' ')
                    
            elif line.startswith('CONTEXT_TAG:'):
                context_tag = line.replace('CONTEXT_TAG:', '').strip()
                
            elif line.startswith('HASHTAGS:'):
                hashtags = line.replace('HASHTAGS:', '').strip()
        
        # Валидация
        if not alpha_take:
            logger.warning(f"Could not parse Alpha Take from response")
            logger.warning(f"  Response: {content[:200]}...")
            return None
        
        logger.info(f"  ✓ Alpha Take: {alpha_take[:100]}...")
        if context_tag:
            logger.info(f"  ✓ Context Tag: {context_tag}")
        if hashtags:
            logger.info(f"  ✓ AI Hashtags: {hashtags}")
        
        return {
            "alpha_take": alpha_take,
            "context_tag": context_tag,
            "hashtags": hashtags
        }
        
    except Exception as e:
        logger.error(f"Error getting Alpha Take: {e}")
        import traceback
        traceback.print_exc()
        return None


def enhance_caption_with_alpha_take(title, text, hashtags_fallback, ai_result):
    """
    Добавляет Alpha Take к caption для Telegram
    
    v2.3.2: ◼️ добавляется перед "Alpha Take"
    
    Format:
    <title>
    
    <original_text_summary>
    
    ◼️ Alpha Take
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
    
    # Используем AI хэштеги если есть, иначе fallback
    hashtags = hashtags_ai if hashtags_ai else hashtags_fallback
    
    # Убираем из текста блок "Alpha Take" если он там есть (для избежания дублирования)
    if 'Alpha Take' in text:
        alpha_start = text.find('Alpha Take')
        if alpha_start > 0:
            text = text[:alpha_start].strip()
    
    # Также убираем "CONTEXT_TAG:" и "HASHTAGS:" если они в тексте
    if 'CONTEXT_TAG:' in text:
        context_start = text.find('CONTEXT_TAG:')
        if context_start > 0:
            text = text[:context_start].strip()
    
    if 'HASHTAGS:' in text:
        hashtags_start = text.find('HASHTAGS:')
        if hashtags_start > 0:
            text = text[:hashtags_start].strip()
    
    # Сокращаем оригинальный текст если добавляем Alpha Take
    max_original_text = 800
    if len(text) > max_original_text:
        text = text[:max_original_text-3] + "..."
    
    # Формируем enhanced caption
    caption = f"<b>{title}</b>\n\n"
    
    # Оригинальный контент (очищенный от дублей)
    caption += f"{text}\n\n"
    
    # Alpha Take секция с ◼️
    caption += f"◼️ <b>Alpha Take</b>\n"
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
        caption += f"◼️ <b>Alpha Take</b>\n"
        caption += f"{alpha_take}\n\n"
        if context_tag:
            caption += f"<i>Context: {context_tag}</i>\n\n"
        caption += f"{hashtags}"
    
    return caption


def enhance_twitter_with_alpha_take(title, alpha_take, context_tag, hashtags):
    """
    Создаёт Twitter контент с Alpha Take
    
    v2.3.2: Clean output for Twitter
    
    Args:
        title: Заголовок
        alpha_take: Alpha Take текст (чистый, без префиксов)
        context_tag: Context Tag
        hashtags: Хештеги (AI-generated или fallback)
        
    Returns:
        str: Twitter-formatted текст (single tweet)
    """
    # Twitter лимит
    max_length = 270
    
    # Формат: Title + Alpha Take + Context + Hashtags
    
    # Резервируем место
    reserved = len(title) + len(hashtags) + 20
    if context_tag:
        reserved += len(f"Context: {context_tag}") + 4
    
    available_for_alpha = max_length - reserved
    
    # Alpha Take короче, обычно влезет
    if len(alpha_take) > available_for_alpha:
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
