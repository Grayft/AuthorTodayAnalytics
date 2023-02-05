from scrapy import Spider, Selector
import re


class AuthorTodaySpider(Spider):
    name = 'author_today'
    start_urls = [
        'https://author.today/work/genre/all?eg=-&fnd=false&page=1'
    ]

    def parse(self, response):
        """Парсит общие данные о всех книгах на сайте"""

        yield self.get_books_on_page(response)

        next_page = self.get_next_page(response)
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def get_books_on_page(self, response) -> dict:
        books = {}
        for panel in response.css('div.book-row'):
            book_data = self.get_book_data(panel)
            books.update({
                panel.css('div.book-title a::text').get().strip(): book_data
            })
        return books

    def get_book_data(self, panel: Selector) -> dict:
        """Парсятся нужные поля книги"""

        common_details = self._get_common_details(panel)
        details = self._get_details(panel)
        statistics = self._get_statistics(panel)
        return {**common_details, **details, **statistics}

    def get_next_page(self, response) -> str:
        """Возвращает относительную ссылку на следующую страницу,
        основываясь на кнопке 'Вперед' в пагинации"""
        return response.css('li.next.skipToNext a::attr(href)').get()

    def _get_common_details(self, panel: Selector) -> dict:
        """Парсинг относительной ссылки, автора, формат и жанры книги"""
        genres = panel.css('div.book-genres a::text').getall()
        common_details = {
            'part_url': panel.css('div.book-title a::attr(href)').get(),
            'author': {
                'name': panel.css('div.book-author a::text').get(),
                'part_url': panel.css('div.book-author a::attr(href)').get()
            },
            'type': genres.pop(0),
            'genres': genres,
        }
        return common_details

    def _get_statistics(self, panel: Selector) -> dict:
        """Парсинг кол-во просмотров, лайков, комментариев и рецензий"""
        raw_statistics = panel.css(
            'div.book-stats span::attr(data-hint)').getall()
        statistics_list = list(map(
            lambda s: s.replace('\xa0', ''), raw_statistics))

        statistics_dict = {
            'cnt_view': self._get_int_value_from_str(statistics_list[0]),
            'cnt_likes': self._get_int_value_from_str(statistics_list[1]),
            'cnt_comments': self._get_int_value_from_str(statistics_list[2]),
            'cnt_review': self._get_int_value_from_str(statistics_list[3]),
        }
        return statistics_dict

    def _get_int_value_from_str(self, str_with_num: str) -> int:
        """Возвращает первое появившееся число в строке"""
        if not str_with_num:
            return None
        value_pattern = re.compile(r'\d+')
        value = re.search(value_pattern, str_with_num).group()
        return int(value)

    def _get_details(self, panel: Selector):
        """Парсинг кол-ва знаков, статуса,
        названия цикла и типа доступа книги."""
        left_part, right_part = panel.css('div.row.book-details div.col-xs-6')
        flag_exclusive = panel.css('div.ribbon span::text').get()
        details = {
            'volume': self._get_book_volume(left_part),
            'access': left_part.css('span.text-success::text').get(),
            'access_price': self._get_int_value_from_str(
                left_part.css('span.text-bold.text-success::text').get()),
            'full_price': self._get_int_value_from_str(
                left_part.css('span.crossed-text::text').get()),
            'sale': left_part.css('span.label-success.m0::text').get(),
            'status': self._get_status_book(right_part),
            'cycle': right_part.css('a::text').get(),
            'flag_exclusive': flag_exclusive or None,
        }
        return details

    def _get_book_volume(self, left_part_details: Selector) -> dict:
        """Возвращает объем книги в виде словаря:
            {'cnt_signs': int} - для текстовой книги
            {'time_duration': str} - для аудиокниги"""
        cnt_signs = left_part_details.css('span.hint-top::text').get()
        if cnt_signs:
            return {'cnt_signs': self._get_int_value_from_str(
                cnt_signs.replace('\xa0', ''))
            }
        time_duration = left_part_details.css('div div::text').getall()[1]
        if time_duration:
            return {'time_duration': time_duration.strip()}

    def _get_status_book(self, right_part_details: Selector) -> str:
        """Возвращает статус книги."""
        in_progress_status = right_part_details.css(
            'span.text-primary::text').get()
        if in_progress_status:
            return in_progress_status.strip()

        full_text_status = right_part_details.css(
            'span.text-success::text').get()
        if full_text_status:
            return full_text_status.strip()
