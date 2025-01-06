from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pyrogram import Client
from pyrogram.errors import RPCError
import asyncio
from datetime import datetime, timedelta

# Создаем FastAPI приложение
app = FastAPI()

# Параметры для подключения к Telegram
API_ID = ""  # Замените на ваш API ID
API_HASH = ""  # Замените на ваш API Hash

# Создаем клиента Pyrogram
app_client = Client("telegram_client", api_id=API_ID, api_hash=API_HASH)

# Модель для отправки сообщений
class SendMessageRequest(BaseModel):
    chat_id: int | str
    text: str

@app.on_event("startup")
async def startup_event():
    # Запускаем Pyrogram клиент при старте приложения
    await app_client.start()

@app.on_event("shutdown")
async def shutdown_event():
    # Останавливаем Pyrogram клиент при завершении работы приложения
    await app_client.stop()

@app.post("/send_message/")
async def send_message(request: SendMessageRequest):
    try:
        # Отправка сообщения в Telegram
        message = await app_client.send_message(chat_id=request.chat_id, text=request.text)
        return {"message_id": message.id, "status": "Message sent successfully"}
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")



@app.get("/getAverageViews")
async def average_views_last_30_days(group_id: int | str):
    chat_id = group_id
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        total_views = 0
        count = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=100):
            if message.date >= start_date and message.views is not None:
                total_views += message.views
                count += 1

        average_views = total_views / count if count > 0 else 0
        return {"average_views": average_views, "message_count": count}
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/getAverageReactions/")
async def average_reactions_last_30_days(group_id: int | str):
    chat_id = group_id
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        total_reactions = 0
        count = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=100):
            if message.date >= start_date and message.reactions:
                if message.reactions.reactions:
                    total_reactions += sum(reaction.count for reaction in message.reactions.reactions)
                count += 1

        average_reactions = round(total_reactions / count, 1) if count > 0 else 0
        return {"average_reactions": average_reactions, "message_count": count}
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/getEngagement/")
async def get_engagement(group_id: int | str):
    chat_id = group_id
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        total_reactions = 0
        total_comments = 0
        total_views = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=100):
            print(message)
            if message.date >= start_date:
                if message.reactions is not None and message.reactions.reactions:
                    total_reactions += sum(reaction.count for reaction in message.reactions.reactions)
                if message.views is not None:
                    total_views += message.views
                if hasattr(message, "forwards") and message.forwards is not None:
                    total_comments += message.forwards


        engagement_rate = ((total_reactions + total_comments) / total_views * 100) if total_views > 0 else 0
        engagement_rate = round(engagement_rate, 1)

        return {
            "engagement_rate_percent": engagement_rate,
            "total_views": total_views,
            "total_reactions": total_reactions,
            "total_comments": total_comments
        }
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/getTotalMessages/")
async def get_total_messages(group_id: int | str):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        total_message_count = 0
        last_30_days_count = 0

        # Перебор истории чата
        async for message in app_client.get_chat_history(chat_id=group_id):  
            total_message_count += 1  # Увеличиваем общее количество сообщений
            if message.date >= start_date:
                last_30_days_count += 1  # Увеличиваем количество сообщений за последние 30 дней

        return {
            "total_messages": total_message_count,
            "total_messages_last_30_days": last_30_days_count
        }
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/getAudienceActivity/")
async def get_audience_activity(group_id: int | str):
    chat_id = group_id
    try:
        # Получаем количество подписчиков
        chat = await app_client.get_chat(chat_id)
        subscribers_count = chat.members_count

        # Получаем среднее количество просмотров за последние 30 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        total_views = 0
        count = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=1000):  # Увеличьте лимит при необходимости
            if message.date >= start_date and message.views is not None:
                total_views += message.views
                count += 1

        # Вычисляем среднее количество просмотров
        average_views = total_views / count if count > 0 else 0

        # Расчёт процента активности
        if subscribers_count > 0:
            activity_percentage = (average_views / subscribers_count) * 100
        else:
            activity_percentage = 0

        return {
            "average_views_last_30_days": average_views,
            "subscribers_count": subscribers_count,
            "audience_activity_percentage": round(activity_percentage, 2)
        }
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/verify/")
async def verify_channel_description(group_id: int | str):
    try:
        # Получаем информацию о чате
        chat = await app_client.get_chat(group_id)
        
        # Получаем описание чата
        description = chat.description
        
        # Проверяем наличие "COLLABA25" в описании
        if description and "COLLABA25" in description:
            return {"status": "Verified", "message": "The description contains 'COLLABA25'."}
        else:
            return {"status": "Not Verified", "message": "The description does not contain 'COLLABA25'."}
    
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/get/")
async def get_channel_info(group_id: int | str):
    chat_id = group_id
    try:
        # Получаем информацию о чате
        chat = await app_client.get_chat(chat_id)
        subs_count = chat.members_count
        description = chat.description
        
        # Получаем среднее количество просмотров за последние 30 дней
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        total_views = 0
        count = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=1000):  # Увеличьте лимит при необходимости
            if message.date >= start_date and message.views is not None:
                total_views += message.views
                count += 1

        # Вычисляем среднее количество просмотров
        avg_views = round(total_views / count, 1) if count > 0 else 0

        # Расчёт процента активности
        activity_percentage = round((avg_views / subs_count) * 100, 1) if subs_count > 0 else 0

        # Проверка на наличие "COLLABA25" в описании
        description_check = "COLLABA25" in description if description else False
        
        # Получаем количество сообщений за последние 30 дней
        total_messages = 0
        last_30_days_messages = 0

        async for message in app_client.get_chat_history(chat_id=chat_id, limit=1000):  # Увеличьте лимит при необходимости
            total_messages += 1  # Увеличиваем общее количество сообщений
            if message.date >= start_date:
                last_30_days_messages += 1  # Увеличиваем количество сообщений за последние 30 дней

        # Собираем всю информацию
        return {
            "total_messages": total_messages,
            "messages_30_days": last_30_days_messages,
            "avg_views_30_days": avg_views,
            "subscribers": subs_count,
            "activity_percentage": activity_percentage,
            "collaba25_in_description": description_check,
        }
    except RPCError as e:
        raise HTTPException(status_code=400, detail=f"Telegram API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# Запуск FastAPI с использованием Uvicorn (для локального тестирования)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
