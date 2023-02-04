from scrapy import Spider


class AuthorTodaySpider(Spider):
    name = 'author_today'
    start_urls = [
        'https://author.today/work/genres'
    ]

    def parse(self, response):
        genres = response.css('div.panel b a::text').getall()

        yield {'genres': genres}

    def parse_books_titles(self, response):
        pass