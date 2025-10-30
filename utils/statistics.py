import io
import logging
from collections import defaultdict

import matplotlib.pyplot as plt

from database.movies import get_movies_by_user

async def generate_movie_statistics(user_id: str) -> tuple[str, io.BytesIO | None, io.BytesIO | None, io.BytesIO | None]:
    try:
        movies = await get_movies_by_user(added_by=user_id)

        if not movies:
            return "У вас пока нет фильмов в списке.", None, None, None

        watched_count = 0
        unwatched_count = 0
        total_rated_count = 0
        unrated_watched_count = 0 
        
        rating_counts = defaultdict(int)
        
        for movie in movies:
            if movie.is_watched:
                watched_count += 1
                if movie.rating is not None:
                    rating = movie.rating 
                    if 1.0 <= rating <= 10.0:
                        rating_counts[rating] += 1 
                        total_rated_count += 1
                else:
                    unrated_watched_count += 1 
            else:
                unwatched_count += 1

        text_report = (
            f"<blockquote>📈 Статистика</blockquote>\n\n"
            f"<b>Фильмов в коллекции: {watched_count + unwatched_count}</b>\n"
            f"Просмотрено: {watched_count}\n"
            f"Не просмотрено: {unwatched_count}\n"
            f"Оценено: {total_rated_count}\n"
        )
        
        ratings_plot_buffer = None
        if total_rated_count > 0:
            plt.style.use('fivethirtyeight')
            fig_ratings, ax_ratings = plt.subplots(figsize=(7, 7))

            sorted_ratings = sorted(rating_counts.items(), key=lambda item: item[0])
            
            labels = [str(r) for r, count in sorted_ratings]
            sizes = [count for r, count in sorted_ratings]

            wedges, texts, autotexts = ax_ratings.pie(
                sizes, 
                labels=labels, 
                autopct='%1.1f%%', 
                startangle=90, 
                wedgeprops={'edgecolor': 'black'}
            )
            ax_ratings.axis('equal') 
            ax_ratings.set_title(f'Статистика по оценкам', fontsize=16)
            plt.setp(autotexts, size=10, weight="bold")
            
            ratings_plot_buffer = io.BytesIO()
            fig_ratings.savefig(ratings_plot_buffer, format='png', bbox_inches='tight', dpi=150)
            plt.close(fig_ratings)
            ratings_plot_buffer.seek(0)

        status_plot_buffer = None
        if watched_count + unwatched_count > 0:
            plt.style.use('fivethirtyeight')
            fig_status, ax_status = plt.subplots(figsize=(6, 4))
            
            status_labels = ['Просмотрено', 'Не просмотрено']
            status_data = [watched_count, unwatched_count]
            colors = ["#1B9853", "#D53E18"]
            
            bars = ax_status.bar(status_labels, status_data, color=colors)
            for bar in bars:
                yval = bar.get_height()
                ax_status.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), ha='center', va='bottom', fontsize=12)

            ax_status.set_title('Статистика просмотра фильмов', fontsize=16)
            
            ax_status.spines['left'].set_visible(False)
            ax_status.get_yaxis().set_visible(False)
            ax_status.spines['right'].set_visible(False)
            ax_status.spines['top'].set_visible(False)
            ax_status.tick_params(axis='x', length=0)
            
            status_plot_buffer = io.BytesIO()
            fig_status.savefig(status_plot_buffer, format='png', bbox_inches='tight', dpi=150)
            plt.close(fig_status)
            status_plot_buffer.seek(0)

        rated_status_plot_buffer = None
        if watched_count > 0: 
            plt.style.use('fivethirtyeight')
            fig_rated, ax_rated = plt.subplots(figsize=(6, 4))
            
            rated_labels = ['Оценено', 'Не оценено']
            rated_data = [total_rated_count, unrated_watched_count]
            rated_colors = ["#D48A00", "#7B7777"] 
            
            bars = ax_rated.bar(rated_labels, rated_data, color=rated_colors)

            for bar in bars:
                yval = bar.get_height()
                ax_rated.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), ha='center', va='bottom', fontsize=12)

            ax_rated.set_title('Статистика оценивания фильмов', fontsize=16)
            
            ax_rated.spines['left'].set_visible(False)
            ax_rated.get_yaxis().set_visible(False)
            ax_rated.spines['right'].set_visible(False)
            ax_rated.spines['top'].set_visible(False)
            ax_rated.tick_params(axis='x', length=0)
            
            rated_status_plot_buffer = io.BytesIO()
            fig_rated.savefig(rated_status_plot_buffer, format='png', bbox_inches='tight', dpi=150)
            plt.close(fig_rated)
            rated_status_plot_buffer.seek(0)
            
        return text_report, ratings_plot_buffer, status_plot_buffer, rated_status_plot_buffer

    except Exception as e:
        logging.error(f"Error generating statistics for user {user_id}: {e}")
        return "Произошла ошибка при получении статистики.", None, None, None
    