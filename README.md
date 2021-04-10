# Scrapers

This package contains scrapers for websites and generic tools. 

## scrap_trustpilot.py
```python
from scrapers.scrap_trustpilot import scrap_reviews_trustpilot
url = "https://fr.trustpilot.com/review/www.compagnie-des-sens.fr"
res = scrap_reviews_truspilot(url)
res
{
'url': 'https://fr.trustpilot.com/review/www.compagnie-des-sens.fr',
'n_reviews': 24,
'reviews': [
    {
        'rating_star': '5 etoiles : excellent',
        'date': '2020-08-25T07:27:32+00:00',
        'title': 'Offre des excellents produits purs',
        'review': 'Offre des excellents produits purs , naturels et pas agressif sur la peau . Je recommande cette marque .',
        'n_reviews_customer_hide': '1 avis',
        'is_verified_hide': False,
        'verification_source_hide': '',
        'review_source_hide': '',
        'reply_content_hide': '',
        'rating_star_cleaned_hide': 5,
        'n_reviews_customer_cleaned_hide': 1,
        'date_year_month_hide': '2020-08',
        'text_cleaned_hide': 'offre des excellents produits purs offre des excellents produits purs , naturels et pas agressif sur la peau . je recommande cette marque .',
        'page': 1
    },
    ...
]}
```

## scrap_avisverifies.py
```python
from scrapers.scrap_avisverifies import scrap_reviews_avisverifies
url = "https://www.avis-verifies.com/avis-clients/skinjay.com"
res = scrap_reviews_avisverifies(url)
res
{
'url': 'https://www.avis-verifies.com/avis-clients/skinjay.com',
'n_reviews': 84,
'reviews': [
    {
        'rating_star': '5',
        'date': '21/11/2020',
        'review': 'Commande livree rapidement \r\nParfait',
        'details_hide': 'suite a une experience du 11/11/2020',
        'rating_star_cleaned_hide': 5,
        'date_year_month_hide': '2020-11',
        'text_cleaned_hide': 'commande livree rapidement \r\nparfait',
        'page': 1
    },
    ...
 ]}
```