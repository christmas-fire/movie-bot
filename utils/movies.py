from datetime import datetime

def format_movie(title: str, added_at: datetime, is_watched: bool,
                 watched_at: datetime, rating: float) -> str:
    text = (
        f"<b>{title}</b>\n"
        f"Добавлен {added_at.strftime("%d.%m.%Y")}\n"
    )
    
    if not is_watched:
        text += f"<i>Не просмотрено</i>\n"
    
    if is_watched and watched_at != None:
        text += (
            f"<i>Просмотрено {watched_at.strftime("%d.%m.%Y")}</i>\n"
        )
        
    if rating != None:
        text += f"<i>Оценка: ⭐️{rating}</i>\n" 
        
    return text
