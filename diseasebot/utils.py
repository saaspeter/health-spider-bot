from diseasebot import urls
import json
from scrapy import Selector
from diseasebot import projectConfig
from bs4 import BeautifulSoup

def getMedicineNameFromListPageNode(website, value):
    if website == urls.WEB_SITE_DRUGS:
        return getATagTextFromNode(value)
    else:
        pass

def getMedicineLinkFromListPageNode(website, value):
    if website == urls.WEB_SITE_DRUGS:
        href = getATagLinkFromNode(value)
        if href and not (href.lower().startswith('http://') or href.lower().startswith('https://')):
            return website+href
        else:
            return href
    else:
        pass


def getDiseaseNameFromListPageNode(website, value):
    return getMedicineNameFromListPageNode(website, value)


def getDiseaseLinkFromListPageNode(website, value):
    return getMedicineLinkFromListPageNode(website, value)

def getATagTextFromNode(value):
    """get text from Html A Tag
    value format: <a href='https://www.drugs.com/aaa'>Aspine</a>"""
    if not value:
        return ''
    selector = Selector(text=value)
    # selector.remove()
    text = selector.xpath('//a/text()').extract_first()
    return text


def getATagLinkFromNode(value):
    """get Href from Html A Tag
    value format: <a href='https://www.drugs.com/aaa'>Aspine</a>"""
    if not value:
        return ''
    selector = Selector(text=value)
    return selector.xpath('//a/@href').extract_first()


# for html node, delete html tag, only retain the text
def deleteHtmlNode(item, field_name, *nodes_express):
    if item and field_name and nodes_express and len(nodes_express)>0:
        value = item.get(field_name)
        if not value:
            return item
        selector = Selector(text=value)
        for node_temp in nodes_express:
            selector.xpath(node_temp).drop()

        # covert selector into text again


# extract Generic name or brand name from html node
def extractNameTemp(item, field_name, website):
    if not item or not item.get(field_name):
        print('error: in extractNameTemp method, item.field_name is empty, field name:'+field_name+' , url:'+item.get("source_url"))
        pass
    if website == urls.WEB_SITE_DRUGS:
        # extract name_general from name_temp
        """
        for drug.com site, the name_temp like this:
        <p class="drug-subtitle">
            <b>Generic name:</b> <a href="a.html">valproic acid</a> (oral route)<br>
            <b>Drug class:</b> <a href="a.html">Fatty acid derivative anticonvulsants</a>
        </p>
        or below format:
        <p class="drug-subtitle">
            <b>Generic name:</b> sildenafil (oral) [&nbsp;<i>sil-DEN-a-fil</i>&nbsp;]<br>
            <b>Brand names:</b> <a href="/a.html">Revatio</a>,<a href="/viagra.html">Viagra</a><br>
        </p>
        """
        # field_value is the 'drug-subtitle' node value, it includes: generic name, brand name
        field_value = item.get(field_name)
        if not field_value or ('Generic name:' not in field_value):
            return item

        selector = Selector(text=field_value)
        # but here, only extract 'Generic name'
        generic_name = selector.xpath('//p[@class="drug-subtitle"]/b[text()="Generic name:"]/following-sibling::'
                               'text()[1]')[0].extract().strip()
        if not generic_name:
            generic_name = selector.xpath('//p[@class="drug-subtitle"]/b[text()="Generic name:"]/following-sibling::'
                                   'a[1]/text()')[0].extract().strip()

        if generic_name:
            if generic_name.endswith('['):
                generic_name = generic_name[:-1]
            generic_name = generic_name.split('(oral')[0].strip()
            # some drugs have so long generic_name, but not necessary, and db has 300 length limit, so trim it
            if len(generic_name) > 300:
                generic_name = generic_name[:300]
            item['name_general'] = generic_name
            # check is_general
            medicine_name = item.get('name')
            if generic_name.lower() != medicine_name.lower():
                item['is_general'] = 0
            else:
                item['is_general'] = 1

        return item
    else:
        pass


def getRequestMetaCustomKey(key):
    return projectConfig.REQUEST_META_PREFIX + key


# extract the pure text from html content
def extractTextFromHtml(html_content: str) -> str:
    if not html_content:
        return html_content
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.text
    # also can use this method, need review the finial result effect.
    # text = soup.get_text()
    return text
