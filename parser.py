def extract_tldr_from_answer(answer):
    """Извлекает только TLDR часть из ответа и очищает от лишнего текста"""
    try:
        # Убираем строку "Researched for Xs"
        answer = '\n'.join([line for line in answer.split('\n') if not line.strip().startswith('Researched for')])
        
        # Ищем TLDR секцию
        if 'TLDR' in answer:
            # Находим начало TLDR
            tldr_start = answer.find('TLDR')
            
            # Находим начало Deep Dive (конец TLDR)
            deep_dive_start = answer.find('Deep Dive')
            
            if deep_dive_start != -1:
                # Извлекаем только TLDR часть
                tldr_section = answer[tldr_start:deep_dive_start].strip()
            else:
                # Если нет Deep Dive, берем все после TLDR до конца
                tldr_section = answer[tldr_start:].strip()
            
            # Убираем саму строку "TLDR" из начала
            tldr_section = tldr_section.replace('TLDR', '', 1).strip()
            
            return tldr_section
        else:
            # Если нет TLDR, возвращаем первые 500 символов
            return answer[:500] + "..."
            
    except Exception as e:
        print(f"⚠️ Ошибка извлечения TLDR: {e}")
        return answer[:500] + "..."

def clean_question_specific_text(question, text):
    """Убирает специфичные для вопросов ненужные строки"""
    try:
        # Для вопроса про upcoming events
        if "What upcoming events may impact crypto?" in question:
            text = text.replace("These are the upcoming crypto events that may impact crypto the most:", "").strip()
        
        # Для вопроса про bullish momentum
        if "What cryptos are showing bullish momentum?" in question:
            text = text.replace("Here are the trending cryptos based on CoinMarketCap's evolving momentum algorithm (news, social, price momentum)", "").strip()
        
        return text
    except Exception as e:
        print(f"⚠️ Ошибка очистки текста: {e}")
        return text

def send_telegram_photo_with_caption(photo_url, caption, parse_mode='HTML'):
    """Отправляет фото с подписью в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        
        print(f"🔍 Попытка отправить фото: {photo_url}")
        print(f"📏 Длина caption: {len(caption)} символов")
        
        # Отправляем фото с подписью
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': parse_mode
        }
        
        # Если текст слишком длинный для caption (лимит 1024 символа)
        if len(caption) > 1020:
            # Отправляем фото без подписи
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'photo': photo_url
            }
            response = requests.post(url, data=payload, timeout=30)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Фото отправлено в Telegram")
                # Ждем немного и отправляем текст отдельным сообщением
                time.sleep(1)
                send_telegram_message(caption, parse_mode)
                return True
        else:
            # Отправляем фото с подписью вместе
            response = requests.post(url, data=payload, timeout=30)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✓ Фото с подписью отправлено в Telegram")
                return True
            else:
                print(f"✗ Ошибка отправки фото: {response.status_code} - {response.text}")
                # Если фото не отправилось - отправляем хотя бы текст
                print("⚠️ Отправляю только текст без фото")
                send_telegram_message(caption, parse_mode)
                return False
                
    except Exception as e:
        print(f"✗ Ошибка при отправке фото в Telegram: {e}")
        traceback.print_exc()
        # В случае ошибки отправляем хотя бы текст
        print("⚠️ Отправляю только текст без фото")
        send_telegram_message(caption, parse_mode)
        return False

def send_question_answer_to_telegram(question_num, total_questions, question, answer):
    """Отправляет вопрос и TLDR в Telegram с картинкой"""
    try:
        # Извлекаем только TLDR часть
        tldr_text = extract_tldr_from_answer(answer)
        
        # Очищаем от специфичных для вопросов строк
        tldr_text = clean_question_specific_text(question, tldr_text)
        
        # Форматируем короткое сообщение без разделительной линии
        short_message = f"""<b>{question}</b>

{tldr_text}"""
        
        # Получаем случайную картинку
        image_url = get_random_image_url()
        
        print(f"\n📤 Отправка вопроса {question_num}/{total_questions} в Telegram с картинкой...")
        print(f"📏 Длина текста: {len(tldr_text)} символов")
        
        send_telegram_photo_with_caption(image_url, short_message)
        
        # Пауза между сообщениями
        time.sleep(1)
        
    except Exception as e:
        print(f"✗ Ошибка при отправке вопроса {question_num}: {e}")
