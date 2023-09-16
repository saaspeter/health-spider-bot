import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Identity, Compose, MapCompose


def replace_line_break(value):
    return value.replace('\n', '').strip()

# note: DefaultLoader will get the first result which will only fetch the first one for a List
class DefaultLoader(ItemLoader):
    default_input_processor = MapCompose(str, str.strip)
    default_output_processor = TakeFirst()


# not use TakeFirst(), so can get all the List items, so not use DefaultLoader
class ListPageLoader(ItemLoader):
    # text_out = Compose(Join(), lambda s: s.strip())
    # for source_sitetag, it is a string, not list, so cannot use MapCompose,
    # the original string value will become list when executing loader.add_value, so need use TakeFirst()
    source_sitetag_out = TakeFirst()
    pass


class MedicineDiseaseItemLoader(DefaultLoader):
    full_article_out = TakeFirst()
    pass

